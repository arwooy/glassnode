# Distribution（分布数据）API 详细文档

## 概述

Distribution API 提供加密资产分布相关的深度数据分析，包括供应分布、持有者分布、地理分布、时间分布等维度。这些分布数据对于理解市场结构、评估去中心化程度、识别集中度风险、制定投资策略和进行风险管理至关重要。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/distribution/`

**支持的资产**: BTC, ETH, USDT, USDC, ADA, DOT, LINK 等主要加密资产

**数据更新频率**: 
- 实时分布：10分钟
- 聚合分布：1小时、24小时
- 历史分布：每日快照

## 核心端点

### 1. 供应分布分析

#### 1.1 按余额区间的供应分布

**端点**: `/supply_distribution`

**描述**: 按不同余额区间分类的代币供应分布，显示财富集中度。

**参数**:
- `a`: 资产符号（如 BTC）
- `i`: 时间间隔（1h, 24h, 1w）
- `s`: 开始时间戳
- `balance_tier`: 余额层级（可选）

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/distribution/supply_distribution?a=BTC&i=24h&s=1609459200" \
  -H "X-Api-Key: YOUR_API_KEY"
```

**示例响应**:
```json
[
  {
    "t": 1726790400,
    "v": {
      "tier_0_001": 156789.45,
      "tier_0_01": 234567.89,
      "tier_0_1": 567890.12,
      "tier_1": 1234567.89,
      "tier_10": 2345678.90,
      "tier_100": 3456789.01,
      "tier_1000": 4567890.12,
      "tier_10000": 1234567.89
    }
  }
]
```

#### 1.2 持有者数量分布

**端点**: `/holder_distribution`

**描述**: 按余额区间分类的持有者数量分布。

**参数**:
- `a`: 资产符号
- `i`: 时间间隔
- `s`: 开始时间戳
- `min_balance`: 最小余额过滤器

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/distribution/holder_distribution?a=BTC&i=24h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

### 2. 地理分布分析

#### 2.1 按地区的分布

**端点**: `/geographic_distribution`

**描述**: 按地理区域分类的持有者和交易活动分布。

**参数**:
- `a`: 资产符号
- `i`: 时间间隔
- `region`: 地区过滤器（可选）

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/distribution/geographic_distribution?a=BTC&i=24h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

### 3. 时间分布分析

#### 3.1 持有时长分布

**端点**: `/holding_period_distribution`

**描述**: 按持有时长分类的代币分布，反映市场成熟度。

**参数**:
- `a`: 资产符号
- `i`: 时间间隔
- `holding_period`: 持有期间分类

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/distribution/holding_period_distribution?a=BTC&i=24h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

## Python 实现类

