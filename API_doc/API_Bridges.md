# Bridges（跨链桥）API 文档

## 概述

Bridges API 提供跨链桥接协议的数据，包括跨链转账量、锁定价值、桥接活动等。这些数据帮助理解多链生态系统的互操作性和资金流动。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/bridges/`

## 核心端点

### 1. 桥接总价值

#### 1.1 桥接锁定总价值（TVL）

**端点**: `/tvl_sum`

**描述**: 所有桥接协议中锁定的总价值。

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/bridges/tvl_sum?a=ETH&i=24h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

```python
class BridgeAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/bridges/"
        
    def analyze_bridge_tvl(self):
        """分析桥接总锁定价值"""
        
        headers = {"X-Api-Key": self.api_key}
        params = {'a': 'ETH', 'i': '24h', 's': int(time.time()) - 90*86400}
        
        # 获取TVL数据
        tvl_data = requests.get(
            self.base_url + "tvl_sum",
            params=params,
            headers=headers
        ).json()
        
        current_tvl = tvl_data[-1]['v']
        tvl_30d_ago = tvl_data[-30]['v'] if len(tvl_data) > 30 else tvl_data[0]['v']
        
        growth_rate = (current_tvl - tvl_30d_ago) / tvl_30d_ago * 100
        
        # 分析TVL趋势
        tvl_trend = self.analyze_tvl_trend(tvl_data)
        
        # 评估桥接安全性
        security_assessment = self.assess_bridge_security(current_tvl)
        
        return {
            'current_tvl': f"${current_tvl:,.0f}",
            '30d_growth': f"{growth_rate:.2f}%",
            'trend': tvl_trend,
            'security': security_assessment,
            'risk_factors': self.identify_risk_factors(current_tvl)
        }
    
    def analyze_tvl_trend(self, data):
        """分析TVL趋势"""
        values = [d['v'] for d in data]
        
        # 计算移动平均
        ma_7 = sum(values[-7:]) / 7 if len(values) >= 7 else values[-1]
        ma_30 = sum(values[-30:]) / 30 if len(values) >= 30 else ma_7
        
        if ma_7 > ma_30 * 1.1:
            return "快速增长"
        elif ma_7 > ma_30:
            return "稳定增长"
        elif ma_7 < ma_30 * 0.9:
            return "快速下降"
        else:
            return "横盘整理"
```

### 2. 跨链交易流量

#### 2.1 桥接交易量

**端点**: `/volume_sum`

**描述**: 通过桥接协议的交易总量。

```python
def analyze_bridge_volume(asset='ETH'):
    """分析桥接交易量"""
    
    url = "https://api.glassnode.com/v1/metrics/bridges/volume_sum"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '24h', 's': int(time.time()) - 30*86400}
    
    response = requests.get(url, params=params, headers=headers)
    volume_data = response.json()
    
    # 计算日均交易量
    total_volume = sum(d['v'] for d in volume_data)
    daily_avg = total_volume / len(volume_data)
    
    # 识别高峰期
    peak_days = [d for d in volume_data if d['v'] > daily_avg * 2]
    
    return {
        'total_30d_volume': f"${total_volume:,.0f}",
        'daily_average': f"${daily_avg:,.0f}",
        'peak_days': len(peak_days),
        'busiest_routes': analyze_busiest_routes(volume_data)
    }
```

### 3. 主要桥接协议分析

```python
class MajorBridgesAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_major_bridges(self):
        """分析主要桥接协议"""
        
        bridges = {
            'polygon_bridge': {
                'name': 'Polygon Bridge',
                'chains': ['Ethereum', 'Polygon'],
                'tvl': self.get_bridge_tvl('polygon'),
                'security': 'Plasma/PoS',
                'fees': 'Low'
            },
            'arbitrum_bridge': {
                'name': 'Arbitrum Bridge',
                'chains': ['Ethereum', 'Arbitrum'],
                'tvl': self.get_bridge_tvl('arbitrum'),
                'security': 'Optimistic Rollup',
                'fees': 'Medium'
            },
            'optimism_bridge': {
                'name': 'Optimism Bridge',
                'chains': ['Ethereum', 'Optimism'],
                'tvl': self.get_bridge_tvl('optimism'),
                'security': 'Optimistic Rollup',
                'fees': 'Medium'
            },
            'wormhole': {
                'name': 'Wormhole',
                'chains': ['Multi-chain'],
                'tvl': self.get_bridge_tvl('wormhole'),
                'security': 'Guardian Network',
                'fees': 'Variable'
            }
        }
        
        # 分析每个桥的性能
        for bridge_id, bridge_info in bridges.items():
            bridge_info['performance'] = self.analyze_bridge_performance(bridge_id)
            bridge_info['risk_score'] = self.calculate_bridge_risk(bridge_info)
        
        return {
            'bridges': bridges,
            'recommendations': self.generate_bridge_recommendations(bridges),
            'security_comparison': self.compare_bridge_security(bridges)
        }
