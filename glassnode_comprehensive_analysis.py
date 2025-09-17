"""
Glassnode综合指标分析系统 - 深度市场分析
分析所有核心指标在不同市场状态下的表现和预测能力
支持牛市、熊市、崩盘期、震荡期的识别和分析
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Tuple, Optional, Any
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


class MarketRegimeDetector:
    """市场状态检测器 - 识别牛市、熊市、崩盘、震荡期"""
    
    @staticmethod
    def detect_market_regime(price_df: pd.DataFrame, window: int = 200) -> pd.DataFrame:
        """
        检测市场状态
        - 牛市：价格高于200日均线且持续上升
        - 熊市：价格低于200日均线且持续下降
        - 崩盘：短期内价格下跌超过20%
        - 震荡：价格在一定范围内波动
        """
        df = price_df.copy()
        
        # 计算移动平均线
        df['ma_200'] = df['price'].rolling(window=200).mean()
        df['ma_50'] = df['price'].rolling(window=50).mean()
        df['ma_20'] = df['price'].rolling(window=20).mean()
        
        # 计算收益率
        df['returns'] = df['price'].pct_change()
        df['returns_7d'] = df['price'].pct_change(7)
        df['returns_30d'] = df['price'].pct_change(30)
        
        # 计算波动率
        df['volatility'] = df['returns'].rolling(window=30).std() * np.sqrt(365)
        
        # 初始化市场状态
        df['regime'] = 'Sideways'
        
        # 牛市条件
        bull_conditions = (
            (df['price'] > df['ma_200']) & 
            (df['ma_50'] > df['ma_200']) &
            (df['returns_30d'] > 0.1)
        )
        df.loc[bull_conditions, 'regime'] = 'Bull'
        
        # 熊市条件
        bear_conditions = (
            (df['price'] < df['ma_200']) & 
            (df['ma_50'] < df['ma_200']) &
            (df['returns_30d'] < -0.1)
        )
        df.loc[bear_conditions, 'regime'] = 'Bear'
        
        # 崩盘条件（优先级最高）
        crash_conditions = (
            (df['returns_7d'] < -0.2) |
            (df['returns'].rolling(3).sum() < -0.15)
        )
        df.loc[crash_conditions, 'regime'] = 'Crash'
        
        # 震荡市场（当不满足其他条件时）
        sideways_conditions = (
            (df['volatility'] < df['volatility'].rolling(90).mean()) &
            (abs(df['returns_30d']) < 0.1)
        )
        df.loc[sideways_conditions & (df['regime'] == 'Sideways'), 'regime'] = 'Sideways'
        
        return df


class GlassnodeMetricsAnalyzer:
    """Glassnode指标综合分析器"""
    
    # 指标类别定义 - 使用正确的API端点
    METRIC_CATEGORIES = {
        'market': {
            'price_usd_close': '收盘价',
            'marketcap_usd': '市值',
            'mvrv': 'MVRV比率',
            'mvrv_z_score': 'MVRV Z-Score',
            'price_realized_usd': '实现价格'
        },
        'indicators': {
            'sopr': 'SOPR（支出产出利润率）',
            'net_unrealized_profit_loss': 'NUPL（净未实现损益）',
            'puell_multiple': 'Puell倍数',
            'reserve_risk': '储备风险',
            'cvdd': 'CVDD（累积价值销毁天数）'
        },
        'supply': {
            'current': '当前供应量',
            'profit_relative': '盈利供应占比',
            'profit_sum': '盈利供应量',
            'loss_sum': '亏损供应量',
            'lth_sum': '长期持有者供应量',
            'illiquid_sum': '非流动供应量',
            'active_more_1y_percent': '活跃1年以上占比'
        },
        'addresses': {
            'active_count': '活跃地址数',
            'new_non_zero_count': '新增非零地址数',
            'sending_count': '发送地址数',
            'receiving_count': '接收地址数',
            'accumulation_count': '累积地址数'
        },
        'transactions': {
            'transfers_to_exchanges_count': '流入交易所笔数',
            'transfers_from_exchanges_count': '流出交易所笔数',
            'transfers_volume_to_exchanges_sum': '流入交易所总量',
            'transfers_volume_from_exchanges_sum': '流出交易所总量',
            'transfers_volume_exchanges_net': '交易所净流量',
            'transfers_count': '转账数量',
            'transfers_volume_sum': '转账总量'
        },
        'mining': {
            'hash_rate_mean': '哈希率',
            'difficulty_latest': '挖矿难度',
            'revenue_sum': '矿工收入',
            'thermocap': '热力学市值',
            'marketcap_thermocap_ratio': '市值/热力学市值比'
        },
        'derivatives': {
            'futures_open_interest_sum': '期货未平仓量',
            'futures_volume_daily_sum': '期货日交易量',
            'futures_funding_rate_perpetual': '永续合约资金费率',
            'options_open_interest_put_call_ratio': '期权看跌看涨比',
            'futures_liquidated_volume_long_sum': '多头爆仓量'
        },
        'institutions': {
            'purpose_etf_holdings_sum': 'Purpose ETF持仓',
            'us_spot_etf_balances_all': '美国现货ETF余额',
            'us_spot_etf_flows': '美国ETF流量',
            'us_spot_etf_net_flows': '美国ETF净流量'
        }
    }
    
    # 指标解释和市场影响
    METRIC_INTERPRETATIONS = {
        'mvrv': {
            'description': 'MVRV衡量市场价值与实现价值的比率',
            'bull_signal': 'MVRV > 3.5 通常标志着牛市后期，可能面临回调',
            'bear_signal': 'MVRV < 1.0 表明大量持币者处于亏损，可能是底部信号',
            'crash_behavior': '崩盘时MVRV会快速下降至1以下',
            'sideways_behavior': '震荡市中MVRV通常在1.5-2.5之间波动'
        },
        'sopr': {
            'description': 'SOPR衡量已实现的利润/损失',
            'bull_signal': 'SOPR持续>1且在回调时守住1.0支撑位',
            'bear_signal': 'SOPR持续<1表明投资者在亏损中卖出',
            'crash_behavior': 'SOPR会急剧下降至0.85-0.9区间',
            'sideways_behavior': 'SOPR在1.0附近小幅波动'
        },
        'nupl': {
            'description': 'NUPL衡量整体市场的未实现损益',
            'bull_signal': 'NUPL > 0.5 表明市场进入贪婪阶段',
            'bear_signal': 'NUPL < 0 表明市场恐慌，可能接近底部',
            'crash_behavior': 'NUPL会快速转负，达到-0.25以下',
            'sideways_behavior': 'NUPL在0-0.25之间波动'
        },
        'puell_multiple': {
            'description': 'Puell倍数衡量矿工收入相对历史平均值',
            'bull_signal': 'Puell > 4 表明矿工收入过高，可能是顶部',
            'bear_signal': 'Puell < 0.5 表明矿工压力大，可能是底部',
            'crash_behavior': '快速下降至0.3-0.5区间',
            'sideways_behavior': '在0.8-1.5之间波动'
        },
        'reserve_risk': {
            'description': '储备风险衡量长期持有者信心',
            'bull_signal': '储备风险<0.002表明长期持有者信心强',
            'bear_signal': '储备风险>0.01表明可能接近顶部',
            'crash_behavior': '储备风险会快速上升',
            'sideways_behavior': '在0.002-0.008之间波动'
        },
        'long_term_holder_supply': {
            'description': '长期持有者供应量反映HODLer行为',
            'bull_signal': 'LTH供应量下降表明老币开始获利了结',
            'bear_signal': 'LTH供应量增加表明积累阶段',
            'crash_behavior': 'LTH可能会恐慌性抛售',
            'sideways_behavior': 'LTH供应量稳定或缓慢增长'
        },
        'exchange_flow': {
            'description': '交易所流量反映买卖压力',
            'bull_signal': '净流出表明持币意愿强',
            'bear_signal': '净流入表明抛售压力大',
            'crash_behavior': '大量流入交易所',
            'sideways_behavior': '流入流出相对平衡'
        },
        'hash_rate': {
            'description': '哈希率反映网络安全性和矿工信心',
            'bull_signal': '哈希率创新高表明矿工看好',
            'bear_signal': '哈希率下降表明矿工退出',
            'crash_behavior': '可能出现矿工投降',
            'sideways_behavior': '哈希率稳定或小幅波动'
        },
        'funding_rate': {
            'description': '资金费率反映衍生品市场情绪',
            'bull_signal': '正费率但不过高(0.01-0.05%)',
            'bear_signal': '负费率表明看空情绪',
            'crash_behavior': '极度负费率(-0.1%以下)',
            'sideways_behavior': '接近中性(±0.01%)'
        }
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://grassnoodle.cloud"
        self.headers = {"x-key": api_key}
        self.data_cache = {}
        
    def fetch_metric(self, endpoint: str, params: dict, cache_key: str = None) -> List[dict]:
        """获取指标数据"""
        if cache_key and cache_key in self.data_cache:
            print(f"  使用缓存: {cache_key}")
            return self.data_cache[cache_key]
            
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 检查是否是权限错误
            if isinstance(data, dict) and data.get('type') == 'metric':
                print(f"  ⚠️ 无法访问: {endpoint} (需要更高级别订阅)")
                return []
            
            if cache_key:
                self.data_cache[cache_key] = data
            
            time.sleep(0.8)  # 增加延迟避免429错误
            return data
        except requests.exceptions.Timeout:
            print(f"  ⏱️ 超时: {endpoint}")
            return []
        except Exception as e:
            print(f"  ❌ 错误: {endpoint} - {str(e)[:50]}")
            return []
    
    def fetch_all_metrics(self, asset: str = "BTC", start_date: str = None, 
                         end_date: str = None) -> Dict[str, pd.DataFrame]:
        """获取所有可用的指标数据"""
        all_data = {}
        params = {"a": asset}
        
        if start_date:
            params["s"] = str(int(datetime.strptime(start_date, "%Y-%m-%d").timestamp()))
        if end_date:
            params["u"] = str(int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()))
        
        print("\n📊 开始获取所有Glassnode指标数据...")
        
        for category, metrics in self.METRIC_CATEGORIES.items():
            print(f"\n📁 {category.upper()} 类别:")
            
            for metric_key, metric_name in metrics.items():
                endpoint = f"/v1/metrics/{category}/{metric_key}"
                cache_key = f"{asset}_{category}_{metric_key}_{start_date}_{end_date}"
                
                print(f"  获取 {metric_name}...", end="")
                data = self.fetch_metric(endpoint, params, cache_key)
                
                if data:
                    df = pd.DataFrame(data)
                    df['date'] = pd.to_datetime(df['t'], unit='s')
                    df[metric_key] = df['v'].astype(float)
                    df = df[['date', metric_key]].set_index('date')
                    all_data[f"{category}_{metric_key}"] = df
                    print(f" ✅ {len(df)} 条数据")
                else:
                    print(f" ❌")
        
        return all_data
    
    def analyze_metric_by_regime(self, metric_df: pd.DataFrame, regime_df: pd.DataFrame, 
                                 metric_name: str) -> Dict:
        """分析指标在不同市场状态下的表现"""
        # 合并数据
        merged = pd.merge(metric_df, regime_df[['regime']], 
                         left_index=True, right_index=True, how='inner')
        
        if merged.empty:
            return {}
        
        analysis = {
            'metric_name': metric_name,
            'overall_stats': {
                'mean': float(merged.iloc[:, 0].mean()),
                'std': float(merged.iloc[:, 0].std()),
                'min': float(merged.iloc[:, 0].min()),
                'max': float(merged.iloc[:, 0].max())
            },
            'regime_stats': {}
        }
        
        # 按市场状态分组统计
        for regime in ['Bull', 'Bear', 'Crash', 'Sideways']:
            regime_data = merged[merged['regime'] == regime]
            if not regime_data.empty:
                metric_col = regime_data.iloc[:, 0]
                analysis['regime_stats'][regime] = {
                    'mean': float(metric_col.mean()),
                    'std': float(metric_col.std()),
                    'min': float(metric_col.min()),
                    'max': float(metric_col.max()),
                    'median': float(metric_col.median()),
                    'q25': float(metric_col.quantile(0.25)),
                    'q75': float(metric_col.quantile(0.75)),
                    'count': len(regime_data),
                    'pct_of_time': len(regime_data) / len(merged) * 100
                }
        
        return analysis
    
    def calculate_predictive_power(self, metric_df: pd.DataFrame, price_df: pd.DataFrame,
                                  max_lag: int = 30) -> Dict:
        """计算指标的预测能力"""
        # 合并数据
        merged = pd.merge(metric_df, price_df, left_index=True, right_index=True, how='inner')
        
        if len(merged) < max_lag * 2:
            return {}
        
        metric_col = merged.iloc[:, 0]
        price_col = merged['price']
        
        # 计算不同滞后期的相关性
        correlations = {}
        for lag in range(-max_lag, max_lag + 1):
            if lag < 0:
                # 指标领先价格
                shifted_metric = metric_col.shift(lag)
                corr = shifted_metric.corr(price_col)
            elif lag > 0:
                # 价格领先指标
                shifted_price = price_col.shift(lag)
                corr = metric_col.corr(shifted_price)
            else:
                # 同期相关
                corr = metric_col.corr(price_col)
            
            if not np.isnan(corr):
                correlations[lag] = corr
        
        # 找到最优滞后期
        if correlations:
            optimal_lag = max(correlations, key=lambda k: abs(correlations[k]))
            optimal_corr = correlations[optimal_lag]
        else:
            optimal_lag = 0
            optimal_corr = 0
        
        # 计算预测准确率（基于方向）
        metric_change = metric_col.pct_change()
        price_change = price_col.pct_change().shift(-1)  # 预测下一期
        
        # 移除NaN值
        valid_mask = ~(metric_change.isna() | price_change.isna())
        metric_direction = (metric_change > 0)[valid_mask]
        price_direction = (price_change > 0)[valid_mask]
        
        if len(metric_direction) > 0:
            direction_accuracy = (metric_direction == price_direction).mean() * 100
        else:
            direction_accuracy = 50.0
        
        return {
            'optimal_lag': optimal_lag,
            'optimal_correlation': optimal_corr,
            'direction_accuracy': direction_accuracy,
            'correlations': correlations
        }
    
    def identify_extremes(self, metric_df: pd.DataFrame, threshold_percentile: int = 95) -> Dict:
        """识别指标的极值点"""
        if metric_df.empty:
            return {}
        
        metric_col = metric_df.iloc[:, 0]
        
        # 计算百分位数
        upper_threshold = metric_col.quantile(threshold_percentile / 100)
        lower_threshold = metric_col.quantile((100 - threshold_percentile) / 100)
        
        # 识别极值
        upper_extremes = metric_col[metric_col >= upper_threshold]
        lower_extremes = metric_col[metric_col <= lower_threshold]
        
        return {
            'upper_threshold': upper_threshold,
            'lower_threshold': lower_threshold,
            'upper_extreme_dates': upper_extremes.index.tolist(),
            'lower_extreme_dates': lower_extremes.index.tolist(),
            'upper_extreme_count': len(upper_extremes),
            'lower_extreme_count': len(lower_extremes)
        }


class ComprehensiveAnalysisReport:
    """综合分析报告生成器"""
    
    def __init__(self):
        self.report_data = {}
        
    def generate_market_overview(self, regime_df: pd.DataFrame) -> Dict:
        """生成市场概览"""
        regime_counts = regime_df['regime'].value_counts()
        regime_pcts = regime_df['regime'].value_counts(normalize=True) * 100
        
        # 计算每个状态的平均持续时间
        regime_durations = {}
        current_regime = None
        current_start = None
        
        for date, regime in regime_df['regime'].items():
            if regime != current_regime:
                if current_regime and current_start:
                    if current_regime not in regime_durations:
                        regime_durations[current_regime] = []
                    duration = (date - current_start).days
                    regime_durations[current_regime].append(duration)
                current_regime = regime
                current_start = date
        
        avg_durations = {regime: np.mean(durations) if durations else 0 
                        for regime, durations in regime_durations.items()}
        
        return {
            'total_days': len(regime_df),
            'regime_distribution': regime_pcts.to_dict(),
            'regime_counts': regime_counts.to_dict(),
            'average_duration_days': avg_durations,
            'current_regime': regime_df['regime'].iloc[-1],
            'volatility_stats': {
                'mean': regime_df['volatility'].mean(),
                'current': regime_df['volatility'].iloc[-1]
            }
        }
    
    def rank_indicators(self, all_analyses: Dict) -> pd.DataFrame:
        """对指标进行排名"""
        rankings = []
        
        for metric_name, analysis in all_analyses.items():
            if 'predictive_power' in analysis and analysis['predictive_power']:
                pred_power = analysis['predictive_power']
                
                # 计算综合得分
                score = (
                    abs(pred_power.get('optimal_correlation', 0)) * 40 +
                    (pred_power.get('direction_accuracy', 50) - 50) * 2
                )
                
                rankings.append({
                    'metric': metric_name,
                    'score': score,
                    'optimal_lag': pred_power.get('optimal_lag', 0),
                    'correlation': pred_power.get('optimal_correlation', 0),
                    'accuracy': pred_power.get('direction_accuracy', 50)
                })
        
        if rankings:
            return pd.DataFrame(rankings).sort_values('score', ascending=False)
        return pd.DataFrame()
    
    def generate_trading_signals(self, metrics_data: Dict, latest_date: datetime) -> List[Dict]:
        """基于指标生成交易信号"""
        signals = []
        
        # MVRV信号
        if 'market_mvrv_z_score' in metrics_data:
            mvrv_z = metrics_data['market_mvrv_z_score'].iloc[-1, 0]
            if mvrv_z > 2.5:
                signals.append({
                    'type': 'SELL',
                    'strength': 'Strong',
                    'indicator': 'MVRV Z-Score',
                    'value': mvrv_z,
                    'reason': 'MVRV Z-Score > 2.5 表明市场过热'
                })
            elif mvrv_z < -0.5:
                signals.append({
                    'type': 'BUY',
                    'strength': 'Strong',
                    'indicator': 'MVRV Z-Score',
                    'value': mvrv_z,
                    'reason': 'MVRV Z-Score < -0.5 表明市场超卖'
                })
        
        # SOPR信号
        if 'indicators_sopr' in metrics_data:
            sopr = metrics_data['indicators_sopr'].iloc[-1, 0]
            sopr_ma = metrics_data['indicators_sopr'].iloc[-7:, 0].mean()
            
            if sopr > 1.05 and sopr < sopr_ma:
                signals.append({
                    'type': 'SELL',
                    'strength': 'Medium',
                    'indicator': 'SOPR',
                    'value': sopr,
                    'reason': 'SOPR开始从高位回落'
                })
            elif 0.95 < sopr < 1.0 and sopr > sopr_ma:
                signals.append({
                    'type': 'BUY',
                    'strength': 'Medium',
                    'indicator': 'SOPR',
                    'value': sopr,
                    'reason': 'SOPR从底部反弹'
                })
        
        # Exchange Flow信号
        if 'transactions_transfers_volume_exchanges_net' in metrics_data:
            exchange_flow = metrics_data['transactions_transfers_volume_exchanges_net'].iloc[-1, 0]
            flow_std = metrics_data['transactions_transfers_volume_exchanges_net'].iloc[:, 0].std()
            
            if exchange_flow > 2 * flow_std:
                signals.append({
                    'type': 'SELL',
                    'strength': 'Medium',
                    'indicator': 'Exchange Flow',
                    'value': exchange_flow,
                    'reason': '大量BTC流入交易所，抛售压力增加'
                })
            elif exchange_flow < -2 * flow_std:
                signals.append({
                    'type': 'BUY',
                    'strength': 'Medium',
                    'indicator': 'Exchange Flow',
                    'value': exchange_flow,
                    'reason': '大量BTC流出交易所，持币意愿增强'
                })
        
        return signals
    
    def create_html_report(self, all_data: Dict, output_file: str = "glassnode_report.html"):
        """创建HTML报告"""
        # 生成各部分内容
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        market_overview = self._format_market_overview(all_data.get('market_overview', {}))
        trading_signals = self._format_trading_signals(all_data.get('trading_signals', []))
        indicator_rankings = self._format_rankings(all_data.get('rankings', pd.DataFrame()))
        core_metrics = self._format_core_metrics(all_data.get('metric_analyses', {}))
        key_insights = self._format_insights(all_data)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Glassnode综合指标分析报告</title>
            <style>
                body {{
                    font-family: Arial, sans-serif; 
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    background-color: #2c3e50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 10px;
                }}
                .section {{
                    background-color: white;
                    margin: 20px 0;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .metric-card {{
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 10px 0;
                }}
                .bull {{ color: #27ae60; font-weight: bold; }}
                .bear {{ color: #e74c3c; font-weight: bold; }}
                .crash {{ color: #8e44ad; font-weight: bold; }}
                .sideways {{ color: #95a5a6; font-weight: bold; }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th, td {{
                    padding: 10px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{ background-color: #34495e; color: white; }}
                .signal-buy {{ background-color: #d4edda; }}
                .signal-sell {{ background-color: #f8d7da; }}
                .chart-container {{
                    width: 100%;
                    height: 400px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔍 Glassnode综合指标分析报告</h1>
                <p>生成时间：{timestamp}</p>
            </div>
            
            <div class="section">
                <h2>📊 市场概览</h2>
                {market_overview}
            </div>
            
            <div class="section">
                <h2>🎯 当前交易信号</h2>
                {trading_signals}
            </div>
            
            <div class="section">
                <h2>🏆 指标排名</h2>
                {indicator_rankings}
            </div>
            
            <div class="section">
                <h2>📈 核心指标详解</h2>
                {core_metrics}
            </div>
            
            <div class="section">
                <h2>💡 关键洞察</h2>
                {key_insights}
            </div>
        </body>
        </html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file
    
    def _format_market_overview(self, overview: Dict) -> str:
        if not overview:
            return "<p>暂无数据</p>"
        
        html = f"""
        <div class="metric-card">
            <h3>当前市场状态：<span class="{overview.get('current_regime', '').lower()}">{overview.get('current_regime', 'Unknown')}</span></h3>
            <p>分析周期：{overview.get('total_days', 0)} 天</p>
            <p>当前波动率：{overview.get('volatility_stats', {}).get('current', 0):.2%}</p>
        </div>
        
        <table>
            <tr>
                <th>市场状态</th>
                <th>时间占比</th>
                <th>平均持续时间</th>
            </tr>
        """
        
        for regime in ['Bull', 'Bear', 'Crash', 'Sideways']:
            pct = overview.get('regime_distribution', {}).get(regime, 0)
            duration = overview.get('average_duration_days', {}).get(regime, 0)
            html += f"""
            <tr>
                <td class="{regime.lower()}">{regime}</td>
                <td>{pct:.1f}%</td>
                <td>{duration:.0f} 天</td>
            </tr>
            """
        
        html += "</table>"
        return html
    
    def _format_trading_signals(self, signals: List[Dict]) -> str:
        if not signals:
            return "<p>当前无明确交易信号</p>"
        
        html = "<table>"
        html += "<tr><th>信号类型</th><th>强度</th><th>指标</th><th>原因</th></tr>"
        
        for signal in signals:
            signal_class = "signal-buy" if signal['type'] == 'BUY' else "signal-sell"
            html += f"""
            <tr class="{signal_class}">
                <td><strong>{signal['type']}</strong></td>
                <td>{signal['strength']}</td>
                <td>{signal['indicator']}</td>
                <td>{signal['reason']}</td>
            </tr>
            """
        
        html += "</table>"
        return html
    
    def _format_rankings(self, rankings: pd.DataFrame) -> str:
        if rankings.empty:
            return "<p>暂无排名数据</p>"
        
        html = "<table>"
        html += "<tr><th>排名</th><th>指标</th><th>综合得分</th><th>相关性</th><th>准确率</th><th>最优滞后期</th></tr>"
        
        for idx, row in rankings.head(10).iterrows():
            lag_desc = f"{row['optimal_lag']} 天"
            if row['optimal_lag'] < 0:
                lag_desc = f"领先 {abs(row['optimal_lag'])} 天"
            elif row['optimal_lag'] == 0:
                lag_desc = "同期"
                
            html += f"""
            <tr>
                <td>{idx + 1}</td>
                <td>{row['metric']}</td>
                <td>{row['score']:.2f}</td>
                <td>{row['correlation']:.3f}</td>
                <td>{row['accuracy']:.1f}%</td>
                <td>{lag_desc}</td>
            </tr>
            """
        
        html += "</table>"
        return html
    
    def _format_core_metrics(self, analyses: Dict) -> str:
        html = ""
        
        # 选择关键指标展示
        key_metrics = ['market_mvrv_z_score', 'indicators_sopr', 'indicators_net_unrealized_profit_loss',
                      'transactions_transfers_volume_exchanges_net', 'supply_profit_relative']
        
        for metric in key_metrics:
            if metric in analyses:
                analysis = analyses[metric]
                interpretation = GlassnodeMetricsAnalyzer.METRIC_INTERPRETATIONS.get(
                    metric.split('_', 1)[1] if '_' in metric else metric, {}
                )
                
                html += f"""
                <div class="metric-card">
                    <h3>{metric}</h3>
                    <p><strong>描述：</strong>{interpretation.get('description', 'N/A')}</p>
                    <p><strong>牛市信号：</strong>{interpretation.get('bull_signal', 'N/A')}</p>
                    <p><strong>熊市信号：</strong>{interpretation.get('bear_signal', 'N/A')}</p>
                """
                
                if 'regime_stats' in analysis:
                    html += "<h4>不同市场状态下的表现：</h4><ul>"
                    for regime, stats in analysis['regime_stats'].items():
                        html += f"<li class='{regime.lower()}'>{regime}: 均值={stats['mean']:.3f}, 中位数={stats['median']:.3f}</li>"
                    html += "</ul>"
                
                html += "</div>"
        
        return html
    
    def _format_insights(self, all_data: Dict) -> str:
        insights = []
        
        # 基于当前市场状态的洞察
        current_regime = all_data.get('market_overview', {}).get('current_regime', '')
        
        if current_regime == 'Bull':
            insights.append("🐂 当前处于牛市状态，建议关注过热信号和获利了结机会")
        elif current_regime == 'Bear':
            insights.append("🐻 当前处于熊市状态，建议寻找底部信号和积累机会")
        elif current_regime == 'Crash':
            insights.append("📉 市场处于崩盘状态，注意风险控制，可考虑逢低布局")
        else:
            insights.append("➡️ 市场处于震荡状态，适合区间交易策略")
        
        # 基于信号的洞察
        signals = all_data.get('trading_signals', [])
        buy_signals = [s for s in signals if s['type'] == 'BUY']
        sell_signals = [s for s in signals if s['type'] == 'SELL']
        
        if len(buy_signals) > len(sell_signals):
            insights.append(f"✅ 买入信号较多({len(buy_signals)}个)，市场可能存在上行机会")
        elif len(sell_signals) > len(buy_signals):
            insights.append(f"⚠️ 卖出信号较多({len(sell_signals)}个)，建议谨慎操作")
        
        # 基于排名的洞察
        rankings = all_data.get('rankings', pd.DataFrame())
        if not rankings.empty:
            best_indicator = rankings.iloc[0]['metric']
            insights.append(f"🏆 当前最佳预测指标：{best_indicator}")
        
        html = "<ul>"
        for insight in insights:
            html += f"<li>{insight}</li>"
        html += "</ul>"
        
        return html


class VisualizationEngine:
    """可视化引擎"""
    
    @staticmethod
    def plot_regime_distribution(regime_df: pd.DataFrame, save_path: str = "regime_distribution.png"):
        """绘制市场状态分布图"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. 时间序列图
        ax1 = axes[0, 0]
        colors = {'Bull': 'green', 'Bear': 'red', 'Crash': 'purple', 'Sideways': 'gray'}
        
        for regime, color in colors.items():
            mask = regime_df['regime'] == regime
            ax1.scatter(regime_df.index[mask], regime_df['price'][mask], 
                       c=color, label=regime, alpha=0.6, s=1)
        
        ax1.set_yscale('log')
        ax1.set_xlabel('日期')
        ax1.set_ylabel('价格 (USD, 对数坐标)')
        ax1.set_title('BTC价格与市场状态')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 饼图
        ax2 = axes[0, 1]
        regime_counts = regime_df['regime'].value_counts()
        ax2.pie(regime_counts.values, labels=regime_counts.index, autopct='%1.1f%%',
               colors=[colors[r] for r in regime_counts.index])
        ax2.set_title('市场状态时间分布')
        
        # 3. 收益率分布
        ax3 = axes[1, 0]
        for regime in ['Bull', 'Bear', 'Crash', 'Sideways']:
            returns = regime_df[regime_df['regime'] == regime]['returns'].dropna()
            if len(returns) > 0:
                ax3.hist(returns, bins=50, alpha=0.5, label=regime, color=colors[regime])
        
        ax3.set_xlabel('日收益率')
        ax3.set_ylabel('频率')
        ax3.set_title('不同市场状态下的收益率分布')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 波动率对比
        ax4 = axes[1, 1]
        volatility_by_regime = regime_df.groupby('regime')['volatility'].mean().sort_values()
        ax4.bar(volatility_by_regime.index, volatility_by_regime.values, 
               color=[colors[r] for r in volatility_by_regime.index])
        ax4.set_xlabel('市场状态')
        ax4.set_ylabel('平均波动率')
        ax4.set_title('不同市场状态的平均波动率')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
    @staticmethod
    def plot_indicator_heatmap(correlations: Dict, save_path: str = "indicator_heatmap.png"):
        """绘制指标相关性热力图"""
        # 准备数据
        indicators = []
        regimes = ['Bull', 'Bear', 'Crash', 'Sideways']
        data = []
        
        for metric_name, analysis in correlations.items():
            if 'regime_stats' in analysis:
                indicators.append(metric_name)
                row = []
                for regime in regimes:
                    if regime in analysis['regime_stats']:
                        row.append(analysis['regime_stats'][regime]['mean'])
                    else:
                        row.append(np.nan)
                data.append(row)
        
        if not data:
            return
        
        # 创建热力图
        fig, ax = plt.subplots(figsize=(10, len(indicators) * 0.5))
        
        # 归一化数据
        data_array = np.array(data)
        # 对每个指标进行标准化
        for i in range(len(data_array)):
            row = data_array[i]
            valid_data = row[~np.isnan(row)]
            if len(valid_data) > 0:
                mean = np.mean(valid_data)
                std = np.std(valid_data)
                if std > 0:
                    data_array[i] = (row - mean) / std
        
        im = ax.imshow(data_array, cmap='RdYlGn', aspect='auto')
        
        # 设置标签
        ax.set_xticks(np.arange(len(regimes)))
        ax.set_yticks(np.arange(len(indicators)))
        ax.set_xticklabels(regimes)
        ax.set_yticklabels(indicators)
        
        # 旋转标签
        plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
        plt.setp(ax.get_yticklabels(), rotation=0, ha="right")
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('标准化值', rotation=270, labelpad=20)
        
        ax.set_title('指标在不同市场状态下的表现热力图')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    @staticmethod
    def plot_prediction_power(rankings: pd.DataFrame, save_path: str = "prediction_power.png"):
        """绘制预测能力图"""
        if rankings.empty:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 1. 综合得分条形图
        top_10 = rankings.head(10)
        ax1.barh(range(len(top_10)), top_10['score'].values, color='steelblue')
        ax1.set_yticks(range(len(top_10)))
        ax1.set_yticklabels(top_10['metric'].values)
        ax1.set_xlabel('综合得分')
        ax1.set_title('Top 10 预测指标')
        ax1.invert_yaxis()
        ax1.grid(True, alpha=0.3)
        
        # 2. 相关性vs准确率散点图
        scatter = ax2.scatter(rankings['correlation'].abs(), 
                            rankings['accuracy'],
                            c=rankings['optimal_lag'],
                            cmap='coolwarm',
                            s=100,
                            alpha=0.6)
        
        ax2.set_xlabel('绝对相关性')
        ax2.set_ylabel('方向预测准确率 (%)')
        ax2.set_title('指标预测能力分布')
        ax2.grid(True, alpha=0.3)
        
        # 添加颜色条
        cbar = plt.colorbar(scatter, ax=ax2)
        cbar.set_label('最优滞后期 (天)', rotation=270, labelpad=20)
        
        # 标注最佳指标
        if len(top_10) > 0:
            best = top_10.iloc[0]
            ax2.annotate(best['metric'], 
                        (abs(best['correlation']), best['accuracy']),
                        xytext=(10, 10), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.5),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    @staticmethod
    def plot_signal_timeline(signals: List[Dict], price_df: pd.DataFrame, 
                            save_path: str = "signal_timeline.png"):
        """绘制信号时间线"""
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # 绘制价格
        ax.plot(price_df.index, price_df['price'], label='BTC价格', color='black', linewidth=1)
        
        # 添加信号标记
        # 这里简化处理，实际应该根据信号的时间戳标注
        if signals:
            latest_price = price_df['price'].iloc[-1]
            for i, signal in enumerate(signals):
                y_pos = latest_price * (1 + 0.05 * (i % 3 - 1))  # 错开显示
                color = 'green' if signal['type'] == 'BUY' else 'red'
                marker = '^' if signal['type'] == 'BUY' else 'v'
                
                ax.scatter(price_df.index[-1], y_pos, 
                          c=color, marker=marker, s=200, 
                          label=f"{signal['type']}: {signal['indicator']}")
        
        ax.set_xlabel('日期')
        ax.set_ylabel('价格 (USD)')
        ax.set_title('交易信号时间线')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()


