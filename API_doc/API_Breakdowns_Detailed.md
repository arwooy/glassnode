# Breakdowns（细分数据）API 详细文档

## 概述

Breakdowns API 提供区块链数据的细分和分类分析，包括地址类型分布、实体类型分析、交易类型统计、资产分布等。这些细分数据对于深入理解区块链生态系统结构、识别市场趋势、进行风险评估和制定投资策略至关重要。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/breakdowns/`

**支持的资产**: BTC, ETH, USDT, USDC, LTC, BCH 等主要加密资产

**数据更新频率**: 
- 实时数据：10分钟
- 聚合数据：1小时、24小时
- 历史数据：完整链上数据

## 核心端点

### 1. 地址类型细分

#### 1.1 按实体类型的地址分布

**端点**: `/entity_addresses`

**描述**: 按实体类型（交易所、矿池、服务商等）分类的活跃地址分布。

**参数**:
- `a`: 资产符号（如 BTC）
- `i`: 时间间隔（1h, 24h, 1w）
- `s`: 开始时间戳
- `entity_type`: 实体类型过滤器（可选）

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/breakdowns/entity_addresses?a=BTC&i=24h&s=1609459200" \
  -H "X-Api-Key: YOUR_API_KEY"
```

**示例响应**:
```json
[
  {
    "t": 1726790400,
    "v": {
      "exchange": 89543,
      "mining_pool": 12456,
      "service": 34521,
      "individual": 1245678,
      "unknown": 156789
    }
  }
]
```

#### 1.2 余额区间分布

**端点**: `/balance_distribution`

**描述**: 按余额区间分类的地址数量分布，反映财富集中度。

**参数**:
- `a`: 资产符号
- `i`: 时间间隔
- `s`: 开始时间戳
- `balance_range`: 余额范围（可选）

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/breakdowns/balance_distribution?a=BTC&i=24h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

### 2. 交易类型细分

#### 2.1 按交易类型的统计

**端点**: `/transaction_types`

**描述**: 按交易类型（P2P、P2SH、P2WPKH等）分类的交易统计。

**参数**:
- `a`: 资产符号
- `i`: 时间间隔
- `s`: 开始时间戳
- `tx_type`: 交易类型过滤器

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/breakdowns/transaction_types?a=BTC&i=1h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

### 3. 供应分布分析

#### 3.1 持有时间分布

**端点**: `/supply_by_holding_time`

**描述**: 按持有时间分类的供应量分布（短期持有者 vs 长期持有者）。

**参数**:
- `a`: 资产符号
- `i`: 时间间隔
- `holding_period`: 持有期间分类

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/breakdowns/supply_by_holding_time?a=BTC&i=24h" \
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

