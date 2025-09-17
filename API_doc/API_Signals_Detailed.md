# Glassnode API - Signals 详细文档

## 概述

Signals API 是 Glassnode 平台中专门用于提供市场信号和指标数据的核心接口。该 API 集成了多种技术分析和链上分析信号，为交易者和分析师提供综合的市场情报。

信号数据包括：
- **技术信号**: RSI、MACD、布林带等传统技术指标
- **链上信号**: 网络活跃度、资金流向、持仓变化等区块链特有指标
- **情绪信号**: 恐慌贪婪指数、社交媒体情绪、市场参与者行为
- **宏观信号**: 宏观经济指标对加密货币市场的影响
- **复合信号**: 多维度数据融合产生的综合市场信号

## 基础信息

**Base URL**: `https://api.glassnode.com/v1/metrics/signals`

**支持的参数**:
- `a`: 资产符号 (btc, eth, etc.)
- `i`: 时间间隔 (1h, 24h, 1w, 1month)
- `s`: 开始时间戳
- `u`: 结束时间戳
- `f`: 输出格式 (JSON, CSV)
- `c`: 货币单位 (native, usd)

## 核心端点

### 1. 技术信号 (Technical Signals)

```python
# RSI 相对强弱指数
GET /v1/metrics/signals/rsi
# 参数: period (默认14), overbought (默认70), oversold (默认30)

# MACD 指标
GET /v1/metrics/signals/macd
# 参数: fast_period (默认12), slow_period (默认26), signal_period (默认9)

# 布林带
GET /v1/metrics/signals/bollinger_bands
# 参数: period (默认20), std_dev (默认2)

# 移动平均线交叉
GET /v1/metrics/signals/ma_crossover
# 参数: short_period (默认50), long_period (默认200)
```

### 2. 链上信号 (On-chain Signals)

```python
# 网络价值交易比 (NVT)
GET /v1/metrics/signals/nvt_signal

# 市值实现比 (MVRV)
GET /v1/metrics/signals/mvrv_ratio

# 长期持有者信号
GET /v1/metrics/signals/lth_behavior

# 矿工流出信号
GET /v1/metrics/signals/miner_outflow
```

### 3. 情绪信号 (Sentiment Signals)

```python
# 恐慌贪婪指数
GET /v1/metrics/signals/fear_greed_index

# 社交情绪指数
GET /v1/metrics/signals/social_sentiment

# 资金费率信号
GET /v1/metrics/signals/funding_rate_signal

# 期权看跌看涨比
GET /v1/metrics/signals/put_call_ratio
```

### 4. 宏观信号 (Macro Signals)

```python
# 美元指数相关性
GET /v1/metrics/signals/dxy_correlation

# 黄金相关性
GET /v1/metrics/signals/gold_correlation

# 股市相关性
GET /v1/metrics/signals/stock_correlation

# 通胀预期影响
GET /v1/metrics/signals/inflation_impact
```

## Python 实现