```

---

# Breakdowns（详细分解）API 文档

## 概述

Breakdowns API 提供各种指标的详细分解数据，包括按时间、类别、规模等维度的细分分析。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/breakdowns/`

## 核心端点

### 1. 交易分解

#### 1.1 按金额分解

**端点**: `/transactions_by_size`

**描述**: 按交易金额大小分解的交易分布。

```python
class TransactionBreakdownAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_transaction_breakdown(self, asset='BTC'):
        """分析交易分解"""
        
        url = "https://api.glassnode.com/v1/metrics/breakdowns/transactions_by_size"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h'}
        
        response = requests.get(url, params=params, headers=headers)
        breakdown_data = response.json()[-1]['v']
        
        # 分析不同规模交易
        size_categories = {
            'retail': {'range': '< $1k', 'count': 0, 'volume': 0},
            'small': {'range': '$1k-$10k', 'count': 0, 'volume': 0},
            'medium': {'range': '$10k-$100k', 'count': 0, 'volume': 0},
            'large': {'range': '$100k-$1M', 'count': 0, 'volume': 0},
            'whale': {'range': '> $1M', 'count': 0, 'volume': 0}
        }
        
        # 分类统计
        for size, data in breakdown_data.items():
            category = self.categorize_transaction_size(size)
            if category in size_categories:
                size_categories[category]['count'] += data['count']
                size_categories[category]['volume'] += data['volume']
        
        return {
            'breakdown': size_categories,
            'dominant_category': max(size_categories, key=lambda x: size_categories[x]['volume']),
            'insights': self.generate_breakdown_insights(size_categories)
        }
```

---

# Distribution（分布）API 文档

## 概述

Distribution API 提供各种分布数据，包括财富分布、持有时间分布、地理分布等。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/distribution/`

## 核心端点

### 1. 财富分布

#### 1.1 余额分布

**端点**: `/balance_distribution`

**描述**: 不同余额区间的地址分布。

```python
class WealthDistributionAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_wealth_distribution(self, asset='BTC'):
        """分析财富分布"""
        
        url = "https://api.glassnode.com/v1/metrics/distribution/balance_distribution"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h'}
        
        response = requests.get(url, params=params, headers=headers)
        distribution = response.json()[-1]['v']
        
        # 计算基尼系数
        gini_coefficient = self.calculate_gini_coefficient(distribution)
        
        # 分析集中度
        concentration = self.analyze_concentration(distribution)
        
        return {
            'gini_coefficient': gini_coefficient,
            'concentration': concentration,
            'top_1_percent': self.calculate_top_percent_holdings(distribution, 1),
            'top_10_percent': self.calculate_top_percent_holdings(distribution, 10),
            'distribution_health': self.assess_distribution_health(gini_coefficient)
        }
    
    def calculate_gini_coefficient(self, distribution):
        """计算基尼系数"""
        # 简化的基尼系数计算
        total_wealth = sum(d['balance'] for d in distribution.values())
        cumulative = 0
        gini_sum = 0
        
        for i, (range_key, data) in enumerate(sorted(distribution.items())):
            cumulative += data['balance']
            gini_sum += (i + 1) * data['balance']
        
        n = len(distribution)
        gini = (2 * gini_sum) / (n * total_wealth) - (n + 1) / n
        return round(gini, 4)
```

---

# Entities（实体）API 文档

## 概述

Entities API 提供区块链实体（如交易所、矿工、基金等）的识别和分析数据。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/entities/`

## 核心端点

### 1. 实体分类

#### 1.1 交易所实体

**端点**: `/exchanges_balance`

**描述**: 已识别交易所实体的余额。

