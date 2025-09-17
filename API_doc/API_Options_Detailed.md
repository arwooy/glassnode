# Options（期权数据）API 详细文档

## 概述

Options API 提供加密货币期权市场的全面数据分析，包括期权交易量、未平仓合约、隐含波动率、希腊字母、期权流动、套利机会等。这些期权数据对于理解市场情绪、预测价格波动、构建复杂交易策略、风险管理和衍生品套利至关重要。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/options/`

**支持的资产**: BTC, ETH 及其主要期权合约

**期权类型覆盖**:
- 看涨期权 (Call Options)
- 看跌期权 (Put Options)  
- 美式期权和欧式期权
- 各种到期日期权

**数据来源**:
- Deribit（主要数据源）
- OKEx Options
- Binance Options
- Bit.com
- PowerTrade

**数据更新频率**: 
- 实时数据：1分钟
- 聚合数据：10分钟、1小时
- 日终数据：每日UTC时间凌晨更新

## 核心端点

### 1. 期权交易量分析

#### 1.1 总交易量

**端点**: `/volume_total`

**描述**: 期权市场的总交易量，反映市场活跃度和参与度。

**参数**:
- `a`: 资产符号（如 BTC）
- `i`: 时间间隔（1h, 24h, 1w）
- `s`: 开始时间戳
- `option_type`: 期权类型（call, put, all）

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/options/volume_total?a=BTC&i=24h&s=1609459200" \
  -H "X-Api-Key: YOUR_API_KEY"
```

**示例响应**:
```json
[
  {
    "t": 1726790400,
    "v": {
      "call_volume": 45678901.23,
      "put_volume": 34567890.12,
      "total_volume": 80246791.35
    }
  }
]
```

#### 1.2 看涨看跌比率

**端点**: `/put_call_ratio`

**描述**: 看跌期权与看涨期权的交易量比率，重要的市场情绪指标。

**参数**:
- `a`: 资产符号
- `i`: 时间间隔
- `metric_type`: 比率类型（volume, open_interest）

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/options/put_call_ratio?a=BTC&i=1h&metric_type=volume" \
  -H "X-Api-Key: YOUR_API_KEY"
```

### 2. 未平仓合约分析

#### 2.1 总未平仓合约

**端点**: `/open_interest`

**描述**: 期权市场的未平仓合约总量，反映市场深度和流动性。

**参数**:
- `a`: 资产符号
- `i`: 时间间隔
- `option_type`: 期权类型
- `expiry`: 到期日过滤器（可选）

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/options/open_interest?a=BTC&i=24h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

#### 2.2 按执行价格分布

**端点**: `/open_interest_by_strike`

**描述**: 按执行价格分布的未平仓合约，显示市场对价格的预期。

**参数**:
- `a`: 资产符号
- `i`: 时间间隔
- `expiry_date`: 特定到期日

### 3. 隐含波动率分析

#### 3.1 隐含波动率指数

**端点**: `/implied_volatility`

**描述**: 期权隐含波动率，反映市场对未来价格波动的预期。

**参数**:
- `a`: 资产符号
- `i`: 时间间隔
- `moneyness`: 价内外程度（atm, itm, otm）

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/options/implied_volatility?a=BTC&i=1h&moneyness=atm" \
  -H "X-Api-Key: YOUR_API_KEY"
```

#### 3.2 波动率偏斜

**端点**: `/volatility_skew`

**描述**: 不同执行价格期权的隐含波动率差异，反映市场对尾部风险的定价。

### 4. 希腊字母分析

#### 4.1 Delta 敞口

**端点**: `/delta_exposure`

**描述**: 市场总Delta敞口，反映方向性风险。

**参数**:
- `a`: 资产符号
- `i`: 时间间隔
- `option_type`: 期权类型

#### 4.2 Gamma 敞口

**端点**: `/gamma_exposure`

**描述**: 市场总Gamma敞口，反映Delta变化的敏感性。

## Python 实现类

