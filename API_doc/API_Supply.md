# Supply（供应分析）API 文档

## 概述

Supply API 提供关于加密货币供应量的详细数据，包括流通供应、流动性分析、长短期持有者分布、损失币估算等。这些指标对于理解市场供需动态和预测价格走势至关重要。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/supply/`

## 核心端点

### 1. 基础供应指标

#### 1.1 流通供应量

**端点**: `/current`

**描述**: 所有已创建/发行的币的总量，包括可能已永久丢失的币。

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/supply/current?a=BTC" \
  -H "X-Api-Key: YOUR_API_KEY"
```

**示例响应**:
```json
[
  {
    "t": 1614556800,
    "v": 18650000
  }
]
```

#### 1.2 发行量

**端点**: `/issued`

**描述**: 通过挖矿或其他机制新发行的币量。

```python
def analyze_supply_inflation(asset='BTC'):
    """分析供应通胀率"""
    
    base_url = "https://api.glassnode.com/v1/metrics/supply/"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '24h', 's': int(time.time()) - 365*86400}
    
    # 获取当前供应量
    current_supply = requests.get(
        base_url + "current",
        params={'a': asset},
        headers=headers
    ).json()[-1]['v']
    
    # 获取一年前供应量
    year_ago_supply = requests.get(
        base_url + "current",
        params={**params, 'u': int(time.time()) - 364*86400},
        headers=headers
    ).json()[-1]['v']
    
    # 计算年通胀率
    annual_inflation = (current_supply - year_ago_supply) / year_ago_supply * 100
    
    # 预测减半影响（BTC 特定）
    if asset == 'BTC':
        blocks_to_halving = calculate_blocks_to_halving()
        days_to_halving = blocks_to_halving * 10 / 60 / 24
        
        return {
            'current_supply': current_supply,
            'annual_inflation_rate': f"{annual_inflation:.2f}%",
            'daily_new_supply': (current_supply - year_ago_supply) / 365,
            'days_to_next_halving': int(days_to_halving),
            'post_halving_inflation': f"{annual_inflation/2:.2f}%"
        }
    
    return {
        'current_supply': current_supply,
        'annual_inflation_rate': f"{annual_inflation:.2f}%"
    }
```

### 2. 流动性分类

#### 2.1 流动供应量

**端点**: `/liquid_sum`

**描述**: 被归类为"流动"实体持有的总供应量。这些币经常移动，可能随时进入市场。

#### 2.2 非流动供应量

**端点**: `/illiquid_sum`

**描述**: 被归类为"非流动"实体持有的总供应量。这些币很少移动，代表长期持有。

#### 2.3 高流动性供应量

**端点**: `/highly_liquid_sum`

**描述**: 极高流动性实体（如交易所）持有的供应量。

**流动性分析系统**:
```python
class LiquidityAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/supply/"
        
    def analyze_supply_dynamics(self, asset='BTC'):
        """分析供应动态和流动性结构"""
        
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h', 's': int(time.time()) - 90*86400}
        
        # 获取不同流动性类别的供应量
        liquid = self.get_data("liquid_sum", params, headers)
        illiquid = self.get_data("illiquid_sum", params, headers)
        highly_liquid = self.get_data("highly_liquid_sum", params, headers)
        
        # 计算当前分布
        total = liquid[-1]['v'] + illiquid[-1]['v'] + highly_liquid[-1]['v']
        
        distribution = {
            'highly_liquid': {
                'amount': highly_liquid[-1]['v'],
                'percentage': highly_liquid[-1]['v'] / total * 100
            },
            'liquid': {
                'amount': liquid[-1]['v'],
                'percentage': liquid[-1]['v'] / total * 100
            },
            'illiquid': {
                'amount': illiquid[-1]['v'],
                'percentage': illiquid[-1]['v'] / total * 100
            }
        }
        
        # 分析趋势
        illiquid_change = (illiquid[-1]['v'] - illiquid[0]['v']) / illiquid[0]['v'] * 100
        
        # 计算供应挤压指数
        squeeze_index = self.calculate_supply_squeeze(distribution)
        
        return {
            'distribution': distribution,
            'illiquid_growth_90d': f"{illiquid_change:.2f}%",
            'supply_squeeze_index': squeeze_index,
            'market_liquidity': self.assess_market_liquidity(distribution),
            'price_impact': self.estimate_price_impact(squeeze_index)
        }
    
    def calculate_supply_squeeze(self, distribution):
        """计算供应挤压指数 (0-100)"""
        
        # 非流动供应占比越高，挤压越严重
        illiquid_ratio = distribution['illiquid']['percentage']
        
        # 考虑交易所供应（高流动性）
        exchange_ratio = distribution['highly_liquid']['percentage']
        
        # 挤压指数：非流动性高 + 交易所供应低 = 供应紧张
        squeeze = (illiquid_ratio * 0.7) + ((100 - exchange_ratio) * 0.3)
        
        return min(100, squeeze)
    
    def assess_market_liquidity(self, distribution):
        """评估市场流动性状况"""
        
        liquid_total = distribution['liquid']['percentage'] + distribution['highly_liquid']['percentage']
        
        if liquid_total > 60:
            return "高流动性 - 市场深度良好"
        elif liquid_total > 40:
            return "中等流动性 - 正常市场条件"
        elif liquid_total > 25:
            return "低流动性 - 价格易波动"
        else:
            return "极低流动性 - 高波动风险"
    
    def estimate_price_impact(self, squeeze_index):
        """估算供应挤压对价格的影响"""
        
        if squeeze_index > 80:
            return "极高影响 - 少量买压可能导致大幅上涨"
        elif squeeze_index > 60:
            return "高影响 - 价格对需求变化敏感"
        elif squeeze_index > 40:
            return "中等影响 - 正常价格弹性"
        else:
            return "低影响 - 充足供应缓冲价格波动"
```