```python
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings('ignore')

@dataclass
class SignalConfig:
    """信号配置类"""
    rsi_period: int = 14
    rsi_overbought: float = 70
    rsi_oversold: float = 30
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    bb_period: int = 20
    bb_std_dev: float = 2
    ma_short: int = 50
    ma_long: int = 200

@dataclass
class SignalResult:
    """信号结果类"""
    signal_type: str
    signal_value: float
    signal_strength: str
    confidence: float
    timestamp: datetime
    recommendation: str
    risk_level: str

class SignalsAnalyzer:
    """
    Signals API 数据分析器
    
    提供全面的信号分析功能，包括技术信号、链上信号、情绪信号和宏观信号的计算与分析。
    """
    
    def __init__(self, api_key: str):
        """
        初始化分析器
        
        Args:
            api_key: Glassnode API密钥
        """
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/signals"
        self.headers = {'X-API-KEY': api_key}
        self.config = SignalConfig()
        
    def fetch_technical_signals(self, asset: str = 'btc', 
                              timeframe: str = '24h',
                              days_back: int = 90) -> pd.DataFrame:
        """
        获取技术信号数据
        
        Args:
            asset: 资产符号
            timeframe: 时间间隔
            days_back: 历史天数
            
        Returns:
            包含技术信号的DataFrame
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        signals_data = []
        
        # RSI 信号
        rsi_url = f"{self.base_url}/rsi"
        rsi_params = {
            'a': asset,
            'i': timeframe,
            's': int(start_time.timestamp()),
            'u': int(end_time.timestamp()),
            'period': self.config.rsi_period
        }
        
        try:
            response = requests.get(rsi_url, headers=self.headers, params=rsi_params)
            if response.status_code == 200:
                rsi_data = response.json()
                for item in rsi_data:
                    signals_data.append({
                        'timestamp': pd.to_datetime(item['t'], unit='s'),
                        'rsi': item['v'],
                        'signal_type': 'technical'
                    })
        except Exception as e:
            print(f"Error fetching RSI data: {e}")
        
        # MACD 信号
        macd_url = f"{self.base_url}/macd"
        macd_params = {
            'a': asset,
            'i': timeframe,
            's': int(start_time.timestamp()),
            'u': int(end_time.timestamp()),
            'fast_period': self.config.macd_fast,
            'slow_period': self.config.macd_slow,
            'signal_period': self.config.macd_signal
        }
        
        try:
            response = requests.get(macd_url, headers=self.headers, params=macd_params)
            if response.status_code == 200:
                macd_data = response.json()
                # 合并MACD数据到现有数据
                for i, item in enumerate(macd_data):
                    if i < len(signals_data):
                        signals_data[i].update({
                            'macd_line': item.get('macd', 0),
                            'macd_signal': item.get('signal', 0),
                            'macd_histogram': item.get('histogram', 0)
                        })
        except Exception as e:
            print(f"Error fetching MACD data: {e}")
        
        if signals_data:
            df = pd.DataFrame(signals_data)
            df = df.set_index('timestamp')
            return df
        else:
            # 返回模拟数据用于演示
            return self._generate_sample_technical_signals(days_back)
    
    def fetch_onchain_signals(self, asset: str = 'btc',
                            timeframe: str = '24h',
                            days_back: int = 90) -> pd.DataFrame:
        """
        获取链上信号数据
        
        Args:
            asset: 资产符号
            timeframe: 时间间隔
            days_back: 历史天数
            
        Returns:
            包含链上信号的DataFrame
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        signals_data = []
        
        # NVT信号
        nvt_url = f"{self.base_url}/nvt_signal"
        nvt_params = {
            'a': asset,
            'i': timeframe,
            's': int(start_time.timestamp()),
            'u': int(end_time.timestamp())
        }
        
        try:
            response = requests.get(nvt_url, headers=self.headers, params=nvt_params)
            if response.status_code == 200:
                nvt_data = response.json()
                for item in nvt_data:
                    signals_data.append({
                        'timestamp': pd.to_datetime(item['t'], unit='s'),
                        'nvt_signal': item['v'],
                        'signal_type': 'onchain'
                    })
        except Exception as e:
            print(f"Error fetching NVT data: {e}")
        
        # MVRV信号
        mvrv_url = f"{self.base_url}/mvrv_ratio"
        try:
            response = requests.get(mvrv_url, headers=self.headers, params=nvt_params)
            if response.status_code == 200:
                mvrv_data = response.json()
                for i, item in enumerate(mvrv_data):
                    if i < len(signals_data):
                        signals_data[i]['mvrv_ratio'] = item['v']
        except Exception as e:
            print(f"Error fetching MVRV data: {e}")
        
        if signals_data:
            df = pd.DataFrame(signals_data)
            df = df.set_index('timestamp')
            return df
        else:
            return self._generate_sample_onchain_signals(days_back)
    
    def fetch_sentiment_signals(self, asset: str = 'btc',
                              timeframe: str = '24h',
                              days_back: int = 90) -> pd.DataFrame:
        """
        获取情绪信号数据
        
        Args:
            asset: 资产符号
            timeframe: 时间间隔
            days_back: 历史天数
            
        Returns:
            包含情绪信号的DataFrame
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        # 返回模拟数据用于演示
        return self._generate_sample_sentiment_signals(days_back)
    
    def calculate_composite_signal(self, 
                                 technical_df: pd.DataFrame,
                                 onchain_df: pd.DataFrame,
                                 sentiment_df: pd.DataFrame,
                                 weights: Dict[str, float] = None) -> pd.DataFrame:
        """
        计算复合信号
        
        Args:
            technical_df: 技术信号数据
            onchain_df: 链上信号数据
            sentiment_df: 情绪信号数据
            weights: 权重配置
            
        Returns:
            复合信号DataFrame
        """
        if weights is None:
            weights = {
                'technical': 0.4,
                'onchain': 0.4,
                'sentiment': 0.2
            }
        
        # 合并所有信号数据
        combined_df = pd.concat([technical_df, onchain_df, sentiment_df], axis=1)
        combined_df = combined_df.fillna(method='ffill').fillna(method='bfill')
        
        # 标准化各个信号
        tech_signals = self._normalize_technical_signals(combined_df)
        onchain_signals = self._normalize_onchain_signals(combined_df)
        sentiment_signals = self._normalize_sentiment_signals(combined_df)
        
        # 计算复合信号
        combined_df['composite_signal'] = (
            tech_signals * weights['technical'] +
            onchain_signals * weights['onchain'] +
            sentiment_signals * weights['sentiment']
        )
        
        # 生成信号强度
        combined_df['signal_strength'] = combined_df['composite_signal'].apply(
            self._get_signal_strength
        )
        
        # 生成推荐
        combined_df['recommendation'] = combined_df['composite_signal'].apply(
            self._get_recommendation
        )
        
        return combined_df
    
    def _normalize_technical_signals(self, df: pd.DataFrame) -> pd.Series:
        """标准化技术信号"""
        tech_score = 0
        
        # RSI信号评分
        if 'rsi' in df.columns:
            rsi_score = df['rsi'].apply(lambda x: 
                1 if x > self.config.rsi_overbought else
                -1 if x < self.config.rsi_oversold else 0
            )
            tech_score += rsi_score * 0.3
        
        # MACD信号评分
        if 'macd_histogram' in df.columns:
            macd_score = np.sign(df['macd_histogram'])
            tech_score += macd_score * 0.4
        
        # 移动平均线信号评分（模拟）
        ma_score = np.random.choice([-1, 0, 1], size=len(df), p=[0.3, 0.4, 0.3])
        tech_score += ma_score * 0.3
        
        return tech_score / 3  # 标准化到[-1, 1]
    
    def _normalize_onchain_signals(self, df: pd.DataFrame) -> pd.Series:
        """标准化链上信号"""
        onchain_score = 0
        
        # NVT信号评分
        if 'nvt_signal' in df.columns:
            nvt_percentile = df['nvt_signal'].rolling(window=30).rank(pct=True)
            nvt_score = (nvt_percentile - 0.5) * 2  # 转换到[-1, 1]
            onchain_score += nvt_score * 0.4
        
        # MVRV信号评分
        if 'mvrv_ratio' in df.columns:
            mvrv_score = df['mvrv_ratio'].apply(lambda x:
                1 if x > 3.2 else
                -1 if x < 1.0 else
                (x - 2.1) / 1.1  # 线性映射到[-1, 1]
            )
            onchain_score += mvrv_score * 0.6
        
        return onchain_score
    
    def _normalize_sentiment_signals(self, df: pd.DataFrame) -> pd.Series:
        """标准化情绪信号"""
        sentiment_score = 0
        
        # 恐慌贪婪指数评分
        if 'fear_greed_index' in df.columns:
            fg_score = (df['fear_greed_index'] - 50) / 50  # 转换到[-1, 1]
            sentiment_score += fg_score * 0.5
        
        # 资金费率信号评分
        if 'funding_rate' in df.columns:
            funding_score = np.tanh(df['funding_rate'] * 1000)  # 标准化
            sentiment_score += funding_score * 0.5
        
        return sentiment_score
    
    def _get_signal_strength(self, signal_value: float) -> str:
        """获取信号强度"""
        abs_signal = abs(signal_value)
        if abs_signal >= 0.8:
            return "Very Strong"
        elif abs_signal >= 0.6:
            return "Strong"
        elif abs_signal >= 0.4:
            return "Moderate"
        elif abs_signal >= 0.2:
            return "Weak"
        else:
            return "Neutral"
    
    def _get_recommendation(self, signal_value: float) -> str:
        """获取交易推荐"""
        if signal_value >= 0.6:
            return "Strong Buy"
        elif signal_value >= 0.3:
            return "Buy"
        elif signal_value >= 0.1:
            return "Weak Buy"
        elif signal_value <= -0.6:
            return "Strong Sell"
        elif signal_value <= -0.3:
            return "Sell"
        elif signal_value <= -0.1:
            return "Weak Sell"
        else:
            return "Hold"
    
    def generate_trading_signals(self, composite_df: pd.DataFrame,
                               stop_loss_pct: float = 0.05,
                               take_profit_pct: float = 0.15) -> List[Dict]:
        """
        生成交易信号
        
        Args:
            composite_df: 复合信号数据
            stop_loss_pct: 止损百分比
            take_profit_pct: 止盈百分比
            
        Returns:
            交易信号列表
        """
        signals = []
        position = None
        
        for idx, row in composite_df.iterrows():
            signal_value = row['composite_signal']
            recommendation = row['recommendation']
            
            # 开仓信号
            if position is None:
                if signal_value >= 0.6:  # 强烈买入信号
                    signals.append({
                        'timestamp': idx,
                        'action': 'BUY',
                        'signal_strength': row['signal_strength'],
                        'signal_value': signal_value,
                        'confidence': abs(signal_value),
                        'stop_loss': -stop_loss_pct,
                        'take_profit': take_profit_pct
                    })
                    position = 'LONG'
                elif signal_value <= -0.6:  # 强烈卖出信号
                    signals.append({
                        'timestamp': idx,
                        'action': 'SELL',
                        'signal_strength': row['signal_strength'],
                        'signal_value': signal_value,
                        'confidence': abs(signal_value),
                        'stop_loss': stop_loss_pct,
                        'take_profit': -take_profit_pct
                    })
                    position = 'SHORT'
            
            # 平仓信号
            else:
                if (position == 'LONG' and signal_value <= -0.3) or \
                   (position == 'SHORT' and signal_value >= 0.3):
                    signals.append({
                        'timestamp': idx,
                        'action': 'CLOSE',
                        'signal_strength': row['signal_strength'],
                        'signal_value': signal_value,
                        'confidence': abs(signal_value),
                        'position_closed': position
                    })
                    position = None
        
        return signals
    
    def analyze_signal_performance(self, signals: List[Dict],
                                 price_data: pd.Series) -> Dict:
        """
        分析信号表现
        
        Args:
            signals: 交易信号列表
            price_data: 价格数据
            
        Returns:
            表现分析结果
        """
        if not signals:
            return {'error': 'No signals to analyze'}
        
        trades = []
        current_trade = None
        
        for signal in signals:
            timestamp = signal['timestamp']
            action = signal['action']
            
            if action in ['BUY', 'SELL'] and current_trade is None:
                current_trade = {
                    'entry_time': timestamp,
                    'entry_price': price_data.get(timestamp, 0),
                    'action': action,
                    'signal_strength': signal['signal_strength']
                }
            elif action == 'CLOSE' and current_trade is not None:
                exit_price = price_data.get(timestamp, 0)
                if current_trade['action'] == 'BUY':
                    pnl = (exit_price - current_trade['entry_price']) / current_trade['entry_price']
                else:
                    pnl = (current_trade['entry_price'] - exit_price) / current_trade['entry_price']
                
                trades.append({
                    'entry_time': current_trade['entry_time'],
                    'exit_time': timestamp,
                    'entry_price': current_trade['entry_price'],
                    'exit_price': exit_price,
                    'action': current_trade['action'],
                    'pnl': pnl,
                    'signal_strength': current_trade['signal_strength']
                })
                current_trade = None
        
        if not trades:
            return {'error': 'No completed trades to analyze'}
        
        trades_df = pd.DataFrame(trades)
        
        # 计算表现指标
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] < 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        
        profit_factor = abs(avg_win * winning_trades / (avg_loss * losing_trades)) if losing_trades > 0 else float('inf')
        
        total_return = trades_df['pnl'].sum()
        sharpe_ratio = trades_df['pnl'].mean() / trades_df['pnl'].std() if trades_df['pnl'].std() > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': self._calculate_max_drawdown(trades_df['pnl'])
        }
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """计算最大回撤"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def visualize_signals(self, composite_df: pd.DataFrame,
                         signals: List[Dict],
                         price_data: pd.Series = None):
        """
        可视化信号分析
        
        Args:
            composite_df: 复合信号数据
            signals: 交易信号列表
            price_data: 价格数据（可选）
        """
        fig = make_subplots(
            rows=4, cols=1,
            subplot_titles=[
                'Price and Trading Signals',
                'Composite Signal',
                'Technical Signals',
                'On-chain & Sentiment Signals'
            ],
            vertical_spacing=0.08,
            row_heights=[0.3, 0.25, 0.25, 0.2]
        )
        
        # 如果没有价格数据，生成模拟数据
        if price_data is None:
            price_data = pd.Series(
                index=composite_df.index,
                data=50000 + np.cumsum(np.random.randn(len(composite_df)) * 1000)
            )
        
        # 第1行：价格和交易信号
        fig.add_trace(
            go.Scatter(
                x=price_data.index,
                y=price_data.values,
                mode='lines',
                name='Price',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )
        
        # 添加交易信号标记
        buy_signals = [s for s in signals if s['action'] == 'BUY']
        sell_signals = [s for s in signals if s['action'] == 'SELL']
        
        if buy_signals:
            buy_times = [s['timestamp'] for s in buy_signals]
            buy_prices = [price_data.get(t, 0) for t in buy_times]
            fig.add_trace(
                go.Scatter(
                    x=buy_times,
                    y=buy_prices,
                    mode='markers',
                    name='Buy Signal',
                    marker=dict(color='green', size=10, symbol='triangle-up')
                ),
                row=1, col=1
            )
        
        if sell_signals:
            sell_times = [s['timestamp'] for s in sell_signals]
            sell_prices = [price_data.get(t, 0) for t in sell_times]
            fig.add_trace(
                go.Scatter(
                    x=sell_times,
                    y=sell_prices,
                    mode='markers',
                    name='Sell Signal',
                    marker=dict(color='red', size=10, symbol='triangle-down')
                ),
                row=1, col=1
            )
        
        # 第2行：复合信号
        fig.add_trace(
            go.Scatter(
                x=composite_df.index,
                y=composite_df['composite_signal'],
                mode='lines',
                name='Composite Signal',
                line=dict(color='purple', width=2)
            ),
            row=2, col=1
        )
        
        # 添加信号阈值线
        fig.add_hline(y=0.6, line_dash="dash", line_color="green", 
                     annotation_text="Strong Buy", row=2, col=1)
        fig.add_hline(y=-0.6, line_dash="dash", line_color="red", 
                     annotation_text="Strong Sell", row=2, col=1)
        fig.add_hline(y=0, line_dash="solid", line_color="gray", 
                     annotation_text="Neutral", row=2, col=1)
        
        # 第3行：技术信号
        if 'rsi' in composite_df.columns:
            fig.add_trace(
                go.Scatter(
                    x=composite_df.index,
                    y=composite_df['rsi'],
                    mode='lines',
                    name='RSI',
                    line=dict(color='orange', width=1.5)
                ),
                row=3, col=1
            )
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        
        if 'macd_histogram' in composite_df.columns:
            fig.add_trace(
                go.Bar(
                    x=composite_df.index,
                    y=composite_df['macd_histogram'],
                    name='MACD Histogram',
                    marker_color='lightblue',
                    opacity=0.7
                ),
                row=3, col=1
            )
        
        # 第4行：链上和情绪信号
        if 'nvt_signal' in composite_df.columns:
            fig.add_trace(
                go.Scatter(
                    x=composite_df.index,
                    y=composite_df['nvt_signal'],
                    mode='lines',
                    name='NVT Signal',
                    line=dict(color='cyan', width=1.5),
                    yaxis='y4'
                ),
                row=4, col=1
            )
        
        if 'fear_greed_index' in composite_df.columns:
            fig.add_trace(
                go.Scatter(
                    x=composite_df.index,
                    y=composite_df['fear_greed_index'],
                    mode='lines',
                    name='Fear & Greed Index',
                    line=dict(color='magenta', width=1.5),
                    yaxis='y5'
                ),
                row=4, col=1
            )
        
        # 更新布局
        fig.update_layout(
            title='Comprehensive Signal Analysis Dashboard',
            height=1200,
            showlegend=True,
            template='plotly_white'
        )
        
        fig.show()
    
    def _generate_sample_technical_signals(self, days_back: int) -> pd.DataFrame:
        """生成示例技术信号数据"""
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=days_back),
            end=datetime.now(),
            freq='D'
        )
        
        np.random.seed(42)
        data = {
            'rsi': np.random.uniform(20, 80, len(dates)),
            'macd_line': np.random.normal(0, 500, len(dates)),
            'macd_signal': np.random.normal(0, 400, len(dates)),
            'signal_type': 'technical'
        }
        
        data['macd_histogram'] = data['macd_line'] - data['macd_signal']
        
        df = pd.DataFrame(data, index=dates)
        return df
    
    def _generate_sample_onchain_signals(self, days_back: int) -> pd.DataFrame:
        """生成示例链上信号数据"""
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=days_back),
            end=datetime.now(),
            freq='D'
        )
        
        np.random.seed(43)
        data = {
            'nvt_signal': np.random.uniform(0, 150, len(dates)),
            'mvrv_ratio': np.random.uniform(0.8, 4.0, len(dates)),
            'lth_behavior': np.random.uniform(-1, 1, len(dates)),
            'signal_type': 'onchain'
        }
        
        df = pd.DataFrame(data, index=dates)
        return df
    
    def _generate_sample_sentiment_signals(self, days_back: int) -> pd.DataFrame:
        """生成示例情绪信号数据"""
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=days_back),
            end=datetime.now(),
            freq='D'
        )
        
        np.random.seed(44)
        data = {
            'fear_greed_index': np.random.uniform(10, 90, len(dates)),
            'social_sentiment': np.random.uniform(-1, 1, len(dates)),
            'funding_rate': np.random.normal(0, 0.001, len(dates)),
            'put_call_ratio': np.random.uniform(0.5, 2.0, len(dates)),
            'signal_type': 'sentiment'
        }
        
        df = pd.DataFrame(data, index=dates)
        return df

# 使用示例
def main():
    """主函数 - 演示Signals API的使用"""
    
    # 初始化分析器
    analyzer = SignalsAnalyzer('your_api_key_here')
    
    print("=== Glassnode Signals API 分析演示 ===\n")
    
    # 1. 获取各类信号数据
    print("1. 获取信号数据...")
    technical_signals = analyzer.fetch_technical_signals('btc', '24h', 90)
    onchain_signals = analyzer.fetch_onchain_signals('btc', '24h', 90)
    sentiment_signals = analyzer.fetch_sentiment_signals('btc', '24h', 90)
    
    print(f"技术信号数据形状: {technical_signals.shape}")
    print(f"链上信号数据形状: {onchain_signals.shape}")
    print(f"情绪信号数据形状: {sentiment_signals.shape}")
    
    # 2. 计算复合信号
    print("\n2. 计算复合信号...")
    composite_signals = analyzer.calculate_composite_signal(
        technical_signals, onchain_signals, sentiment_signals
    )
    
    print(f"复合信号数据形状: {composite_signals.shape}")
    print("\n最新信号值:")
    latest_signal = composite_signals.iloc[-1]
    print(f"复合信号值: {latest_signal['composite_signal']:.3f}")
    print(f"信号强度: {latest_signal['signal_strength']}")
    print(f"推荐: {latest_signal['recommendation']}")
    
    # 3. 生成交易信号
    print("\n3. 生成交易信号...")
    trading_signals = analyzer.generate_trading_signals(composite_signals)
    
    print(f"生成交易信号数量: {len(trading_signals)}")
    if trading_signals:
        print("\n最近5个交易信号:")
        for signal in trading_signals[-5:]:
            print(f"时间: {signal['timestamp'].strftime('%Y-%m-%d')}, "
                  f"动作: {signal['action']}, "
                  f"强度: {signal['signal_strength']}, "
                  f"置信度: {signal['confidence']:.3f}")
    
    # 4. 分析信号表现
    print("\n4. 分析信号表现...")
    # 生成模拟价格数据
    price_data = pd.Series(
        index=composite_signals.index,
        data=50000 + np.cumsum(np.random.randn(len(composite_signals)) * 1000)
    )
    
    performance = analyzer.analyze_signal_performance(trading_signals, price_data)
    
    if 'error' not in performance:
        print(f"总交易次数: {performance['total_trades']}")
        print(f"胜率: {performance['win_rate']:.2%}")
        print(f"盈亏比: {performance['profit_factor']:.2f}")
        print(f"总收益率: {performance['total_return']:.2%}")
        print(f"夏普比率: {performance['sharpe_ratio']:.3f}")
        print(f"最大回撤: {performance['max_drawdown']:.2%}")
    else:
        print(f"无法分析表现: {performance['error']}")
    
    # 5. 信号统计分析
    print("\n5. 信号统计分析...")
    signal_stats = {
        'RSI超买信号': len(technical_signals[technical_signals['rsi'] > 70]),
        'RSI超卖信号': len(technical_signals[technical_signals['rsi'] < 30]),
        'MACD金叉信号': len(technical_signals[technical_signals['macd_histogram'] > 0]),
        'MACD死叉信号': len(technical_signals[technical_signals['macd_histogram'] < 0]),
        'NVT高估信号': len(onchain_signals[onchain_signals['nvt_signal'] > 100]),
        'MVRV高估信号': len(onchain_signals[onchain_signals['mvrv_ratio'] > 3.2]),
        '恐慌信号': len(sentiment_signals[sentiment_signals['fear_greed_index'] < 25]),
        '贪婪信号': len(sentiment_signals[sentiment_signals['fear_greed_index'] > 75])
    }
    
    for signal_type, count in signal_stats.items():
        print(f"{signal_type}: {count}次")
    
    # 6. 可视化信号
    print("\n6. 生成信号可视化...")
    try:
        analyzer.visualize_signals(composite_signals, trading_signals, price_data)
        print("信号可视化图表已生成")
    except Exception as e:
        print(f"可视化生成失败: {e}")
    
    print("\n=== 分析完成 ===")

if __name__ == "__main__":
    main()
```

