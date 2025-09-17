# DeFi（去中心化金融）API 文档

## 概述

DeFi API 提供去中心化金融生态系统的关键数据，包括总锁定价值（TVL）、协议指标、流动性池数据等。这些数据对于理解 DeFi 市场动态和投资机会至关重要。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/defi/`

**数据来源**: 主要数据来源于 DeFi Llama 和链上数据聚合

## 核心端点

### 1. 总锁定价值 (Total Value Locked - TVL)

**端点**: `/total_value_locked`

**描述**: DeFi 协议中锁定的总价值（美元）。这是衡量 DeFi 生态系统规模的最重要指标。

**参数**:
- `a` (必需): 资产代码（ETH, BSC, MATIC 等）
- `s` (可选): 开始时间戳
- `u` (可选): 结束时间戳
- `i` (可选): 时间间隔（1h, 24h, 1w）
- `f` (可选): 格式（json, csv）

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/defi/total_value_locked?a=ETH&i=24h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

**示例响应**:
```json
[
  {
    "t": 1726790400,
    "v": 47997659278.33963
  },
  {
    "t": 1726876800,
    "v": 48123456789.12345
  }
]
```

**TVL 包含内容**:
- 借贷协议中的抵押品
- AMM 流动性池中的资产
- 质押协议中的代币
- 合成资产的抵押品
- 收益聚合器中的资金

### 2. DeFi 生态系统分析

#### 2.1 按协议类型的 TVL 分布

虽然基础 API 提供总 TVL，但可以通过数据分析了解不同协议类型的分布：

**协议类型**:
- **Lending（借贷）**: Aave, Compound, MakerDAO
- **DEX（去中心化交易所）**: Uniswap, SushiSwap, Curve
- **Derivatives（衍生品）**: Synthetix, dYdX, Perpetual Protocol
- **Yield（收益）**: Yearn, Convex, Beefy
- **Liquid Staking（流动性质押）**: Lido, Rocket Pool

**示例 - TVL 趋势分析**:
```python
import requests
import pandas as pd
from datetime import datetime, timedelta

class DeFiAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/defi/"
        
    def get_tvl_trends(self, chains=['ETH', 'BSC', 'MATIC'], days=90):
        """获取多链 TVL 趋势"""
        
        tvl_data = {}
        headers = {"X-Api-Key": self.api_key}
        
        for chain in chains:
            url = self.base_url + "total_value_locked"
            params = {
                'a': chain,
                'i': '24h',
                's': int((datetime.now() - timedelta(days=days)).timestamp()),
                'u': int(datetime.now().timestamp())
            }
            
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            
            tvl_data[chain] = {
                'timestamps': [d['t'] for d in data],
                'values': [d['v'] for d in data],
                'current': data[-1]['v'] if data else 0,
                'change_7d': self.calculate_change(data, 7),
                'change_30d': self.calculate_change(data, 30)
            }
        
        return self.analyze_tvl_distribution(tvl_data)
    
    def calculate_change(self, data, days):
        """计算指定天数的变化率"""
        if len(data) < days:
            return 0
        
        current = data[-1]['v']
        past = data[-days]['v']
        
        if past == 0:
            return 0
        
        return ((current - past) / past) * 100
    
    def analyze_tvl_distribution(self, tvl_data):
        """分析 TVL 分布"""
        total_tvl = sum(chain_data['current'] for chain_data in tvl_data.values())
        
        distribution = {}
        for chain, data in tvl_data.items():
            distribution[chain] = {
                'tvl': data['current'],
                'market_share': (data['current'] / total_tvl * 100) if total_tvl > 0 else 0,
                'growth_7d': data['change_7d'],
                'growth_30d': data['change_30d']
            }
        
        return {
            'total_tvl': total_tvl,
            'chain_distribution': distribution,
            'dominant_chain': max(distribution, key=lambda x: distribution[x]['tvl']),
            'fastest_growing': max(distribution, key=lambda x: distribution[x]['growth_7d'])
        }