class BreakdownsAnalyzer:
    """
    Glassnode Breakdowns API 分析器
    提供细分数据的获取、分析和可视化功能
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/breakdowns/"
        self.headers = {"X-Api-Key": self.api_key}
        
    def get_entity_address_distribution(self, asset: str = 'BTC', 
                                      days: int = 30) -> Dict:
        """获取实体地址分布数据"""
        
        url = self.base_url + "entity_addresses"
        params = {
            'a': asset,
            'i': '24h',
            's': int((datetime.now() - timedelta(days=days)).timestamp()),
            'u': int(datetime.now().timestamp())
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            return self.process_entity_distribution(data, asset)
            
        except Exception as e:
            print(f"获取实体地址分布数据失败: {e}")
            return {}
    
    def process_entity_distribution(self, data: List, asset: str) -> Dict:
        """处理实体分布数据"""
        
        if not data:
            return {}
        
        # 获取最新数据
        latest = data[-1]['v']
        total_addresses = sum(latest.values())
        
        # 计算各实体类型占比
        distribution = {}
        for entity_type, count in latest.items():
            distribution[entity_type] = {
                'address_count': count,
                'percentage': (count / total_addresses * 100) if total_addresses > 0 else 0
            }
        
        # 分析趋势
        if len(data) > 7:
            week_ago = data[-7]['v']
            trends = {}
            for entity_type in latest.keys():
                current = latest[entity_type]
                past = week_ago.get(entity_type, 0)
                change = ((current - past) / past * 100) if past > 0 else 0
                trends[entity_type] = change
        else:
            trends = {}
        
        return {
            'asset': asset,
            'timestamp': data[-1]['t'],
            'total_addresses': total_addresses,
            'distribution': distribution,
            'weekly_trends': trends,
            'analysis': self.analyze_entity_distribution(distribution, trends)
        }
    
    def analyze_entity_distribution(self, distribution: Dict, trends: Dict) -> Dict:
        """分析实体分布特征"""
        
        analysis = {
            'dominant_entity': max(distribution.keys(), 
                                 key=lambda x: distribution[x]['address_count']),
            'diversification_score': self.calculate_diversification_score(distribution),
            'market_structure': self.assess_market_structure(distribution),
            'growth_leaders': [],
            'decline_entities': []
        }
        
        # 分析增长和下降趋势
        for entity_type, change in trends.items():
            if change > 5:
                analysis['growth_leaders'].append({
                    'entity': entity_type,
                    'growth_rate': change
                })
            elif change < -5:
                analysis['decline_entities'].append({
                    'entity': entity_type,
                    'decline_rate': change
                })
        
        return analysis
    
    def calculate_diversification_score(self, distribution: Dict) -> float:
        """计算多样化评分（基于赫芬达尔指数）"""
        
        percentages = [data['percentage'] for data in distribution.values()]
        herfindahl_index = sum((p/100)**2 for p in percentages)
        
        # 转换为多样化评分（0-100，100最多样化）
        diversification_score = (1 - herfindahl_index) * 100
        
        return round(diversification_score, 2)
    
    def assess_market_structure(self, distribution: Dict) -> str:
        """评估市场结构"""
        
        exchange_pct = distribution.get('exchange', {}).get('percentage', 0)
        individual_pct = distribution.get('individual', {}).get('percentage', 0)
        
        if exchange_pct > 50:
            return "交易所主导"
        elif individual_pct > 60:
            return "散户主导"
        elif exchange_pct > 30 and individual_pct > 30:
            return "平衡分布"
        else:
            return "机构化程度高"
    
    def get_balance_distribution(self, asset: str = 'BTC', days: int = 30) -> Dict:
        """获取余额分布数据"""
        
        url = self.base_url + "balance_distribution"
        params = {
            'a': asset,
            'i': '24h',
            's': int((datetime.now() - timedelta(days=days)).timestamp())
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            return self.analyze_balance_distribution(data, asset)
            
        except Exception as e:
            print(f"获取余额分布数据失败: {e}")
            return {}
    
    def analyze_balance_distribution(self, data: List, asset: str) -> Dict:
        """分析余额分布"""
        
        if not data:
            return {}
        
        latest = data[-1]['v']
        
        # 定义余额区间
        balance_ranges = {
            'dust': {'min': 0, 'max': 0.001},
            'small': {'min': 0.001, 'max': 0.1},
            'medium': {'min': 0.1, 'max': 1},
            'large': {'min': 1, 'max': 100},
            'whale': {'min': 100, 'max': float('inf')}
        }
        
        # 计算分布统计
        total_addresses = sum(latest.values())
        distribution_stats = {}
        
        for range_name, addresses in latest.items():
            distribution_stats[range_name] = {
                'address_count': addresses,
                'percentage': (addresses / total_addresses * 100) if total_addresses > 0 else 0
            }
        
        # 计算基尼系数
        gini_coefficient = self.calculate_gini_coefficient(latest)
        
        return {
            'asset': asset,
            'timestamp': data[-1]['t'],
            'distribution': distribution_stats,
            'gini_coefficient': gini_coefficient,
            'wealth_concentration': self.assess_wealth_concentration(gini_coefficient),
            'trends': self.analyze_balance_trends(data)
        }
    
    def calculate_gini_coefficient(self, distribution: Dict) -> float:
        """计算基尼系数"""
        
        # 简化计算，实际需要更详细的余额数据
        percentages = list(distribution.values())
        percentages.sort()
        
        n = len(percentages)
        cumsum = np.cumsum(percentages)
        
        return (n + 1 - 2 * sum(cumsum) / cumsum[-1]) / n if cumsum[-1] > 0 else 0
    
    def assess_wealth_concentration(self, gini: float) -> str:
        """评估财富集中度"""
        
        if gini < 0.3:
            return "相对平等"
        elif gini < 0.5:
            return "中等集中"
        elif gini < 0.7:
            return "高度集中"
        else:
            return "极度集中"
    
    def get_transaction_type_breakdown(self, asset: str = 'BTC', 
                                     days: int = 7) -> Dict:
        """获取交易类型细分数据"""
        
        url = self.base_url + "transaction_types"
        params = {
            'a': asset,
            'i': '1h',
            's': int((datetime.now() - timedelta(days=days)).timestamp())
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            return self.analyze_transaction_types(data, asset)
            
        except Exception as e:
            print(f"获取交易类型数据失败: {e}")
            return {}
    
    def analyze_transaction_types(self, data: List, asset: str) -> Dict:
        """分析交易类型分布"""
        
        if not data:
            return {}
        
        # 汇总统计
        type_totals = {}
        for entry in data:
            for tx_type, count in entry['v'].items():
                type_totals[tx_type] = type_totals.get(tx_type, 0) + count
        
        total_transactions = sum(type_totals.values())
        
        # 计算占比
        type_distribution = {}
        for tx_type, count in type_totals.items():
            type_distribution[tx_type] = {
                'transaction_count': count,
                'percentage': (count / total_transactions * 100) if total_transactions > 0 else 0
            }
        
        return {
            'asset': asset,
            'period_days': len(data) / 24,  # 假设每小时一个数据点
            'total_transactions': total_transactions,
            'type_distribution': type_distribution,
            'dominant_type': max(type_distribution.keys(), 
                               key=lambda x: type_distribution[x]['transaction_count']),
            'adoption_trends': self.analyze_adoption_trends(data)
        }
    
    def analyze_adoption_trends(self, data: List) -> Dict:
        """分析采用趋势"""
        
        if len(data) < 24:  # 需要至少24小时数据
            return {}
        
        # 比较最近24小时和之前24小时的数据
        recent_24h = data[-24:]
        previous_24h = data[-48:-24] if len(data) >= 48 else []
        
        trends = {}
        
        if previous_24h:
            # 计算各类型交易数量变化
            recent_totals = {}
            previous_totals = {}
            
            for entry in recent_24h:
                for tx_type, count in entry['v'].items():
                    recent_totals[tx_type] = recent_totals.get(tx_type, 0) + count
            
            for entry in previous_24h:
                for tx_type, count in entry['v'].items():
                    previous_totals[tx_type] = previous_totals.get(tx_type, 0) + count
            
            for tx_type in recent_totals.keys():
                recent = recent_totals[tx_type]
                previous = previous_totals.get(tx_type, 0)
                
                if previous > 0:
                    change = ((recent - previous) / previous) * 100
                    trends[tx_type] = {
                        'change_24h': change,
                        'direction': 'increasing' if change > 0 else 'decreasing'
                    }
        
        return trends

    def generate_comprehensive_report(self, asset: str = 'BTC') -> Dict:
        """生成综合细分分析报告"""
        
        # 获取各类数据
        entity_data = self.get_entity_address_distribution(asset)
        balance_data = self.get_balance_distribution(asset)
        tx_type_data = self.get_transaction_type_breakdown(asset)
        
        # 综合分析
        report = {
            'asset': asset,
            'report_date': datetime.now().isoformat(),
            'entity_analysis': entity_data,
            'balance_analysis': balance_data,
            'transaction_analysis': tx_type_data,
            'key_insights': self.extract_key_insights(entity_data, balance_data, tx_type_data),
            'risk_assessment': self.assess_breakdown_risks(entity_data, balance_data),
            'recommendations': self.generate_recommendations(entity_data, balance_data, tx_type_data)
        }
        
        return report
    
    def extract_key_insights(self, entity_data: Dict, balance_data: Dict, 
                           tx_data: Dict) -> List[str]:
        """提取关键洞察"""
        
        insights = []
        
        # 实体分析洞察
        if entity_data:
            market_structure = entity_data.get('analysis', {}).get('market_structure', '')
            insights.append(f"市场结构: {market_structure}")
            
            diversification = entity_data.get('analysis', {}).get('diversification_score', 0)
            if diversification > 70:
                insights.append("地址分布高度多样化，市场去中心化程度较高")
            elif diversification < 30:
                insights.append("地址分布集中，市场中心化程度较高")
        
        # 余额分析洞察
        if balance_data:
            concentration = balance_data.get('wealth_concentration', '')
            insights.append(f"财富集中度: {concentration}")
            
            gini = balance_data.get('gini_coefficient', 0)
            if gini > 0.7:
                insights.append("财富高度集中，大户影响力显著")
        
        # 交易类型洞察
        if tx_data:
            dominant_type = tx_data.get('dominant_type', '')
            insights.append(f"主要交易类型: {dominant_type}")
        
        return insights
    
    def assess_breakdown_risks(self, entity_data: Dict, balance_data: Dict) -> Dict:
        """评估细分数据相关风险"""
        
        risks = {
            'centralization_risk': 0,
            'liquidity_risk': 0,
            'market_manipulation_risk': 0,
            'overall_risk_level': 'low'
        }
        
        # 中心化风险
        if entity_data:
            diversification = entity_data.get('analysis', {}).get('diversification_score', 100)
            risks['centralization_risk'] = max(0, 100 - diversification)
        
        # 流动性风险
        if balance_data:
            gini = balance_data.get('gini_coefficient', 0)
            risks['liquidity_risk'] = gini * 100
        
        # 市场操纵风险
        if entity_data and balance_data:
            # 结合实体集中度和余额集中度
            entity_concentration = 100 - entity_data.get('analysis', {}).get('diversification_score', 100)
            balance_concentration = balance_data.get('gini_coefficient', 0) * 100
            risks['market_manipulation_risk'] = (entity_concentration + balance_concentration) / 2
        
        # 综合风险等级
        avg_risk = (risks['centralization_risk'] + risks['liquidity_risk'] + 
                   risks['market_manipulation_risk']) / 3
        
        if avg_risk < 30:
            risks['overall_risk_level'] = 'low'
        elif avg_risk < 60:
            risks['overall_risk_level'] = 'medium'
        else:
            risks['overall_risk_level'] = 'high'
        
        return risks
    
    def generate_recommendations(self, entity_data: Dict, balance_data: Dict, 
                               tx_data: Dict) -> List[str]:
        """生成建议"""
        
        recommendations = []
        
        # 基于实体分析的建议
        if entity_data:
            market_structure = entity_data.get('analysis', {}).get('market_structure', '')
            if market_structure == "交易所主导":
                recommendations.append("市场由交易所主导，注意交易所风险和监管影响")
            elif market_structure == "散户主导":
                recommendations.append("散户参与度高，市场情绪影响较大")
        
        # 基于余额分析的建议
        if balance_data:
            concentration = balance_data.get('wealth_concentration', '')
            if concentration in ["高度集中", "极度集中"]:
                recommendations.append("财富高度集中，大户动向需要密切关注")
                recommendations.append("建议监控大额转账和持仓变化")
        
        # 基于交易类型的建议
        if tx_data:
            adoption_trends = tx_data.get('adoption_trends', {})
            for tx_type, trend_data in adoption_trends.items():
                if trend_data.get('change_24h', 0) > 20:
                    recommendations.append(f"{tx_type}交易类型快速增长，关注新用例发展")
        
        if not recommendations:
            recommendations.append("当前细分数据显示市场结构相对健康")
        
        return recommendations

    def visualize_entity_distribution(self, entity_data: Dict, save_path: str = None):
        """可视化实体分布"""
        
        if not entity_data or 'distribution' not in entity_data:
            print("无可视化数据")
            return
        
        distribution = entity_data['distribution']
        
        # 创建饼图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 地址数量分布
        labels = []
        sizes = []
        colors = plt.cm.Set3(np.linspace(0, 1, len(distribution)))
        
        for entity_type, data in distribution.items():
            labels.append(f"{entity_type}\n({data['address_count']:,})")
            sizes.append(data['address_count'])
        
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title(f"{entity_data['asset']} 实体地址分布")
        
        # 百分比柱状图
        entity_types = list(distribution.keys())
        percentages = [data['percentage'] for data in distribution.values()]
        
        ax2.bar(entity_types, percentages, color=colors)
        ax2.set_title("实体类型占比")
        ax2.set_ylabel("占比 (%)")
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def visualize_balance_distribution(self, balance_data: Dict, save_path: str = None):
        """可视化余额分布"""
        
        if not balance_data or 'distribution' not in balance_data:
            print("无可视化数据")
            return
        
        distribution = balance_data['distribution']
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        balance_ranges = list(distribution.keys())
        address_counts = [data['address_count'] for data in distribution.values()]
        
        # 对数刻度柱状图
        ax.bar(balance_ranges, address_counts)
        ax.set_yscale('log')
        ax.set_title(f"{balance_data['asset']} 余额分布 (对数刻度)")
        ax.set_xlabel("余额区间")
        ax.set_ylabel("地址数量 (对数刻度)")
        ax.tick_params(axis='x', rotation=45)
        
        # 添加基尼系数信息
        gini = balance_data.get('gini_coefficient', 0)
        concentration = balance_data.get('wealth_concentration', '')
        ax.text(0.02, 0.95, f"基尼系数: {gini:.3f}\n财富集中度: {concentration}", 
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
```

## 数据处理和可视化示例

### 1. 实体分布分析

```python
# 初始化分析器
analyzer = BreakdownsAnalyzer(api_key="YOUR_API_KEY")

# 获取比特币实体分布
btc_entities = analyzer.get_entity_address_distribution('BTC', days=30)

print("比特币实体分布分析:")
print(f"总地址数: {btc_entities['total_addresses']:,}")
print(f"多样化评分: {btc_entities['analysis']['diversification_score']}")
print(f"市场结构: {btc_entities['analysis']['market_structure']}")

# 可视化
analyzer.visualize_entity_distribution(btc_entities, 'btc_entity_distribution.png')
```

### 2. 多资产对比分析

```python
def compare_asset_breakdowns(assets=['BTC', 'ETH', 'LTC']):
    """对比多个资产的细分数据"""
    
    comparison_data = {}
    
    for asset in assets:
        entity_data = analyzer.get_entity_address_distribution(asset)
        balance_data = analyzer.get_balance_distribution(asset)
        
        comparison_data[asset] = {
            'diversification_score': entity_data.get('analysis', {}).get('diversification_score', 0),
            'market_structure': entity_data.get('analysis', {}).get('market_structure', ''),
            'gini_coefficient': balance_data.get('gini_coefficient', 0),
            'wealth_concentration': balance_data.get('wealth_concentration', '')
        }
    
    # 创建对比表
    df = pd.DataFrame(comparison_data).T
    
    print("资产细分数据对比:")
    print(df)
    
    return df

# 执行对比分析
comparison = compare_asset_breakdowns(['BTC', 'ETH', 'LTC'])
```

### 3. 时间序列趋势分析

```python
def analyze_breakdown_trends(asset='BTC', period_days=90):
    """分析细分数据的时间趋势"""
    
    # 获取历史数据
    url = analyzer.base_url + "entity_addresses"
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
        row.update(entry['v'])
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    df.set_index('timestamp', inplace=True)
    
    # 计算各实体类型的趋势
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()
    
    entity_types = [col for col in df.columns if col != 'timestamp']
    
    for i, entity_type in enumerate(entity_types[:4]):
        if i < len(axes):
            df[entity_type].plot(ax=axes[i], title=f"{entity_type} 地址数趋势")
            axes[i].set_ylabel("地址数量")
    
    plt.suptitle(f"{asset} 实体地址趋势分析")
    plt.tight_layout()
    plt.show()
    
    return df

# 分析比特币90天趋势
btc_trends = analyze_breakdown_trends('BTC', 90)
```

## 交易策略和市场分析

### 1. 基于细分数据的市场时机判断

```python
class BreakdownTradingStrategy:
    """基于细分数据的交易策略"""
    
    def __init__(self, analyzer: BreakdownsAnalyzer):
        self.analyzer = analyzer
        
    def assess_market_sentiment(self, asset: str) -> Dict:
        """基于细分数据评估市场情绪"""
        
        entity_data = self.analyzer.get_entity_address_distribution(asset)
        balance_data = self.analyzer.get_balance_distribution(asset)
        
        signals = {
            'bullish_signals': [],
            'bearish_signals': [],
            'neutral_signals': []
        }
        
        # 分析实体增长趋势
        if entity_data and 'weekly_trends' in entity_data:
            trends = entity_data['weekly_trends']
            
            # 散户地址增长
            if trends.get('individual', 0) > 5:
                signals['bullish_signals'].append("散户参与度提升")
            elif trends.get('individual', 0) < -5:
                signals['bearish_signals'].append("散户参与度下降")
            
            # 交易所地址变化
            if trends.get('exchange', 0) > 10:
                signals['bearish_signals'].append("交易所地址快速增长（可能抛售压力）")
            elif trends.get('exchange', 0) < -5:
                signals['bullish_signals'].append("交易所地址减少（可能持有意愿增强）")
        
        # 分析财富集中度变化
        if balance_data:
            concentration = balance_data.get('wealth_concentration', '')
            if concentration in ["高度集中", "极度集中"]:
                signals['neutral_signals'].append("财富高度集中，注意大户动向")
        
        # 综合信号评分
        bullish_score = len(signals['bullish_signals'])
        bearish_score = len(signals['bearish_signals'])
        
        if bullish_score > bearish_score:
            overall_sentiment = "偏乐观"
        elif bearish_score > bullish_score:
            overall_sentiment = "偏悲观"
        else:
            overall_sentiment = "中性"
        
        return {
            'asset': asset,
            'overall_sentiment': overall_sentiment,
            'signals': signals,
            'confidence_level': self.calculate_confidence(signals)
        }
    
    def calculate_confidence(self, signals: Dict) -> str:
        """计算信号置信度"""
        
        total_signals = sum(len(signal_list) for signal_list in signals.values())
        
        if total_signals >= 5:
            return "高"
        elif total_signals >= 3:
            return "中"
        else:
            return "低"
    
    def generate_trading_recommendation(self, asset: str) -> Dict:
        """生成交易建议"""
        
        sentiment_analysis = self.assess_market_sentiment(asset)
        entity_data = self.analyzer.get_entity_address_distribution(asset)
        
        recommendation = {
            'action': 'hold',
            'confidence': 'medium',
            'reasoning': [],
            'risk_factors': [],
            'entry_conditions': [],
            'exit_conditions': []
        }
        
        sentiment = sentiment_analysis['overall_sentiment']
        
        if sentiment == "偏乐观":
            recommendation['action'] = 'buy'
            recommendation['reasoning'].append("市场情绪偏乐观，散户参与度上升")
            recommendation['entry_conditions'].append("确认突破关键阻力位")
            recommendation['exit_conditions'].append("散户参与度开始下降")
            
        elif sentiment == "偏悲观":
            recommendation['action'] = 'sell'
            recommendation['reasoning'].append("市场情绪偏悲观，可能面临抛售压力")
            recommendation['entry_conditions'].append("等待超卖反弹机会")
            recommendation['exit_conditions'].append("技术指标确认反转")
        
        # 添加风险因素
        if entity_data:
            market_structure = entity_data.get('analysis', {}).get('market_structure', '')
            if market_structure == "交易所主导":
                recommendation['risk_factors'].append("交易所主导市场，流动性风险较高")
        
        recommendation['confidence'] = sentiment_analysis['confidence_level']
        
        return recommendation

# 使用示例
strategy = BreakdownTradingStrategy(analyzer)

# 评估比特币市场情绪
btc_sentiment = strategy.assess_market_sentiment('BTC')
print("比特币市场情绪分析:")
print(f"整体情绪: {btc_sentiment['overall_sentiment']}")
print(f"置信度: {btc_sentiment['confidence_level']}")

# 生成交易建议
btc_recommendation = strategy.generate_trading_recommendation('BTC')
print(f"\n交易建议: {btc_recommendation['action']}")
print(f"理由: {', '.join(btc_recommendation['reasoning'])}")
```

### 2. 大户监控策略

```python
class WhaleMonitoringStrategy:
    """大户监控策略"""
    
    def __init__(self, analyzer: BreakdownsAnalyzer):
        self.analyzer = analyzer
        
    def monitor_whale_activity(self, asset: str) -> Dict:
        """监控大户活动"""
        
        balance_data = self.analyzer.get_balance_distribution(asset)
        
        if not balance_data:
            return {}
        
        # 分析大户比例变化
        distribution = balance_data.get('distribution', {})
        whale_percentage = distribution.get('whale', {}).get('percentage', 0)
        large_percentage = distribution.get('large', {}).get('percentage', 0)
        
        total_whale_control = whale_percentage + large_percentage
        
        whale_analysis = {
            'whale_control_percentage': total_whale_control,
            'concentration_level': self.assess_concentration_level(total_whale_control),
            'market_impact_risk': self.assess_market_impact_risk(total_whale_control),
            'monitoring_alerts': self.generate_whale_alerts(total_whale_control),
            'recommended_actions': self.recommend_whale_actions(total_whale_control)
        }
        
        return whale_analysis
    
    def assess_concentration_level(self, whale_control: float) -> str:
        """评估集中度水平"""
        
        if whale_control > 70:
            return "极高集中"
        elif whale_control > 50:
            return "高度集中"
        elif whale_control > 30:
            return "中等集中"
        else:
            return "相对分散"
    
    def assess_market_impact_risk(self, whale_control: float) -> str:
        """评估市场影响风险"""
        
        if whale_control > 60:
            return "极高风险"
        elif whale_control > 40:
            return "高风险"
        elif whale_control > 20:
            return "中等风险"
        else:
            return "低风险"
    
    def generate_whale_alerts(self, whale_control: float) -> List[str]:
        """生成大户警报"""
        
        alerts = []
        
        if whale_control > 70:
            alerts.append("⚠️ 极高大户集中度，市场极易受操纵")
            alerts.append("⚠️ 建议密切监控大额转账")
        elif whale_control > 50:
            alerts.append("🔶 高大户集中度，需关注大户动向")
        elif whale_control > 30:
            alerts.append("🟡 中等大户集中度，保持适度关注")
        
        return alerts
    
    def recommend_whale_actions(self, whale_control: float) -> List[str]:
        """推荐大户相关行动"""
        
        actions = []
        
        if whale_control > 60:
            actions.append("设置严格的止损策略")
            actions.append("减少仓位规模")
            actions.append("增加市场监控频率")
        elif whale_control > 40:
            actions.append("实施分批建仓策略")
            actions.append("关注链上大额转账数据")
        else:
            actions.append("可以采用正常的交易策略")
        
        return actions

# 使用示例
whale_monitor = WhaleMonitoringStrategy(analyzer)

# 监控比特币大户活动
btc_whale_analysis = whale_monitor.monitor_whale_activity('BTC')
print("比特币大户分析:")
print(f"大户控制比例: {btc_whale_analysis.get('whale_control_percentage', 0):.1f}%")
print(f"集中度水平: {btc_whale_analysis.get('concentration_level', 'N/A')}")
print(f"市场影响风险: {btc_whale_analysis.get('market_impact_risk', 'N/A')}")

if btc_whale_analysis.get('monitoring_alerts'):
    print("\n警报:")
    for alert in btc_whale_analysis['monitoring_alerts']:
        print(f"  {alert}")
```

## 常见问题

### Q1: 细分数据的更新频率如何？

细分数据的更新频率取决于具体的端点：
- 实体地址分布：每24小时更新
- 余额分布：每24小时更新
- 交易类型统计：每1小时更新

建议根据分析需求选择合适的查询间隔。

### Q2: 如何理解地址实体分类？

地址实体分类基于链上行为模式和已知信息：
- **Exchange（交易所）**: 已识别的交易所地址
- **Mining Pool（矿池）**: 挖矿相关地址
- **Service（服务商）**: DeFi协议、钱包服务等
- **Individual（个人）**: 个人用户地址
- **Unknown（未知）**: 无法分类的地址

### Q3: 基尼系数如何解读？

基尼系数反映财富分布的不平等程度：
- 0: 完全平等
- 0.3以下: 相对平等
- 0.3-0.5: 中等不平等
- 0.5-0.7: 高度不平等
- 0.7以上: 极度不平等

### Q4: 如何处理数据缺失？

当遇到数据缺失时：
1. 检查API参数是否正确
2. 验证时间范围是否合理
3. 考虑使用备选时间间隔
4. 实施数据插值或平滑处理

## 最佳实践

1. **多维度分析**: 结合实体分布、余额分布和交易类型进行综合分析
2. **趋势监控**: 关注长期趋势而非短期波动
3. **风险管理**: 基于集中度指标调整风险敞口
4. **实时警报**: 设置自动化监控系统，及时发现异常变化
5. **历史对比**: 与历史数据对比，识别结构性变化
6. **跨资产比较**: 对比不同资产的细分特征，发现投资机会

---

*本文档详细介绍了 Glassnode Breakdowns API 的使用方法，包括数据获取、分析技术和实际应用案例。细分数据是深入理解区块链生态系统结构和制定精准投资策略的重要工具。*