## 数据处理示例

### 信号强度分析

```python
def analyze_signal_strength_distribution():
    """分析信号强度分布"""
    analyzer = SignalsAnalyzer('your_api_key_here')
    
    # 获取复合信号数据
    technical_signals = analyzer.fetch_technical_signals('btc', '24h', 365)
    onchain_signals = analyzer.fetch_onchain_signals('btc', '24h', 365)
    sentiment_signals = analyzer.fetch_sentiment_signals('btc', '24h', 365)
    
    composite_signals = analyzer.calculate_composite_signal(
        technical_signals, onchain_signals, sentiment_signals
    )
    
    # 分析信号强度分布
    strength_counts = composite_signals['signal_strength'].value_counts()
    
    plt.figure(figsize=(12, 8))
    
    # 信号强度分布饼图
    plt.subplot(2, 2, 1)
    plt.pie(strength_counts.values, labels=strength_counts.index, autopct='%1.1f%%')
    plt.title('Signal Strength Distribution')
    
    # 复合信号时间序列
    plt.subplot(2, 2, 2)
    plt.plot(composite_signals.index, composite_signals['composite_signal'])
    plt.axhline(y=0.6, color='g', linestyle='--', alpha=0.7, label='Strong Buy')
    plt.axhline(y=-0.6, color='r', linestyle='--', alpha=0.7, label='Strong Sell')
    plt.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
    plt.title('Composite Signal Over Time')
    plt.legend()
    
    # 信号值分布直方图
    plt.subplot(2, 2, 3)
    plt.hist(composite_signals['composite_signal'], bins=50, alpha=0.7)
    plt.axvline(x=0.6, color='g', linestyle='--', label='Strong Buy Threshold')
    plt.axvline(x=-0.6, color='r', linestyle='--', label='Strong Sell Threshold')
    plt.title('Signal Value Distribution')
    plt.xlabel('Signal Value')
    plt.ylabel('Frequency')
    plt.legend()
    
    # 推荐分布
    plt.subplot(2, 2, 4)
    recommendation_counts = composite_signals['recommendation'].value_counts()
    plt.bar(recommendation_counts.index, recommendation_counts.values)
    plt.title('Recommendation Distribution')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.show()
    
    return composite_signals
```