```python
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class OptionsAnalyzer:
    """
    Glassnode Options API 分析器
    提供期权数据的获取、分析和可视化功能
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/options/"
        self.headers = {"X-Api-Key": self.api_key}
        
        # 期权相关常数
        self.RISK_FREE_RATE = 0.05  # 无风险利率，可根据实际情况调整
        self.TRADING_DAYS = 365     # 年化天数
        
    def get_option_volume(self, asset: str = 'BTC', days: int = 30) -> Dict:
        """获取期权交易量数据"""
        
        url = self.base_url + "volume_total"
        params = {
            'a': asset,
            'i': '24h',
            's': int((datetime.now() - timedelta(days=days)).timestamp()),
            'u': int(datetime.now().timestamp())
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            return self.analyze_option_volume(data, asset)
            
        except Exception as e:
            print(f"获取期权交易量数据失败: {e}")
            return {}
    
    def analyze_option_volume(self, data: List, asset: str) -> Dict:
        """分析期权交易量数据"""
        
        if not data:
            return {}
        
        # 转换为DataFrame进行分析
        df_data = []
        for entry in data:
            row = {
                'timestamp': pd.to_datetime(entry['t'], unit='s'),
                'call_volume': entry['v'].get('call_volume', 0),
                'put_volume': entry['v'].get('put_volume', 0),
                'total_volume': entry['v'].get('total_volume', 0)
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df.set_index('timestamp', inplace=True)
        
        # 计算统计指标
        stats = {
            'current_total_volume': df['total_volume'].iloc[-1],
            'current_call_volume': df['call_volume'].iloc[-1],
            'current_put_volume': df['put_volume'].iloc[-1],
            'avg_daily_volume': df['total_volume'].mean(),
            'volume_volatility': df['total_volume'].std(),
            'call_put_ratio': df['call_volume'].iloc[-1] / df['put_volume'].iloc[-1] if df['put_volume'].iloc[-1] > 0 else 0,
            'volume_trend': self.calculate_volume_trend(df),
            'activity_level': self.assess_activity_level(df)
        }
        
        return {
            'asset': asset,
            'timestamp': df.index[-1],
            'volume_statistics': stats,
            'volume_trends': self.analyze_volume_trends(df),
            'market_sentiment': self.derive_volume_sentiment(stats),
            'trading_insights': self.generate_volume_insights(stats, df)
        }
    
    def calculate_volume_trend(self, df: pd.DataFrame) -> str:
        """计算交易量趋势"""
        
        if len(df) < 7:
            return 'insufficient_data'
        
        recent_avg = df['total_volume'].tail(7).mean()
        earlier_avg = df['total_volume'].head(7).mean()
        
        if recent_avg > earlier_avg * 1.2:
            return 'increasing'
        elif recent_avg < earlier_avg * 0.8:
            return 'decreasing'
        else:
            return 'stable'
    
    def assess_activity_level(self, df: pd.DataFrame) -> str:
        """评估活跃度水平"""
        
        current_volume = df['total_volume'].iloc[-1]
        avg_volume = df['total_volume'].mean()
        
        if current_volume > avg_volume * 1.5:
            return 'high'
        elif current_volume < avg_volume * 0.5:
            return 'low'
        else:
            return 'normal'
    
    def analyze_volume_trends(self, df: pd.DataFrame) -> Dict:
        """分析交易量趋势"""
        
        trends = {
            'call_trend': '',
            'put_trend': '',
            'ratio_trend': '',
            'correlation_with_spot': 0
        }
        
        if len(df) >= 14:
            # 看涨期权趋势
            call_slope = np.polyfit(range(len(df)), df['call_volume'], 1)[0]
            trends['call_trend'] = 'increasing' if call_slope > 0 else 'decreasing'
            
            # 看跌期权趋势
            put_slope = np.polyfit(range(len(df)), df['put_volume'], 1)[0]
            trends['put_trend'] = 'increasing' if put_slope > 0 else 'decreasing'
            
            # 比率趋势
            df['call_put_ratio'] = df['call_volume'] / df['put_volume'].replace(0, np.nan)
            ratio_slope = np.polyfit(range(len(df)), df['call_put_ratio'].fillna(0), 1)[0]
            trends['ratio_trend'] = 'increasing' if ratio_slope > 0 else 'decreasing'
        
        return trends
    
    def derive_volume_sentiment(self, stats: Dict) -> Dict:
        """从交易量推导市场情绪"""
        
        sentiment = {
            'overall_sentiment': 'neutral',
            'confidence_level': 'medium',
            'sentiment_indicators': []
        }
        
        call_put_ratio = stats.get('call_put_ratio', 1)
        activity_level = stats.get('activity_level', 'normal')
        
        # 基于看涨看跌比率判断情绪
        if call_put_ratio > 1.5:
            sentiment['overall_sentiment'] = 'bullish'
            sentiment['sentiment_indicators'].append("看涨期权交易量显著高于看跌期权")
        elif call_put_ratio < 0.7:
            sentiment['overall_sentiment'] = 'bearish'
            sentiment['sentiment_indicators'].append("看跌期权交易量显著高于看涨期权")
        else:
            sentiment['overall_sentiment'] = 'neutral'
            sentiment['sentiment_indicators'].append("看涨看跌期权交易量相对平衡")
        
        # 基于活跃度调整置信度
        if activity_level == 'high':
            sentiment['confidence_level'] = 'high'
            sentiment['sentiment_indicators'].append("高交易活跃度增强信号可靠性")
        elif activity_level == 'low':
            sentiment['confidence_level'] = 'low'
            sentiment['sentiment_indicators'].append("低交易活跃度降低信号可靠性")
        
        return sentiment
    
    def generate_volume_insights(self, stats: Dict, df: pd.DataFrame) -> List[str]:
        """生成交易量洞察"""
        
        insights = []
        
        # 交易量水平分析
        current_volume = stats['current_total_volume']
        avg_volume = stats['avg_daily_volume']
        
        if current_volume > avg_volume * 2:
            insights.append("当前交易量异常高，可能存在重要市场事件")
        elif current_volume < avg_volume * 0.3:
            insights.append("当前交易量异常低，市场可能缺乏关注")
        
        # 看涨看跌比率分析
        call_put_ratio = stats['call_put_ratio']
        if call_put_ratio > 2:
            insights.append("极高的看涨看跌比率，市场过度乐观")
        elif call_put_ratio < 0.5:
            insights.append("极低的看涨看跌比率，市场过度悲观")
        
        # 趋势分析
        trend = stats['volume_trend']
        if trend == 'increasing':
            insights.append("期权交易量呈上升趋势，市场关注度提高")
        elif trend == 'decreasing':
            insights.append("期权交易量呈下降趋势，市场关注度降低")
        
        return insights
    
    def get_put_call_ratio(self, asset: str = 'BTC', days: int = 30) -> Dict:
        """获取看涨看跌比率数据"""
        
        url = self.base_url + "put_call_ratio"
        params = {
            'a': asset,
            'i': '1h',
            's': int((datetime.now() - timedelta(days=days)).timestamp()),
            'metric_type': 'volume'
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            return self.analyze_put_call_ratio(data, asset)
            
        except Exception as e:
            print(f"获取看涨看跌比率数据失败: {e}")
            return {}
    
    def analyze_put_call_ratio(self, data: List, asset: str) -> Dict:
        """分析看涨看跌比率"""
        
        if not data:
            return {}
        
        # 转换为时间序列
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['t'], unit='s')
        df.set_index('timestamp', inplace=True)
        
        # 计算统计指标
        current_ratio = df['v'].iloc[-1]
        mean_ratio = df['v'].mean()
        std_ratio = df['v'].std()
        
        # 计算Z-score（标准化偏离）
        z_score = (current_ratio - mean_ratio) / std_ratio if std_ratio > 0 else 0
        
        # 计算移动平均
        df['ma_7'] = df['v'].rolling(window=7).mean()
        df['ma_24'] = df['v'].rolling(window=24).mean()
        
        return {
            'asset': asset,
            'current_ratio': current_ratio,
            'historical_mean': mean_ratio,
            'z_score': z_score,
            'ratio_level': self.classify_ratio_level(current_ratio),
            'market_sentiment': self.interpret_ratio_sentiment(current_ratio, z_score),
            'extremes': self.identify_ratio_extremes(df),
            'trading_signals': self.generate_ratio_signals(current_ratio, mean_ratio, z_score)
        }
    
    def classify_ratio_level(self, ratio: float) -> str:
        """分类比率水平"""
        
        if ratio > 1.5:
            return 'extremely_bearish'
        elif ratio > 1.2:
            return 'bearish'
        elif ratio > 0.8:
            return 'neutral'
        elif ratio > 0.6:
            return 'bullish'
        else:
            return 'extremely_bullish'
    
    def interpret_ratio_sentiment(self, ratio: float, z_score: float) -> Dict:
        """解释比率市场情绪"""
        
        sentiment = {
            'primary_signal': '',
            'secondary_signal': '',
            'contrarian_opportunity': False,
            'confidence': 'medium'
        }
        
        # 主要信号
        if ratio > 1.2:
            sentiment['primary_signal'] = 'bearish'
        elif ratio < 0.8:
            sentiment['primary_signal'] = 'bullish'
        else:
            sentiment['primary_signal'] = 'neutral'
        
        # 极端值的逆向信号
        if abs(z_score) > 2:
            sentiment['contrarian_opportunity'] = True
            sentiment['secondary_signal'] = 'contrarian_reversal'
            sentiment['confidence'] = 'high'
        elif abs(z_score) > 1.5:
            sentiment['confidence'] = 'medium'
        else:
            sentiment['confidence'] = 'low'
        
        return sentiment
    
    def identify_ratio_extremes(self, df: pd.DataFrame) -> Dict:
        """识别比率极值"""
        
        extremes = {
            'recent_high': df['v'].tail(168).max(),  # 最近7天的最高值
            'recent_low': df['v'].tail(168).min(),   # 最近7天的最低值
            'all_time_high': df['v'].max(),
            'all_time_low': df['v'].min(),
            'extreme_events': []
        }
        
        # 识别极端事件（超过2个标准差）
        mean_val = df['v'].mean()
        std_val = df['v'].std()
        
        extreme_threshold = 2 * std_val
        extreme_points = df[abs(df['v'] - mean_val) > extreme_threshold]
        
        for idx, row in extreme_points.iterrows():
            extremes['extreme_events'].append({
                'timestamp': idx,
                'ratio': row['v'],
                'type': 'high' if row['v'] > mean_val else 'low'
            })
        
        return extremes
    
    def generate_ratio_signals(self, current: float, mean: float, z_score: float) -> List[str]:
        """生成基于比率的交易信号"""
        
        signals = []
        
        if z_score > 2:
            signals.append("看跌比率极高，考虑逆向买入机会")
        elif z_score > 1.5:
            signals.append("看跌比率偏高，可能存在买入机会")
        elif z_score < -2:
            signals.append("看跌比率极低，考虑逆向卖出机会")
        elif z_score < -1.5:
            signals.append("看跌比率偏低，可能存在卖出机会")
        
        if current > 1.5:
            signals.append("极度恐慌情绪，历史上常为底部信号")
        elif current < 0.5:
            signals.append("极度贪婪情绪，历史上常为顶部信号")
        
        return signals
    
    def get_implied_volatility(self, asset: str = 'BTC', days: int = 30) -> Dict:
        """获取隐含波动率数据"""
        
        url = self.base_url + "implied_volatility"
        params = {
            'a': asset,
            'i': '1h',
            's': int((datetime.now() - timedelta(days=days)).timestamp()),
            'moneyness': 'atm'  # 平值期权
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            return self.analyze_implied_volatility(data, asset)
            
        except Exception as e:
            print(f"获取隐含波动率数据失败: {e}")
            return {}
    
    def analyze_implied_volatility(self, data: List, asset: str) -> Dict:
        """分析隐含波动率"""
        
        if not data:
            return {}
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['t'], unit='s')
        df.set_index('timestamp', inplace=True)
        
        current_iv = df['v'].iloc[-1]
        mean_iv = df['v'].mean()
        std_iv = df['v'].std()
        
        # 计算波动率指标
        analysis = {
            'current_iv': current_iv,
            'mean_iv': mean_iv,
            'iv_percentile': self.calculate_iv_percentile(df['v'], current_iv),
            'iv_rank': self.calculate_iv_rank(df['v'], current_iv),
            'volatility_regime': self.identify_volatility_regime(current_iv, mean_iv, std_iv),
            'term_structure': self.analyze_term_structure(asset),
            'trading_opportunities': self.identify_volatility_opportunities(current_iv, mean_iv)
        }
        
        return analysis
    
    def calculate_iv_percentile(self, iv_series: pd.Series, current_iv: float) -> float:
        """计算隐含波动率百分位"""
        
        return (iv_series < current_iv).sum() / len(iv_series) * 100
    
    def calculate_iv_rank(self, iv_series: pd.Series, current_iv: float) -> float:
        """计算隐含波动率排名"""
        
        min_iv = iv_series.min()
        max_iv = iv_series.max()
        
        if max_iv == min_iv:
            return 50  # 避免除零错误
        
        return (current_iv - min_iv) / (max_iv - min_iv) * 100
    
    def identify_volatility_regime(self, current: float, mean: float, std: float) -> str:
        """识别波动率制度"""
        
        z_score = (current - mean) / std if std > 0 else 0
        
        if z_score > 1.5:
            return 'high_volatility'
        elif z_score < -1.5:
            return 'low_volatility'
        else:
            return 'normal_volatility'
    
    def analyze_term_structure(self, asset: str) -> Dict:
        """分析期限结构"""
        
        # 获取不同到期日的隐含波动率
        term_structure = {
            'shape': 'normal',  # normal, inverted, flat
            'short_term_iv': 0,
            'long_term_iv': 0,
            'term_premium': 0
        }
        
        # 这里简化处理，实际应该获取不同到期日的IV数据
        # 由于API限制，这里使用模拟数据结构
        
        return term_structure
    
    def identify_volatility_opportunities(self, current_iv: float, mean_iv: float) -> List[str]:
        """识别波动率交易机会"""
        
        opportunities = []
        
        iv_ratio = current_iv / mean_iv if mean_iv > 0 else 1
        
        if iv_ratio > 1.3:
            opportunities.append("隐含波动率相对较高，考虑卖出波动率策略")
            opportunities.append("可以考虑卖出跨式或宽跨式策略")
        elif iv_ratio < 0.7:
            opportunities.append("隐含波动率相对较低，考虑买入波动率策略")
            opportunities.append("可以考虑买入跨式或长期期权策略")
        
        if current_iv > 80:
            opportunities.append("绝对波动率很高，市场预期大幅波动")
        elif current_iv < 20:
            opportunities.append("绝对波动率很低，市场可能过于平静")
        
        return opportunities
    
    def get_options_open_interest(self, asset: str = 'BTC', days: int = 30) -> Dict:
        """获取期权未平仓合约数据"""
        
        url = self.base_url + "open_interest"
        params = {
            'a': asset,
            'i': '24h',
            's': int((datetime.now() - timedelta(days=days)).timestamp())
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            return self.analyze_open_interest(data, asset)
            
        except Exception as e:
            print(f"获取未平仓合约数据失败: {e}")
            return {}
    
    def analyze_open_interest(self, data: List, asset: str) -> Dict:
        """分析未平仓合约"""
        
        if not data:
            return {}
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['t'], unit='s')
        df.set_index('timestamp', inplace=True)
        
        # 分离看涨和看跌未平仓合约
        df['call_oi'] = df['v'].apply(lambda x: x.get('call_oi', 0) if isinstance(x, dict) else 0)
        df['put_oi'] = df['v'].apply(lambda x: x.get('put_oi', 0) if isinstance(x, dict) else 0)
        df['total_oi'] = df['call_oi'] + df['put_oi']
        
        analysis = {
            'current_total_oi': df['total_oi'].iloc[-1],
            'current_call_oi': df['call_oi'].iloc[-1],
            'current_put_oi': df['put_oi'].iloc[-1],
            'oi_trend': self.calculate_oi_trend(df),
            'oi_concentration': self.analyze_oi_concentration(df),
            'liquidity_metrics': self.calculate_liquidity_metrics(df),
            'support_resistance': self.identify_oi_levels(asset)
        }
        
        return analysis
    
    def calculate_oi_trend(self, df: pd.DataFrame) -> Dict:
        """计算未平仓合约趋势"""
        
        if len(df) < 7:
            return {}
        
        recent_oi = df['total_oi'].tail(7).mean()
        earlier_oi = df['total_oi'].head(7).mean()
        
        return {
            'direction': 'increasing' if recent_oi > earlier_oi else 'decreasing',
            'change_rate': (recent_oi - earlier_oi) / earlier_oi * 100 if earlier_oi > 0 else 0,
            'volatility': df['total_oi'].std() / df['total_oi'].mean() if df['total_oi'].mean() > 0 else 0
        }
    
    def analyze_oi_concentration(self, df: pd.DataFrame) -> Dict:
        """分析未平仓合约集中度"""
        
        return {
            'call_put_oi_ratio': df['call_oi'].iloc[-1] / df['put_oi'].iloc[-1] if df['put_oi'].iloc[-1] > 0 else 0,
            'oi_distribution': 'call_heavy' if df['call_oi'].iloc[-1] > df['put_oi'].iloc[-1] else 'put_heavy',
            'concentration_score': self.calculate_concentration_score(df)
        }
    
    def calculate_concentration_score(self, df: pd.DataFrame) -> float:
        """计算集中度评分"""
        
        # 基于看涨看跌比率的变异系数
        if len(df) > 1:
            call_put_ratios = df['call_oi'] / df['put_oi'].replace(0, np.nan)
            cv = call_put_ratios.std() / call_put_ratios.mean() if call_put_ratios.mean() > 0 else 0
            return min(100, cv * 100)
        
        return 0
    
    def calculate_liquidity_metrics(self, df: pd.DataFrame) -> Dict:
        """计算流动性指标"""
        
        return {
            'oi_stability': 1 - (df['total_oi'].std() / df['total_oi'].mean()) if df['total_oi'].mean() > 0 else 0,
            'growth_consistency': self.calculate_growth_consistency(df['total_oi']),
            'liquidity_score': self.calculate_liquidity_score(df)
        }
    
    def calculate_growth_consistency(self, series: pd.Series) -> float:
        """计算增长一致性"""
        
        if len(series) < 3:
            return 0
        
        changes = series.pct_change().dropna()
        consistency = 1 - (changes.std() / abs(changes.mean())) if changes.mean() != 0 else 0
        
        return max(0, min(1, consistency))
    
    def calculate_liquidity_score(self, df: pd.DataFrame) -> float:
        """计算流动性评分"""
        
        # 综合考虑未平仓合约规模、稳定性和增长
        size_score = min(100, df['total_oi'].iloc[-1] / 1000000)  # 假设100万为满分
        stability_score = (1 - df['total_oi'].std() / df['total_oi'].mean()) * 100 if df['total_oi'].mean() > 0 else 0
        
        return (size_score + stability_score) / 2
    
    def identify_oi_levels(self, asset: str) -> Dict:
        """识别基于未平仓合约的支撑阻力位"""
        
        # 简化实现，实际需要获取按执行价格分布的未平仓合约数据
        return {
            'major_support_levels': [],
            'major_resistance_levels': [],
            'max_pain_point': 0,  # 最大痛苦点
            'gamma_squeeze_levels': []
        }
    
    def calculate_options_greeks(self, spot_price: float, strike_price: float, 
                               time_to_expiry: float, implied_vol: float, 
                               option_type: str = 'call') -> Dict:
        """计算期权希腊字母"""
        
        # 使用Black-Scholes模型计算希腊字母
        from scipy.stats import norm
        
        # 参数标准化
        S = spot_price
        K = strike_price
        T = time_to_expiry / 365  # 转换为年
        r = self.RISK_FREE_RATE
        sigma = implied_vol / 100  # 转换为小数
        
        # 计算d1和d2
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        # 计算希腊字母
        if option_type.lower() == 'call':
            delta = norm.cdf(d1)
            theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)
        else:  # put
            delta = norm.cdf(d1) - 1
            theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)
        
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100  # 除以100转换为1%变化的影响
        rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100 if option_type.lower() == 'call' else -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100
        
        return {
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega,
            'rho': rho
        }
    
    def analyze_volatility_surface(self, asset: str) -> Dict:
        """分析波动率曲面"""
        
        # 简化的波动率曲面分析
        surface_analysis = {
            'atm_volatility': 0,
            'term_structure_slope': 0,
            'skew_characteristics': {},
            'arbitrage_opportunities': []
        }
        
        return surface_analysis
    
    def generate_options_strategy_recommendations(self, market_outlook: str, 
                                                volatility_outlook: str,
                                                risk_tolerance: str) -> List[Dict]:
        """生成期权策略建议"""
        
        strategies = []
        
        # 基于市场和波动率展望推荐策略
        if market_outlook == 'bullish':
            if volatility_outlook == 'low':
                strategies.append({
                    'strategy': 'Long Call',
                    'description': '买入看涨期权，看好价格上涨且波动率较低',
                    'risk': 'limited',
                    'reward': 'unlimited',
                    'best_scenario': '价格大幅上涨'
                })
                strategies.append({
                    'strategy': 'Bull Call Spread',
                    'description': '牛市看涨价差，降低成本',
                    'risk': 'limited',
                    'reward': 'limited',
                    'best_scenario': '价格温和上涨'
                })
            else:  # high volatility
                strategies.append({
                    'strategy': 'Bull Put Spread',
                    'description': '牛市看跌价差，获得时间价值',
                    'risk': 'limited',
                    'reward': 'limited',
                    'best_scenario': '价格稳定或温和上涨'
                })
        
        elif market_outlook == 'bearish':
            if volatility_outlook == 'low':
                strategies.append({
                    'strategy': 'Long Put',
                    'description': '买入看跌期权，看好价格下跌',
                    'risk': 'limited',
                    'reward': 'high',
                    'best_scenario': '价格大幅下跌'
                })
            else:  # high volatility
                strategies.append({
                    'strategy': 'Bear Call Spread',
                    'description': '熊市看涨价差，获得时间价值',
                    'risk': 'limited',
                    'reward': 'limited',
                    'best_scenario': '价格下跌或保持低位'
                })
        
        elif market_outlook == 'neutral':
            if volatility_outlook == 'low':
                strategies.append({
                    'strategy': 'Iron Condor',
                    'description': '铁鹰策略，从时间衰减中获利',
                    'risk': 'limited',
                    'reward': 'limited',
                    'best_scenario': '价格在一定区间内波动'
                })
            else:  # high volatility
                strategies.append({
                    'strategy': 'Long Straddle',
                    'description': '买入跨式策略，预期大幅波动',
                    'risk': 'limited',
                    'reward': 'unlimited',
                    'best_scenario': '价格大幅波动（任一方向）'
                })
        
        # 根据风险承受能力调整
        if risk_tolerance == 'low':
            strategies = [s for s in strategies if s['risk'] == 'limited']
        
        return strategies
    
    def calculate_strategy_payoff(self, strategy_components: List[Dict], 
                                spot_prices: np.ndarray) -> Dict:
        """计算策略收益图"""
        
        payoffs = np.zeros_like(spot_prices)
        
        for component in strategy_components:
            option_type = component['type']  # 'call' or 'put'
            strike = component['strike']
            premium = component['premium']
            position = component['position']  # 'long' or 'short'
            quantity = component['quantity']
            
            # 计算单个期权的收益
            if option_type == 'call':
                intrinsic_value = np.maximum(spot_prices - strike, 0)
            else:  # put
                intrinsic_value = np.maximum(strike - spot_prices, 0)
            
            # 考虑头寸方向
            if position == 'long':
                option_payoff = (intrinsic_value - premium) * quantity
            else:  # short
                option_payoff = (premium - intrinsic_value) * quantity
            
            payoffs += option_payoff
        
        return {
            'spot_prices': spot_prices,
            'payoffs': payoffs,
            'max_profit': np.max(payoffs),
            'max_loss': np.min(payoffs),
            'breakeven_points': self.find_breakeven_points(spot_prices, payoffs)
        }
    
    def find_breakeven_points(self, spot_prices: np.ndarray, payoffs: np.ndarray) -> List[float]:
        """找到损益平衡点"""
        
        breakeven_points = []
        
        # 找到收益为零的点
        for i in range(len(payoffs) - 1):
            if payoffs[i] * payoffs[i + 1] <= 0:  # 符号变化，表示跨越零点
                # 线性插值找到精确的零点
                if payoffs[i + 1] != payoffs[i]:
                    zero_point = spot_prices[i] - payoffs[i] * (spot_prices[i + 1] - spot_prices[i]) / (payoffs[i + 1] - payoffs[i])
                    breakeven_points.append(zero_point)
        
        return breakeven_points

    def generate_comprehensive_options_report(self, asset: str = 'BTC') -> Dict:
        """生成综合期权报告"""
        
        # 获取各类期权数据
        volume_data = self.get_option_volume(asset)
        put_call_data = self.get_put_call_ratio(asset)
        iv_data = self.get_implied_volatility(asset)
        oi_data = self.get_options_open_interest(asset)
        
        # 综合分析
        report = {
            'asset': asset,
            'report_timestamp': datetime.now().isoformat(),
            'volume_analysis': volume_data,
            'put_call_analysis': put_call_data,
            'volatility_analysis': iv_data,
            'open_interest_analysis': oi_data,
            'market_sentiment_summary': self.synthesize_market_sentiment(
                volume_data, put_call_data, iv_data
            ),
            'trading_opportunities': self.identify_trading_opportunities(
                volume_data, put_call_data, iv_data, oi_data
            ),
            'risk_warnings': self.identify_risk_warnings(
                volume_data, put_call_data, iv_data, oi_data
            )
        }
        
        return report
    
    def synthesize_market_sentiment(self, volume_data: Dict, 
                                  put_call_data: Dict, iv_data: Dict) -> Dict:
        """综合市场情绪"""
        
        sentiment_summary = {
            'overall_sentiment': 'neutral',
            'confidence_level': 'medium',
            'contributing_factors': [],
            'contrarian_signals': []
        }
        
        sentiment_scores = []
        
        # 基于交易量的情绪
        if volume_data and 'market_sentiment' in volume_data:
            vol_sentiment = volume_data['market_sentiment']['overall_sentiment']
            if vol_sentiment == 'bullish':
                sentiment_scores.append(1)
                sentiment_summary['contributing_factors'].append("期权交易量显示乐观情绪")
            elif vol_sentiment == 'bearish':
                sentiment_scores.append(-1)
                sentiment_summary['contributing_factors'].append("期权交易量显示悲观情绪")
            else:
                sentiment_scores.append(0)
        
        # 基于看涨看跌比率的情绪
        if put_call_data and 'market_sentiment' in put_call_data:
            pc_sentiment = put_call_data['market_sentiment']
            if pc_sentiment.get('contrarian_opportunity'):
                sentiment_summary['contrarian_signals'].append("看涨看跌比率显示逆向机会")
        
        # 基于隐含波动率的情绪
        if iv_data and 'volatility_regime' in iv_data:
            vol_regime = iv_data['volatility_regime']
            if vol_regime == 'high_volatility':
                sentiment_summary['contributing_factors'].append("高隐含波动率表明市场不确定性")
            elif vol_regime == 'low_volatility':
                sentiment_summary['contributing_factors'].append("低隐含波动率表明市场平静")
        
        # 综合评估
        if sentiment_scores:
            avg_score = sum(sentiment_scores) / len(sentiment_scores)
            if avg_score > 0.3:
                sentiment_summary['overall_sentiment'] = 'bullish'
            elif avg_score < -0.3:
                sentiment_summary['overall_sentiment'] = 'bearish'
            else:
                sentiment_summary['overall_sentiment'] = 'neutral'
        
        return sentiment_summary
    
    def identify_trading_opportunities(self, volume_data: Dict, put_call_data: Dict, 
                                     iv_data: Dict, oi_data: Dict) -> List[Dict]:
        """识别交易机会"""
        
        opportunities = []
        
        # 基于波动率的机会
        if iv_data:
            for opp in iv_data.get('trading_opportunities', []):
                opportunities.append({
                    'type': 'volatility',
                    'description': opp,
                    'timeframe': 'short_term'
                })
        
        # 基于看涨看跌比率的机会
        if put_call_data and 'trading_signals' in put_call_data:
            for signal in put_call_data['trading_signals']:
                opportunities.append({
                    'type': 'sentiment_contrarian',
                    'description': signal,
                    'timeframe': 'medium_term'
                })
        
        # 基于交易量异常的机会
        if volume_data and 'trading_insights' in volume_data:
            for insight in volume_data['trading_insights']:
                if '异常' in insight:
                    opportunities.append({
                        'type': 'volume_anomaly',
                        'description': insight,
                        'timeframe': 'immediate'
                    })
        
        return opportunities
    
    def identify_risk_warnings(self, volume_data: Dict, put_call_data: Dict,
                             iv_data: Dict, oi_data: Dict) -> List[str]:
        """识别风险警告"""
        
        warnings = []
        
        # 流动性风险
        if oi_data and 'liquidity_metrics' in oi_data:
            liquidity_score = oi_data['liquidity_metrics'].get('liquidity_score', 0)
            if liquidity_score < 30:
                warnings.append("期权流动性较低，可能存在较大买卖价差")
        
        # 极端情绪风险
        if put_call_data and 'ratio_level' in put_call_data:
            ratio_level = put_call_data['ratio_level']
            if ratio_level in ['extremely_bearish', 'extremely_bullish']:
                warnings.append("市场情绪极端，可能出现急剧反转")
        
        # 波动率风险
        if iv_data and 'volatility_regime' in iv_data:
            if iv_data['volatility_regime'] == 'high_volatility':
                warnings.append("隐含波动率处于高位，期权价格可能被高估")
        
        # 交易量异常风险
        if volume_data and 'volume_statistics' in volume_data:
            activity_level = volume_data['volume_statistics'].get('activity_level', 'normal')
            if activity_level == 'low':
                warnings.append("期权交易活跃度低，信号可靠性降低")
        
        return warnings

    def visualize_options_landscape(self, report: Dict, save_path: str = None):
        """可视化期权市场格局"""
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. 看涨看跌比率时间序列
        if 'put_call_analysis' in report:
            # 模拟时间序列数据展示
            ax = axes[0, 0]
            ax.set_title("看涨看跌比率趋势")
            ax.set_ylabel("Put/Call Ratio")
            ax.axhline(y=1, color='gray', linestyle='--', alpha=0.5, label='平衡线')
            ax.axhline(y=1.2, color='red', linestyle='--', alpha=0.5, label='看跌偏好')
            ax.axhline(y=0.8, color='green', linestyle='--', alpha=0.5, label='看涨偏好')
            ax.legend()
        
        # 2. 隐含波动率分布
        if 'volatility_analysis' in report and 'current_iv' in report['volatility_analysis']:
            ax = axes[0, 1]
            current_iv = report['volatility_analysis']['current_iv']
            iv_percentile = report['volatility_analysis'].get('iv_percentile', 50)
            
            # 创建IV分布图
            ax.bar(['当前IV', '历史均值'], [current_iv, current_iv * 0.8], 
                   color=['blue', 'gray'], alpha=0.7)
            ax.set_title("隐含波动率水平")
            ax.set_ylabel("隐含波动率 (%)")
            ax.text(0, current_iv + 1, f'百分位: {iv_percentile:.1f}%', ha='center')
        
        # 3. 交易量分析
        if 'volume_analysis' in report and 'volume_statistics' in report['volume_analysis']:
            ax = axes[1, 0]
            vol_stats = report['volume_analysis']['volume_statistics']
            
            call_vol = vol_stats.get('current_call_volume', 0)
            put_vol = vol_stats.get('current_put_volume', 0)
            
            ax.pie([call_vol, put_vol], labels=['看涨期权', '看跌期权'], 
                   autopct='%1.1f%%', startangle=90)
            ax.set_title("期权交易量分布")
        
        # 4. 市场情绪雷达图
        if 'market_sentiment_summary' in report:
            ax = axes[1, 1]
            
            # 创建简化的情绪指标
            sentiment_metrics = ['交易量情绪', '比率情绪', '波动率情绪', '整体情绪']
            values = [0.6, 0.4, 0.7, 0.5]  # 示例值，实际应从报告中提取
            
            angles = np.linspace(0, 2 * np.pi, len(sentiment_metrics), endpoint=False)
            values += values[:1]
            angles = np.concatenate((angles, [angles[0]]))
            
            ax.plot(angles, values, 'o-', linewidth=2)
            ax.fill(angles, values, alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(sentiment_metrics)
            ax.set_title("市场情绪雷达图")
            ax.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
```