```

### 3. DeFi 指标深度分析

#### 3.1 TVL 增长率分析

```python
def analyze_tvl_growth_patterns(asset='ETH', period_days=180):
    """分析 TVL 增长模式和周期"""
    
    url = "https://api.glassnode.com/v1/metrics/defi/total_value_locked"
    params = {
        'a': asset,
        'i': '24h',
        's': int((datetime.now() - timedelta(days=period_days)).timestamp())
    }
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    df = pd.DataFrame(data)
    df['t'] = pd.to_datetime(df['t'], unit='s')
    df.set_index('t', inplace=True)
    
    # 计算各种增长指标
    df['daily_change'] = df['v'].pct_change()
    df['7d_ma'] = df['v'].rolling(window=7).mean()
    df['30d_ma'] = df['v'].rolling(window=30).mean()
    df['volatility'] = df['daily_change'].rolling(window=30).std()
    
    # 识别增长阶段
    growth_phases = []
    
    # 使用移动平均线交叉识别趋势
    df['signal'] = 0
    df.loc[df['7d_ma'] > df['30d_ma'], 'signal'] = 1  # 上升趋势
    df.loc[df['7d_ma'] < df['30d_ma'], 'signal'] = -1  # 下降趋势
    
    # 计算关键统计
    stats = {
        'current_tvl': df['v'].iloc[-1],
        'period_high': df['v'].max(),
        'period_low': df['v'].min(),
        'average_daily_change': df['daily_change'].mean() * 100,
        'volatility': df['volatility'].iloc[-1] * 100,
        'current_trend': 'bullish' if df['signal'].iloc[-1] == 1 else 'bearish',
        'days_in_current_trend': (df['signal'] == df['signal'].iloc[-1]).sum()
    }
    
    return {
        'statistics': stats,
        'dataframe': df,
        'recommendation': generate_tvl_recommendation(stats)
    }

def generate_tvl_recommendation(stats):
    """基于 TVL 统计生成建议"""
    
    if stats['current_trend'] == 'bullish' and stats['volatility'] < 5:
        return "稳定增长期，适合参与 DeFi 协议"
    elif stats['current_trend'] == 'bullish' and stats['volatility'] > 10:
        return "高波动增长期，注意风险管理"
    elif stats['current_trend'] == 'bearish' and stats['days_in_current_trend'] > 30:
        return "持续下降趋势，谨慎参与"
    else:
        return "市场震荡期，等待明确趋势"