### 信号相关性分析

```python
def analyze_signal_correlations():
    """分析不同信号之间的相关性"""
    analyzer = SignalsAnalyzer('your_api_key_here')
    
    # 获取各类信号
    technical_signals = analyzer.fetch_technical_signals('btc', '24h', 180)
    onchain_signals = analyzer.fetch_onchain_signals('btc', '24h', 180)
    sentiment_signals = analyzer.fetch_sentiment_signals('btc', '24h', 180)
    
    # 合并所有信号
    all_signals = pd.concat([technical_signals, onchain_signals, sentiment_signals], axis=1)
    
    # 选择数值列计算相关性
    numeric_columns = all_signals.select_dtypes(include=[np.number]).columns
    correlation_matrix = all_signals[numeric_columns].corr()
    
    # 绘制相关性热力图
    plt.figure(figsize=(14, 10))
    sns.heatmap(correlation_matrix, 
                annot=True, 
                cmap='coolwarm', 
                center=0,
                square=True,
                fmt='.2f')
    plt.title('Signal Correlation Matrix')
    plt.tight_layout()
    plt.show()
    
    # 找出高相关性信号对
    high_correlations = []
    for i in range(len(correlation_matrix.columns)):
        for j in range(i+1, len(correlation_matrix.columns)):
            corr_value = correlation_matrix.iloc[i, j]
            if abs(corr_value) > 0.7:  # 高相关性阈值
                high_correlations.append({
                    'signal1': correlation_matrix.columns[i],
                    'signal2': correlation_matrix.columns[j],
                    'correlation': corr_value
                })
    
    print("高相关性信号对:")
    for corr in sorted(high_correlations, key=lambda x: abs(x['correlation']), reverse=True):
        print(f"{corr['signal1']} vs {corr['signal2']}: {corr['correlation']:.3f}")
    
    return correlation_matrix
```