### 3. 持有者时间分类

#### 3.1 长期持有者供应量

**端点**: `/lth_sum`

**描述**: 长期持有者（LTH，持币超过155天）持有的供应量。

#### 3.2 短期持有者供应量

**端点**: `/sth_sum`

**描述**: 短期持有者（STH，持币少于155天）持有的供应量。

**持有者行为分析**:
```python
def analyze_holder_behavior(asset='BTC'):
    """分析长短期持有者行为"""
    
    base_url = "https://api.glassnode.com/v1/metrics/supply/"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '24h', 's': int(time.time()) - 180*86400}
    
    # 获取 LTH 和 STH 数据
    lth_response = requests.get(base_url + "lth_sum", params=params, headers=headers)
    sth_response = requests.get(base_url + "sth_sum", params=params, headers=headers)
    
    lth_data = lth_response.json()
    sth_data = sth_response.json()
    
    # 分析趋势
    lth_current = lth_data[-1]['v']
    lth_30d_ago = lth_data[-30]['v'] if len(lth_data) > 30 else lth_data[0]['v']
    
    sth_current = sth_data[-1]['v']
    sth_30d_ago = sth_data[-30]['v'] if len(sth_data) > 30 else sth_data[0]['v']
    
    # 计算变化
    lth_change = (lth_current - lth_30d_ago) / lth_30d_ago * 100
    sth_change = (sth_current - sth_30d_ago) / sth_30d_ago * 100
    
    # 判断市场阶段
    if lth_change > 2 and sth_change < -2:
        phase = "积累期 - 短期持有者向长期持有者转换"
    elif lth_change < -2 and sth_change > 2:
        phase = "分配期 - 长期持有者获利了结"
    elif lth_change > 0 and sth_change > 0:
        phase = "扩张期 - 新资金进入市场"
    else:
        phase = "整理期 - 市场平衡状态"
    
    # 计算 LTH/STH 比率
    lth_sth_ratio = lth_current / sth_current if sth_current > 0 else 0
    
    return {
        'lth_supply': lth_current,
        'sth_supply': sth_current,
        'lth_change_30d': f"{lth_change:.2f}%",
        'sth_change_30d': f"{sth_change:.2f}%",
        'lth_sth_ratio': round(lth_sth_ratio, 2),
        'market_phase': phase,
        'holder_conviction': "强" if lth_sth_ratio > 3 else "中等" if lth_sth_ratio > 1.5 else "弱"
    }
```

### 4. 盈亏供应分析

#### 4.1 盈利供应量

**端点**: `/profit_sum`

**描述**: 处于盈利状态的币的总量（当前价格高于获取成本）。

#### 4.2 盈利供应百分比

**端点**: `/profit_relative`

**描述**: 盈利供应占总供应的百分比。

#### 4.3 亏损供应量

**端点**: `/loss_sum`

**描述**: 处于亏损状态的币的总量。