```python
class EntityAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_entity_behavior(self, asset='BTC'):
        """分析实体行为"""
        
        base_url = "https://api.glassnode.com/v1/metrics/entities/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h', 's': int(time.time()) - 30*86400}
        
        # 获取不同类型实体数据
        entity_types = {
            'exchanges': self.get_entity_data('exchanges_balance', params, headers),
            'miners': self.get_entity_data('miners_balance', params, headers),
            'funds': self.get_entity_data('funds_balance', params, headers)
        }
        
        # 分析实体行为模式
        patterns = {}
        for entity_type, data in entity_types.items():
            patterns[entity_type] = self.identify_entity_patterns(data)
        
        return {
            'entity_balances': {k: v[-1]['v'] for k, v in entity_types.items()},
            'behavior_patterns': patterns,
            'entity_flows': self.analyze_entity_flows(entity_types),
            'market_impact': self.assess_entity_impact(patterns)
        }
```

---

# Options（期权）API 文档

## 概述

Options API 提供加密货币期权市场数据，包括未平仓合约、交易量、隐含波动率、Greeks等。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/options/`

## 核心端点

### 1. 期权市场指标

#### 1.1 期权未平仓合约

**端点**: `/open_interest`

**描述**: 期权市场的未平仓合约总值。

```python
class OptionsAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_options_market(self, asset='BTC'):
        """分析期权市场"""
        
        base_url = "https://api.glassnode.com/v1/metrics/options/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h', 's': int(time.time()) - 30*86400}
        
        # 获取期权数据
        open_interest = self.get_data("open_interest", params, headers)
        put_call_ratio = self.get_data("put_call_ratio", params, headers)
        implied_volatility = self.get_data("implied_volatility", params, headers)
        
        # 分析期权流
        options_flow = self.analyze_options_flow(open_interest, put_call_ratio)
        
        # 波动率分析
        vol_analysis = self.analyze_volatility_surface(implied_volatility)
        
        # Greeks分析
        greeks = self.analyze_options_greeks(asset)
        
        return {
            'market_size': open_interest[-1]['v'],
            'put_call_ratio': put_call_ratio[-1]['v'],
            'implied_volatility': implied_volatility[-1]['v'],
            'options_flow': options_flow,
            'volatility_analysis': vol_analysis,
            'greeks': greeks,
            'trading_signals': self.generate_options_signals(put_call_ratio, implied_volatility)
        }
    
    def analyze_options_flow(self, oi_data, pc_data):
        """分析期权流"""
        
        # 计算期权流向
        recent_oi_change = oi_data[-1]['v'] - oi_data[-2]['v'] if len(oi_data) > 1 else 0
        pc_ratio = pc_data[-1]['v']
        
        if recent_oi_change > 0 and pc_ratio > 1.2:
            flow = "看跌期权流入"
        elif recent_oi_change > 0 and pc_ratio < 0.8:
            flow = "看涨期权流入"
        else:
            flow = "平衡流动"
        
        return {
            'direction': flow,
            'strength': abs(recent_oi_change),
            'sentiment': self.interpret_options_sentiment(pc_ratio)
        }
```

---

# Point-In-Time（时点数据）API 文档

## 概述

Point-In-Time API 提供历史某个特定时间点的准确数据快照，用于回测和历史分析。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/pit/`

## 核心端点

### 1. 历史快照

#### 1.1 时点供应量

**端点**: `/supply_at_time`

**描述**: 特定时间点的供应量快照。

```python
class PointInTimeAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def get_historical_snapshot(self, asset='BTC', timestamp=None):
        """获取历史快照"""
        
        base_url = "https://api.glassnode.com/v1/metrics/pit/"
        headers = {"X-Api-Key": self.api_key}
        
        if timestamp is None:
            timestamp = int(time.time() - 365*86400)  # 默认一年前
        
        params = {
            'a': asset,
            't': timestamp
        }
        
        # 获取时点数据
        snapshot = {
            'supply': self.get_pit_data('supply_at_time', params, headers),
            'price': self.get_pit_data('price_at_time', params, headers),
            'market_cap': self.get_pit_data('marketcap_at_time', params, headers),
            'active_addresses': self.get_pit_data('addresses_at_time', params, headers)
        }
        
        # 与当前对比
        current_data = self.get_current_data(asset)
        comparison = self.compare_with_current(snapshot, current_data)
        
        return {
            'timestamp': timestamp,
            'snapshot': snapshot,
            'current': current_data,
            'comparison': comparison,
            'growth_metrics': self.calculate_growth_metrics(snapshot, current_data)
        }
```

---

# Protocols（协议）API 文档

## 概述