```python
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from scipy import stats
from sklearn.cluster import KMeans

class DistributionAnalyzer:
    """
    Glassnode Distribution API 分析器
    提供分布数据的获取、分析和可视化功能
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/distribution/"
        self.headers = {"X-Api-Key": self.api_key}
        
    def get_supply_distribution(self, asset: str = 'BTC', days: int = 30) -> Dict:
        """获取供应分布数据"""
        
        url = self.base_url + "supply_distribution"
        params = {
            'a': asset,
            'i': '24h',
            's': int((datetime.now() - timedelta(days=days)).timestamp()),
            'u': int(datetime.now().timestamp())
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            return self.analyze_supply_distribution(data, asset)
            
        except Exception as e:
            print(f"获取供应分布数据失败: {e}")
            return {}
    
    def analyze_supply_distribution(self, data: List, asset: str) -> Dict:
        """分析供应分布数据"""
        
        if not data:
            return {}
        
        latest = data[-1]['v']
        total_supply = sum(latest.values())
        
        # 计算各层级的分布统计
        distribution_stats = {}
        for tier, supply in latest.items():
            distribution_stats[tier] = {
                'supply_amount': supply,
                'percentage': (supply / total_supply * 100) if total_supply > 0 else 0
            }
        
        # 计算集中度指标
        gini_coefficient = self.calculate_gini_from_distribution(latest)
        herfindahl_index = self.calculate_herfindahl_index(latest)
        
        # 分析趋势
        trends = self.analyze_distribution_trends(data) if len(data) > 7 else {}
        
        return {
            'asset': asset,
            'timestamp': data[-1]['t'],
            'total_supply': total_supply,
            'distribution_stats': distribution_stats,
            'concentration_metrics': {
                'gini_coefficient': gini_coefficient,
                'herfindahl_index': herfindahl_index,
                'concentration_level': self.assess_concentration_level(gini_coefficient)
            },
            'trends': trends,
            'insights': self.generate_distribution_insights(distribution_stats, gini_coefficient)
        }
    
    def calculate_gini_from_distribution(self, distribution: Dict) -> float:
        """计算基尼系数"""
        
        values = list(distribution.values())
        values.sort()
        
        n = len(values)
        cumsum = np.cumsum(values)
        
        if cumsum[-1] == 0:
            return 0
        
        return (n + 1 - 2 * sum(cumsum) / cumsum[-1]) / n
    
    def calculate_herfindahl_index(self, distribution: Dict) -> float:
        """计算赫芬达尔指数"""
        
        total = sum(distribution.values())
        if total == 0:
            return 0
        
        shares = [value / total for value in distribution.values()]
        return sum(share ** 2 for share in shares)
    
    def assess_concentration_level(self, gini: float) -> str:
        """评估集中度水平"""
        
        if gini < 0.25:
            return "低集中度"
        elif gini < 0.50:
            return "中等集中度"
        elif gini < 0.70:
            return "高集中度"
        else:
            return "极高集中度"
    
    def analyze_distribution_trends(self, data: List) -> Dict:
        """分析分布趋势"""
        
        if len(data) < 7:
            return {}
        
        current = data[-1]['v']
        week_ago = data[-7]['v']
        
        trends = {}
        for tier in current.keys():
            current_val = current[tier]
            past_val = week_ago.get(tier, 0)
            
            if past_val > 0:
                change_pct = ((current_val - past_val) / past_val) * 100
                trends[tier] = {
                    'change_7d': change_pct,
                    'direction': 'increasing' if change_pct > 0 else 'decreasing',
                    'magnitude': 'significant' if abs(change_pct) > 5 else 'moderate'
                }
        
        return trends
    
    def generate_distribution_insights(self, stats: Dict, gini: float) -> List[str]:
        """生成分布洞察"""
        
        insights = []
        
        # 找出最大的余额层级
        largest_tier = max(stats.keys(), key=lambda x: stats[x]['supply_amount'])
        largest_pct = stats[largest_tier]['percentage']
        
        insights.append(f"最大余额层级 {largest_tier} 占总供应量的 {largest_pct:.1f}%")
        
        # 基尼系数分析
        if gini > 0.7:
            insights.append("供应高度集中，存在显著的财富不平等")
        elif gini > 0.5:
            insights.append("供应相对集中，需关注大户影响")
        else:
            insights.append("供应分布相对均匀")
        
        # 小额持有者分析
        small_holders = [tier for tier in stats.keys() if '0_001' in tier or '0_01' in tier]
        small_holder_pct = sum(stats[tier]['percentage'] for tier in small_holders)
        
        if small_holder_pct > 20:
            insights.append("小额持有者占比较高，散户参与度较好")
        else:
            insights.append("小额持有者占比较低，可能存在准入门槛")
        
        return insights
    
    def get_holder_distribution(self, asset: str = 'BTC', days: int = 30) -> Dict:
        """获取持有者分布数据"""
        
        url = self.base_url + "holder_distribution"
        params = {
            'a': asset,
            'i': '24h',
            's': int((datetime.now() - timedelta(days=days)).timestamp())
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            return self.analyze_holder_distribution(data, asset)
            
        except Exception as e:
            print(f"获取持有者分布数据失败: {e}")
            return {}
    
    def analyze_holder_distribution(self, data: List, asset: str) -> Dict:
        """分析持有者分布数据"""
        
        if not data:
            return {}
        
        latest = data[-1]['v']
        total_holders = sum(latest.values())
        
        # 计算持有者分布统计
        holder_stats = {}
        for tier, count in latest.items():
            holder_stats[tier] = {
                'holder_count': count,
                'percentage': (count / total_holders * 100) if total_holders > 0 else 0
            }
        
        # 计算持有者集中度
        holder_concentration = self.calculate_holder_concentration(latest)
        
        return {
            'asset': asset,
            'timestamp': data[-1]['t'],
            'total_holders': total_holders,
            'holder_stats': holder_stats,
            'concentration_analysis': holder_concentration,
            'market_structure': self.assess_market_structure(holder_stats),
            'participation_metrics': self.calculate_participation_metrics(holder_stats)
        }
    
    def calculate_holder_concentration(self, distribution: Dict) -> Dict:
        """计算持有者集中度"""
        
        total = sum(distribution.values())
        
        # 计算前20%持有者的占比（帕累托分析）
        sorted_tiers = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
        top_20_pct_count = int(len(sorted_tiers) * 0.2)
        top_20_pct_holders = sum(count for _, count in sorted_tiers[:top_20_pct_count])
        
        return {
            'top_20_percent_ratio': (top_20_pct_holders / total * 100) if total > 0 else 0,
            'holder_herfindahl': self.calculate_herfindahl_index(distribution),
            'participation_rate': self.estimate_participation_rate(distribution)
        }
    
    def estimate_participation_rate(self, distribution: Dict) -> float:
        """估算参与率"""
        
        # 基于小额持有者比例估算
        small_holder_tiers = ['tier_0_001', 'tier_0_01', 'tier_0_1']
        small_holders = sum(distribution.get(tier, 0) for tier in small_holder_tiers)
        total_holders = sum(distribution.values())
        
        return (small_holders / total_holders * 100) if total_holders > 0 else 0
    
    def assess_market_structure(self, holder_stats: Dict) -> str:
        """评估市场结构"""
        
        # 基于不同层级持有者的分布判断市场结构
        whale_tiers = ['tier_1000', 'tier_10000']
        whale_percentage = sum(holder_stats.get(tier, {}).get('percentage', 0) 
                              for tier in whale_tiers)
        
        retail_tiers = ['tier_0_001', 'tier_0_01', 'tier_0_1']
        retail_percentage = sum(holder_stats.get(tier, {}).get('percentage', 0) 
                               for tier in retail_tiers)
        
        if whale_percentage > 60:
            return "鲸鱼主导"
        elif retail_percentage > 70:
            return "散户主导"
        elif whale_percentage > 30 and retail_percentage > 30:
            return "均衡分布"
        else:
            return "机构化分布"
    
    def calculate_participation_metrics(self, holder_stats: Dict) -> Dict:
        """计算参与度指标"""
        
        total_percentage = sum(data['percentage'] for data in holder_stats.values())
        
        # 计算不同层级的参与度
        metrics = {
            'retail_participation': 0,
            'institutional_participation': 0,
            'whale_participation': 0,
            'diversity_index': 0
        }
        
        retail_tiers = ['tier_0_001', 'tier_0_01', 'tier_0_1']
        institutional_tiers = ['tier_1', 'tier_10', 'tier_100']
        whale_tiers = ['tier_1000', 'tier_10000']
        
        metrics['retail_participation'] = sum(
            holder_stats.get(tier, {}).get('percentage', 0) 
            for tier in retail_tiers
        )
        
        metrics['institutional_participation'] = sum(
            holder_stats.get(tier, {}).get('percentage', 0) 
            for tier in institutional_tiers
        )
        
        metrics['whale_participation'] = sum(
            holder_stats.get(tier, {}).get('percentage', 0) 
            for tier in whale_tiers
        )
        
        # 多样性指数（基于熵）
        percentages = [data['percentage'] for data in holder_stats.values() if data['percentage'] > 0]
        if percentages:
            normalized = [p / sum(percentages) for p in percentages]
            metrics['diversity_index'] = -sum(p * np.log2(p) for p in normalized if p > 0)
        
        return metrics
    
    def get_holding_period_distribution(self, asset: str = 'BTC', days: int = 30) -> Dict:
        """获取持有时长分布数据"""
        
        url = self.base_url + "holding_period_distribution"
        params = {
            'a': asset,
            'i': '24h',
            's': int((datetime.now() - timedelta(days=days)).timestamp())
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            return self.analyze_holding_period_distribution(data, asset)
            
        except Exception as e:
            print(f"获取持有时长分布数据失败: {e}")
            return {}
    
    def analyze_holding_period_distribution(self, data: List, asset: str) -> Dict:
        """分析持有时长分布"""
        
        if not data:
            return {}
        
        latest = data[-1]['v']
        
        # 定义持有期间类别
        period_categories = {
            'short_term': ['1d_1w', '1w_1m'],
            'medium_term': ['1m_3m', '3m_6m'],
            'long_term': ['6m_1y', '1y_2y'],
            'hodlers': ['2y_plus']
        }
        
        # 计算各类别的分布
        category_distribution = {}
        total_supply = sum(latest.values())
        
        for category, periods in period_categories.items():
            category_supply = sum(latest.get(period, 0) for period in periods)
            category_distribution[category] = {
                'supply_amount': category_supply,
                'percentage': (category_supply / total_supply * 100) if total_supply > 0 else 0
            }
        
        # 分析市场成熟度
        maturity_analysis = self.assess_market_maturity(category_distribution)
        
        return {
            'asset': asset,
            'timestamp': data[-1]['t'],
            'period_distribution': category_distribution,
            'maturity_analysis': maturity_analysis,
            'holding_behavior': self.analyze_holding_behavior(category_distribution),
            'stability_metrics': self.calculate_stability_metrics(category_distribution)
        }
    
    def assess_market_maturity(self, distribution: Dict) -> Dict:
        """评估市场成熟度"""
        
        hodler_pct = distribution.get('hodlers', {}).get('percentage', 0)
        long_term_pct = distribution.get('long_term', {}).get('percentage', 0)
        short_term_pct = distribution.get('short_term', {}).get('percentage', 0)
        
        maturity_score = (hodler_pct * 2 + long_term_pct * 1.5 + 
                         max(0, 50 - short_term_pct)) / 3
        
        if maturity_score > 60:
            maturity_level = "高度成熟"
        elif maturity_score > 40:
            maturity_level = "中等成熟"
        else:
            maturity_level = "早期阶段"
        
        return {
            'maturity_score': round(maturity_score, 2),
            'maturity_level': maturity_level,
            'hodler_dominance': hodler_pct > 40,
            'speculative_activity': short_term_pct > 30
        }
    
    def analyze_holding_behavior(self, distribution: Dict) -> Dict:
        """分析持有行为"""
        
        behavior = {
            'dominant_behavior': '',
            'investment_style': '',
            'risk_profile': '',
            'market_sentiment': ''
        }
        
        hodler_pct = distribution.get('hodlers', {}).get('percentage', 0)
        short_term_pct = distribution.get('short_term', {}).get('percentage', 0)
        medium_term_pct = distribution.get('medium_term', {}).get('percentage', 0)
        
        # 主导行为
        max_category = max(distribution.keys(), 
                          key=lambda x: distribution[x]['percentage'])
        behavior['dominant_behavior'] = max_category
        
        # 投资风格
        if hodler_pct > 40:
            behavior['investment_style'] = "价值投资导向"
        elif short_term_pct > 40:
            behavior['investment_style'] = "交易投机导向"
        else:
            behavior['investment_style'] = "混合投资风格"
        
        # 风险概况
        if short_term_pct > 50:
            behavior['risk_profile'] = "高风险偏好"
        elif hodler_pct > 50:
            behavior['risk_profile'] = "低风险偏好"
        else:
            behavior['risk_profile'] = "中等风险偏好"
        
        return behavior
    
    def calculate_stability_metrics(self, distribution: Dict) -> Dict:
        """计算稳定性指标"""
        
        # 供应稳定性
        stable_supply = (distribution.get('long_term', {}).get('percentage', 0) + 
                        distribution.get('hodlers', {}).get('percentage', 0))
        
        # 流动性指标
        liquid_supply = (distribution.get('short_term', {}).get('percentage', 0) + 
                        distribution.get('medium_term', {}).get('percentage', 0))
        
        return {
            'supply_stability': stable_supply,
            'liquid_supply_ratio': liquid_supply,
            'stability_score': min(100, stable_supply * 1.2),
            'volatility_risk': max(0, liquid_supply - 30)
        }
    
    def compare_distributions(self, assets: List[str], metric: str = 'supply') -> Dict:
        """比较多个资产的分布"""
        
        comparison_data = {}
        
        for asset in assets:
            if metric == 'supply':
                data = self.get_supply_distribution(asset)
            elif metric == 'holder':
                data = self.get_holder_distribution(asset)
            elif metric == 'holding_period':
                data = self.get_holding_period_distribution(asset)
            else:
                continue
            
            comparison_data[asset] = data
        
        return self.analyze_cross_asset_distribution(comparison_data, metric)
    
    def analyze_cross_asset_distribution(self, data: Dict, metric: str) -> Dict:
        """分析跨资产分布比较"""
        
        analysis = {
            'comparison_metric': metric,
            'asset_rankings': {},
            'patterns': [],
            'outliers': [],
            'correlations': {}
        }
        
        if metric == 'supply':
            # 按集中度排名
            concentration_scores = {}
            for asset, asset_data in data.items():
                if 'concentration_metrics' in asset_data:
                    concentration_scores[asset] = asset_data['concentration_metrics']['gini_coefficient']
            
            analysis['asset_rankings']['by_concentration'] = sorted(
                concentration_scores.items(), key=lambda x: x[1], reverse=True
            )
        
        elif metric == 'holder':
            # 按持有者多样性排名
            diversity_scores = {}
            for asset, asset_data in data.items():
                if 'participation_metrics' in asset_data:
                    diversity_scores[asset] = asset_data['participation_metrics']['diversity_index']
            
            analysis['asset_rankings']['by_diversity'] = sorted(
                diversity_scores.items(), key=lambda x: x[1], reverse=True
            )
        
        return analysis

    def generate_distribution_report(self, asset: str = 'BTC') -> Dict:
        """生成分布综合报告"""
        
        # 获取各类分布数据
        supply_dist = self.get_supply_distribution(asset)
        holder_dist = self.get_holder_distribution(asset)
        holding_period_dist = self.get_holding_period_distribution(asset)
        
        # 综合分析
        report = {
            'asset': asset,
            'report_timestamp': datetime.now().isoformat(),
            'supply_analysis': supply_dist,
            'holder_analysis': holder_dist,
            'holding_period_analysis': holding_period_dist,
            'comprehensive_insights': self.extract_comprehensive_insights(
                supply_dist, holder_dist, holding_period_dist
            ),
            'risk_assessment': self.assess_distribution_risks(
                supply_dist, holder_dist, holding_period_dist
            ),
            'investment_implications': self.derive_investment_implications(
                supply_dist, holder_dist, holding_period_dist
            )
        }
        
        return report
    
    def extract_comprehensive_insights(self, supply_data: Dict, 
                                     holder_data: Dict, 
                                     period_data: Dict) -> List[str]:
        """提取综合洞察"""
        
        insights = []
        
        # 供应集中度洞察
        if supply_data and 'concentration_metrics' in supply_data:
            gini = supply_data['concentration_metrics']['gini_coefficient']
            if gini > 0.7:
                insights.append("供应高度集中，大户影响力极强")
            elif gini < 0.3:
                insights.append("供应分布相对均匀，去中心化程度较高")
        
        # 持有者结构洞察
        if holder_data and 'market_structure' in holder_data:
            structure = holder_data['market_structure']
            insights.append(f"市场结构呈现{structure}特征")
        
        # 持有行为洞察
        if period_data and 'maturity_analysis' in period_data:
            maturity = period_data['maturity_analysis']['maturity_level']
            insights.append(f"市场处于{maturity}阶段")
        
        # 交叉分析洞察
        if (supply_data and holder_data and 
            supply_data.get('concentration_metrics', {}).get('gini_coefficient', 0) > 0.6 and
            holder_data.get('market_structure') == "鲸鱼主导"):
            insights.append("供应和持有者双重集中，存在较高的市场操纵风险")
        
        return insights
    
    def assess_distribution_risks(self, supply_data: Dict, 
                                holder_data: Dict, 
                                period_data: Dict) -> Dict:
        """评估分布相关风险"""
        
        risks = {
            'concentration_risk': 0,
            'liquidity_risk': 0,
            'volatility_risk': 0,
            'manipulation_risk': 0,
            'overall_risk_score': 0,
            'risk_level': 'low'
        }
        
        # 集中度风险
        if supply_data and 'concentration_metrics' in supply_data:
            gini = supply_data['concentration_metrics']['gini_coefficient']
            risks['concentration_risk'] = min(100, gini * 100)
        
        # 流动性风险
        if period_data and 'stability_metrics' in period_data:
            liquid_ratio = period_data['stability_metrics']['liquid_supply_ratio']
            if liquid_ratio < 30:
                risks['liquidity_risk'] = (30 - liquid_ratio) * 3
            else:
                risks['liquidity_risk'] = 0
        
        # 波动性风险
        if period_data and 'stability_metrics' in period_data:
            volatility_risk = period_data['stability_metrics'].get('volatility_risk', 0)
            risks['volatility_risk'] = volatility_risk
        
        # 操纵风险
        concentration_risk = risks['concentration_risk']
        if holder_data and 'market_structure' in holder_data:
            if holder_data['market_structure'] == "鲸鱼主导":
                risks['manipulation_risk'] = min(100, concentration_risk * 1.2)
            else:
                risks['manipulation_risk'] = concentration_risk * 0.8
        
        # 综合风险评分
        risk_components = [
            risks['concentration_risk'],
            risks['liquidity_risk'],
            risks['volatility_risk'],
            risks['manipulation_risk']
        ]
        
        risks['overall_risk_score'] = sum(risk_components) / len(risk_components)
        
        # 风险等级
        if risks['overall_risk_score'] < 25:
            risks['risk_level'] = 'low'
        elif risks['overall_risk_score'] < 50:
            risks['risk_level'] = 'medium'
        elif risks['overall_risk_score'] < 75:
            risks['risk_level'] = 'high'
        else:
            risks['risk_level'] = 'extreme'
        
        return risks
    
    def derive_investment_implications(self, supply_data: Dict, 
                                     holder_data: Dict, 
                                     period_data: Dict) -> Dict:
        """推导投资影响"""
        
        implications = {
            'position_sizing': 'normal',
            'entry_strategy': 'gradual',
            'exit_strategy': 'planned',
            'risk_management': 'standard',
            'time_horizon': 'medium_term',
            'recommendations': []
        }
        
        # 基于集中度调整仓位
        if supply_data and 'concentration_metrics' in supply_data:
            gini = supply_data['concentration_metrics']['gini_coefficient']
            if gini > 0.7:
                implications['position_sizing'] = 'reduced'
                implications['recommendations'].append("由于高集中度，建议减少仓位规模")
        
        # 基于持有者结构调整策略
        if holder_data and 'market_structure' in holder_data:
            structure = holder_data['market_structure']
            if structure == "鲸鱼主导":
                implications['entry_strategy'] = 'cautious'
                implications['recommendations'].append("鲸鱼主导市场，建议谨慎进入")
            elif structure == "散户主导":
                implications['entry_strategy'] = 'opportunistic'
                implications['recommendations'].append("散户主导市场，可寻找情绪化机会")
        
        # 基于持有期间调整时间范围
        if period_data and 'maturity_analysis' in period_data:
            maturity = period_data['maturity_analysis']['maturity_level']
            if maturity == "高度成熟":
                implications['time_horizon'] = 'long_term'
                implications['recommendations'].append("市场成熟，适合长期持有")
            elif maturity == "早期阶段":
                implications['time_horizon'] = 'short_term'
                implications['recommendations'].append("早期市场，建议短期交易为主")
        
        return implications

    def visualize_supply_distribution(self, supply_data: Dict, save_path: str = None):
        """可视化供应分布"""
        
        if not supply_data or 'distribution_stats' not in supply_data:
            print("无可视化数据")
            return
        
        distribution = supply_data['distribution_stats']
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. 饼图 - 供应量分布
        tiers = list(distribution.keys())
        amounts = [data['supply_amount'] for data in distribution.values()]
        
        ax1.pie(amounts, labels=tiers, autopct='%1.1f%%', startangle=90)
        ax1.set_title(f"{supply_data['asset']} 供应量分布")
        
        # 2. 柱状图 - 百分比分布
        percentages = [data['percentage'] for data in distribution.values()]
        ax2.bar(tiers, percentages)
        ax2.set_title("各层级占比")
        ax2.set_ylabel("占比 (%)")
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. 洛伦兹曲线
        sorted_amounts = sorted(amounts)
        cumulative = np.cumsum(sorted_amounts)
        normalized_cumulative = cumulative / cumulative[-1]
        
        x = np.linspace(0, 1, len(normalized_cumulative))
        ax3.plot(x, normalized_cumulative, 'b-', linewidth=2, label='洛伦兹曲线')
        ax3.plot([0, 1], [0, 1], 'r--', label='完全平等线')
        ax3.set_xlabel("累积人口比例")
        ax3.set_ylabel("累积财富比例")
        ax3.set_title("财富分布洛伦兹曲线")
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 集中度指标
        gini = supply_data.get('concentration_metrics', {}).get('gini_coefficient', 0)
        herfindahl = supply_data.get('concentration_metrics', {}).get('herfindahl_index', 0)
        
        metrics = ['基尼系数', '赫芬达尔指数']
        values = [gini, herfindahl]
        
        bars = ax4.bar(metrics, values, color=['skyblue', 'lightcoral'])
        ax4.set_title("集中度指标")
        ax4.set_ylabel("指标值")
        
        # 添加数值标签
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{value:.3f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def visualize_holder_distribution(self, holder_data: Dict, save_path: str = None):
        """可视化持有者分布"""
        
        if not holder_data or 'holder_stats' not in holder_data:
            print("无可视化数据")
            return
        
        stats = holder_data['holder_stats']
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 1. 持有者数量分布
        tiers = list(stats.keys())
        counts = [data['holder_count'] for data in stats.values()]
        
        ax1.bar(tiers, counts, log=True)
        ax1.set_yscale('log')
        ax1.set_title(f"{holder_data['asset']} 持有者数量分布 (对数刻度)")
        ax1.set_xlabel("余额层级")
        ax1.set_ylabel("持有者数量 (对数刻度)")
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. 参与度指标雷达图
        if 'participation_metrics' in holder_data:
            metrics = holder_data['participation_metrics']
            
            categories = ['散户参与', '机构参与', '鲸鱼参与', '多样性指数']
            values = [
                metrics.get('retail_participation', 0),
                metrics.get('institutional_participation', 0),
                metrics.get('whale_participation', 0),
                metrics.get('diversity_index', 0) * 10  # 缩放显示
            ]
            
            # 创建雷达图
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)
            values += values[:1]  # 闭合图形
            angles = np.concatenate((angles, [angles[0]]))
            
            ax2.plot(angles, values, 'o-', linewidth=2)
            ax2.fill(angles, values, alpha=0.25)
            ax2.set_xticks(angles[:-1])
            ax2.set_xticklabels(categories)
            ax2.set_title("持有者参与度雷达图")
            ax2.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
```

