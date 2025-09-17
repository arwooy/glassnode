"""
Glassnode指标信息增益(Information Gain)分析
计算各指标对未来价格预测的信息增益，评估预测价值
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
from scipy.stats import entropy
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from sklearn.preprocessing import KBinsDiscretizer
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


class InformationGainAnalyzer:
    """信息增益分析器"""
    
    def __init__(self):
        self.results = {}
        
    def calculate_entropy(self, data: np.ndarray, bins: int = 10) -> float:
        """
        计算数据的熵
        
        Parameters:
        - data: 数据数组
        - bins: 分箱数量
        
        Returns:
        - 熵值
        """
        # 离散化数据
        hist, _ = np.histogram(data[~np.isnan(data)], bins=bins)
        # 计算概率
        probs = hist / hist.sum()
        # 移除零概率
        probs = probs[probs > 0]
        # 计算熵
        return -np.sum(probs * np.log2(probs))
    
    def calculate_conditional_entropy(self, X: np.ndarray, Y: np.ndarray, bins: int = 10) -> float:
        """
        计算条件熵 H(Y|X)
        
        Parameters:
        - X: 条件变量
        - Y: 目标变量
        - bins: 分箱数量
        
        Returns:
        - 条件熵
        """
        # 离散化数据
        X_discrete = pd.qcut(X, bins, labels=False, duplicates='drop')
        Y_discrete = pd.qcut(Y, bins, labels=False, duplicates='drop')
        
        # 计算联合概率和边际概率
        joint_prob = pd.crosstab(X_discrete, Y_discrete, normalize=True)
        X_prob = pd.Series(X_discrete).value_counts(normalize=True)
        
        # 计算条件熵
        conditional_entropy = 0
        for x_val in X_prob.index:
            if x_val in joint_prob.index:
                # P(Y|X=x)的分布
                conditional_dist = joint_prob.loc[x_val] / X_prob[x_val]
                # 移除零概率
                conditional_dist = conditional_dist[conditional_dist > 0]
                # 计算该条件下的熵
                h = -np.sum(conditional_dist * np.log2(conditional_dist))
                # 加权累加
                conditional_entropy += X_prob[x_val] * h
        
        return conditional_entropy
    
    def calculate_information_gain(self, indicator: np.ndarray, target: np.ndarray, bins: int = 10) -> Dict:
        """
        计算信息增益
        
        Parameters:
        - indicator: 指标数据
        - target: 目标数据（未来价格变化）
        - bins: 分箱数量
        
        Returns:
        - 信息增益相关指标
        """
        # 移除NaN
        valid_mask = ~(np.isnan(indicator) | np.isnan(target))
        indicator_clean = indicator[valid_mask]
        target_clean = target[valid_mask]
        
        if len(indicator_clean) < 100:
            return {}
        
        # 离散化数据
        try:
            # 使用分位数进行离散化
            indicator_discrete = pd.qcut(indicator_clean, bins, labels=False, duplicates='drop')
            target_discrete = pd.qcut(target_clean, bins, labels=False, duplicates='drop')
        except:
            # 如果分位数失败，使用等宽分箱
            indicator_discrete = pd.cut(indicator_clean, bins, labels=False)
            target_discrete = pd.cut(target_clean, bins, labels=False)
        
        # 计算目标变量的熵
        target_probs = pd.Series(target_discrete).value_counts(normalize=True)
        H_target = -np.sum(target_probs * np.log2(target_probs + 1e-10))
        
        # 计算条件熵 H(Y|X)
        H_target_given_indicator = 0
        indicator_probs = pd.Series(indicator_discrete).value_counts(normalize=True)
        
        for x_val in indicator_probs.index:
            # 获取X=x_val时的Y分布
            mask = indicator_discrete == x_val
            if mask.sum() > 0:
                y_given_x = target_discrete[mask]
                y_probs = pd.Series(y_given_x).value_counts(normalize=True)
                # 计算H(Y|X=x_val)
                h_y_given_x = -np.sum(y_probs * np.log2(y_probs + 1e-10))
                # 加权
                H_target_given_indicator += indicator_probs[x_val] * h_y_given_x
        
        # 信息增益（必须为非负）
        information_gain = max(0, H_target - H_target_given_indicator)
        
        # 指标熵
        H_indicator = -np.sum(indicator_probs * np.log2(indicator_probs + 1e-10))
        
        # 信息增益比（归一化）
        gain_ratio = information_gain / H_indicator if H_indicator > 0 else 0
        
        # 对称不确定性（Symmetric Uncertainty）
        symmetric_uncertainty = 2 * information_gain / (H_target + H_indicator) if (H_target + H_indicator) > 0 else 0
        
        # 计算互信息（另一种方式）
        from sklearn.metrics import mutual_info_score
        mutual_info = mutual_info_score(indicator_discrete, target_discrete)
        
        return {
            'information_gain': information_gain,
            'gain_ratio': gain_ratio,
            'symmetric_uncertainty': symmetric_uncertainty,
            'mutual_information_discrete': mutual_info,
            'normalized_mi_discrete': mutual_info / min(H_target, H_indicator) if min(H_target, H_indicator) > 0 else 0,
            'target_entropy': H_target,
            'conditional_entropy': H_target_given_indicator,
            'indicator_entropy': H_indicator,
            'reduction_ratio': information_gain / H_target if H_target > 0 else 0  # 不确定性减少比例
        }
    
    def calculate_mutual_information(self, indicator: pd.Series, target: pd.Series, 
                                   discrete: bool = False) -> Dict:
        """
        使用sklearn计算互信息
        
        Parameters:
        - indicator: 指标数据
        - target: 目标数据
        - discrete: 是否离散化
        
        Returns:
        - 互信息相关指标
        """
        # 准备数据
        data = pd.DataFrame({
            'indicator': indicator,
            'target': target
        }).dropna()
        
        if len(data) < 100:
            return {}
        
        X = data[['indicator']].values
        y = data['target'].values
        
        if discrete:
            # 离散化目标变量（分类）
            discretizer = KBinsDiscretizer(n_bins=5, encode='ordinal', strategy='quantile')
            y_discrete = discretizer.fit_transform(y.reshape(-1, 1)).ravel().astype(int)
            
            # 计算分类互信息
            mi_score = mutual_info_classif(X, y_discrete, random_state=42)[0]
            
            # 计算最大可能的互信息（完美预测）
            max_mi = self.calculate_entropy(y_discrete, bins=5)
            
        else:
            # 计算回归互信息
            mi_score = mutual_info_regression(X, y, random_state=42)[0]
            
            # 估计最大互信息（使用目标变量的熵作为上界）
            max_mi = self.calculate_entropy(y, bins=10)
        
        # 归一化互信息
        normalized_mi = mi_score / max_mi if max_mi > 0 else 0
        
        return {
            'mutual_information': mi_score,
            'normalized_mi': normalized_mi,
            'max_possible_mi': max_mi
        }
    
    def calculate_transfer_entropy(self, indicator: pd.Series, target: pd.Series, 
                                  lag: int = 1, bins: int = 5) -> float:
        """
        计算转移熵（Transfer Entropy）
        衡量指标对目标的信息流动
        
        Parameters:
        - indicator: 指标数据
        - target: 目标数据  
        - lag: 滞后期
        - bins: 分箱数量
        
        Returns:
        - 转移熵值
        """
        # 准备数据
        n = len(target)
        if n < lag + 100:
            return 0
        
        # 创建滞后变量
        target_current = target[lag:].values
        target_past = target[:-lag].values
        indicator_past = indicator[:-lag].values
        
        # 离散化
        discretizer = KBinsDiscretizer(n_bins=bins, encode='ordinal', strategy='quantile')
        
        # 安全地进行离散化
        try:
            target_current_d = discretizer.fit_transform(target_current.reshape(-1, 1)).ravel()
            target_past_d = discretizer.fit_transform(target_past.reshape(-1, 1)).ravel()
            indicator_past_d = discretizer.fit_transform(indicator_past.reshape(-1, 1)).ravel()
        except:
            return 0
        
        # 计算概率分布
        # P(target_t | target_t-1, indicator_t-1)
        joint_with_indicator = pd.crosstab(
            [target_past_d, indicator_past_d],
            target_current_d,
            normalize=True
        )
        
        # P(target_t | target_t-1)
        joint_without_indicator = pd.crosstab(
            target_past_d,
            target_current_d,
            normalize=True
        )
        
        # 计算转移熵
        te = 0
        for tp in np.unique(target_past_d):
            for ip in np.unique(indicator_past_d):
                for tc in np.unique(target_current_d):
                    # 联合概率
                    if (tp, ip) in joint_with_indicator.index and tc in joint_with_indicator.columns:
                        p_joint = joint_with_indicator.loc[(tp, ip), tc]
                    else:
                        p_joint = 0
                    
                    if p_joint > 0:
                        # 条件概率
                        if tp in joint_without_indicator.index and tc in joint_without_indicator.columns:
                            p_cond_without = joint_without_indicator.loc[tp, tc]
                        else:
                            p_cond_without = 0
                        
                        if p_cond_without > 0:
                            # 边际概率
                            p_marginal = (target_past_d == tp).mean() * (indicator_past_d == ip).mean()
                            
                            if p_marginal > 0:
                                # 转移熵贡献
                                te += p_joint * np.log2(p_joint / (p_cond_without * p_marginal))
        
        return te
    
    def analyze_predictive_information(self, indicator_df: pd.DataFrame, price_df: pd.DataFrame,
                                      horizons: List[int] = [1, 3, 7, 14, 30]) -> Dict:
        """
        分析指标的预测信息含量
        
        Parameters:
        - indicator_df: 指标数据
        - price_df: 价格数据
        - horizons: 预测时间跨度列表
        
        Returns:
        - 各时间跨度的信息增益指标
        """
        results = {}
        
        # 合并数据
        data = pd.merge(indicator_df, price_df, left_index=True, right_index=True, how='inner')
        indicator_col = data.iloc[:, 0]
        price_col = data.iloc[:, -1]
        
        for horizon in horizons:
            # 计算未来收益率
            future_return = price_col.pct_change(horizon).shift(-horizon)
            
            # 信息增益分析（连续变量）
            ig_continuous = self.calculate_information_gain(
                indicator_col.values,
                future_return.values,
                bins=10
            )
            
            # 互信息分析（回归）
            mi_regression = self.calculate_mutual_information(
                indicator_col,
                future_return,
                discrete=False
            )
            
            # 互信息分析（分类）
            mi_classification = self.calculate_mutual_information(
                indicator_col,
                future_return,
                discrete=True
            )
            
            # 转移熵
            te_score = self.calculate_transfer_entropy(
                indicator_col,
                future_return,
                lag=horizon,
                bins=5
            )
            
            # 计算相关系数作为对比
            correlation = indicator_col.corr(future_return)
            
            results[horizon] = {
                'information_gain': ig_continuous.get('information_gain', 0),
                'gain_ratio': ig_continuous.get('gain_ratio', 0),
                'symmetric_uncertainty': ig_continuous.get('symmetric_uncertainty', 0),
                'reduction_ratio': ig_continuous.get('reduction_ratio', 0),
                'mutual_info_regression': mi_regression.get('mutual_information', 0),
                'normalized_mi_regression': mi_regression.get('normalized_mi', 0),
                'mutual_info_classification': mi_classification.get('mutual_information', 0),
                'normalized_mi_classification': mi_classification.get('normalized_mi', 0),
                'transfer_entropy': te_score,
                'correlation': correlation,
                'correlation_squared': correlation ** 2  # R-squared
            }
        
        return results


class IGVisualization:
    """信息增益可视化"""
    
    @staticmethod
    def plot_ig_comparison(all_results: Dict, metric: str = 'information_gain'):
        """
        绘制信息增益对比图
        
        Parameters:
        - all_results: 所有指标的IG结果
        - metric: 要显示的指标
        """
        # 准备数据
        data = []
        for indicator, horizons in all_results.items():
            for horizon, metrics in horizons.items():
                if metric in metrics:
                    data.append({
                        'indicator': indicator.replace('_', ' ').title(),
                        'horizon': horizon,
                        metric: metrics[metric]
                    })
        
        if not data:
            return
        
        df = pd.DataFrame(data)
        
        # 创建透视表
        pivot = df.pivot(index='indicator', columns='horizon', values=metric)
        
        # 绘制热力图
        plt.figure(figsize=(14, 10))
        
        # 使用适当的颜色映射
        if 'correlation' in metric:
            cmap = 'RdBu_r'
            center = 0
            vmin, vmax = -1, 1
        else:
            cmap = 'YlOrRd'
            center = None
            vmin, vmax = 0, pivot.max().max()
        
        sns.heatmap(
            pivot,
            annot=True,
            fmt='.3f',
            cmap=cmap,
            center=center,
            vmin=vmin,
            vmax=vmax,
            cbar_kws={'label': metric.replace('_', ' ').title()},
            linewidths=0.5
        )
        
        plt.title(f'{metric.replace("_", " ").title()} - 各指标不同预测期的信息含量')
        plt.xlabel('预测时间跨度（天）')
        plt.ylabel('指标')
        plt.tight_layout()
        plt.savefig(f'ig_{metric}_heatmap.png', dpi=150, bbox_inches='tight')
        plt.show()
    
    @staticmethod
    def plot_ig_by_horizon(all_results: Dict):
        """
        按时间跨度绘制信息增益
        """
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        horizons = [1, 3, 7, 14, 30]
        
        for idx, horizon in enumerate(horizons):
            ax = axes[idx // 3, idx % 3]
            
            # 收集该时间跨度的数据
            ig_scores = []
            mi_scores = []
            indicators = []
            
            for indicator, h_data in all_results.items():
                if horizon in h_data:
                    indicators.append(indicator.split('_')[-1])  # 简化名称
                    ig_scores.append(h_data[horizon].get('information_gain', 0))
                    mi_scores.append(h_data[horizon].get('normalized_mi_regression', 0))
            
            if indicators:
                x = np.arange(len(indicators))
                width = 0.35
                
                bars1 = ax.bar(x - width/2, ig_scores, width, label='Information Gain', color='steelblue')
                bars2 = ax.bar(x + width/2, mi_scores, width, label='Normalized MI', color='coral')
                
                ax.set_xlabel('指标')
                ax.set_ylabel('信息量')
                ax.set_title(f'{horizon}天预测')
                ax.set_xticks(x)
                ax.set_xticklabels(indicators, rotation=45, ha='right')
                ax.legend()
                ax.grid(True, alpha=0.3)
        
        # 隐藏多余的子图
        if len(horizons) < 6:
            axes[-1, -1].axis('off')
        
        plt.suptitle('不同时间跨度的信息增益对比', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('ig_by_horizon.png', dpi=150, bbox_inches='tight')
        plt.show()
    
    @staticmethod
    def plot_ig_ranking(all_results: Dict):
        """
        绘制信息增益排名
        """
        # 计算每个指标的平均信息增益
        avg_scores = {}
        
        for indicator, horizons in all_results.items():
            scores = []
            for h, metrics in horizons.items():
                # 综合多个信息指标
                composite_score = (
                    metrics.get('information_gain', 0) * 0.3 +
                    metrics.get('normalized_mi_regression', 0) * 0.3 +
                    metrics.get('symmetric_uncertainty', 0) * 0.2 +
                    metrics.get('transfer_entropy', 0) * 0.2
                )
                scores.append(composite_score)
            
            avg_scores[indicator] = np.mean(scores)
        
        # 排序
        sorted_indicators = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 绘图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # 条形图
        indicators = [x[0].replace('_', ' ').title() for x in sorted_indicators[:10]]
        scores = [x[1] for x in sorted_indicators[:10]]
        
        ax1.barh(range(len(indicators)), scores, color='teal')
        ax1.set_yticks(range(len(indicators)))
        ax1.set_yticklabels(indicators)
        ax1.set_xlabel('综合信息得分')
        ax1.set_title('Top 10 预测信息含量指标')
        ax1.invert_yaxis()
        
        # 添加数值标签
        for i, v in enumerate(scores):
            ax1.text(v + 0.001, i, f'{v:.3f}', va='center')
        
        # 雷达图
        categories = ['IG', 'MI', 'SU', 'TE', 'Corr']
        
        # 选择前5个指标
        top_5 = sorted_indicators[:5]
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        ax2 = plt.subplot(122, projection='polar')
        
        for indicator, _ in top_5:
            if indicator in all_results:
                # 取7天预测的数据
                if 7 in all_results[indicator]:
                    metrics = all_results[indicator][7]
                    values = [
                        metrics.get('information_gain', 0),
                        metrics.get('normalized_mi_regression', 0),
                        metrics.get('symmetric_uncertainty', 0),
                        metrics.get('transfer_entropy', 0),
                        abs(metrics.get('correlation', 0))
                    ]
                    values += values[:1]
                    
                    ax2.plot(angles, values, 'o-', linewidth=2, 
                            label=indicator.split('_')[-1])
                    ax2.fill(angles, values, alpha=0.1)
        
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(categories)
        ax2.set_title('信息指标雷达图（7天预测）')
        ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig('ig_ranking.png', dpi=150, bbox_inches='tight')
        plt.show()


class IGReportGenerator:
    """信息增益报告生成器"""
    
    @staticmethod
    def generate_summary(all_results: Dict) -> Dict:
        """
        生成信息增益分析摘要
        """
        summary = {
            'best_indicators_by_horizon': {},
            'best_indicators_by_metric': {},
            'average_scores': {},
            'insights': []
        }
        
        # 按时间跨度找最佳指标
        for horizon in [1, 3, 7, 14, 30]:
            best_ig = None
            best_mi = None
            best_te = None
            
            for indicator, h_data in all_results.items():
                if horizon in h_data:
                    metrics = h_data[horizon]
                    
                    # Information Gain
                    if best_ig is None or metrics.get('information_gain', 0) > best_ig[1]:
                        best_ig = (indicator, metrics.get('information_gain', 0))
                    
                    # Mutual Information
                    if best_mi is None or metrics.get('normalized_mi_regression', 0) > best_mi[1]:
                        best_mi = (indicator, metrics.get('normalized_mi_regression', 0))
                    
                    # Transfer Entropy
                    if best_te is None or metrics.get('transfer_entropy', 0) > best_te[1]:
                        best_te = (indicator, metrics.get('transfer_entropy', 0))
            
            summary['best_indicators_by_horizon'][horizon] = {
                'information_gain': best_ig,
                'mutual_information': best_mi,
                'transfer_entropy': best_te
            }
        
        # 计算平均得分
        for indicator, h_data in all_results.items():
            avg_ig = np.mean([m.get('information_gain', 0) for m in h_data.values()])
            avg_mi = np.mean([m.get('normalized_mi_regression', 0) for m in h_data.values()])
            avg_te = np.mean([m.get('transfer_entropy', 0) for m in h_data.values()])
            
            summary['average_scores'][indicator] = {
                'avg_information_gain': avg_ig,
                'avg_mutual_information': avg_mi,
                'avg_transfer_entropy': avg_te,
                'composite_score': (avg_ig + avg_mi + avg_te) / 3
            }
        
        # 生成洞察
        # 找出信息含量最高的指标
        best_overall = max(summary['average_scores'].items(), 
                         key=lambda x: x[1]['composite_score'])
        summary['insights'].append(
            f"最高信息含量指标: {best_overall[0]} (综合得分: {best_overall[1]['composite_score']:.3f})"
        )
        
        # 找出最佳预测时间跨度
        horizon_scores = {}
        for h in [1, 3, 7, 14, 30]:
            scores = []
            for ind, h_data in all_results.items():
                if h in h_data:
                    scores.append(h_data[h].get('information_gain', 0))
            horizon_scores[h] = np.mean(scores) if scores else 0
        
        best_horizon = max(horizon_scores.items(), key=lambda x: x[1])
        summary['insights'].append(
            f"最佳预测时间跨度: {best_horizon[0]}天 (平均IG: {best_horizon[1]:.3f})"
        )
        
        return summary


def main():
    """主函数"""
    # 配置
    API_KEY = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
    START_DATE = "2021-01-01"
    END_DATE = "2024-12-31"
    
    # 要分析的指标
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
        ('mining', 'hash_rate_mean')
    ]
    
    HORIZONS = [1, 3, 7, 14, 30]
    
    print("=" * 80)
    print("📊 Glassnode指标信息增益(Information Gain)分析")
    print("=" * 80)
    print(f"分析周期: {START_DATE} 至 {END_DATE}")
    print(f"预测跨度: {HORIZONS} 天")
    
    # 初始化
    ig_analyzer = InformationGainAnalyzer()
    visualizer = IGVisualization()
    reporter = IGReportGenerator()
    
    # 获取数据（使用之前的数据获取逻辑）
    print("\n📊 Step 1: 获取数据...")
    
    # 这里简化处理，直接创建模拟数据
    # 实际使用时应该调用Glassnode API
    from glassnode_prediction_analysis import GlassnodeDataFetcher
    
    fetcher = GlassnodeDataFetcher(API_KEY)
    metrics_data = fetcher.fetch_metrics(METRICS_TO_ANALYZE, START_DATE, END_DATE)
    
    if 'market_price_usd_close' not in metrics_data:
        print("❌ 无法获取价格数据")
        return
    
    price_df = metrics_data['market_price_usd_close'].rename(columns={'price_usd_close': 'price'})
    
    # 分析信息增益
    print("\n📊 Step 2: 计算信息增益...")
    all_results = {}
    
    for metric_name, metric_df in metrics_data.items():
        if metric_name == 'market_price_usd_close':
            continue
        
        print(f"\n分析 {metric_name}...")
        results = ig_analyzer.analyze_predictive_information(
            metric_df, price_df, HORIZONS
        )
        
        all_results[metric_name] = results
        
        # 显示关键指标
        for h in [1, 7, 30]:
            if h in results:
                ig = results[h].get('information_gain', 0)
                mi = results[h].get('normalized_mi_regression', 0)
                print(f"  {h}天: IG={ig:.3f}, MI={mi:.3f}")
    
    # 生成可视化
    print("\n📊 Step 3: 生成可视化...")
    
    # 信息增益热力图
    visualizer.plot_ig_comparison(all_results, 'information_gain')
    print("  ✅ 信息增益热力图")
    
    # 互信息热力图
    visualizer.plot_ig_comparison(all_results, 'normalized_mi_regression')
    print("  ✅ 互信息热力图")
    
    # 对称不确定性热力图
    visualizer.plot_ig_comparison(all_results, 'symmetric_uncertainty')
    print("  ✅ 对称不确定性热力图")
    
    # 按时间跨度对比
    visualizer.plot_ig_by_horizon(all_results)
    print("  ✅ 时间跨度对比图")
    
    # 综合排名
    visualizer.plot_ig_ranking(all_results)
    print("  ✅ 综合排名图")
    
    # 生成报告
    print("\n📊 Step 4: 生成分析报告...")
    summary = reporter.generate_summary(all_results)
    
    # 保存详细结果
    detailed_report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'period': {'start': START_DATE, 'end': END_DATE},
        'summary': summary,
        'detailed_results': {
            indicator: {
                str(horizon): metrics
                for horizon, metrics in horizons.items()
            }
            for indicator, horizons in all_results.items()
        }
    }
    
    with open('information_gain_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(detailed_report, f, indent=2, ensure_ascii=False, default=str)
    
    print("✅ 报告已保存: information_gain_analysis.json")
    
    # 打印关键发现
    print("\n" + "=" * 80)
    print("🎯 关键发现")
    print("=" * 80)
    
    print("\n📈 最佳信息增益指标（按时间跨度）:")
    for horizon, best in summary['best_indicators_by_horizon'].items():
        if best['information_gain']:
            print(f"  {horizon}天: {best['information_gain'][0]} (IG={best['information_gain'][1]:.3f})")
    
    print("\n📊 综合信息含量排名（前5）:")
    sorted_avg = sorted(summary['average_scores'].items(), 
                       key=lambda x: x[1]['composite_score'], 
                       reverse=True)[:5]
    
    for i, (indicator, scores) in enumerate(sorted_avg, 1):
        print(f"  {i}. {indicator}:")
        print(f"     - 信息增益: {scores['avg_information_gain']:.3f}")
        print(f"     - 互信息: {scores['avg_mutual_information']:.3f}")
        print(f"     - 转移熵: {scores['avg_transfer_entropy']:.3f}")
        print(f"     - 综合得分: {scores['composite_score']:.3f}")
    
    print("\n💡 关键洞察:")
    for insight in summary['insights']:
        print(f"  • {insight}")
    
    # 创建IG与相关性对比表
    print("\n📋 信息增益 vs 相关性对比:")
    print("=" * 80)
    print(f"{'指标':<30} {'7天IG':>10} {'7天MI':>10} {'7天相关性':>10} {'IG/Corr比':>10}")
    print("-" * 80)
    
    for indicator, h_data in all_results.items():
        if 7 in h_data:
            ig = h_data[7].get('information_gain', 0)
            mi = h_data[7].get('normalized_mi_regression', 0)
            corr = abs(h_data[7].get('correlation', 0))
            ratio = ig / corr if corr > 0 else 0
            
            ind_name = indicator.split('_')[-1][:25]
            print(f"{ind_name:<30} {ig:>10.3f} {mi:>10.3f} {corr:>10.3f} {ratio:>10.2f}")
    
    print("\n✅ 分析完成！")
    
    print("\n生成的文件:")
    print("  1. information_gain_analysis.json - 详细分析结果")
    print("  2. ig_information_gain_heatmap.png - 信息增益热力图")
    print("  3. ig_normalized_mi_regression_heatmap.png - 互信息热力图")
    print("  4. ig_symmetric_uncertainty_heatmap.png - 对称不确定性热力图")
    print("  5. ig_by_horizon.png - 时间跨度对比")
    print("  6. ig_ranking.png - 综合排名图")


if __name__ == "__main__":
    main()