**盈亏分析系统**:
```python
class ProfitLossAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_supply_pl_distribution(self, asset='BTC'):
        """分析供应盈亏分布"""
        
        base_url = "https://api.glassnode.com/v1/metrics/supply/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h'}
        
        # 获取盈亏数据
        profit_sum = requests.get(
            base_url + "profit_sum", 
            params=params, 
            headers=headers
        ).json()[-1]['v']
        
        loss_sum = requests.get(
            base_url + "loss_sum", 
            params=params, 
            headers=headers
        ).json()[-1]['v']
        
        profit_relative = requests.get(
            base_url + "profit_relative", 
            params=params, 
            headers=headers
        ).json()[-1]['v']
        
        # 历史对比
        hist_params = {**params, 's': int(time.time()) - 365*86400}
        profit_history = requests.get(
            base_url + "profit_relative", 
            params=hist_params, 
            headers=headers
        ).json()
        
        # 计算百分位
        values = [d['v'] for d in profit_history]
        percentile = sum(1 for v in values if v < profit_relative) / len(values) * 100
        
        # 市场情绪判断
        if profit_relative > 95:
            sentiment = "极度贪婪 - 获利回吐风险高"
        elif profit_relative > 75:
            sentiment = "贪婪 - 注意风险"
        elif profit_relative > 50:
            sentiment = "中性偏乐观"
        elif profit_relative > 25:
            sentiment = "恐慌 - 潜在买入机会"
        else:
            sentiment = "极度恐慌 - 历史底部区域"
        
        return {
            'profit_supply': profit_sum,
            'loss_supply': loss_sum,
            'profit_percentage': f"{profit_relative:.2f}%",
            'historical_percentile': f"{percentile:.1f}%",
            'market_sentiment': sentiment,
            'risk_reward': self.calculate_risk_reward(profit_relative)
        }
    
    def calculate_risk_reward(self, profit_percentage):
        """计算风险回报比"""
        
        # 盈利供应越高，上涨空间越小，风险越大
        upside_potential = max(0, 100 - profit_percentage)
        downside_risk = profit_percentage
        
        if downside_risk > 0:
            risk_reward_ratio = upside_potential / downside_risk
        else:
            risk_reward_ratio = float('inf')
        
        if risk_reward_ratio > 2:
            assessment = "优秀的风险回报比"
        elif risk_reward_ratio > 1:
            assessment = "良好的风险回报比"
        elif risk_reward_ratio > 0.5:
            assessment = "一般的风险回报比"
        else:
            assessment = "较差的风险回报比"
        
        return {
            'ratio': round(risk_reward_ratio, 2),
            'assessment': assessment,
            'upside_potential': f"{upside_potential:.1f}%",
            'downside_risk': f"{downside_risk:.1f}%"
        }
```

### 5. 特殊供应指标

#### 5.1 可能丢失的供应

**端点**: `/probably_lost`

**描述**: 自首个比特币交易所上线以来从未移动的币，可能已永久丢失。

```python
def analyze_lost_supply(asset='BTC'):
    """分析可能丢失的供应"""
    
    url = "https://api.glassnode.com/v1/metrics/supply/probably_lost"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset}
    
    response = requests.get(url, params=params, headers=headers)
    lost_supply = response.json()[-1]['v']
    
    # 获取总供应量
    total_url = "https://api.glassnode.com/v1/metrics/supply/current"
    total_response = requests.get(total_url, params=params, headers=headers)
    total_supply = total_response.json()[-1]['v']
    
    # 计算有效供应量
    effective_supply = total_supply - lost_supply
    lost_percentage = lost_supply / total_supply * 100
    
    # 对价格的影响
    scarcity_premium = lost_percentage / 10  # 简化模型：每10%丢失增加1倍稀缺性溢价
    
    return {
        'total_supply': total_supply,
        'lost_supply': lost_supply,
        'effective_supply': effective_supply,
        'lost_percentage': f"{lost_percentage:.2f}%",
        'scarcity_premium_factor': round(1 + scarcity_premium, 2),
        'impact': "实际流通供应比名义供应少，增加稀缺性"
    }
```

#### 5.2 交易所供应量

**端点**: `/exchange_sum`

**描述**: 已知交易所地址持有的总供应量。

```python
def analyze_exchange_supply(asset='BTC'):
    """分析交易所供应量"""
    
    url = "https://api.glassnode.com/v1/metrics/supply/exchange_sum"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '24h', 's': int(time.time()) - 90*86400}
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    # 分析趋势
    current = data[-1]['v']
    day_30_ago = data[-30]['v'] if len(data) > 30 else data[0]['v']
    day_90_ago = data[0]['v']
    
    change_30d = (current - day_30_ago) / day_30_ago * 100
    change_90d = (current - day_90_ago) / day_90_ago * 100
    
    # 判断资金流向
    if change_30d < -5:
        flow = "大量流出交易所 - 看涨信号"
    elif change_30d < -2:
        flow = "温和流出交易所 - 偏看涨"
    elif change_30d > 5:
        flow = "大量流入交易所 - 看跌信号"
    elif change_30d > 2:
        flow = "温和流入交易所 - 偏看跌"
    else:
        flow = "相对平衡"
    
    return {
        'exchange_balance': current,
        'change_30d': f"{change_30d:.2f}%",
        'change_90d': f"{change_90d:.2f}%",
        'flow_direction': flow,
        'selling_pressure': "高" if change_30d > 5 else "中" if change_30d > 0 else "低"
    }
```