## 交易策略示例

### 多信号融合策略

```python
class MultiSignalTradingStrategy:
    """多信号融合交易策略"""
    
    def __init__(self, analyzer: SignalsAnalyzer):
        self.analyzer = analyzer
        self.position = None
        self.entry_price = 0
        self.trades = []
        
    def execute_strategy(self, composite_signals: pd.DataFrame,
                        price_data: pd.Series,
                        initial_capital: float = 10000) -> Dict:
        """
        执行多信号融合策略
        
        Args:
            composite_signals: 复合信号数据
            price_data: 价格数据
            initial_capital: 初始资金
            
        Returns:
            策略执行结果
        """
        capital = initial_capital
        portfolio_value = []
        
        for timestamp, row in composite_signals.iterrows():
            current_price = price_data.get(timestamp, 0)
            signal_value = row['composite_signal']
            signal_strength = row['signal_strength']
            
            # 开仓逻辑
            if self.position is None:
                if signal_value >= 0.7 and signal_strength in ['Strong', 'Very Strong']:
                    # 强买入信号
                    position_size = capital * 0.8  # 使用80%资金
                    shares = position_size / current_price
                    
                    self.position = {
                        'type': 'LONG',
                        'shares': shares,
                        'entry_price': current_price,
                        'entry_time': timestamp,
                        'stop_loss': current_price * 0.95,  # 5%止损
                        'take_profit': current_price * 1.20  # 20%止盈
                    }
                    
                    capital -= position_size
                    
                elif signal_value <= -0.7 and signal_strength in ['Strong', 'Very Strong']:
                    # 强卖出信号（做空）
                    position_size = capital * 0.8
                    shares = position_size / current_price
                    
                    self.position = {
                        'type': 'SHORT',
                        'shares': shares,
                        'entry_price': current_price,
                        'entry_time': timestamp,
                        'stop_loss': current_price * 1.05,  # 5%止损
                        'take_profit': current_price * 0.80  # 20%止盈
                    }
                    
                    capital += position_size  # 做空获得资金
            
            # 平仓逻辑
            elif self.position is not None:
                should_close = False
                close_reason = ""
                
                # 信号反转平仓
                if (self.position['type'] == 'LONG' and signal_value <= -0.4) or \
                   (self.position['type'] == 'SHORT' and signal_value >= 0.4):
                    should_close = True
                    close_reason = "Signal Reversal"
                
                # 止损/止盈平仓
                elif self.position['type'] == 'LONG':
                    if current_price <= self.position['stop_loss']:
                        should_close = True
                        close_reason = "Stop Loss"
                    elif current_price >= self.position['take_profit']:
                        should_close = True
                        close_reason = "Take Profit"
                
                elif self.position['type'] == 'SHORT':
                    if current_price >= self.position['stop_loss']:
                        should_close = True
                        close_reason = "Stop Loss"
                    elif current_price <= self.position['take_profit']:
                        should_close = True
                        close_reason = "Take Profit"
                
                # 执行平仓
                if should_close:
                    if self.position['type'] == 'LONG':
                        pnl = (current_price - self.position['entry_price']) * self.position['shares']
                        capital += self.position['shares'] * current_price
                    else:  # SHORT
                        pnl = (self.position['entry_price'] - current_price) * self.position['shares']
                        capital -= self.position['shares'] * current_price
                    
                    # 记录交易
                    self.trades.append({
                        'entry_time': self.position['entry_time'],
                        'exit_time': timestamp,
                        'type': self.position['type'],
                        'entry_price': self.position['entry_price'],
                        'exit_price': current_price,
                        'shares': self.position['shares'],
                        'pnl': pnl,
                        'pnl_pct': pnl / (self.position['entry_price'] * self.position['shares']),
                        'close_reason': close_reason,
                        'signal_value': signal_value
                    })
                    
                    self.position = None
            
            # 计算当前组合价值
            current_portfolio_value = capital
            if self.position is not None:
                if self.position['type'] == 'LONG':
                    current_portfolio_value += self.position['shares'] * current_price
                else:  # SHORT
                    current_portfolio_value += self.position['shares'] * (2 * self.position['entry_price'] - current_price)
            
            portfolio_value.append({
                'timestamp': timestamp,
                'portfolio_value': current_portfolio_value,
                'capital': capital,
                'signal_value': signal_value
            })
        
        # 计算策略表现
        portfolio_df = pd.DataFrame(portfolio_value)
        portfolio_df.set_index('timestamp', inplace=True)
        
        final_value = portfolio_df['portfolio_value'].iloc[-1]
        total_return = (final_value - initial_capital) / initial_capital
        
        # 计算其他指标
        portfolio_returns = portfolio_df['portfolio_value'].pct_change().dropna()
        sharpe_ratio = portfolio_returns.mean() / portfolio_returns.std() * np.sqrt(252) if portfolio_returns.std() > 0 else 0
        max_drawdown = self._calculate_max_drawdown(portfolio_df['portfolio_value'])
        
        return {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_trades': len(self.trades),
            'winning_trades': len([t for t in self.trades if t['pnl'] > 0]),
            'win_rate': len([t for t in self.trades if t['pnl'] > 0]) / len(self.trades) if self.trades else 0,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'portfolio_history': portfolio_df,
            'trades': self.trades
        }
    
    def _calculate_max_drawdown(self, portfolio_values: pd.Series) -> float:
        """计算最大回撤"""
        running_max = portfolio_values.expanding().max()
        drawdown = (portfolio_values - running_max) / running_max
        return drawdown.min()
    
    def plot_strategy_performance(self, results: Dict):
        """绘制策略表现"""
        portfolio_df = results['portfolio_history']
        trades = results['trades']
        
        fig, axes = plt.subplots(3, 1, figsize=(15, 12))
        
        # 组合价值曲线
        axes[0].plot(portfolio_df.index, portfolio_df['portfolio_value'], 
                    label='Portfolio Value', linewidth=2)
        axes[0].axhline(y=results['initial_capital'], color='gray', 
                       linestyle='--', alpha=0.7, label='Initial Capital')
        axes[0].set_title('Portfolio Value Over Time')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # 信号值
        axes[1].plot(portfolio_df.index, portfolio_df['signal_value'], 
                    color='purple', alpha=0.7, label='Composite Signal')
        axes[1].axhline(y=0.7, color='green', linestyle='--', alpha=0.7)
        axes[1].axhline(y=-0.7, color='red', linestyle='--', alpha=0.7)
        axes[1].axhline(y=0, color='gray', linestyle='-', alpha=0.5)
        axes[1].set_title('Signal Values')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # 累计收益
        cumulative_returns = (portfolio_df['portfolio_value'] / results['initial_capital'] - 1) * 100
        axes[2].plot(portfolio_df.index, cumulative_returns, 
                    color='green', linewidth=2)
        axes[2].axhline(y=0, color='gray', linestyle='-', alpha=0.5)
        axes[2].set_title('Cumulative Returns (%)')
        axes[2].grid(True, alpha=0.3)
        
        # 标记交易点
        for trade in trades:
            if trade['type'] == 'LONG':
                axes[0].axvline(x=trade['entry_time'], color='green', alpha=0.3)
                axes[0].axvline(x=trade['exit_time'], color='red', alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # 打印策略统计
        print("策略表现统计:")
        print(f"总收益率: {results['total_return']:.2%}")
        print(f"总交易次数: {results['total_trades']}")
        print(f"胜率: {results['win_rate']:.2%}")
        print(f"夏普比率: {results['sharpe_ratio']:.3f}")
        print(f"最大回撤: {results['max_drawdown']:.2%}")
```