def main():
    """主函数"""
    # 配置
    API_KEY = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
    START_DATE = "2021-01-01"
    END_DATE = "2024-12-31"
    
    print("=" * 80)
    print("🚀 Glassnode综合指标深度分析系统")
    print("=" * 80)
    print(f"分析周期：{START_DATE} 至 {END_DATE}")
    
    # 初始化组件
    detector = MarketRegimeDetector()
    analyzer = GlassnodeMetricsAnalyzer(API_KEY)
    reporter = ComprehensiveAnalysisReport()
    viz = VisualizationEngine()
    
    # Step 1: 获取价格数据并检测市场状态
    print("\n📊 Step 1: 获取价格数据并检测市场状态...")
    
    price_params = {"a": "BTC"}
    if START_DATE:
        price_params["s"] = str(int(datetime.strptime(START_DATE, "%Y-%m-%d").timestamp()))
    if END_DATE:
        price_params["u"] = str(int(datetime.strptime(END_DATE, "%Y-%m-%d").timestamp()))
    
    price_data = analyzer.fetch_metric(
        "/v1/metrics/market/price_usd_close",
        price_params,
        f"price_BTC_{START_DATE}_{END_DATE}"
    )
    
    if not price_data:
        print("❌ 无法获取价格数据")
        return
    
    price_df = pd.DataFrame(price_data)
    price_df['date'] = pd.to_datetime(price_df['t'], unit='s')
    price_df['price'] = price_df['v'].astype(float)
    price_df = price_df[['date', 'price']].set_index('date')
    
    print(f"✅ 获取到 {len(price_df)} 条价格数据")
    print(f"   价格范围: ${price_df['price'].min():,.2f} - ${price_df['price'].max():,.2f}")
    
    # 检测市场状态
    regime_df = detector.detect_market_regime(price_df)
    print(f"✅ 市场状态检测完成")
    
    # Step 2: 获取所有指标数据
    print("\n📊 Step 2: 获取所有Glassnode指标...")
    metrics_data = analyzer.fetch_all_metrics("BTC", START_DATE, END_DATE)
    print(f"\n✅ 成功获取 {len(metrics_data)} 个指标")
    
    # Step 3: 分析每个指标
    print("\n📊 Step 3: 分析指标表现...")
    metric_analyses = {}
    
    for metric_name, metric_df in metrics_data.items():
        print(f"  分析 {metric_name}...", end="")
        
        # 按市场状态分析
        regime_analysis = analyzer.analyze_metric_by_regime(metric_df, regime_df, metric_name)
        
        # 计算预测能力
        predictive_power = analyzer.calculate_predictive_power(metric_df, price_df, max_lag=14)
        
        # 识别极值
        extremes = analyzer.identify_extremes(metric_df)
        
        metric_analyses[metric_name] = {
            'regime_analysis': regime_analysis,
            'predictive_power': predictive_power,
            'extremes': extremes
        }
        
        print(" ✅")
    
    # Step 4: 生成综合分析
    print("\n📊 Step 4: 生成综合分析报告...")
    
    # 市场概览
    market_overview = reporter.generate_market_overview(regime_df)
    print(f"  当前市场状态: {market_overview['current_regime']}")
    
    # 指标排名
    rankings = reporter.rank_indicators(metric_analyses)
    if not rankings.empty:
        print(f"  最佳预测指标: {rankings.iloc[0]['metric']}")
    
    # 交易信号
    trading_signals = reporter.generate_trading_signals(metrics_data, price_df.index[-1])
    print(f"  生成交易信号: {len(trading_signals)} 个")
    
    # Step 5: 可视化
    print("\n📊 Step 5: 生成可视化图表...")
    
    # 市场状态分布图
    viz.plot_regime_distribution(regime_df, "market_regime_distribution.png")
    print("  ✅ 市场状态分布图")
    
    # 指标热力图
    viz.plot_indicator_heatmap(
        {k: v['regime_analysis'] for k, v in metric_analyses.items() if v['regime_analysis']},
        "indicator_heatmap.png"
    )
    print("  ✅ 指标热力图")
    
    # 预测能力图
    if not rankings.empty:
        viz.plot_prediction_power(rankings, "prediction_power.png")
        print("  ✅ 预测能力分析图")
    
    # 信号时间线
    viz.plot_signal_timeline(trading_signals, price_df, "signal_timeline.png")
    print("  ✅ 信号时间线图")
    
    # Step 6: 生成HTML报告
    print("\n📊 Step 6: 生成HTML报告...")
    
    all_report_data = {
        'market_overview': market_overview,
        'trading_signals': trading_signals,
        'rankings': rankings,
        'metric_analyses': {k: v['regime_analysis'] for k, v in metric_analyses.items()},
        'raw_metrics': metrics_data
    }
    
    html_file = reporter.create_html_report(all_report_data, "glassnode_comprehensive_report.html")
    print(f"  ✅ HTML报告: {html_file}")
    
    # Step 7: 保存详细数据
    print("\n📊 Step 7: 保存分析结果...")
    
    # 保存JSON格式的详细分析结果
    json_results = {
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'period': {'start': START_DATE, 'end': END_DATE},
        'market_overview': market_overview,
        'trading_signals': trading_signals,
        'top_indicators': rankings.head(20).to_dict('records') if not rankings.empty else [],
        'metric_count': len(metrics_data),
        'metrics_available': list(metrics_data.keys())
    }
    
    with open('glassnode_comprehensive_results.json', 'w', encoding='utf-8') as f:
        json.dump(json_results, f, indent=2, ensure_ascii=False, default=str)
    print("  ✅ 详细结果: glassnode_comprehensive_results.json")
    
    # 打印关键洞察
    print("\n" + "=" * 80)
    print("🎯 关键洞察")
    print("=" * 80)
    
    # 市场状态分析
    print(f"\n📈 市场状态分布:")
    for regime, pct in market_overview['regime_distribution'].items():
        print(f"  {regime}: {pct:.1f}% (平均持续 {market_overview['average_duration_days'].get(regime, 0):.0f} 天)")
    
    # 最佳指标
    if not rankings.empty:
        print(f"\n🏆 Top 5 预测指标:")
        for idx, row in rankings.head(5).iterrows():
            lag_desc = "同期"
            if row['optimal_lag'] < 0:
                lag_desc = f"领先{abs(row['optimal_lag'])}天"
            elif row['optimal_lag'] > 0:
                lag_desc = f"滞后{row['optimal_lag']}天"
            
            print(f"  {idx+1}. {row['metric']}: 相关性={row['correlation']:.3f}, "
                  f"准确率={row['accuracy']:.1f}%, {lag_desc}")
    
    # 当前信号
    if trading_signals:
        print(f"\n💡 当前交易信号:")
        for signal in trading_signals[:3]:  # 只显示前3个
            print(f"  [{signal['type']}] {signal['indicator']}: {signal['reason']}")
    
    print("\n✅ 分析完成！")
    print("\n生成的文件:")
    print("  1. glassnode_comprehensive_report.html - 综合HTML报告")
    print("  2. glassnode_comprehensive_results.json - 详细JSON数据")
    print("  3. market_regime_distribution.png - 市场状态分布图")
    print("  4. indicator_heatmap.png - 指标热力图")
    print("  5. prediction_power.png - 预测能力分析图")
    print("  6. signal_timeline.png - 信号时间线图")


if __name__ == "__main__":
    main()