## 数据处理和可视化示例

### 1. 供应分布深度分析

```python
# 初始化分析器
analyzer = DistributionAnalyzer(api_key="YOUR_API_KEY")

# 获取比特币供应分布
btc_supply = analyzer.get_supply_distribution('BTC', days=30)

print("比特币供应分布分析:")
print(f"基尼系数: {btc_supply['concentration_metrics']['gini_coefficient']:.3f}")
print(f"集中度水平: {btc_supply['concentration_metrics']['concentration_level']}")

# 可视化供应分布
analyzer.visualize_supply_distribution(btc_supply, 'btc_supply_distribution.png')
```

### 2. 多资产分布对比

```python
def comprehensive_distribution_comparison(assets=['BTC', 'ETH', 'ADA']):
    """综合分布对比分析"""
    
    comparison_results = {}
    
    for asset in assets:
        supply_data = analyzer.get_supply_distribution(asset)
        holder_data = analyzer.get_holder_distribution(asset)
        
        comparison_results[asset] = {
            'gini_coefficient': supply_data.get('concentration_metrics', {}).get('gini_coefficient', 0),
            'market_structure': holder_data.get('market_structure', ''),
            'diversity_index': holder_data.get('participation_metrics', {}).get('diversity_index', 0),
            'retail_participation': holder_data.get('participation_metrics', {}).get('retail_participation', 0)
        }
    
    # 创建对比图表
    df = pd.DataFrame(comparison_results).T
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 基尼系数对比
    df['gini_coefficient'].plot(kind='bar', ax=axes[0,0], title='基尼系数对比')
    axes[0,0].set_ylabel('基尼系数')
    
    # 多样性指数对比
    df['diversity_index'].plot(kind='bar', ax=axes[0,1], title='多样性指数对比', color='green')
    axes[0,1].set_ylabel('多样性指数')
    
    # 散户参与度对比
    df['retail_participation'].plot(kind='bar', ax=axes[1,0], title='散户参与度对比', color='orange')
    axes[1,0].set_ylabel('散户参与度 (%)')
    
    # 市场结构分布
    structure_counts = df['market_structure'].value_counts()
    axes[1,1].pie(structure_counts.values, labels=structure_counts.index, autopct='%1.1f%%')
    axes[1,1].set_title('市场结构分布')
    
    plt.tight_layout()
    plt.show()
    
    return df

# 执行多资产对比
comparison_df = comprehensive_distribution_comparison(['BTC', 'ETH', 'ADA'])
print("\n多资产分布对比:")
print(comparison_df)
```