## 数据处理和可视化示例

### 1. 期权交易量分析

```python
# 初始化分析器
analyzer = OptionsAnalyzer(api_key="YOUR_API_KEY")

# 获取比特币期权交易量
btc_volume = analyzer.get_option_volume('BTC', days=30)

print("比特币期权交易量分析:")
print(f"当前总交易量: ${btc_volume['volume_statistics']['current_total_volume']:,.2f}")
print(f"看涨看跌比率: {btc_volume['volume_statistics']['call_put_ratio']:.2f}")
print(f"市场情绪: {btc_volume['market_sentiment']['overall_sentiment']}")
print(f"活跃度水平: {btc_volume['volume_statistics']['activity_level']}")

# 可视化交易量趋势
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# 交易量分布饼图
call_vol = btc_volume['volume_statistics']['current_call_volume']
put_vol = btc_volume['volume_statistics']['current_put_volume']

ax1.pie([call_vol, put_vol], labels=['看涨期权', '看跌期权'], 
        autopct='%1.1f%%', startangle=90, colors=['green', 'red'])
ax1.set_title("期权交易量分布")

# 情绪指标
sentiment_indicators = btc_volume['market_sentiment']['sentiment_indicators']
if sentiment_indicators:
    ax2.text(0.1, 0.5, '\n'.join(sentiment_indicators), 
             transform=ax2.transAxes, fontsize=12,
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    ax2.set_title("市场情绪指标")
    ax2.axis('off')

plt.tight_layout()
plt.show()
```

