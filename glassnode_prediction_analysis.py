"""
Glassnode指标预测能力深度分析系统
分析各指标在不同市场状态下的预测性能：提前时间、准确率、召回率、F1值
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


class PredictionAnalyzer:
    """指标预测能力分析器"""
    
    def __init__(self):
        self.results = {}
        
    def create_price_targets(self, price_df: pd.DataFrame, horizons: List[int] = [1, 3, 7, 14, 30]):
        """
        创建不同时间跨度的价格目标
        
        Parameters:
        - price_df: 价格数据
        - horizons: 预测时间跨度列表（天数）
        
        Returns:
        - DataFrame with price change targets
        """
        targets = pd.DataFrame(index=price_df.index)
        
        for h in horizons:
            # 未来h天的收益率
            targets[f'return_{h}d'] = price_df['price'].pct_change(h).shift(-h)
            
            # 二分类标签（涨/跌）
            targets[f'direction_{h}d'] = (targets[f'return_{h}d'] > 0).astype(int)
            
            # 多分类标签（大涨/小涨/横盘/小跌/大跌）
            returns = targets[f'return_{h}d']
            conditions = [
                (returns > 0.10),  # 大涨 >10%
                (returns > 0.02),  # 小涨 2-10%
                (returns > -0.02),  # 横盘 -2%到2%
                (returns > -0.10),  # 小跌 -10%到-2%
                (returns <= -0.10)  # 大跌 <-10%
            ]
            choices = [4, 3, 2, 1, 0]  # 标签：0=大跌, 1=小跌, 2=横盘, 3=小涨, 4=大涨
            targets[f'category_{h}d'] = np.select(conditions, choices, default=2)
            
            # 极端事件标签
            targets[f'extreme_up_{h}d'] = (returns > 0.15).astype(int)  # 极端上涨 >15%
            targets[f'extreme_down_{h}d'] = (returns < -0.15).astype(int)  # 极端下跌 <-15%
        
        return targets
    
    def calculate_indicator_signals(self, indicator_df: pd.DataFrame, indicator_name: str) -> pd.DataFrame:
        """
        计算指标的交易信号
        
        Parameters:
        - indicator_df: 指标数据
        - indicator_name: 指标名称
        
        Returns:
        - DataFrame with indicator signals
        """
        signals = pd.DataFrame(index=indicator_df.index)
        indicator_col = indicator_df.iloc[:, 0]
        
        # 基础信号
        signals['value'] = indicator_col
        signals['ma_7'] = indicator_col.rolling(7).mean()
        signals['ma_30'] = indicator_col.rolling(30).mean()
        
        # Z-Score标准化
        signals['z_score'] = (indicator_col - indicator_col.rolling(90).mean()) / indicator_col.rolling(90).std()
        
        # 变化率
        signals['change_1d'] = indicator_col.pct_change()
        signals['change_7d'] = indicator_col.pct_change(7)
        signals['change_30d'] = indicator_col.pct_change(30)
        
        # 动量
        signals['momentum'] = indicator_col - indicator_col.shift(14)
        
        # 相对强弱
        gains = signals['change_1d'].where(signals['change_1d'] > 0, 0)
        losses = -signals['change_1d'].where(signals['change_1d'] < 0, 0)
        avg_gain = gains.rolling(14).mean()
        avg_loss = losses.rolling(14).mean()
        rs = avg_gain / avg_loss
        signals['rsi'] = 100 - (100 / (1 + rs))
        
        # 生成交易信号
        # 根据不同指标类型设置阈值
        if 'mvrv' in indicator_name.lower():
            signals['signal_strong_buy'] = (signals['z_score'] < -1).astype(int)
            signals['signal_buy'] = (signals['z_score'] < 0).astype(int)
            signals['signal_sell'] = (signals['z_score'] > 2).astype(int)
            signals['signal_strong_sell'] = (signals['z_score'] > 3).astype(int)
            
        elif 'sopr' in indicator_name.lower():
            signals['signal_strong_buy'] = (indicator_col < 0.95).astype(int)
            signals['signal_buy'] = ((indicator_col < 1.0) & (indicator_col > indicator_col.shift(1))).astype(int)
            signals['signal_sell'] = ((indicator_col > 1.05) & (indicator_col < indicator_col.shift(1))).astype(int)
            signals['signal_strong_sell'] = (indicator_col > 1.1).astype(int)
            
        elif 'nupl' in indicator_name.lower() or 'profit' in indicator_name.lower():
            signals['signal_strong_buy'] = (indicator_col < 0).astype(int)
            signals['signal_buy'] = (indicator_col < 0.25).astype(int)
            signals['signal_sell'] = (indicator_col > 0.5).astype(int)
            signals['signal_strong_sell'] = (indicator_col > 0.75).astype(int)
            
        else:
            # 通用信号（基于Z-Score）
            signals['signal_strong_buy'] = (signals['z_score'] < -2).astype(int)
            signals['signal_buy'] = (signals['z_score'] < -1).astype(int)
            signals['signal_sell'] = (signals['z_score'] > 1).astype(int)
            signals['signal_strong_sell'] = (signals['z_score'] > 2).astype(int)
        
        # 综合信号（-2到2的连续值）
        signals['composite_signal'] = 0
        signals.loc[signals['signal_strong_sell'] == 1, 'composite_signal'] = -2
        signals.loc[signals['signal_sell'] == 1, 'composite_signal'] = -1
        signals.loc[signals['signal_buy'] == 1, 'composite_signal'] = 1
        signals.loc[signals['signal_strong_buy'] == 1, 'composite_signal'] = 2
        
        return signals
    
    def evaluate_prediction_performance(self, signals: pd.DataFrame, targets: pd.DataFrame, 
                                      horizon: int, signal_col: str = 'composite_signal') -> Dict:
        """
        评估预测性能
        
        Parameters:
        - signals: 信号数据
        - targets: 目标数据
        - horizon: 预测时间跨度
        - signal_col: 使用的信号列
        
        Returns:
        - 性能指标字典
        """
        # 合并数据
        data = pd.merge(signals[[signal_col]], targets, left_index=True, right_index=True, how='inner')
        data = data.dropna()
        
        if len(data) < 100:
            return {}
        
        results = {
            'horizon_days': horizon,
            'sample_size': len(data)
        }
        
        # 方向预测（二分类）
        direction_col = f'direction_{horizon}d'
        if direction_col in data.columns:
            # 将信号转换为二分类（正信号=1，负信号=0）
            pred_direction = (data[signal_col] > 0).astype(int)
            true_direction = data[direction_col]
            
            # 计算混淆矩阵
            tn, fp, fn, tp = confusion_matrix(true_direction, pred_direction).ravel()
            
            # 计算指标
            accuracy = (tp + tn) / (tp + tn + fp + fn)
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            results['direction_prediction'] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'confusion_matrix': {
                    'true_positive': int(tp),
                    'true_negative': int(tn),
                    'false_positive': int(fp),
                    'false_negative': int(fn)
                }
            }
            
            # Matthews相关系数
            mcc_denominator = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
            if mcc_denominator > 0:
                mcc = (tp * tn - fp * fn) / mcc_denominator
                results['direction_prediction']['mcc'] = mcc
        
        # 极端事件预测
        extreme_up_col = f'extreme_up_{horizon}d'
        extreme_down_col = f'extreme_down_{horizon}d'
        
        if extreme_up_col in data.columns:
            # 极端上涨预测（强买信号）
            pred_extreme_up = (data[signal_col] >= 2).astype(int)
            true_extreme_up = data[extreme_up_col]
            
            if true_extreme_up.sum() > 0:
                tp_up = ((pred_extreme_up == 1) & (true_extreme_up == 1)).sum()
                fp_up = ((pred_extreme_up == 1) & (true_extreme_up == 0)).sum()
                fn_up = ((pred_extreme_up == 0) & (true_extreme_up == 1)).sum()
                
                precision_up = tp_up / (tp_up + fp_up) if (tp_up + fp_up) > 0 else 0
                recall_up = tp_up / (tp_up + fn_up) if (tp_up + fn_up) > 0 else 0
                f1_up = 2 * (precision_up * recall_up) / (precision_up + recall_up) if (precision_up + recall_up) > 0 else 0
                
                results['extreme_up_prediction'] = {
                    'precision': precision_up,
                    'recall': recall_up,
                    'f1_score': f1_up,
                    'true_positives': int(tp_up),
                    'false_positives': int(fp_up),
                    'false_negatives': int(fn_up)
                }
        
        if extreme_down_col in data.columns:
            # 极端下跌预测（强卖信号）
            pred_extreme_down = (data[signal_col] <= -2).astype(int)
            true_extreme_down = data[extreme_down_col]
            
            if true_extreme_down.sum() > 0:
                tp_down = ((pred_extreme_down == 1) & (true_extreme_down == 1)).sum()
                fp_down = ((pred_extreme_down == 1) & (true_extreme_down == 0)).sum()
                fn_down = ((pred_extreme_down == 0) & (true_extreme_down == 1)).sum()
                
                precision_down = tp_down / (tp_down + fp_down) if (tp_down + fp_down) > 0 else 0
                recall_down = tp_down / (tp_down + fn_down) if (tp_down + fn_down) > 0 else 0
                f1_down = 2 * (precision_down * recall_down) / (precision_down + recall_down) if (precision_down + recall_down) > 0 else 0
                
                results['extreme_down_prediction'] = {
                    'precision': precision_down,
                    'recall': recall_down,
                    'f1_score': f1_down,
                    'true_positives': int(tp_down),
                    'false_positives': int(fp_down),
                    'false_negatives': int(fn_down)
                }
        
        # 收益率相关性
        return_col = f'return_{horizon}d'
        if return_col in data.columns:
            correlation = data[signal_col].corr(data[return_col])
            results['return_correlation'] = correlation
        
        return results
    
    def evaluate_by_market_regime(self, signals: pd.DataFrame, targets: pd.DataFrame,
                                 market_regimes: pd.DataFrame, horizon: int) -> Dict:
        """
        按市场状态评估预测性能
        
        Parameters:
        - signals: 信号数据
        - targets: 目标数据
        - market_regimes: 市场状态数据
        - horizon: 预测时间跨度
        
        Returns:
        - 各市场状态下的性能指标
        """
        # 合并所有数据
        data = pd.merge(signals[['composite_signal']], targets, left_index=True, right_index=True, how='inner')
        data = pd.merge(data, market_regimes[['regime']], left_index=True, right_index=True, how='inner')
        data = data.dropna()
        
        regime_results = {}
        
        for regime in ['Bull', 'Bear', 'Crash', 'Sideways']:
            regime_data = data[data['regime'] == regime]
            
            if len(regime_data) < 30:  # 样本太少则跳过
                continue
            
            # 方向预测
            direction_col = f'direction_{horizon}d'
            if direction_col in regime_data.columns:
                pred = (regime_data['composite_signal'] > 0).astype(int)
                true = regime_data[direction_col]
                
                if len(np.unique(true)) > 1:  # 确保有不同的类别
                    precision, recall, f1, _ = precision_recall_fscore_support(
                        true, pred, average='binary', zero_division=0
                    )
                    accuracy = (pred == true).mean()
                    
                    regime_results[regime] = {
                        'sample_size': len(regime_data),
                        'accuracy': float(accuracy),
                        'precision': float(precision),
                        'recall': float(recall),
                        'f1_score': float(f1)
                    }
                    
                    # 计算该市场状态下的平均收益
                    return_col = f'return_{horizon}d'
                    if return_col in regime_data.columns:
                        # 买入信号时的平均收益
                        buy_returns = regime_data[regime_data['composite_signal'] > 0][return_col]
                        if len(buy_returns) > 0:
                            regime_results[regime]['avg_return_on_buy_signal'] = float(buy_returns.mean())
                            regime_results[regime]['win_rate'] = float((buy_returns > 0).mean())
                        
                        # 卖出信号时的平均收益（应该是负的才对）
                        sell_returns = regime_data[regime_data['composite_signal'] < 0][return_col]
                        if len(sell_returns) > 0:
                            regime_results[regime]['avg_return_on_sell_signal'] = float(sell_returns.mean())
                            regime_results[regime]['sell_accuracy'] = float((sell_returns < 0).mean())
        
        return regime_results


class MarketRegimeAnalyzer:
    """市场状态分析器"""
    
    @staticmethod
    def detect_market_regimes(price_df: pd.DataFrame) -> pd.DataFrame:
        """
        检测市场状态
        
        Parameters:
        - price_df: 价格数据
        
        Returns:
        - DataFrame with market regimes
        """
        df = price_df.copy()
        
        # 计算技术指标
        df['returns'] = df['price'].pct_change()
        df['volatility'] = df['returns'].rolling(30).std() * np.sqrt(365)
        df['ma_50'] = df['price'].rolling(50).mean()
        df['ma_200'] = df['price'].rolling(200).mean()
        
        # 计算不同时间窗口的收益
        df['return_7d'] = df['price'].pct_change(7)
        df['return_30d'] = df['price'].pct_change(30)
        df['return_90d'] = df['price'].pct_change(90)
        
        # 初始化市场状态
        df['regime'] = 'Sideways'
        
        # 定义市场状态
        # 牛市：价格在上升趋势，低波动率
        bull_condition = (
            (df['price'] > df['ma_200']) &
            (df['ma_50'] > df['ma_200']) &
            (df['return_30d'] > 0.1) &
            (df['volatility'] < df['volatility'].rolling(90).mean() * 1.5)
        )
        
        # 熊市：价格在下降趋势
        bear_condition = (
            (df['price'] < df['ma_200']) &
            (df['ma_50'] < df['ma_200']) &
            (df['return_30d'] < -0.1)
        )
        
        # 崩盘：短期大幅下跌
        crash_condition = (
            (df['return_7d'] < -0.2) |
            ((df['return_30d'] < -0.3) & (df['volatility'] > df['volatility'].rolling(90).mean() * 2))
        )
        
        # 应用条件
        df.loc[bull_condition, 'regime'] = 'Bull'
        df.loc[bear_condition, 'regime'] = 'Bear'
        df.loc[crash_condition, 'regime'] = 'Crash'  # 崩盘优先级最高
        
        return df


class GlassnodeDataFetcher:
    """Glassnode数据获取器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://grassnoodle.cloud"
        self.headers = {"x-key": api_key}
        
    def fetch_metrics(self, metrics: List[Tuple[str, str]], start_date: str, end_date: str) -> Dict:
        """
        获取多个指标数据
        
        Parameters:
        - metrics: 指标列表 [(category, metric_name), ...]
        - start_date: 开始日期
        - end_date: 结束日期
        
        Returns:
        - 指标数据字典
        """
        params = {
            "a": "BTC",
            "s": str(int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())),
            "u": str(int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()))
        }
        
        data_dict = {}
        
        for category, metric in metrics:
            endpoint = f"/v1/metrics/{category}/{metric}"
            full_name = f"{category}_{metric}"
            
            try:
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        df = pd.DataFrame(data)
                        df['date'] = pd.to_datetime(df['t'], unit='s')
                        df[metric] = df['v'].astype(float)
                        df = df[['date', metric]].set_index('date')
                        data_dict[full_name] = df
                        print(f"✅ {full_name}: {len(df)} 条数据")
                    else:
                        print(f"⚠️ {full_name}: 无数据")
                elif response.status_code == 429:
                    print(f"⏳ {full_name}: 限流，等待...")
                    time.sleep(5)
                else:
                    print(f"❌ {full_name}: {response.status_code}")
                
                time.sleep(1)  # 请求间隔
                
            except Exception as e:
                print(f"❌ {full_name}: {str(e)[:50]}")
        
        return data_dict