### 3. 时间序列分布趋势分析

```python
def analyze_distribution_time_series(asset='BTC', period_days=90):
    """分析分布的时间序列趋势"""
    
    # 获取历史数据
    url = analyzer.base_url + "supply_distribution"
    params = {
        'a': asset,
        'i': '24h',
        's': int((datetime.now() - timedelta(days=period_days)).timestamp())
    }
    
    response = requests.get(url, params=params, headers=analyzer.headers)
    data = response.json()
    
    # 转换为DataFrame
    df_data = []
    for entry in data:
        row = {'timestamp': pd.to_datetime(entry['t'], unit='s')}
        
        # 计算基尼系数
        gini = analyzer.calculate_gini_from_distribution(entry['v'])
        row['gini_coefficient'] = gini
        
        # 计算大户占比（假设tier_1000和tier_10000为大户）
        total_supply = sum(entry['v'].values())
        whale_supply = entry['v'].get('tier_1000', 0) + entry['v'].get('tier_10000', 0)
        row['whale_percentage'] = (whale_supply / total_supply * 100) if total_supply > 0 else 0
        
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    df.set_index('timestamp', inplace=True)
    
    # 可视化趋势
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # 基尼系数趋势
    df['gini_coefficient'].plot(ax=ax1, title=f'{asset} 基尼系数趋势')
    ax1.set_ylabel('基尼系数')
    ax1.grid(True, alpha=0.3)
    
    # 大户占比趋势
    df['whale_percentage'].plot(ax=ax2, title=f'{asset} 大户占比趋势', color='red')
    ax2.set_ylabel('大户占比 (%)')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # 计算趋势统计
    gini_trend = df['gini_coefficient'].pct_change().mean() * 100
    whale_trend = df['whale_percentage'].pct_change().mean() * 100
    
    print(f"{asset} 分布趋势分析:")
    print(f"基尼系数变化趋势: {gini_trend:+.3f}% (平均日变化)")
    print(f"大户占比变化趋势: {whale_trend:+.3f}% (平均日变化)")
    
    return df

# 分析比特币90天分布趋势
btc_trends = analyze_distribution_time_series('BTC', 90)
```