### 2. 看涨看跌比率分析

```python
def analyze_put_call_ratio_extremes(asset='BTC', days=30):
    """分析看涨看跌比率的极值情况"""
    
    pc_data = analyzer.get_put_call_ratio(asset, days=days)
    
    if not pc_data:
        print("无看涨看跌比率数据")
        return
    
    print(f"{asset} 看涨看跌比率分析:")
    print(f"当前比率: {pc_data['current_ratio']:.2f}")
    print(f"历史平均: {pc_data['historical_mean']:.2f}")
    print(f"Z-Score: {pc_data['z_score']:.2f}")
    print(f"比率水平: {pc_data['ratio_level']}")
    
    # 可视化比率分析
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 当前比率vs历史水平
    ratios = ['当前比率', '历史均值', '极端看涨(0.5)', '极端看跌(1.5)']
    values = [pc_data['current_ratio'], pc_data['historical_mean'], 0.5, 1.5]
    colors = ['blue', 'gray', 'green', 'red']
    
    bars = ax1.bar(ratios, values, color=colors, alpha=0.7)
    ax1.set_title("看涨看跌比率对比")
    ax1.set_ylabel("比率值")
    ax1.axhline(y=1, color='black', linestyle='--', alpha=0.5, label='中性线')
    
    # 添加数值标签
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{value:.2f}', ha='center', va='bottom')
    
    # 交易信号
    signals = pc_data.get('trading_signals', [])
    if signals:
        signal_text = '\n'.join(f"• {signal}" for signal in signals)
        ax2.text(0.05, 0.95, signal_text, transform=ax2.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        ax2.set_title("交易信号")
        ax2.axis('off')
    
    plt.tight_layout()
    plt.show()
    
    # 识别极端事件
    extremes = pc_data.get('extremes', {})
    if extremes.get('extreme_events'):
        print(f"\n近期极端事件 (±2σ):")
        for event in extremes['extreme_events'][-5:]:  # 显示最近5个
            print(f"  {event['timestamp'].strftime('%Y-%m-%d')}: {event['ratio']:.2f} ({event['type']})")
    
    return pc_data

# 分析比特币看涨看跌比率
btc_pc_ratio = analyze_put_call_ratio_extremes('BTC', 30)
```

