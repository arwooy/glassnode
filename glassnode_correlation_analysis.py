"""
Glassnode链上指标与市场价格相关性分析系统
分析核心指标（SOPR, MVRV, NUPL等）与BTC价格的相关性及时间滞后效应
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
from scipy import stats
from scipy.signal import correlate
import warnings
warnings.filterwarnings('ignore')

class GlassnodeAnalyzer:
    """Glassnode数据分析器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://grassnoodle.cloud"
        self.headers = {"x-key": api_key}
        self.data_cache = {}
        
    def fetch_metric(self, endpoint: str, params: dict, cache_key: str = None) -> List[dict]:
        """获取指标数据"""
        if cache_key and cache_key in self.data_cache:
            print(f"使用缓存数据: {cache_key}")
            return self.data_cache[cache_key]
            
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if cache_key:
                self.data_cache[cache_key] = data
            
            time.sleep(0.5)  # 避免频率限制
            return data
        except Exception as e:
            print(f"获取数据失败 {endpoint}: {e}")
            return []
    
    def get_price_data(self, asset: str = "BTC", start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取价格数据"""
        params = {"a": asset}
        if start_date:
            params["s"] = str(int(datetime.strptime(start_date, "%Y-%m-%d").timestamp()))
        if end_date:
            params["u"] = str(int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()))
        
        data = self.fetch_metric(
            "/v1/metrics/market/price_usd_close",
            params,
            f"price_{asset}_{start_date}_{end_date}"
        )
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['t'], unit='s')
        df['price'] = df['v'].astype(float)
        return df[['date', 'price']].set_index('date')
    
    def get_sopr(self, asset: str = "BTC", start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取SOPR数据"""
        params = {"a": asset}
        if start_date:
            params["s"] = str(int(datetime.strptime(start_date, "%Y-%m-%d").timestamp()))
        if end_date:
            params["u"] = str(int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()))
        
        data = self.fetch_metric(
            "/v1/metrics/indicators/sopr",
            params,
            f"sopr_{asset}_{start_date}_{end_date}"
        )
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['t'], unit='s')
        df['sopr'] = df['v'].astype(float)
        return df[['date', 'sopr']].set_index('date')
    
    def get_mvrv(self, asset: str = "BTC", start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取MVRV数据"""
        params = {"a": asset}
        if start_date:
            params["s"] = str(int(datetime.strptime(start_date, "%Y-%m-%d").timestamp()))
        if end_date:
            params["u"] = str(int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()))
        
        # 尝试获取MVRV Z-Score
        data = self.fetch_metric(
            "/v1/metrics/market/mvrv_z_score",
            params,
            f"mvrv_zscore_{asset}_{start_date}_{end_date}"
        )
        
        if not data:
            # 如果Z-Score不可用，尝试普通MVRV
            data = self.fetch_metric(
                "/v1/metrics/market/mvrv",
                params,
                f"mvrv_{asset}_{start_date}_{end_date}"
            )
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['t'], unit='s')
        df['mvrv'] = df['v'].astype(float)
        return df[['date', 'mvrv']].set_index('date')
    
    def get_nupl(self, asset: str = "BTC", start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取NUPL数据"""
        params = {"a": asset}
        if start_date:
            params["s"] = str(int(datetime.strptime(start_date, "%Y-%m-%d").timestamp()))
        if end_date:
            params["u"] = str(int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()))
        
        data = self.fetch_metric(
            "/v1/metrics/indicators/net_unrealized_profit_loss",
            params,
            f"nupl_{asset}_{start_date}_{end_date}"
        )
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['t'], unit='s')
        df['nupl'] = df['v'].astype(float)
        return df[['date', 'nupl']].set_index('date')
    
    def get_exchange_flows(self, asset: str = "BTC", start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取交易所流量数据"""
        params = {"a": asset}
        if start_date:
            params["s"] = str(int(datetime.strptime(start_date, "%Y-%m-%d").timestamp()))
        if end_date:
            params["u"] = str(int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()))
        
        # 获取交易所净流量
        data = self.fetch_metric(
            "/v1/metrics/transactions/transfers_volume_to_exchanges_net",
            params,
            f"exchange_flow_{asset}_{start_date}_{end_date}"
        )
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['t'], unit='s')
        df['exchange_flow'] = df['v'].astype(float)
        return df[['date', 'exchange_flow']].set_index('date')
    
    def get_long_term_holder_supply(self, asset: str = "BTC", start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取长期持有者供应量"""
        params = {"a": asset}
        if start_date:
            params["s"] = str(int(datetime.strptime(start_date, "%Y-%m-%d").timestamp()))
        if end_date:
            params["u"] = str(int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()))
        
        data = self.fetch_metric(
            "/v1/metrics/supply/long_term_holder_supply",
            params,
            f"lth_supply_{asset}_{start_date}_{end_date}"
        )
        
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['t'], unit='s')
        df['lth_supply'] = df['v'].astype(float)
        return df[['date', 'lth_supply']].set_index('date')