### 动态权重优化策略

```python
class DynamicWeightOptimizer:
    """动态权重优化器"""
    
    def __init__(self, lookback_window: int = 30):
        self.lookback_window = lookback_window
        
    def optimize_signal_weights(self, 
                              technical_signals: pd.DataFrame,
                              onchain_signals: pd.DataFrame,
                              sentiment_signals: pd.DataFrame,
                              price_data: pd.Series) -> pd.DataFrame:
        """
        基于历史表现动态优化信号权重
        
        Args:
            technical_signals: 技术信号数据
            onchain_signals: 链上信号数据
            sentiment_signals: 情绪信号数据
            price_data: 价格数据
            
        Returns:
            包含动态权重的DataFrame
        """
        combined_df = pd.concat([technical_signals, onchain_signals, sentiment_signals], axis=1)
        combined_df = combined_df.fillna(method='ffill').fillna(method='bfill')
        
        # 计算价格变化
        price_changes = price_data.pct_change().shift(-1)  # 下一期收益
        
        weights_history = []
        
        for i in range(self.lookback_window, len(combined_df)):
            # 获取历史窗口数据
            window_data = combined_df.iloc[i-self.lookback_window:i]
            window_returns = price_changes.iloc[i-self.lookback_window:i]
            
            # 计算各类信号与收益的相关性
            tech_correlation = self._calculate_signal_correlation(
                window_data, window_returns, 'technical'
            )
            onchain_correlation = self._calculate_signal_correlation(
                window_data, window_returns, 'onchain'
            )
            sentiment_correlation = self._calculate_signal_correlation(
                window_data, window_returns, 'sentiment'
            )
            
            # 基于相关性计算权重
            correlations = np.array([tech_correlation, onchain_correlation, sentiment_correlation])
            abs_correlations = np.abs(correlations)
            
            # 防止除零错误
            if abs_correlations.sum() > 0:
                weights = abs_correlations / abs_correlations.sum()
            else:
                weights = np.array([1/3, 1/3, 1/3])  # 均等权重
            
            weights_history.append({
                'timestamp': combined_df.index[i],
                'tech_weight': weights[0],
                'onchain_weight': weights[1],
                'sentiment_weight': weights[2],
                'tech_corr': tech_correlation,
                'onchain_corr': onchain_correlation,
                'sentiment_corr': sentiment_correlation
            })
        
        weights_df = pd.DataFrame(weights_history)
        weights_df.set_index('timestamp', inplace=True)
        
        return weights_df
    
    def _calculate_signal_correlation(self, 
                                    signals_df: pd.DataFrame,
                                    returns: pd.Series,
                                    signal_type: str) -> float:
        """计算特定类型信号与收益的相关性"""
        if signal_type == 'technical':
            signal_columns = ['rsi', 'macd_histogram']
        elif signal_type == 'onchain':
            signal_columns = ['nvt_signal', 'mvrv_ratio']
        else:  # sentiment
            signal_columns = ['fear_greed_index', 'funding_rate']
        
        correlations = []
        for col in signal_columns:
            if col in signals_df.columns:
                valid_data = pd.concat([signals_df[col], returns], axis=1).dropna()
                if len(valid_data) > 2:
                    corr = valid_data.iloc[:, 0].corr(valid_data.iloc[:, 1])
                    if not np.isnan(corr):
                        correlations.append(abs(corr))
        
        return np.mean(correlations) if correlations else 0.0
    
    def apply_dynamic_weights(self,
                            technical_signals: pd.DataFrame,
                            onchain_signals: pd.DataFrame,
                            sentiment_signals: pd.DataFrame,
                            weights_df: pd.DataFrame) -> pd.DataFrame:
        """应用动态权重计算复合信号"""
        combined_df = pd.concat([technical_signals, onchain_signals, sentiment_signals], axis=1)
        combined_df = combined_df.fillna(method='ffill').fillna(method='bfill')
        
        # 标准化信号
        tech_normalized = self._normalize_signals(combined_df, 'technical')
        onchain_normalized = self._normalize_signals(combined_df, 'onchain')
        sentiment_normalized = self._normalize_signals(combined_df, 'sentiment')
        
        # 应用动态权重
        dynamic_signals = []
        for timestamp in weights_df.index:
            if timestamp in combined_df.index:
                weights = weights_df.loc[timestamp]
                
                composite_signal = (
                    tech_normalized.loc[timestamp] * weights['tech_weight'] +
                    onchain_normalized.loc[timestamp] * weights['onchain_weight'] +
                    sentiment_normalized.loc[timestamp] * weights['sentiment_weight']
                )
                
                dynamic_signals.append({
                    'timestamp': timestamp,
                    'composite_signal': composite_signal,
                    'tech_weight': weights['tech_weight'],
                    'onchain_weight': weights['onchain_weight'],
                    'sentiment_weight': weights['sentiment_weight']
                })
        
        dynamic_df = pd.DataFrame(dynamic_signals)
        dynamic_df.set_index('timestamp', inplace=True)
        
        return dynamic_df
    
    def _normalize_signals(self, df: pd.DataFrame, signal_type: str) -> pd.Series:
        """标准化特定类型的信号"""
        if signal_type == 'technical':
            # RSI标准化
            rsi_norm = (df['rsi'] - 50) / 50 if 'rsi' in df.columns else 0
            # MACD标准化
            macd_norm = np.tanh(df['macd_histogram'] / 1000) if 'macd_histogram' in df.columns else 0
            return (rsi_norm + macd_norm) / 2
            
        elif signal_type == 'onchain':
            # NVT标准化
            nvt_norm = np.tanh((df['nvt_signal'] - 75) / 50) if 'nvt_signal' in df.columns else 0
            # MVRV标准化
            mvrv_norm = np.tanh((df['mvrv_ratio'] - 2.1) / 1.1) if 'mvrv_ratio' in df.columns else 0
            return (nvt_norm + mvrv_norm) / 2
            
        else:  # sentiment
            # 恐慌贪婪指数标准化
            fg_norm = (df['fear_greed_index'] - 50) / 50 if 'fear_greed_index' in df.columns else 0
            # 资金费率标准化
            funding_norm = np.tanh(df['funding_rate'] * 1000) if 'funding_rate' in df.columns else 0
            return (fg_norm + funding_norm) / 2
```