### 3. 隐含波动率分析

```python
def analyze_implied_volatility_opportunities(asset='BTC'):
    """分析隐含波动率交易机会"""
    
    iv_data = analyzer.get_implied_volatility(asset, days=30)
    
    if not iv_data:
        print("无隐含波动率数据")
        return
    
    print(f"{asset} 隐含波动率分析:")
    print(f"当前IV: {iv_data['current_iv']:.1f}%")
    print(f"历史均值: {iv_data['mean_iv']:.1f}%")
    print(f"IV百分位: {iv_data['iv_percentile']:.1f}%")
    print(f"IV排名: {iv_data['iv_rank']:.1f}%")
    print(f"波动率制度: {iv_data['volatility_regime']}")
    
    # 可视化波动率分析
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # IV水平对比
    iv_levels = ['当前IV', '历史均值', '高波动率(80%)', '低波动率(20%)']
    iv_values = [iv_data['current_iv'], iv_data['mean_iv'], 80, 20]
    colors = ['blue', 'gray', 'red', 'green']
    
    bars = ax1.bar(iv_levels, iv_values, color=colors, alpha=0.7)
    ax1.set_title("隐含波动率水平对比")
    ax1.set_ylabel("隐含波动率 (%)")
    
    # 添加当前位置指示
    ax1.axhline(y=iv_data['current_iv'], color='blue', linestyle='--', alpha=0.8)
    
    # 百分位和排名可视化
    percentile = iv_data['iv_percentile']
    rank = iv_data['iv_rank']
    
    ax2.bar(['IV百分位', 'IV排名'], [percentile, rank], 
            color=['orange', 'purple'], alpha=0.7)
    ax2.set_title("相对位置指标")
    ax2.set_ylabel("百分比 (%)")
    ax2.set_ylim(0, 100)
    
    # 添加解释线
    ax2.axhline(y=80, color='red', linestyle='--', alpha=0.5, label='高位')
    ax2.axhline(y=20, color='green', linestyle='--', alpha=0.5, label='低位')
    ax2.legend()
    
    plt.tight_layout()
    plt.show()
    
    # 显示交易机会
    opportunities = iv_data.get('trading_opportunities', [])
    if opportunities:
        print(f"\n波动率交易机会:")
        for i, opp in enumerate(opportunities, 1):
            print(f"  {i}. {opp}")
    
    return iv_data

# 分析以太坊隐含波动率
eth_iv = analyze_implied_volatility_opportunities('ETH')
```