class CorrelationAnalyzer:
    """相关性分析器"""
    
    def __init__(self):
        self.results = {}
        
    def calculate_correlation(self, df1: pd.Series, df2: pd.Series, method: str = 'pearson') -> float:
        """计算相关系数"""
        if method == 'pearson':
            return df1.corr(df2)
        elif method == 'spearman':
            return df1.corr(df2, method='spearman')
        elif method == 'kendall':
            return df1.corr(df2, method='kendall')
    
    def calculate_lagged_correlation(self, indicator: pd.Series, price: pd.Series, 
                                    max_lag: int = 30) -> Dict[int, float]:
        """计算滞后相关性"""
        correlations = {}
        
        for lag in range(-max_lag, max_lag + 1):
            if lag < 0:
                # 指标领先价格
                shifted_indicator = indicator.shift(lag)
                corr = shifted_indicator.corr(price)
            elif lag > 0:
                # 价格领先指标
                shifted_price = price.shift(lag)
                corr = indicator.corr(shifted_price)
            else:
                # 同期相关
                corr = indicator.corr(price)
            
            correlations[lag] = corr
        
        return correlations
    
    def find_optimal_lag(self, correlations: Dict[int, float]) -> Tuple[int, float]:
        """找到最优滞后期"""
        # 移除NaN值
        valid_corrs = {k: v for k, v in correlations.items() if not np.isnan(v)}
        
        if not valid_corrs:
            return 0, 0.0
        
        # 找到绝对值最大的相关系数
        optimal_lag = max(valid_corrs, key=lambda k: abs(valid_corrs[k]))
        optimal_corr = valid_corrs[optimal_lag]
        
        return optimal_lag, optimal_corr
    
    def calculate_granger_causality(self, indicator: pd.Series, price: pd.Series, 
                                   max_lag: int = 5) -> Dict:
        """计算格兰杰因果关系"""
        from statsmodels.tsa.stattools import grangercausalitytests
        
        # 准备数据
        data = pd.DataFrame({
            'price': price,
            'indicator': indicator
        }).dropna()
        
        try:
            # 测试指标是否格兰杰因果于价格
            results = grangercausalitytests(data[['price', 'indicator']], max_lag, verbose=False)
            
            causality_results = {}
            for lag in range(1, max_lag + 1):
                test_result = results[lag][0]
                # 使用参数F检验的p值
                p_value = test_result['params_ftest'][1]
                causality_results[lag] = {
                    'p_value': p_value,
                    'significant': p_value < 0.05
                }
            
            return causality_results
        except Exception as e:
            print(f"格兰杰因果检验失败: {e}")
            return {}
    
    def analyze_prediction_power(self, indicator: pd.Series, price: pd.Series, 
                                threshold: float = 0.05) -> Dict:
        """分析指标的预测能力"""
        # 计算价格变化
        price_returns = price.pct_change()
        
        # 计算指标变化
        indicator_change = indicator.pct_change()
        
        # 定义极端事件（价格大幅变化）
        extreme_events = abs(price_returns) > price_returns.std() * 2
        
        # 检查指标在极端事件前的表现
        prediction_results = {
            'sensitivity': 0,  # 灵敏度
            'specificity': 0,  # 特异性
            'accuracy': 0,     # 准确率
            'lead_time': []    # 领先时间
        }
        
        # 计算各种指标
        for lag in range(1, 11):  # 检查1-10天的领先
            shifted_indicator = indicator_change.shift(lag)
            
            # 指标异常定义
            indicator_signal = abs(shifted_indicator) > shifted_indicator.std() * 1.5
            
            # 计算混淆矩阵
            tp = ((indicator_signal == True) & (extreme_events == True)).sum()
            tn = ((indicator_signal == False) & (extreme_events == False)).sum()
            fp = ((indicator_signal == True) & (extreme_events == False)).sum()
            fn = ((indicator_signal == False) & (extreme_events == True)).sum()
            
            if tp + fn > 0:
                sensitivity = tp / (tp + fn)
                if sensitivity > prediction_results['sensitivity']:
                    prediction_results['sensitivity'] = sensitivity
                    prediction_results['lead_time'].append(lag)
            
            if tn + fp > 0:
                specificity = tn / (tn + fp)
                prediction_results['specificity'] = max(prediction_results['specificity'], specificity)
            
            if tp + tn + fp + fn > 0:
                accuracy = (tp + tn) / (tp + tn + fp + fn)
                prediction_results['accuracy'] = max(prediction_results['accuracy'], accuracy)
        
        return prediction_results