## 常见问题解答 (FAQ)

### Q1: 如何选择最适合的信号组合？
A: 选择信号组合需要考虑：
1. **市场环境**: 趋势市场偏重技术信号，震荡市场偏重链上信号
2. **时间框架**: 短期交易重视情绪信号，长期投资重视基本面信号
3. **风险偏好**: 保守策略增加确认信号，激进策略可用单一强信号
4. **历史表现**: 通过回测验证不同组合的历史效果

### Q2: 信号出现冲突时如何处理？
A: 处理信号冲突的方法：
1. **权重投票**: 根据信号强度和历史准确率分配权重
2. **时间优先**: 优先考虑时效性更强的信号
3. **确认等待**: 等待更多信号确认再行动
4. **分批执行**: 根据不同信号分批建仓或平仓

### Q3: 如何避免信号过拟合？
A: 避免过拟合的策略：
1. **样本外验证**: 使用未参与优化的数据验证策略
2. **简单原则**: 优先选择逻辑简单、参数较少的信号
3. **稳健性测试**: 测试参数微调对结果的影响
4. **定期重新训练**: 定期更新模型参数适应市场变化

### Q4: 信号延迟问题如何解决？
A: 解决信号延迟的方法：
1. **实时数据**: 确保使用最新的API数据
2. **预测模型**: 使用机器学习预测信号走向
3. **领先指标**: 结合领先性较强的链上指标
4. **多时间框架**: 结合不同时间周期的信号