## 交易策略和市场分析

### 1. 期权策略构建

```python
class OptionsStrategyBuilder:
    """期权策略构建器"""
    
    def __init__(self, analyzer: OptionsAnalyzer):
        self.analyzer = analyzer
        
    def build_volatility_strategy(self, asset: str, outlook: str) -> Dict:
        """构建波动率策略"""
        
        iv_data = self.analyzer.get_implied_volatility(asset)
        current_price = 45000  # 示例现价，实际应从市场数据获取
        
        if not iv_data:
            return {}
        
        current_iv = iv_data.get('current_iv', 50)
        iv_rank = iv_data.get('iv_rank', 50)
        
        strategy = {
            'strategy_type': '',
            'components': [],
            'rationale': '',
            'max_profit': 0,
            'max_loss': 0,
            'breakeven_points': [],
            'time_decay_impact': '',
            'volatility_impact': ''
        }
        
        if outlook == 'high_volatility' and iv_rank < 30:
            # 买入波动率策略：Long Straddle
            strike = current_price
            call_premium = 2000  # 示例权利金
            put_premium = 1800
            
            strategy.update({
                'strategy_type': 'Long Straddle',
                'components': [
                    {'type': 'call', 'strike': strike, 'premium': call_premium, 
                     'position': 'long', 'quantity': 1},
                    {'type': 'put', 'strike': strike, 'premium': put_premium, 
                     'position': 'long', 'quantity': 1}
                ],
                'rationale': f'当前IV排名{iv_rank:.1f}%较低，预期波动率上升',
                'max_loss': call_premium + put_premium,
                'time_decay_impact': '负面，需要快速波动',
                'volatility_impact': '正面，波动率上升有利'
            })
            
        elif outlook == 'low_volatility' and iv_rank > 70:
            # 卖出波动率策略：Short Iron Condor
            strategy.update({
                'strategy_type': 'Short Iron Condor',
                'rationale': f'当前IV排名{iv_rank:.1f}%较高，预期波动率下降',
                'time_decay_impact': '正面，时间流逝有利',
                'volatility_impact': '负面，波动率下降有利'
            })
        
        return strategy
    
    def build_directional_strategy(self, asset: str, direction: str, 
                                 confidence: str) -> Dict:
        """构建方向性策略"""
        
        pc_data = self.analyzer.get_put_call_ratio(asset)
        current_price = 45000  # 示例现价
        
        strategy = {
            'strategy_type': '',
            'components': [],
            'rationale': '',
            'risk_reward_ratio': 0
        }
        
        if direction == 'bullish':
            if confidence == 'high':
                # 高信心：Long Call
                strategy.update({
                    'strategy_type': 'Long Call',
                    'components': [
                        {'type': 'call', 'strike': current_price + 2000, 
                         'premium': 1500, 'position': 'long', 'quantity': 1}
                    ],
                    'rationale': '高信心看涨，买入虚值看涨期权'
                })
            else:
                # 中等信心：Bull Call Spread
                strategy.update({
                    'strategy_type': 'Bull Call Spread',
                    'components': [
                        {'type': 'call', 'strike': current_price, 
                         'premium': 2000, 'position': 'long', 'quantity': 1},
                        {'type': 'call', 'strike': current_price + 5000, 
                         'premium': 800, 'position': 'short', 'quantity': 1}
                    ],
                    'rationale': '中等信心看涨，降低成本的价差策略'
                })
        
        elif direction == 'bearish':
            if confidence == 'high':
                strategy.update({
                    'strategy_type': 'Long Put',
                    'rationale': '高信心看跌，买入看跌期权'
                })
            else:
                strategy.update({
                    'strategy_type': 'Bear Put Spread',
                    'rationale': '中等信心看跌，降低成本的价差策略'
                })
        
        return strategy
    
    def optimize_strategy_parameters(self, strategy: Dict, 
                                   market_conditions: Dict) -> Dict:
        """优化策略参数"""
        
        optimized = strategy.copy()
        
        # 基于隐含波动率调整
        if 'current_iv' in market_conditions:
            iv = market_conditions['current_iv']
            
            if iv > 60:  # 高IV环境
                # 倾向于卖出期权策略
                if strategy['strategy_type'] in ['Long Call', 'Long Put']:
                    optimized['risk_warning'] = "高IV环境，考虑价差策略降低成本"
            
            elif iv < 25:  # 低IV环境
                # 倾向于买入期权策略
                if 'Short' in strategy['strategy_type']:
                    optimized['risk_warning'] = "低IV环境，卖出策略风险较高"
        
        # 基于时间衰减调整
        time_to_expiry = market_conditions.get('days_to_expiry', 30)
        
        if time_to_expiry < 7:
            optimized['time_warning'] = "临近到期，时间衰减风险较高"
        elif time_to_expiry > 90:
            optimized['time_consideration'] = "长期期权，时间价值较高"
        
        return optimized
    
    def calculate_strategy_greeks(self, strategy: Dict, 
                                spot_price: float) -> Dict:
        """计算策略的希腊字母"""
        
        total_greeks = {
            'delta': 0,
            'gamma': 0,
            'theta': 0,
            'vega': 0,
            'rho': 0
        }
        
        for component in strategy.get('components', []):
            # 获取期权参数
            option_type = component['type']
            strike = component['strike']
            premium = component['premium']
            position = component['position']
            quantity = component['quantity']
            
            # 计算单个期权的希腊字母
            greeks = self.analyzer.calculate_options_greeks(
                spot_price=spot_price,
                strike_price=strike,
                time_to_expiry=30,  # 假设30天到期
                implied_vol=50,     # 假设50%IV
                option_type=option_type
            )
            
            # 考虑头寸方向和数量
            multiplier = quantity if position == 'long' else -quantity
            
            for greek in total_greeks:
                total_greeks[greek] += greeks[greek] * multiplier
        
        # 解释希腊字母
        greek_interpretation = {
            'delta_exposure': self.interpret_delta(total_greeks['delta']),
            'gamma_risk': self.interpret_gamma(total_greeks['gamma']),
            'theta_decay': self.interpret_theta(total_greeks['theta']),
            'vega_sensitivity': self.interpret_vega(total_greeks['vega'])
        }
        
        return {
            'total_greeks': total_greeks,
            'interpretations': greek_interpretation
        }
    
    def interpret_delta(self, delta: float) -> str:
        """解释Delta敞口"""
        
        if delta > 0.5:
            return f"强烈看涨敞口 (Δ={delta:.2f})，价格上涨每$1获利${delta:.2f}"
        elif delta > 0.1:
            return f"温和看涨敞口 (Δ={delta:.2f})"
        elif delta > -0.1:
            return f"Delta中性 (Δ={delta:.2f})，方向风险较小"
        elif delta > -0.5:
            return f"温和看跌敞口 (Δ={delta:.2f})"
        else:
            return f"强烈看跌敞口 (Δ={delta:.2f})，价格下跌每$1获利${-delta:.2f}"
    
    def interpret_gamma(self, gamma: float) -> str:
        """解释Gamma风险"""
        
        if abs(gamma) > 0.01:
            return f"高Gamma风险 (Γ={gamma:.3f})，Delta变化敏感"
        elif abs(gamma) > 0.005:
            return f"中等Gamma风险 (Γ={gamma:.3f})"
        else:
            return f"低Gamma风险 (Γ={gamma:.3f})，Delta相对稳定"
    
    def interpret_theta(self, theta: float) -> str:
        """解释Theta时间衰减"""
        
        if theta < -50:
            return f"高时间衰减 (Θ={theta:.0f})，每日损失${-theta:.0f}"
        elif theta < -10:
            return f"中等时间衰减 (Θ={theta:.0f})"
        elif theta > 10:
            return f"时间衰减有利 (Θ={theta:.0f})，每日获利${theta:.0f}"
        else:
            return f"时间衰减影响较小 (Θ={theta:.0f})"
    
    def interpret_vega(self, vega: float) -> str:
        """解释Vega波动率敏感性"""
        
        if abs(vega) > 100:
            return f"高波动率敏感性 (ν={vega:.0f})，IV变化1%影响${vega:.0f}"
        elif abs(vega) > 50:
            return f"中等波动率敏感性 (ν={vega:.0f})"
        else:
            return f"低波动率敏感性 (ν={vega:.0f})"

# 使用示例
strategy_builder = OptionsStrategyBuilder(analyzer)

# 构建波动率策略
volatility_strategy = strategy_builder.build_volatility_strategy('BTC', 'high_volatility')
print("波动率策略:")
print(f"策略类型: {volatility_strategy.get('strategy_type', 'N/A')}")
print(f"策略理由: {volatility_strategy.get('rationale', 'N/A')}")

# 构建方向性策略
directional_strategy = strategy_builder.build_directional_strategy('BTC', 'bullish', 'high')
print(f"\n方向性策略:")
print(f"策略类型: {directional_strategy.get('strategy_type', 'N/A')}")
print(f"策略理由: {directional_strategy.get('rationale', 'N/A')}")

# 计算策略希腊字母
if volatility_strategy.get('components'):
    greeks_analysis = strategy_builder.calculate_strategy_greeks(volatility_strategy, 45000)
    print(f"\n策略希腊字母分析:")
    for greek, interpretation in greeks_analysis['interpretations'].items():
        print(f"{greek}: {interpretation}")
```