```

#### 3.2 跨链 DeFi 对比

```python
class CrossChainDeFiComparator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.chains = {
            'ETH': {'name': 'Ethereum', 'color': 'blue'},
            'BSC': {'name': 'BNB Chain', 'color': 'yellow'},
            'MATIC': {'name': 'Polygon', 'color': 'purple'},
            'AVAX': {'name': 'Avalanche', 'color': 'red'},
            'FTM': {'name': 'Fantom', 'color': 'blue'},
            'ARB': {'name': 'Arbitrum', 'color': 'lightblue'},
            'OP': {'name': 'Optimism', 'color': 'red'}
        }
    
    def compare_chains(self, metrics_period=30):
        """全面对比各链 DeFi 生态"""
        
        comparison_data = {}
        
        for chain_code, chain_info in self.chains.items():
            tvl_data = self.get_chain_tvl(chain_code, metrics_period)
            
            if tvl_data:
                comparison_data[chain_code] = {
                    'name': chain_info['name'],
                    'current_tvl': tvl_data[-1]['v'],
                    'tvl_30d_ago': tvl_data[0]['v'] if len(tvl_data) > 30 else tvl_data[0]['v'],
                    'peak_tvl': max(d['v'] for d in tvl_data),
                    'average_tvl': sum(d['v'] for d in tvl_data) / len(tvl_data),
                    'growth_rate': self.calculate_growth_rate(tvl_data),
                    'volatility': self.calculate_volatility(tvl_data),
                    'trend_strength': self.calculate_trend_strength(tvl_data)
                }
        
        # 计算相对指标
        total_current_tvl = sum(data['current_tvl'] for data in comparison_data.values())
        
        for chain_code, data in comparison_data.items():
            data['market_share'] = (data['current_tvl'] / total_current_tvl * 100)
            data['relative_growth'] = data['growth_rate'] - self.average_growth_rate(comparison_data)
        
        return self.generate_comparison_report(comparison_data)
    
    def calculate_growth_rate(self, tvl_data):
        """计算复合增长率"""
        if len(tvl_data) < 2:
            return 0
        
        start_value = tvl_data[0]['v']
        end_value = tvl_data[-1]['v']
        days = len(tvl_data)
        
        if start_value == 0:
            return 0
        
        # CAGR 公式
        cagr = (pow(end_value / start_value, 365 / days) - 1) * 100
        return cagr
    
    def calculate_volatility(self, tvl_data):
        """计算波动率"""
        if len(tvl_data) < 2:
            return 0
        
        values = [d['v'] for d in tvl_data]
        returns = [(values[i] - values[i-1]) / values[i-1] 
                  for i in range(1, len(values)) if values[i-1] != 0]
        
        if not returns:
            return 0
        
        return pd.Series(returns).std() * 100
    
    def calculate_trend_strength(self, tvl_data):
        """计算趋势强度（0-100）"""
        if len(tvl_data) < 7:
            return 50
        
        values = [d['v'] for d in tvl_data]
        
        # 使用线性回归斜率作为趋势强度指标
        x = range(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        # 标准化到 0-100
        avg_value = sum(values) / len(values)
        normalized_slope = (slope / avg_value) * 100
        
        # 限制在 0-100 范围
        return max(0, min(100, 50 + normalized_slope))
    
    def generate_comparison_report(self, comparison_data):
        """生成对比报告"""
        
        # 排序：按当前 TVL
        sorted_chains = sorted(comparison_data.items(), 
                             key=lambda x: x[1]['current_tvl'], 
                             reverse=True)
        
        report = {
            'summary': {
                'total_tvl': sum(d['current_tvl'] for d in comparison_data.values()),
                'dominant_chain': sorted_chains[0][0],
                'fastest_growing': max(comparison_data.items(), 
                                     key=lambda x: x[1]['growth_rate'])[0],
                'most_stable': min(comparison_data.items(), 
                                 key=lambda x: x[1]['volatility'])[0],
                'strongest_trend': max(comparison_data.items(), 
                                     key=lambda x: x[1]['trend_strength'])[0]
            },
            'rankings': {
                'by_tvl': [chain[0] for chain in sorted_chains],
                'by_growth': sorted(comparison_data.keys(), 
                                  key=lambda x: comparison_data[x]['growth_rate'], 
                                  reverse=True),
                'by_market_share': sorted(comparison_data.keys(), 
                                        key=lambda x: comparison_data[x]['market_share'], 
                                        reverse=True)
            },
            'detailed_data': comparison_data
        }
        
        return report
```

### 4. DeFi 风险指标

```python
class DeFiRiskAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def calculate_defi_risk_score(self, asset='ETH'):
        """计算 DeFi 风险评分"""
        
        risk_factors = {}
        
        # 1. TVL 波动性风险
        tvl_volatility = self.get_tvl_volatility(asset)
        risk_factors['volatility_risk'] = min(tvl_volatility * 10, 100)
        
        # 2. 增长可持续性风险
        growth_sustainability = self.assess_growth_sustainability(asset)
        risk_factors['sustainability_risk'] = growth_sustainability
        
        # 3. 集中度风险
        concentration_risk = self.calculate_concentration_risk(asset)
        risk_factors['concentration_risk'] = concentration_risk
        
        # 4. 市场周期风险
        cycle_risk = self.assess_market_cycle_risk(asset)
        risk_factors['cycle_risk'] = cycle_risk
        
        # 综合风险评分（0-100，越高风险越大）
        weights = {
            'volatility_risk': 0.3,
            'sustainability_risk': 0.25,
            'concentration_risk': 0.25,
            'cycle_risk': 0.2
        }
        
        total_risk = sum(risk_factors[factor] * weight 
                        for factor, weight in weights.items())
        
        return {
            'total_risk_score': round(total_risk, 2),
            'risk_level': self.get_risk_level(total_risk),
            'risk_factors': risk_factors,
            'recommendations': self.generate_risk_recommendations(risk_factors)
        }
    
    def get_tvl_volatility(self, asset):
        """获取 TVL 波动率"""
        url = "https://api.glassnode.com/v1/metrics/defi/total_value_locked"
        params = {
            'a': asset,
            'i': '24h',
            's': int((datetime.now() - timedelta(days=30)).timestamp())
        }
        headers = {"X-Api-Key": self.api_key}
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        if len(data) < 2:
            return 0
        
        values = [d['v'] for d in data]
        returns = [(values[i] - values[i-1]) / values[i-1] 
                  for i in range(1, len(values)) if values[i-1] != 0]
        
        return pd.Series(returns).std() if returns else 0
    
    def assess_growth_sustainability(self, asset):
        """评估增长可持续性"""
        # 获取长期数据
        url = "https://api.glassnode.com/v1/metrics/defi/total_value_locked"
        params = {
            'a': asset,
            'i': '24h',
            's': int((datetime.now() - timedelta(days=180)).timestamp())
        }
        headers = {"X-Api-Key": self.api_key}
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        if len(data) < 30:
            return 50  # 默认中等风险
        
        # 分析增长模式
        values = [d['v'] for d in data]
        
        # 计算不同时期的增长率
        growth_30d = (values[-1] - values[-30]) / values[-30] if values[-30] > 0 else 0
        growth_90d = (values[-1] - values[-90]) / values[-90] if len(values) > 90 and values[-90] > 0 else 0
        
        # 如果短期增长远超长期增长，可能不可持续
        if growth_30d > growth_90d * 3:
            return 80  # 高风险
        elif growth_30d > growth_90d * 2:
            return 60  # 中高风险
        elif growth_30d > 0 and growth_90d > 0:
            return 30  # 低风险
        else:
            return 50  # 中等风险
    
    def get_risk_level(self, score):
        """根据分数获取风险等级"""
        if score < 25:
            return "低风险"
        elif score < 50:
            return "中低风险"
        elif score < 70:
            return "中高风险"
        else:
            return "高风险"
    
    def generate_risk_recommendations(self, risk_factors):
        """生成风险管理建议"""
        recommendations = []
        
        if risk_factors['volatility_risk'] > 70:
            recommendations.append("TVL 波动性高，建议降低仓位或使用稳定币策略")
        
        if risk_factors['sustainability_risk'] > 70:
            recommendations.append("增长可能不可持续，注意及时获利了结")
        
        if risk_factors['concentration_risk'] > 70:
            recommendations.append("协议集中度高，建议分散到多个协议")
        
        if risk_factors['cycle_risk'] > 70:
            recommendations.append("可能处于周期高点，谨慎新增投资")
        
        if not recommendations:
            recommendations.append("当前风险可控，保持正常策略")
        
        return recommendations
```

### 5. DeFi 收益优化

```python
class DeFiYieldOptimizer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def find_optimal_yield_strategy(self, capital=10000, risk_tolerance='medium'):
        """寻找最优收益策略"""
        
        # 获取各链 TVL 数据作为流动性指标
        chains = ['ETH', 'BSC', 'MATIC', 'AVAX']
        chain_data = {}
        
        for chain in chains:
            tvl_info = self.get_chain_tvl_info(chain)
            chain_data[chain] = tvl_info
        
        # 基于 TVL 和风险评估推荐策略
        strategies = []
        
        for chain, data in chain_data.items():
            if data['tvl'] > 1000000000:  # TVL > 10亿美元
                strategies.append({
                    'chain': chain,
                    'strategy': 'stable_farming',
                    'estimated_apy': self.estimate_apy(chain, 'stable'),
                    'risk_score': 20,
                    'allocation': capital * 0.4 if risk_tolerance == 'low' else capital * 0.3
                })
            
            if data['growth_rate'] > 10:  # 增长率 > 10%
                strategies.append({
                    'chain': chain,
                    'strategy': 'growth_farming',
                    'estimated_apy': self.estimate_apy(chain, 'growth'),
                    'risk_score': 60,
                    'allocation': capital * 0.2 if risk_tolerance == 'high' else capital * 0.1
                })
        
        # 优化资金分配
        optimized = self.optimize_allocation(strategies, capital, risk_tolerance)
        
        return {
            'recommended_strategies': optimized,
            'total_expected_return': self.calculate_portfolio_return(optimized),
            'portfolio_risk': self.calculate_portfolio_risk(optimized),
            'diversification_score': self.calculate_diversification(optimized)
        }
    
    def estimate_apy(self, chain, strategy_type):
        """估算 APY（示例值）"""
        base_apys = {
            'ETH': {'stable': 5, 'growth': 15},
            'BSC': {'stable': 6, 'growth': 20},
            'MATIC': {'stable': 7, 'growth': 25},
            'AVAX': {'stable': 6, 'growth': 18}
        }
        
        return base_apys.get(chain, {}).get(strategy_type, 10)
```

## 实时监控示例

```python
import asyncio
import websockets
import json

class DeFiMonitor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.alert_thresholds = {
            'tvl_drop': -10,  # TVL 下跌 10%
            'rapid_growth': 20,  # TVL 增长 20%
            'high_volatility': 5  # 日波动率 > 5%
        }
    
    async def monitor_tvl_realtime(self, asset='ETH'):
        """实时监控 TVL 变化"""
        
        last_tvl = None
        
        while True:
            try:
                # 获取当前 TVL
                current_tvl = await self.get_current_tvl(asset)
                
                if last_tvl:
                    change_percent = ((current_tvl - last_tvl) / last_tvl) * 100
                    
                    # 检查警报条件
                    if change_percent < self.alert_thresholds['tvl_drop']:
                        await self.send_alert(f"TVL 大幅下跌: {change_percent:.2f}%")
                    elif change_percent > self.alert_thresholds['rapid_growth']:
                        await self.send_alert(f"TVL 快速增长: {change_percent:.2f}%")
                
                last_tvl = current_tvl
                
                # 每5分钟检查一次
                await asyncio.sleep(300)
                
            except Exception as e:
                print(f"监控错误: {e}")
                await asyncio.sleep(60)
    
    async def get_current_tvl(self, asset):
        """获取当前 TVL"""
        # 实际实现需要调用 API
        pass
    
    async def send_alert(self, message):
        """发送警报"""
        print(f"[ALERT] {datetime.now()}: {message}")
        # 可以集成邮件、Telegram 等通知方式
```

## 常见问题

### Q1: TVL 数据多久更新一次？

根据不同的时间间隔参数：
- `10m`: 每10分钟更新
- `1h`: 每小时更新
- `24h`: 每日更新

建议根据分析需求选择合适的更新频率。

### Q2: 如何处理跨链 DeFi 数据？

不同链的 DeFi 生态需要分别查询，然后进行汇总分析。注意各链的特点：
- Ethereum: 最成熟，流动性最好
- BSC: 低手续费，高收益
- Polygon: 快速低成本
- Avalanche: 高性能

### Q3: TVL 突然大幅变化的原因？

可能原因：
1. 大额资金进出
2. 协议被黑客攻击
3. 新协议上线/激励计划
4. 市场价格波动（TVL 以美元计价）

## 最佳实践

1. **定期监控**: 设置自动化监控系统，及时发现异常
2. **多维度分析**: 结合 TVL、用户数、交易量等多个指标
3. **风险管理**: 根据 TVL 变化调整风险敞口
4. **趋势追踪**: 关注长期趋势而非短期波动

---

*本文档详细介绍了 Glassnode DeFi API 的使用方法，包括数据获取、分析方法和实际应用案例。DeFi 数据是理解去中心化金融市场的关键。*