### Q5: 如何评估信号质量？
A: 信号质量评估指标：
1. **准确率**: 信号预测正确的比例
2. **夏普比率**: 风险调整后收益
3. **最大回撤**: 策略可能的最大损失
4. **信号覆盖度**: 有效信号在总时间中的占比
5. **稳定性**: 不同市场环境下的表现一致性

## 最佳实践建议

### 1. 信号配置优化
```python
# 推荐的信号配置
optimal_config = {
    'rsi_period': 14,           # RSI周期
    'rsi_overbought': 75,       # RSI超买阈值
    'rsi_oversold': 25,         # RSI超卖阈值
    'macd_fast': 12,            # MACD快线周期
    'macd_slow': 26,            # MACD慢线周期
    'composite_buy_threshold': 0.6,    # 复合买入阈值
    'composite_sell_threshold': -0.6,  # 复合卖出阈值
    'signal_confirmation_period': 2    # 信号确认周期
}
```

### 2. 风险管理规则
```python
risk_management_rules = {
    'max_position_size': 0.8,      # 最大仓位比例
    'stop_loss_percentage': 0.05,  # 止损比例
    'take_profit_percentage': 0.15, # 止盈比例
    'max_daily_trades': 3,         # 日最大交易次数
    'signal_strength_filter': 'Strong',  # 最低信号强度要求
    'confirmation_signals': 2       # 需要确认的信号数量
}
```

### 3. 性能监控指标
```python
performance_metrics = {
    'sharpe_ratio_target': 1.5,     # 目标夏普比率
    'max_drawdown_limit': 0.15,     # 最大回撤限制
    'win_rate_target': 0.55,        # 目标胜率
    'profit_factor_target': 1.8,    # 目标盈亏比
    'monitoring_frequency': '1h'     # 监控频率
}
```

### 4. 信号优化流程
1. **数据收集**: 收集充足的历史数据进行分析
2. **特征工程**: 构建有效的技术和基本面特征
3. **信号测试**: 单独测试每个信号的有效性
4. **组合优化**: 找到最佳的信号权重组合
5. **回测验证**: 在历史数据上验证策略表现
6. **实盘监控**: 实时监控信号表现并调整
7. **持续改进**: 根据市场变化持续优化信号

Signals API 为加密货币交易提供了强大的市场信号分析能力。通过合理配置和使用这些信号，交易者可以更好地把握市场机会，提高交易决策的质量和成功率。记住，任何交易信号都不是100%准确的，应该结合多种分析方法和严格的风险管理来使用。