### 2. 期权套利机会识别

```python
class OptionsArbitrageDetector:
    """期权套利机会检测器"""
    
    def __init__(self, analyzer: OptionsAnalyzer):
        self.analyzer = analyzer
        
    def detect_put_call_parity_violations(self, asset: str) -> List[Dict]:
        """检测看涨看跌平价违约"""
        
        arbitrage_opportunities = []
        
        # 简化的平价关系检测
        # C - P = S - K * e^(-r*T)
        # 其中C=看涨期权价格，P=看跌期权价格，S=现价，K=执行价，r=无风险利率，T=到期时间
        
        # 示例数据（实际应从API获取）
        spot_price = 45000
        strike_prices = [42000, 44000, 45000, 46000, 48000]
        time_to_expiry = 30  # 天
        
        for strike in strike_prices:
            # 模拟期权价格（实际应从市场数据获取）
            call_price = max(spot_price - strike, 0) + 1000
            put_price = max(strike - spot_price, 0) + 800
            
            # 计算理论平价关系
            risk_free_rate = 0.05
            time_fraction = time_to_expiry / 365
            theoretical_difference = spot_price - strike * np.exp(-risk_free_rate * time_fraction)
            actual_difference = call_price - put_price
            
            # 检测违约
            violation = abs(actual_difference - theoretical_difference)
            
            if violation > 100:  # 阈值
                arbitrage_opportunities.append({
                    'type': 'put_call_parity',
                    'strike': strike,
                    'violation_amount': violation,
                    'call_price': call_price,
                    'put_price': put_price,
                    'theoretical_diff': theoretical_difference,
                    'actual_diff': actual_difference,
                    'arbitrage_action': self.recommend_parity_action(actual_difference, theoretical_difference)
                })
        
        return arbitrage_opportunities
    
    def recommend_parity_action(self, actual: float, theoretical: float) -> str:
        """推荐平价套利行动"""
        
        if actual > theoretical:
            return "卖出看涨期权，买入看跌期权，买入标的"
        else:
            return "买入看涨期权，卖出看跌期权，卖出标的"
    
    def detect_volatility_arbitrage(self, asset: str) -> List[Dict]:
        """检测波动率套利机会"""
        
        iv_data = self.analyzer.get_implied_volatility(asset)
        
        if not iv_data:
            return []
        
        arbitrage_opportunities = []
        current_iv = iv_data.get('current_iv', 50)
        
        # 历史波动率vs隐含波动率
        # 简化计算，实际需要计算历史波动率
        historical_vol = current_iv * 0.8  # 示例：假设历史波动率较低
        
        vol_spread = current_iv - historical_vol
        
        if abs(vol_spread) > 10:  # 10%的阈值
            arbitrage_opportunities.append({
                'type': 'volatility_spread',
                'current_iv': current_iv,
                'historical_vol': historical_vol,
                'spread': vol_spread,
                'opportunity': self.recommend_volatility_action(vol_spread),
                'expected_convergence': '2-4周'
            })
        
        return arbitrage_opportunities
    
    def recommend_volatility_action(self, spread: float) -> str:
        """推荐波动率套利行动"""
        
        if spread > 10:
            return "隐含波动率过高，卖出期权组合，Delta对冲"
        elif spread < -10:
            return "隐含波动率过低，买入期权组合，Delta对冲"
        else:
            return "波动率差异较小，无明显套利机会"
    
    def detect_calendar_spread_opportunities(self, asset: str) -> List[Dict]:
        """检测日历价差机会"""
        
        opportunities = []
        
        # 不同到期日的同一执行价期权价差
        # 示例数据
        near_month_iv = 45  # 近月隐含波动率
        far_month_iv = 40   # 远月隐含波动率
        
        iv_spread = near_month_iv - far_month_iv
        
        if iv_spread > 5:  # 近月IV显著高于远月
            opportunities.append({
                'type': 'time_spread',
                'near_month_iv': near_month_iv,
                'far_month_iv': far_month_iv,
                'iv_spread': iv_spread,
                'strategy': '卖出近月期权，买入远月期权',
                'rationale': '近月期权溢价相对远月较高'
            })
        
        elif iv_spread < -5:  # 远月IV显著高于近月
            opportunities.append({
                'type': 'time_spread',
                'near_month_iv': near_month_iv,
                'far_month_iv': far_month_iv,
                'iv_spread': iv_spread,
                'strategy': '买入近月期权，卖出远月期权',
                'rationale': '远月期权溢价相对近月较高'
            })
        
        return opportunities
    
    def scan_all_arbitrage_opportunities(self, asset: str) -> Dict:
        """扫描所有套利机会"""
        
        all_opportunities = {
            'put_call_parity': self.detect_put_call_parity_violations(asset),
            'volatility_arbitrage': self.detect_volatility_arbitrage(asset),
            'calendar_spreads': self.detect_calendar_spread_opportunities(asset),
            'summary': {
                'total_opportunities': 0,
                'high_priority': [],
                'execution_difficulty': {},
                'capital_requirements': {}
            }
        }
        
        # 汇总统计
        total_count = sum(len(opportunities) for opportunities in [
            all_opportunities['put_call_parity'],
            all_opportunities['volatility_arbitrage'],
            all_opportunities['calendar_spreads']
        ])
        
        all_opportunities['summary']['total_opportunities'] = total_count
        
        # 识别高优先级机会
        high_priority = []
        
        for parity_opp in all_opportunities['put_call_parity']:
            if parity_opp['violation_amount'] > 200:
                high_priority.append({
                    'type': 'put_call_parity',
                    'priority_score': parity_opp['violation_amount'],
                    'description': f"平价违约${parity_opp['violation_amount']:.0f}"
                })
        
        for vol_opp in all_opportunities['volatility_arbitrage']:
            if abs(vol_opp['spread']) > 15:
                high_priority.append({
                    'type': 'volatility',
                    'priority_score': abs(vol_opp['spread']),
                    'description': f"波动率价差{vol_opp['spread']:.1f}%"
                })
        
        all_opportunities['summary']['high_priority'] = sorted(
            high_priority, key=lambda x: x['priority_score'], reverse=True
        )
        
        return all_opportunities

# 使用示例
arbitrage_detector = OptionsArbitrageDetector(analyzer)

# 扫描比特币套利机会
btc_arbitrage = arbitrage_detector.scan_all_arbitrage_opportunities('BTC')

print("比特币期权套利机会扫描:")
print(f"总机会数量: {btc_arbitrage['summary']['total_opportunities']}")

if btc_arbitrage['summary']['high_priority']:
    print("\n高优先级机会:")
    for i, opp in enumerate(btc_arbitrage['summary']['high_priority'][:3], 1):
        print(f"{i}. {opp['type']}: {opp['description']} (评分: {opp['priority_score']:.1f})")

# 详细分析看涨看跌平价机会
if btc_arbitrage['put_call_parity']:
    print(f"\n看涨看跌平价违约机会:")
    for opp in btc_arbitrage['put_call_parity']:
        print(f"执行价 ${opp['strike']}: 违约金额 ${opp['violation_amount']:.0f}")
        print(f"  推荐行动: {opp['arbitrage_action']}")
```