### 6. 供应年龄分布

```python
class SupplyAgeAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_hodl_waves(self, asset='BTC'):
        """分析 HODL 波浪（供应年龄分布）"""
        
        # 定义年龄区间
        age_bands = {
            '1d-1w': {'min': 1, 'max': 7, 'supply': 0},
            '1w-1m': {'min': 7, 'max': 30, 'supply': 0},
            '1m-3m': {'min': 30, 'max': 90, 'supply': 0},
            '3m-6m': {'min': 90, 'max': 180, 'supply': 0},
            '6m-1y': {'min': 180, 'max': 365, 'supply': 0},
            '1y-2y': {'min': 365, 'max': 730, 'supply': 0},
            '2y-3y': {'min': 730, 'max': 1095, 'supply': 0},
            '3y-5y': {'min': 1095, 'max': 1825, 'supply': 0},
            '5y+': {'min': 1825, 'max': float('inf'), 'supply': 0}
        }
        
        # 获取各年龄段的供应量（简化示例）
        # 实际需要更详细的 API 端点
        
        # 分析结果
        young_supply = sum(v['supply'] for k, v in age_bands.items() 
                          if v['max'] <= 180)
        old_supply = sum(v['supply'] for k, v in age_bands.items() 
                        if v['min'] >= 365)
        
        # 计算 HODL 比率
        hodl_ratio = old_supply / (young_supply + old_supply) if (young_supply + old_supply) > 0 else 0
        
        return {
            'age_distribution': age_bands,
            'young_supply_ratio': young_supply,
            'old_supply_ratio': old_supply,
            'hodl_strength': hodl_ratio,
            'market_maturity': self.assess_market_maturity(hodl_ratio)
        }
    
    def assess_market_maturity(self, hodl_ratio):
        """评估市场成熟度"""
        
        if hodl_ratio > 0.7:
            return "成熟市场 - 强劲的长期持有者基础"
        elif hodl_ratio > 0.5:
            return "发展中市场 - 平衡的持有者结构"
        elif hodl_ratio > 0.3:
            return "活跃市场 - 较多短期交易"
        else:
            return "投机市场 - 以短期交易为主"
```

### 7. 综合供应分析仪表板