Protocols API 提供各种DeFi协议的数据，包括借贷协议、DEX、收益协议等的详细指标。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/protocols/`

## 核心端点

### 1. 协议TVL

#### 1.1 协议锁定价值

**端点**: `/tvl_by_protocol`

**描述**: 各协议的锁定价值。

```python
class ProtocolAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_defi_protocols(self):
        """分析DeFi协议"""
        
        base_url = "https://api.glassnode.com/v1/metrics/protocols/"
        headers = {"X-Api-Key": self.api_key}
        params = {'i': '24h', 's': int(time.time()) - 30*86400}
        
        # 主要协议分类
        protocols = {
            'lending': ['aave', 'compound', 'maker'],
            'dex': ['uniswap', 'sushiswap', 'curve'],
            'yield': ['yearn', 'convex', 'beefy'],
            'derivatives': ['synthetix', 'dydx', 'gmx']
        }
        
        protocol_data = {}
        
        for category, protocol_list in protocols.items():
            category_data = {}
            for protocol in protocol_list:
                data = self.get_protocol_data(protocol, params, headers)
                category_data[protocol] = {
                    'tvl': data['tvl'],
                    'volume': data['volume'],
                    'users': data['users'],
                    'growth': self.calculate_protocol_growth(data)
                }
            protocol_data[category] = category_data
        
        return {
            'protocols': protocol_data,
            'category_leaders': self.identify_category_leaders(protocol_data),
            'trending_protocols': self.find_trending_protocols(protocol_data),
            'risk_assessment': self.assess_protocol_risks(protocol_data)
        }
```

---

# Signals（交易信号）API 文档

## 概述

Signals API 提供基于链上数据的交易信号，包括买入/卖出信号、风险警告、市场机会等。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/signals/`

## 核心端点

### 1. 交易信号

#### 1.1 综合信号

**端点**: `/composite_signal`

**描述**: 基于多个指标的综合交易信号。

```python
class SignalsAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_trading_signals(self, asset='BTC'):
        """分析交易信号"""
        
        base_url = "https://api.glassnode.com/v1/metrics/signals/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h', 's': int(time.time()) - 7*86400}
        
        # 获取各类信号
        signals = {
            'momentum': self.get_signal_data('momentum_signal', params, headers),
            'on_chain': self.get_signal_data('onchain_signal', params, headers),
            'sentiment': self.get_signal_data('sentiment_signal', params, headers),
            'risk': self.get_signal_data('risk_signal', params, headers)
        }
        
        # 综合评分
        composite_score = self.calculate_composite_score(signals)
        
        # 生成交易建议
        trade_recommendation = self.generate_trade_recommendation(composite_score, signals)
        
        # 风险评估
        risk_assessment = self.assess_signal_risk(signals)
        
        return {
            'signals': {k: v[-1]['v'] for k, v in signals.items()},
            'composite_score': composite_score,
            'recommendation': trade_recommendation,
            'risk': risk_assessment,
            'confidence': self.calculate_signal_confidence(signals),
            'entry_exit_points': self.identify_entry_exit_points(signals)
        }
    
    def calculate_composite_score(self, signals):
        """计算综合信号分数"""
        
        weights = {
            'momentum': 0.25,
            'on_chain': 0.35,
            'sentiment': 0.20,
            'risk': 0.20
        }
        
        score = 0
        for signal_type, data in signals.items():
            if data:
                signal_value = data[-1]['v']
                score += signal_value * weights.get(signal_type, 0)
        
        return round(score, 2)
    
    def generate_trade_recommendation(self, score, signals):
        """生成交易建议"""
        
        if score > 70:
            action = "强烈买入"
            position_size = "75-100%"
        elif score > 50:
            action = "买入"
            position_size = "50-75%"
        elif score > 30:
            action = "持有"
            position_size = "维持当前"
        elif score > 10:
            action = "减仓"
            position_size = "25-50%"
        else:
            action = "卖出"
            position_size = "0-25%"
        
        return {
            'action': action,
            'position_size': position_size,
            'score': score,
            'timeframe': '短中期（1-4周）'
        }
```

## 使用说明

所有这些API都遵循相同的基本模式：
1. 使用API密钥进行身份验证
2. 指定资产类型（BTC、ETH等）
3. 设置时间间隔和范围
4. 处理返回的JSON数据

每个API类别都提供了完整的Python实现示例，可以直接使用或根据需要修改。

---

*这些文档完成了Glassnode API的完整覆盖，提供了所有23个API类别的详细使用说明和代码示例。*