## 常见问题

### Q1: 期权数据的实时性如何？

期权数据的更新频率：
- **实时价格数据**: 1分钟更新（主要交易所）
- **隐含波动率**: 10分钟更新
- **未平仓合约**: 每小时更新
- **希腊字母**: 实时计算，基于最新价格

数据延迟通常在几秒到几分钟之间。

### Q2: 如何理解隐含波动率的意义？

隐含波动率反映市场对未来价格波动的预期：
- **高IV**: 市场预期大幅波动，期权价格相对较贵
- **低IV**: 市场预期温和波动，期权价格相对便宜
- **IV百分位**: 当前IV在历史区间中的位置
- **IV排名**: 当前IV在过去一年中的排名

### Q3: 看涨看跌比率如何解读？

看涨看跌比率的解读：
- **比率 > 1**: 看跌期权交易量大于看涨期权，市场偏悲观
- **比率 < 1**: 看涨期权交易量大于看跌期权，市场偏乐观
- **极端值**: 通常具有逆向指标意义
- **历史对比**: 需要与历史水平对比判断极端程度

### Q4: 期权希腊字母的实际应用？

希腊字母的实际应用：
- **Delta**: 对冲比率，价格敏感性
- **Gamma**: Delta稳定性，再平衡频率
- **Theta**: 时间衰减，持有成本
- **Vega**: 波动率敏感性，IV变化影响
- **Rho**: 利率敏感性（通常影响较小）

## 最佳实践

1. **多维度分析**: 结合交易量、比率、波动率和未平仓合约进行综合分析
2. **历史对比**: 与历史数据对比，识别异常和极值
3. **风险管理**: 使用希腊字母进行风险控制和对冲
4. **策略优化**: 根据市场条件动态调整期权策略
5. **套利识别**: 持续监控价格偏差和套利机会
6. **流动性考虑**: 关注期权流动性，避免在薄弱市场交易

---

*本文档详细介绍了 Glassnode Options API 的使用方法，包括数据获取、分析技术和实际应用案例。期权数据是理解市场情绪和构建复杂交易策略的重要工具。*