```python
class SupplyDashboard:
    def __init__(self, api_key):
        self.api_key = api_key
        self.analyzers = {
            'liquidity': LiquidityAnalyzer(api_key),
            'profit_loss': ProfitLossAnalyzer(api_key),
            'age': SupplyAgeAnalyzer(api_key)
        }
        
    def generate_comprehensive_report(self, asset='BTC'):
        """生成综合供应分析报告"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'asset': asset,
            'summary': {},
            'liquidity': {},
            'holders': {},
            'profit_loss': {},
            'signals': []
        }
        
        # 流动性分析
        report['liquidity'] = self.analyzers['liquidity'].analyze_supply_dynamics(asset)
        
        # 持有者分析
        report['holders'] = analyze_holder_behavior(asset)
        
        # 盈亏分析
        report['profit_loss'] = self.analyzers['profit_loss'].analyze_supply_pl_distribution(asset)
        
        # 生成综合信号
        report['signals'] = self.generate_trading_signals(report)
        
        # 生成摘要
        report['summary'] = self.generate_summary(report)
        
        return report
    
    def generate_trading_signals(self, data):
        """基于供应数据生成交易信号"""
        
        signals = []
        
        # 供应挤压信号
        if data['liquidity']['supply_squeeze_index'] > 70:
            signals.append({
                'type': 'supply_squeeze',
                'action': 'BUY',
                'reason': '供应紧张，少量需求可能推高价格',
                'confidence': 'HIGH'
            })
        
        # 持有者行为信号
        if "积累期" in data['holders']['market_phase']:
            signals.append({
                'type': 'accumulation',
                'action': 'BUY',
                'reason': '短期持有者转为长期持有者',
                'confidence': 'MEDIUM'
            })
        
        # 盈亏信号
        if float(data['profit_loss']['profit_percentage'].strip('%')) < 30:
            signals.append({
                'type': 'capitulation',
                'action': 'BUY',
                'reason': '大量供应处于亏损，可能接近底部',
                'confidence': 'HIGH'
            })
        
        return signals
    
    def generate_summary(self, data):
        """生成执行摘要"""
        
        supply_score = 0
        
        # 计算综合评分
        if data['liquidity']['supply_squeeze_index'] > 60:
            supply_score += 30
        
        if data['holders']['holder_conviction'] == "强":
            supply_score += 25
        
        profit_pct = float(data['profit_loss']['profit_percentage'].strip('%'))
        if profit_pct < 50:
            supply_score += 25
        elif profit_pct > 80:
            supply_score -= 20
        
        # 市场状态判断
        if supply_score > 60:
            market_state = "看涨 - 供应面支持价格上涨"
        elif supply_score > 30:
            market_state = "中性 - 供需相对平衡"
        else:
            market_state = "看跌 - 供应压力较大"
        
        return {
            'supply_score': supply_score,
            'market_state': market_state,
            'key_insights': self.extract_key_insights(data)
        }
    
    def extract_key_insights(self, data):
        """提取关键洞察"""
        
        insights = []
        
        # 流动性洞察
        if data['liquidity']['supply_squeeze_index'] > 70:
            insights.append("供应严重紧缺，价格上涨潜力大")
        
        # 持有者洞察
        if data['holders']['lth_sth_ratio'] > 3:
            insights.append("长期持有者占主导，市场信心强")
        
        # 盈亏洞察
        profit_pct = float(data['profit_loss']['profit_percentage'].strip('%'))
        if profit_pct > 90:
            insights.append("警告：大部分供应处于盈利，获利回吐风险高")
        elif profit_pct < 40:
            insights.append("机会：大量供应处于亏损，可能接近底部")
        
        return insights
```

### 8. 供应预测模型

```python
def predict_supply_impact(asset='BTC', horizon_days=30):
    """预测供应变化对价格的影响"""
    
    # 获取历史数据
    supply_metrics = get_supply_metrics(asset, 365)
    price_data = get_price_data(asset, 365)
    
    # 构建特征
    features = {
        'illiquid_ratio': calculate_illiquid_ratio(supply_metrics),
        'exchange_flow': calculate_exchange_flow(supply_metrics),
        'lth_sth_ratio': calculate_lth_sth_ratio(supply_metrics),
        'profit_supply_ratio': calculate_profit_ratio(supply_metrics)
    }
    
    # 简化的影响模型
    price_impact = 0
    
    # 非流动供应影响
    if features['illiquid_ratio'] > 0.6:
        price_impact += 20  # 20% 上涨压力
    
    # 交易所流量影响
    if features['exchange_flow'] < -5:  # 流出
        price_impact += 15
    elif features['exchange_flow'] > 5:  # 流入
        price_impact -= 15
    
    # LTH/STH 比率影响
    if features['lth_sth_ratio'] > 3:
        price_impact += 10
    
    # 盈利供应影响
    if features['profit_supply_ratio'] > 0.9:
        price_impact -= 20  # 获利回吐压力
    elif features['profit_supply_ratio'] < 0.4:
        price_impact += 15  # 抛压减少
    
    return {
        'horizon': f"{horizon_days} days",
        'predicted_price_impact': f"{price_impact:+.1f}%",
        'confidence_level': calculate_confidence(features),
        'key_factors': identify_key_factors(features, price_impact)
    }
```

## 常见问题

### Q1: 流动性分类是如何定义的？

- **非流动**：很少移动的币，通常由长期持有者控制
- **流动**：定期移动但不频繁交易
- **高流动**：频繁交易，通常在交易所

### Q2: LTH 和 STH 的 155 天分界线是如何确定的？

基于历史数据分析，155 天是短期投机者和长期投资者行为模式的统计分界点。

### Q3: 为什么交易所供应量很重要？

交易所供应量直接影响市场流动性和潜在抛压：
- 流入增加 = 潜在卖压
- 流出增加 = 持有意愿强

## 最佳实践

1. **多维度分析**：结合流动性、持有者、盈亏等多个维度
2. **动态跟踪**：供应指标变化缓慢但意义重大，需要长期跟踪
3. **相对比较**：关注指标的相对变化而非绝对值
4. **周期考虑**：不同市场周期中同一指标的含义可能不同

---

*本文档详细介绍了 Glassnode Supply API 的使用方法。供应分析是理解市场供需关系和预测价格走势的基础。*