## 交易策略和市场分析

### 1. 分布驱动的交易策略

```python
class DistributionTradingStrategy:
    """基于分布数据的交易策略"""
    
    def __init__(self, analyzer: DistributionAnalyzer):
        self.analyzer = analyzer
        
    def generate_distribution_signals(self, asset: str) -> Dict:
        """生成基于分布的交易信号"""
        
        supply_data = self.analyzer.get_supply_distribution(asset)
        holder_data = self.analyzer.get_holder_distribution(asset)
        period_data = self.analyzer.get_holding_period_distribution(asset)
        
        signals = {
            'buy_signals': [],
            'sell_signals': [],
            'hold_signals': [],
            'overall_recommendation': 'hold',
            'confidence_level': 'medium'
        }
        
        # 基于供应集中度的信号
        if supply_data and 'concentration_metrics' in supply_data:
            gini = supply_data['concentration_metrics']['gini_coefficient']
            
            if gini < 0.3:
                signals['buy_signals'].append("供应分布均匀，去中心化程度高")
            elif gini > 0.7:
                signals['sell_signals'].append("供应高度集中，存在操纵风险")
        
        # 基于持有者结构的信号
        if holder_data and 'market_structure' in holder_data:
            structure = holder_data['market_structure']
            
            if structure == "散户主导":
                signals['buy_signals'].append("散户主导市场，情绪反应强烈，寻找超卖机会")
            elif structure == "鲸鱼主导":
                signals['sell_signals'].append("鲸鱼主导市场，价格易被操纵")
            elif structure == "均衡分布":
                signals['hold_signals'].append("市场结构均衡，适合持有")
        
        # 基于持有期间的信号
        if period_data and 'maturity_analysis' in period_data:
            maturity = period_data['maturity_analysis']
            
            if maturity['hodler_dominance']:
                signals['buy_signals'].append("长期持有者主导，供应稳定")
            
            if maturity['speculative_activity']:
                signals['sell_signals'].append("投机活动活跃，波动性可能增加")
        
        # 综合评估
        buy_score = len(signals['buy_signals'])
        sell_score = len(signals['sell_signals'])
        
        if buy_score > sell_score + 1:
            signals['overall_recommendation'] = 'buy'
            signals['confidence_level'] = 'high' if buy_score > 3 else 'medium'
        elif sell_score > buy_score + 1:
            signals['overall_recommendation'] = 'sell'
            signals['confidence_level'] = 'high' if sell_score > 3 else 'medium'
        else:
            signals['overall_recommendation'] = 'hold'
        
        return signals
    
    def calculate_position_sizing(self, asset: str, base_position: float = 1.0) -> Dict:
        """基于分布风险计算仓位大小"""
        
        supply_data = self.analyzer.get_supply_distribution(asset)
        
        position_adjustment = {
            'base_position': base_position,
            'adjusted_position': base_position,
            'adjustment_factor': 1.0,
            'reasoning': []
        }
        
        if supply_data and 'concentration_metrics' in supply_data:
            gini = supply_data['concentration_metrics']['gini_coefficient']
            
            # 基于基尼系数调整仓位
            if gini > 0.8:
                adjustment_factor = 0.5
                position_adjustment['reasoning'].append("极高集中度，大幅减仓")
            elif gini > 0.6:
                adjustment_factor = 0.7
                position_adjustment['reasoning'].append("高集中度，适度减仓")
            elif gini < 0.3:
                adjustment_factor = 1.2
                position_adjustment['reasoning'].append("低集中度，可适度增仓")
            else:
                adjustment_factor = 1.0
                position_adjustment['reasoning'].append("集中度适中，保持正常仓位")
            
            position_adjustment['adjustment_factor'] = adjustment_factor
            position_adjustment['adjusted_position'] = base_position * adjustment_factor
        
        return position_adjustment
    
    def identify_accumulation_opportunities(self, asset: str) -> Dict:
        """识别累积机会"""
        
        holder_data = self.analyzer.get_holder_distribution(asset)
        period_data = self.analyzer.get_holding_period_distribution(asset)
        
        opportunities = {
            'accumulation_score': 0,
            'opportunity_level': 'low',
            'optimal_timing': [],
            'risk_factors': []
        }
        
        score = 0
        
        # 基于持有者结构评分
        if holder_data and 'participation_metrics' in holder_data:
            retail_participation = holder_data['participation_metrics'].get('retail_participation', 0)
            
            if retail_participation > 50:
                score += 20
                opportunities['optimal_timing'].append("散户参与度高，适合逆向累积")
            elif retail_participation < 20:
                score += 10
                opportunities['risk_factors'].append("散户参与度低，流动性可能不足")
        
        # 基于持有期间评分
        if period_data and 'stability_metrics' in period_data:
            stability = period_data['stability_metrics'].get('supply_stability', 0)
            
            if stability > 60:
                score += 25
                opportunities['optimal_timing'].append("供应稳定，适合长期累积")
            
            volatility_risk = period_data['stability_metrics'].get('volatility_risk', 0)
            if volatility_risk > 40:
                score -= 15
                opportunities['risk_factors'].append("高波动性风险")
        
        opportunities['accumulation_score'] = max(0, min(100, score))
        
        # 确定机会等级
        if opportunities['accumulation_score'] > 70:
            opportunities['opportunity_level'] = 'high'
        elif opportunities['accumulation_score'] > 40:
            opportunities['opportunity_level'] = 'medium'
        else:
            opportunities['opportunity_level'] = 'low'
        
        return opportunities

# 使用示例
strategy = DistributionTradingStrategy(analyzer)

# 生成比特币分布信号
btc_signals = strategy.generate_distribution_signals('BTC')
print("比特币分布交易信号:")
print(f"总体建议: {btc_signals['overall_recommendation']}")
print(f"置信度: {btc_signals['confidence_level']}")
print("买入信号:", btc_signals['buy_signals'])
print("卖出信号:", btc_signals['sell_signals'])

# 计算仓位大小
position_sizing = strategy.calculate_position_sizing('BTC', 10000)
print(f"\n仓位建议:")
print(f"调整因子: {position_sizing['adjustment_factor']:.2f}")
print(f"调整后仓位: ${position_sizing['adjusted_position']:,.2f}")
```