class PredictionReportGenerator:
    """预测报告生成器"""
    
    @staticmethod
    def create_performance_matrix(all_results: Dict) -> pd.DataFrame:
        """
        创建性能矩阵
        
        Parameters:
        - all_results: 所有指标的预测结果
        
        Returns:
        - 性能矩阵DataFrame
        """
        rows = []
        
        for indicator, horizons_data in all_results.items():
            for horizon, perf_data in horizons_data.items():
                if 'direction_prediction' in perf_data:
                    row = {
                        'indicator': indicator,
                        'horizon_days': horizon,
                        'accuracy': perf_data['direction_prediction']['accuracy'],
                        'precision': perf_data['direction_prediction']['precision'],
                        'recall': perf_data['direction_prediction']['recall'],
                        'f1_score': perf_data['direction_prediction']['f1_score']
                    }
                    
                    if 'return_correlation' in perf_data:
                        row['correlation'] = perf_data['return_correlation']
                    
                    rows.append(row)
        
        if rows:
            return pd.DataFrame(rows)
        return pd.DataFrame()
    
    @staticmethod
    def plot_prediction_heatmap(performance_matrix: pd.DataFrame, metric: str = 'f1_score'):
        """
        绘制预测性能热力图
        
        Parameters:
        - performance_matrix: 性能矩阵
        - metric: 要显示的指标
        """
        if performance_matrix.empty:
            return
        
        # 创建透视表
        pivot = performance_matrix.pivot(
            index='indicator',
            columns='horizon_days',
            values=metric
        )
        
        # 绘制热力图
        plt.figure(figsize=(12, 8))
        sns.heatmap(
            pivot,
            annot=True,
            fmt='.3f',
            cmap='RdYlGn',
            center=0.5,
            vmin=0,
            vmax=1,
            cbar_kws={'label': metric.replace('_', ' ').title()}
        )
        
        plt.title(f'指标预测性能热力图 - {metric.replace("_", " ").title()}')
        plt.xlabel('预测时间跨度（天）')
        plt.ylabel('指标')
        plt.tight_layout()
        plt.savefig(f'prediction_{metric}_heatmap.png', dpi=150, bbox_inches='tight')
        plt.show()
    
    @staticmethod
    def plot_regime_performance(regime_results: Dict):
        """
        绘制不同市场状态下的预测性能
        
        Parameters:
        - regime_results: 各市场状态的预测结果
        """
        if not regime_results:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 准备数据
        indicators = list(regime_results.keys())
        regimes = ['Bull', 'Bear', 'Crash', 'Sideways']
        metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        
        for idx, metric in enumerate(metrics):
            ax = axes[idx // 2, idx % 2]
            
            # 创建数据矩阵
            data = []
            for indicator in indicators:
                row = []
                for regime in regimes:
                    if regime in regime_results[indicator]:
                        value = regime_results[indicator][regime].get(metric, 0)
                        row.append(value)
                    else:
                        row.append(np.nan)
                data.append(row)
            
            # 绘制热力图
            im = ax.imshow(data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
            
            # 设置标签
            ax.set_xticks(np.arange(len(regimes)))
            ax.set_yticks(np.arange(len(indicators)))
            ax.set_xticklabels(regimes)
            ax.set_yticklabels(indicators)
            
            # 添加数值标签
            for i in range(len(indicators)):
                for j in range(len(regimes)):
                    if not np.isnan(data[i][j]):
                        text = ax.text(j, i, f'{data[i][j]:.2f}',
                                     ha="center", va="center", color="black", fontsize=8)
            
            ax.set_title(f'{metric.replace("_", " ").title()}')
            
            # 添加颜色条
            plt.colorbar(im, ax=ax)
        
        plt.suptitle('不同市场状态下的预测性能', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('regime_performance.png', dpi=150, bbox_inches='tight')
        plt.show()
    
    @staticmethod
    def generate_summary_report(all_results: Dict, regime_results: Dict) -> Dict:
        """
        生成综合报告
        
        Parameters:
        - all_results: 所有预测结果
        - regime_results: 各市场状态结果
        
        Returns:
        - 综合报告字典
        """
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {},
            'best_indicators': {},
            'regime_analysis': {},
            'recommendations': []
        }
        
        # 找出最佳指标
        best_by_horizon = {}
        
        for indicator, horizons_data in all_results.items():
            for horizon, perf_data in horizons_data.items():
                if 'direction_prediction' not in perf_data:
                    continue
                
                f1 = perf_data['direction_prediction']['f1_score']
                
                if horizon not in best_by_horizon or f1 > best_by_horizon[horizon]['f1_score']:
                    best_by_horizon[horizon] = {
                        'indicator': indicator,
                        'f1_score': f1,
                        'accuracy': perf_data['direction_prediction']['accuracy'],
                        'precision': perf_data['direction_prediction']['precision'],
                        'recall': perf_data['direction_prediction']['recall']
                    }
        
        report['best_indicators'] = best_by_horizon
        
        # 分析各市场状态
        regime_summary = {}
        for regime in ['Bull', 'Bear', 'Crash', 'Sideways']:
            regime_indicators = []
            
            for indicator, regimes_data in regime_results.items():
                if regime in regimes_data:
                    regime_indicators.append({
                        'indicator': indicator,
                        'f1_score': regimes_data[regime].get('f1_score', 0),
                        'accuracy': regimes_data[regime].get('accuracy', 0)
                    })
            
            if regime_indicators:
                # 按F1分数排序
                regime_indicators.sort(key=lambda x: x['f1_score'], reverse=True)
                regime_summary[regime] = {
                    'best_indicator': regime_indicators[0]['indicator'],
                    'best_f1': regime_indicators[0]['f1_score'],
                    'best_accuracy': regime_indicators[0]['accuracy']
                }
        
        report['regime_analysis'] = regime_summary
        
        # 生成建议
        recommendations = []
        
        # 短期交易建议（1-3天）
        if 1 in best_by_horizon:
            best_1d = best_by_horizon[1]
            recommendations.append(
                f"短期交易（1天）: 使用 {best_1d['indicator']} "
                f"(准确率={best_1d['accuracy']:.1%}, F1={best_1d['f1_score']:.3f})"
            )
        
        # 中期交易建议（7-14天）
        if 7 in best_by_horizon:
            best_7d = best_by_horizon[7]
            recommendations.append(
                f"中期交易（7天）: 使用 {best_7d['indicator']} "
                f"(准确率={best_7d['accuracy']:.1%}, F1={best_7d['f1_score']:.3f})"
            )
        
        # 长期投资建议（30天）
        if 30 in best_by_horizon:
            best_30d = best_by_horizon[30]
            recommendations.append(
                f"长期投资（30天）: 使用 {best_30d['indicator']} "
                f"(准确率={best_30d['accuracy']:.1%}, F1={best_30d['f1_score']:.3f})"
            )
        
        # 市场状态建议
        for regime, data in regime_summary.items():
            recommendations.append(
                f"{regime}市场: 优先使用 {data['best_indicator']} "
                f"(F1={data['best_f1']:.3f})"
            )
        
        report['recommendations'] = recommendations
        
        return report


def main():
    """主函数"""
    # 配置
    API_KEY = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
    START_DATE = "2021-01-01"
    END_DATE = "2024-12-31"
    
    # 要分析的核心指标
    METRICS_TO_ANALYZE = [
        ('market', 'price_usd_close'),
        ('market', 'mvrv'),
        ('market', 'mvrv_z_score'),
        ('indicators', 'sopr'),
        ('indicators', 'net_unrealized_profit_loss'),
        ('indicators', 'puell_multiple'),
        ('indicators', 'reserve_risk'),
        ('supply', 'profit_relative'),
        ('addresses', 'active_count'),
        ('mining', 'hash_rate_mean'),
        ('derivatives', 'futures_funding_rate_perpetual')
    ]
    
    # 预测时间跨度
    HORIZONS = [1, 3, 7, 14, 30]
    
    print("=" * 80)
    print("🔬 Glassnode指标预测能力深度分析")
    print("=" * 80)
    print(f"分析周期: {START_DATE} 至 {END_DATE}")
    print(f"预测跨度: {HORIZONS} 天")
    print(f"分析指标: {len(METRICS_TO_ANALYZE)} 个")
    
    # 初始化组件
    fetcher = GlassnodeDataFetcher(API_KEY)
    predictor = PredictionAnalyzer()
    regime_analyzer = MarketRegimeAnalyzer()
    reporter = PredictionReportGenerator()
    
    # Step 1: 获取数据
    print("\n📊 Step 1: 获取指标数据...")
    metrics_data = fetcher.fetch_metrics(METRICS_TO_ANALYZE, START_DATE, END_DATE)
    
    if 'market_price_usd_close' not in metrics_data:
        print("❌ 无法获取价格数据")
        return
    
    price_df = metrics_data['market_price_usd_close'].rename(columns={'price_usd_close': 'price'})
    
    # Step 2: 检测市场状态
    print("\n📊 Step 2: 检测市场状态...")
    market_regimes = regime_analyzer.detect_market_regimes(price_df)
    
    regime_distribution = market_regimes['regime'].value_counts()
    print("市场状态分布:")
    for regime, count in regime_distribution.items():
        pct = count / len(market_regimes) * 100
        print(f"  {regime}: {count} 天 ({pct:.1f}%)")
    
    # Step 3: 创建价格目标
    print("\n📊 Step 3: 创建预测目标...")
    price_targets = predictor.create_price_targets(price_df, HORIZONS)
    
    # Step 4: 分析每个指标
    print("\n📊 Step 4: 分析指标预测能力...")
    all_results = {}
    regime_results = {}
    
    for metric_full_name, metric_df in metrics_data.items():
        if metric_full_name == 'market_price_usd_close':
            continue  # 跳过价格本身
        
        print(f"\n分析 {metric_full_name}...")
        
        # 计算指标信号
        signals = predictor.calculate_indicator_signals(metric_df, metric_full_name)
        
        # 评估不同时间跨度的预测性能
        horizon_results = {}
        for horizon in HORIZONS:
            perf = predictor.evaluate_prediction_performance(signals, price_targets, horizon)
            if perf:
                horizon_results[horizon] = perf
                
                if 'direction_prediction' in perf:
                    print(f"  {horizon}天: 准确率={perf['direction_prediction']['accuracy']:.1%}, "
                          f"F1={perf['direction_prediction']['f1_score']:.3f}")
        
        all_results[metric_full_name] = horizon_results
        
        # 评估不同市场状态下的性能
        regime_perf = predictor.evaluate_by_market_regime(
            signals, price_targets, market_regimes, 7  # 使用7天作为标准
        )
        if regime_perf:
            regime_results[metric_full_name] = regime_perf
    
    # Step 5: 生成性能矩阵
    print("\n📊 Step 5: 生成性能分析...")
    performance_matrix = reporter.create_performance_matrix(all_results)
    
    if not performance_matrix.empty:
        # 找出最佳指标
        print("\n🏆 最佳预测指标（按F1分数）:")
        best_indicators = performance_matrix.groupby('horizon_days').apply(
            lambda x: x.nlargest(1, 'f1_score')[['indicator', 'f1_score', 'accuracy', 'precision', 'recall']]
        )
        print(best_indicators.to_string())
        
        # 保存性能矩阵
        performance_matrix.to_csv('prediction_performance_matrix.csv', index=False)
        print("\n✅ 性能矩阵已保存: prediction_performance_matrix.csv")
    
    # Step 6: 可视化
    print("\n📊 Step 6: 生成可视化...")
    
    # F1分数热力图
    reporter.plot_prediction_heatmap(performance_matrix, 'f1_score')
    print("  ✅ F1分数热力图")
    
    # 准确率热力图
    reporter.plot_prediction_heatmap(performance_matrix, 'accuracy')
    print("  ✅ 准确率热力图")
    
    # 召回率热力图
    reporter.plot_prediction_heatmap(performance_matrix, 'recall')
    print("  ✅ 召回率热力图")
    
    # 不同市场状态性能
    if regime_results:
        reporter.plot_regime_performance(regime_results)
        print("  ✅ 市场状态性能图")
    
    # Step 7: 生成综合报告
    print("\n📊 Step 7: 生成综合报告...")
    summary_report = reporter.generate_summary_report(all_results, regime_results)
    
    # 保存报告
    with open('prediction_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(summary_report, f, indent=2, ensure_ascii=False, default=str)
    print("✅ 分析报告已保存: prediction_analysis_report.json")
    
    # 打印关键发现
    print("\n" + "=" * 80)
    print("🎯 关键发现")
    print("=" * 80)
    
    print("\n📈 最佳指标（按预测时间跨度）:")
    for horizon, best in summary_report['best_indicators'].items():
        print(f"  {horizon}天预测: {best['indicator']}")
        print(f"    - 准确率: {best['accuracy']:.1%}")
        print(f"    - 精确率: {best['precision']:.1%}")
        print(f"    - 召回率: {best['recall']:.1%}")
        print(f"    - F1分数: {best['f1_score']:.3f}")
    
    print("\n📊 市场状态最佳指标:")
    for regime, data in summary_report['regime_analysis'].items():
        print(f"  {regime}: {data['best_indicator']} (F1={data['best_f1']:.3f})")
    
    print("\n💡 交易建议:")
    for rec in summary_report['recommendations']:
        print(f"  • {rec}")
    
    # 创建详细的性能表格
    print("\n📋 详细性能指标:")
    if not performance_matrix.empty:
        # 按F1分数排序的Top 10
        top_10 = performance_matrix.nlargest(10, 'f1_score')
        print("\nTop 10 指标-时间组合（按F1分数）:")
        for idx, row in top_10.iterrows():
            print(f"  {row['indicator']} ({row['horizon_days']}天):")
            print(f"    准确率={row['accuracy']:.1%}, 精确率={row['precision']:.1%}, "
                  f"召回率={row['recall']:.1%}, F1={row['f1_score']:.3f}")
    
    print("\n✅ 分析完成！")
    print("\n生成的文件:")
    print("  1. prediction_performance_matrix.csv - 详细性能数据")
    print("  2. prediction_analysis_report.json - 综合分析报告")
    print("  3. prediction_f1_score_heatmap.png - F1分数热力图")
    print("  4. prediction_accuracy_heatmap.png - 准确率热力图")
    print("  5. prediction_recall_heatmap.png - 召回率热力图")
    print("  6. regime_performance.png - 市场状态性能图")


if __name__ == "__main__":
    main()