class VisualizationModule:
    """可视化模块"""
    
    @staticmethod
    def plot_correlation_heatmap(correlations: Dict[str, float], title: str = "Indicator Correlation Heatmap"):
        """绘制相关性热力图"""
        plt.figure(figsize=(10, 8))
        
        # 准备数据
        indicators = list(correlations.keys())
        corr_values = list(correlations.values())
        
        # 创建矩阵
        corr_matrix = np.array(corr_values).reshape(1, -1)
        
        sns.heatmap(corr_matrix, 
                   annot=True, 
                   fmt='.3f',
                   xticklabels=indicators,
                   yticklabels=['Price Correlation'],
                   cmap='coolwarm',
                   center=0,
                   vmin=-1,
                   vmax=1,
                   cbar_kws={'label': 'Correlation Coefficient'})
        
        plt.title(title)
        plt.tight_layout()
        plt.savefig('correlation_heatmap.png', dpi=300)
        plt.show()
    
    @staticmethod
    def plot_lagged_correlation(lag_correlations: Dict[str, Dict[int, float]], 
                                title: str = "Lagged Correlation Analysis"):
        """绘制滞后相关性图"""
        fig, axes = plt.subplots(len(lag_correlations), 1, figsize=(12, 4*len(lag_correlations)))
        
        if len(lag_correlations) == 1:
            axes = [axes]
        
        for idx, (indicator, correlations) in enumerate(lag_correlations.items()):
            lags = list(correlations.keys())
            corrs = list(correlations.values())
            
            axes[idx].bar(lags, corrs, color=['red' if c < 0 else 'green' for c in corrs])
            axes[idx].set_xlabel('Lag (days)')
            axes[idx].set_ylabel('Correlation Coefficient')
            axes[idx].set_title(f'{indicator} - Lagged Correlation')
            axes[idx].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            axes[idx].grid(True, alpha=0.3)
            
            # 标记最优滞后期
            optimal_lag = max(correlations, key=lambda k: abs(correlations[k]))
            axes[idx].axvline(x=optimal_lag, color='blue', linestyle='--', 
                             label=f'Optimal Lag: {optimal_lag} days')
            axes[idx].legend()
        
        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig('lagged_correlation.png', dpi=300)
        plt.show()
    
    @staticmethod
    def plot_indicator_vs_price(indicator_data: pd.DataFrame, price_data: pd.DataFrame, 
                               indicator_name: str, optimal_lag: int = 0):
        """绘制指标与价格对比图"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
        
        # 价格图
        ax1.plot(price_data.index, price_data.values, label='BTC Price', color='blue', linewidth=1)
        ax1.set_ylabel('Price (USD)', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper left')
        ax1.set_title(f'BTC Price vs {indicator_name}')
        
        # 指标图
        color = 'red'
        ax2.plot(indicator_data.index, indicator_data.values, 
                label=f'{indicator_name}', color=color, linewidth=1)
        
        if optimal_lag != 0:
            shifted_indicator = indicator_data.shift(optimal_lag)
            ax2.plot(shifted_indicator.index, shifted_indicator.values, 
                    label=f'{indicator_name} (Lag {optimal_lag} days)', 
                    color='orange', linewidth=1, linestyle='--')
        
        ax2.set_xlabel('Date')
        ax2.set_ylabel(indicator_name, color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='upper left')
        
        plt.tight_layout()
        plt.savefig(f'{indicator_name.lower()}_vs_price.png', dpi=300)
        plt.show()
    
    @staticmethod
    def plot_prediction_analysis(prediction_results: Dict[str, Dict], title: str = "Prediction Power Analysis"):
        """绘制预测能力分析图"""
        indicators = list(prediction_results.keys())
        sensitivities = [prediction_results[ind]['sensitivity'] for ind in indicators]
        specificities = [prediction_results[ind]['specificity'] for ind in indicators]
        accuracies = [prediction_results[ind]['accuracy'] for ind in indicators]
        
        x = np.arange(len(indicators))
        width = 0.25
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        bars1 = ax.bar(x - width, sensitivities, width, label='Sensitivity', color='green')
        bars2 = ax.bar(x, specificities, width, label='Specificity', color='blue')
        bars3 = ax.bar(x + width, accuracies, width, label='Accuracy', color='orange')
        
        ax.set_xlabel('Indicator')
        ax.set_ylabel('Score')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(indicators, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.2f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom',
                           fontsize=8)
        
        plt.tight_layout()
        plt.savefig('prediction_analysis.png', dpi=300)
        plt.show()


def main():
    """主函数"""
    # 配置
    API_KEY = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"  # 使用提供的API密钥
    START_DATE = "2023-01-01"
    END_DATE = "2024-12-31"
    
    print("=" * 80)
    print("Glassnode核心指标与BTC价格相关性分析")
    print("=" * 80)
    
    # 初始化分析器
    glassnode = GlassnodeAnalyzer(API_KEY)
    correlation_analyzer = CorrelationAnalyzer()
    viz = VisualizationModule()
    
    # 获取价格数据
    print("\n1. 获取BTC价格数据...")
    price_df = glassnode.get_price_data("BTC", START_DATE, END_DATE)
    
    if price_df.empty:
        print("错误：无法获取价格数据")
        return
    
    print(f"获取到 {len(price_df)} 条价格数据")
    print(f"价格范围: ${price_df['price'].min():.2f} - ${price_df['price'].max():.2f}")
    
    # 获取各项指标数据
    indicators_data = {}
    
    print("\n2. 获取链上指标数据...")
    
    # SOPR
    print("   - 获取SOPR数据...")
    sopr_df = glassnode.get_sopr("BTC", START_DATE, END_DATE)
    if not sopr_df.empty:
        indicators_data['SOPR'] = sopr_df
        print(f"     获取到 {len(sopr_df)} 条SOPR数据")
    
    # MVRV
    print("   - 获取MVRV数据...")
    mvrv_df = glassnode.get_mvrv("BTC", START_DATE, END_DATE)
    if not mvrv_df.empty:
        indicators_data['MVRV'] = mvrv_df
        print(f"     获取到 {len(mvrv_df)} 条MVRV数据")
    
    # NUPL
    print("   - 获取NUPL数据...")
    nupl_df = glassnode.get_nupl("BTC", START_DATE, END_DATE)
    if not nupl_df.empty:
        indicators_data['NUPL'] = nupl_df
        print(f"     获取到 {len(nupl_df)} 条NUPL数据")
    
    # 交易所流量
    print("   - 获取交易所流量数据...")
    exchange_df = glassnode.get_exchange_flows("BTC", START_DATE, END_DATE)
    if not exchange_df.empty:
        indicators_data['Exchange_Flow'] = exchange_df
        print(f"     获取到 {len(exchange_df)} 条交易所流量数据")
    
    # 长期持有者供应量
    print("   - 获取长期持有者供应量数据...")
    lth_df = glassnode.get_long_term_holder_supply("BTC", START_DATE, END_DATE)
    if not lth_df.empty:
        indicators_data['LTH_Supply'] = lth_df
        print(f"     获取到 {len(lth_df)} 条长期持有者供应量数据")
    
    if not indicators_data:
        print("错误：无法获取任何指标数据")
        return
    
    # 分析相关性
    print("\n3. 分析相关性...")
    
    # 同期相关性
    simple_correlations = {}
    lagged_correlations = {}
    optimal_lags = {}
    prediction_results = {}
    granger_results = {}
    
    for indicator_name, indicator_df in indicators_data.items():
        print(f"\n   分析 {indicator_name}...")
        
        # 合并数据
        merged_df = pd.merge(price_df, indicator_df, left_index=True, right_index=True, how='inner')
        
        if len(merged_df) < 30:
            print(f"     数据点过少，跳过 {indicator_name}")
            continue
        
        # 计算简单相关性
        corr = correlation_analyzer.calculate_correlation(
            merged_df['price'], 
            merged_df[merged_df.columns[1]]
        )
        simple_correlations[indicator_name] = corr
        print(f"     同期相关系数: {corr:.4f}")
        
        # 计算滞后相关性
        lag_corrs = correlation_analyzer.calculate_lagged_correlation(
            merged_df[merged_df.columns[1]], 
            merged_df['price'],
            max_lag=30
        )
        lagged_correlations[indicator_name] = lag_corrs
        
        # 找到最优滞后期
        opt_lag, opt_corr = correlation_analyzer.find_optimal_lag(lag_corrs)
        optimal_lags[indicator_name] = {'lag': opt_lag, 'correlation': opt_corr}
        
        if opt_lag < 0:
            print(f"     最优滞后期: 指标领先价格 {abs(opt_lag)} 天，相关系数: {opt_corr:.4f}")
        elif opt_lag > 0:
            print(f"     最优滞后期: 价格领先指标 {opt_lag} 天，相关系数: {opt_corr:.4f}")
        else:
            print(f"     最优滞后期: 同期，相关系数: {opt_corr:.4f}")
        
        # 计算预测能力
        pred_results = correlation_analyzer.analyze_prediction_power(
            merged_df[merged_df.columns[1]], 
            merged_df['price']
        )
        prediction_results[indicator_name] = pred_results
        print(f"     预测能力 - 灵敏度: {pred_results['sensitivity']:.2%}, "
              f"特异性: {pred_results['specificity']:.2%}, "
              f"准确率: {pred_results['accuracy']:.2%}")
        
        # 格兰杰因果检验
        if len(merged_df) > 100:
            granger = correlation_analyzer.calculate_granger_causality(
                merged_df[merged_df.columns[1]], 
                merged_df['price'],
                max_lag=5
            )
            if granger:
                granger_results[indicator_name] = granger
                significant_lags = [lag for lag, result in granger.items() if result['significant']]
                if significant_lags:
                    print(f"     格兰杰因果: 在滞后 {significant_lags} 期显著")
    
    # 生成报告
    print("\n" + "=" * 80)
    print("分析报告总结")
    print("=" * 80)
    
    print("\n最佳预测指标排名（按相关性）:")
    sorted_indicators = sorted(optimal_lags.items(), 
                              key=lambda x: abs(x[1]['correlation']), 
                              reverse=True)
    
    for rank, (indicator, info) in enumerate(sorted_indicators, 1):
        lag = info['lag']
        corr = info['correlation']
        
        if lag < 0:
            lag_desc = f"领先{abs(lag)}天"
        elif lag > 0:
            lag_desc = f"滞后{lag}天"
        else:
            lag_desc = "同期"
        
        print(f"{rank}. {indicator}: {lag_desc}, 相关系数={corr:.4f}")
    
    print("\n关键发现:")
    
    # 找出领先指标
    leading_indicators = [(name, info) for name, info in optimal_lags.items() if info['lag'] < 0]
    if leading_indicators:
        print(f"\n领先指标（可用于预测）:")
        for name, info in leading_indicators:
            print(f"  - {name}: 领先{abs(info['lag'])}天，相关系数={info['correlation']:.4f}")
    
    # 找出同期指标
    concurrent_indicators = [(name, info) for name, info in optimal_lags.items() if info['lag'] == 0]
    if concurrent_indicators:
        print(f"\n同期指标（实时反映市场）:")
        for name, info in concurrent_indicators:
            print(f"  - {name}: 相关系数={info['correlation']:.4f}")
    
    # 找出滞后指标
    lagging_indicators = [(name, info) for name, info in optimal_lags.items() if info['lag'] > 0]
    if lagging_indicators:
        print(f"\n滞后指标（确认趋势）:")
        for name, info in lagging_indicators:
            print(f"  - {name}: 滞后{info['lag']}天，相关系数={info['correlation']:.4f}")
    
    # 可视化
    print("\n4. 生成可视化图表...")
    
    # 相关性热力图
    if simple_correlations:
        viz.plot_correlation_heatmap(simple_correlations)
    
    # 滞后相关性图
    if lagged_correlations:
        viz.plot_lagged_correlation(dict(list(lagged_correlations.items())[:3]))  # 只显示前3个
    
    # 预测能力分析
    if prediction_results:
        viz.plot_prediction_analysis(prediction_results)
    
    # 指标与价格对比图（选择相关性最高的指标）
    if sorted_indicators:
        best_indicator = sorted_indicators[0][0]
        best_lag = sorted_indicators[0][1]['lag']
        
        if best_indicator in indicators_data:
            merged_df = pd.merge(price_df, indicators_data[best_indicator], 
                                left_index=True, right_index=True, how='inner')
            viz.plot_indicator_vs_price(
                merged_df[merged_df.columns[1]], 
                merged_df['price'],
                best_indicator,
                best_lag
            )
    
    # 保存详细结果
    print("\n5. 保存分析结果...")
    
    results = {
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'period': {'start': START_DATE, 'end': END_DATE},
        'correlations': simple_correlations,
        'optimal_lags': optimal_lags,
        'prediction_power': prediction_results,
        'granger_causality': granger_results
    }
    
    with open('glassnode_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print("\n分析完成！结果已保存到:")
    print("  - glassnode_analysis_results.json (详细数据)")
    print("  - correlation_heatmap.png (相关性热力图)")
    print("  - lagged_correlation.png (滞后相关性图)")
    print("  - prediction_analysis.png (预测能力分析)")
    print(f"  - {best_indicator.lower()}_vs_price.png (最佳指标对比图)")


if __name__ == "__main__":
    main()