### 2. 风险管理策略

```python
class DistributionRiskManager:
    """基于分布的风险管理"""
    
    def __init__(self, analyzer: DistributionAnalyzer):
        self.analyzer = analyzer
        
    def assess_portfolio_distribution_risk(self, portfolio: Dict) -> Dict:
        """评估投资组合的分布风险"""
        
        portfolio_risk = {
            'assets': {},
            'overall_risk_score': 0,
            'risk_diversification': 0,
            'recommendations': []
        }
        
        total_value = sum(portfolio.values())
        risk_scores = []
        
        for asset, value in portfolio.items():
            # 获取资产分布数据
            supply_data = self.analyzer.get_supply_distribution(asset)
            
            if supply_data and 'concentration_metrics' in supply_data:
                gini = supply_data['concentration_metrics']['gini_coefficient']
                asset_risk = gini * 100
                
                portfolio_risk['assets'][asset] = {
                    'weight': value / total_value,
                    'gini_coefficient': gini,
                    'risk_score': asset_risk,
                    'risk_contribution': (value / total_value) * asset_risk
                }
                
                risk_scores.append(asset_risk)
        
        # 计算加权平均风险
        if portfolio_risk['assets']:
            portfolio_risk['overall_risk_score'] = sum(
                data['risk_contribution'] for data in portfolio_risk['assets'].values()
            )
            
            # 计算风险分散度
            risk_std = np.std(risk_scores) if risk_scores else 0
            portfolio_risk['risk_diversification'] = 100 - risk_std
        
        # 生成建议
        if portfolio_risk['overall_risk_score'] > 70:
            portfolio_risk['recommendations'].append("投资组合整体集中度风险高，建议分散投资")
        
        high_risk_assets = [asset for asset, data in portfolio_risk['assets'].items() 
                           if data['risk_score'] > 80]
        if high_risk_assets:
            portfolio_risk['recommendations'].append(
                f"高风险资产 {', '.join(high_risk_assets)} 需要减少配置"
            )
        
        return portfolio_risk
    
    def set_dynamic_stop_losses(self, asset: str, entry_price: float) -> Dict:
        """基于分布设置动态止损"""
        
        supply_data = self.analyzer.get_supply_distribution(asset)
        holder_data = self.analyzer.get_holder_distribution(asset)
        
        stop_loss_config = {
            'initial_stop_loss': 0.1,  # 10%
            'trailing_stop': 0.05,     # 5%
            'volatility_adjustment': 1.0,
            'reasoning': []
        }
        
        # 基于供应集中度调整
        if supply_data and 'concentration_metrics' in supply_data:
            gini = supply_data['concentration_metrics']['gini_coefficient']
            
            if gini > 0.7:
                stop_loss_config['initial_stop_loss'] = 0.15  # 更严格止损
                stop_loss_config['trailing_stop'] = 0.08
                stop_loss_config['reasoning'].append("高集中度，设置严格止损")
            elif gini < 0.3:
                stop_loss_config['initial_stop_loss'] = 0.08  # 放宽止损
                stop_loss_config['trailing_stop'] = 0.04
                stop_loss_config['reasoning'].append("低集中度，可放宽止损")
        
        # 基于市场结构调整
        if holder_data and 'market_structure' in holder_data:
            structure = holder_data['market_structure']
            
            if structure == "鲸鱼主导":
                stop_loss_config['volatility_adjustment'] = 1.5
                stop_loss_config['reasoning'].append("鲸鱼主导市场，增加波动性缓冲")
            elif structure == "散户主导":
                stop_loss_config['volatility_adjustment'] = 1.2
                stop_loss_config['reasoning'].append("散户主导市场，适度增加缓冲")
        
        # 计算最终止损价格
        adjusted_stop_loss = (stop_loss_config['initial_stop_loss'] * 
                             stop_loss_config['volatility_adjustment'])
        
        stop_loss_config['stop_loss_price'] = entry_price * (1 - adjusted_stop_loss)
        stop_loss_config['trailing_stop_price'] = entry_price * (1 - stop_loss_config['trailing_stop'])
        
        return stop_loss_config

# 使用示例
risk_manager = DistributionRiskManager(analyzer)

# 评估投资组合风险
portfolio = {'BTC': 50000, 'ETH': 30000, 'ADA': 20000}
portfolio_risk = risk_manager.assess_portfolio_distribution_risk(portfolio)

print("投资组合分布风险评估:")
print(f"整体风险评分: {portfolio_risk['overall_risk_score']:.2f}")
print(f"风险分散度: {portfolio_risk['risk_diversification']:.2f}")
print("建议:", portfolio_risk['recommendations'])

# 设置动态止损
btc_stop_loss = risk_manager.set_dynamic_stop_losses('BTC', 45000)
print(f"\n比特币动态止损设置:")
print(f"止损价格: ${btc_stop_loss['stop_loss_price']:,.2f}")
print(f"追踪止损: {btc_stop_loss['trailing_stop']*100:.1f}%")
```

## 常见问题

### Q1: 分布数据的准确性如何保证？

分布数据基于完整的链上数据分析：
- 使用全节点数据确保完整性
- 定期校验和更新地址分类
- 采用多重验证机制
- 考虑了地址聚类和实体识别

### Q2: 如何理解基尼系数的意义？

基尼系数反映财富分布不平等程度：
- 0: 完全平等分布
- 0.3以下: 相对平等
- 0.3-0.5: 中等不平等
- 0.5-0.7: 高度不平等  
- 0.7以上: 极度不平等

在加密货币中，基尼系数通常较高，需要结合其他指标综合分析。

### Q3: 持有期间分布如何影响价格？

持有期间分布影响市场流动性和价格稳定性：
- **短期持有者多**: 流动性高，价格波动大
- **长期持有者多**: 供应稳定，价格相对稳定
- **混合分布**: 取决于短期和长期持有者的相对比例

### Q4: 地理分布数据如何获取？

地理分布基于多种数据源：
- 交易所地理位置
- IP地址分析
- 已知实体地理信息
- 监管报告数据

需要注意这类数据可能存在一定误差。

## 最佳实践

1. **多维度分析**: 结合供应分布、持有者分布和时间分布进行综合分析
2. **趋势监控**: 关注分布变化趋势而非静态快照
3. **风险评估**: 基于集中度指标调整投资策略和风险管理
4. **动态调整**: 根据分布变化动态调整仓位和止损策略
5. **跨资产比较**: 通过对比不同资产的分布特征发现投资机会
6. **历史对比**: 与历史分布模式对比，识别异常和机会

---

*本文档详细介绍了 Glassnode Distribution API 的使用方法，包括数据获取、分析技术和实际应用案例。分布数据是理解市场结构和制定精准投资策略的重要基础。*