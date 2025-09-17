# Addresses（地址分析）API 文档

## 概述

Addresses API 提供了关于区块链地址的全面分析数据，包括地址活跃度、余额分布、盈亏状况等关键指标。这些数据对于理解网络使用情况和用户行为至关重要。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/addresses/`

## 端点列表

### 1. 累积地址数 (Accumulation Addresses)

**端点**: `/accumulation_count`

**描述**: 统计独特的累积地址数量，排除交易所和矿工地址。累积地址是指持续增加余额而很少或从不减少的地址。

**参数**:
- `a` (必需): 资产代码（如 BTC, ETH）
- `s` (可选): 开始时间戳
- `u` (可选): 结束时间戳
- `i` (可选): 时间间隔（24h, 1w, 1month）

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/addresses/accumulation_count?a=BTC&i=24h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

**示例响应**:
```json
[
  {
    "t": 1614556800,
    "v": 12345
  }
]
```

### 2. 活跃地址数 (Active Addresses)

**端点**: `/active_count`

**描述**: 在指定时间段内作为发送方或接收方活跃的唯一地址数量。这是衡量网络活动的重要指标。

**用途**: 
- 评估网络使用率
- 识别用户活动趋势
- 对比不同时期的网络活跃度

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/addresses/active_count?a=ETH&i=1h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

### 3. 地址供应分布 (Supply Distribution)

**端点**: `/supply_distribution_relative`

**描述**: 显示流通供应量在不同余额区间的相对分布。帮助了解财富集中度。

**余额区间**:
- < 0.001 币
- 0.001 - 0.01 币
- 0.01 - 0.1 币
- 0.1 - 1 币
- 1 - 10 币
- 10 - 100 币
- 100 - 1k 币
- 1k - 10k 币
- > 10k 币

**示例用法**:
```python
# Python 示例
import requests

url = "https://api.glassnode.com/v1/metrics/addresses/supply_distribution_relative"
params = {
    "a": "BTC",
    "i": "24h"
}
headers = {
    "X-Api-Key": "YOUR_API_KEY"
}

response = requests.get(url, params=params, headers=headers)
data = response.json()
```

### 4. 盈利地址数 (Addresses in Profit)

**端点**: `/profit_count`

**描述**: 统计平均买入价格低于当前价格的地址数量，表明这些地址处于盈利状态。

**计算方法**:
1. 计算每个地址的平均买入成本
2. 与当前市场价格比较
3. 统计盈利地址总数

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/addresses/profit_count?a=BTC" \
  -H "X-Api-Key: YOUR_API_KEY"
```

### 5. 亏损地址数 (Addresses in Loss)

**端点**: `/loss_count`

**描述**: 统计平均买入价格高于当前价格的地址数量。

**应用场景**:
- 市场情绪分析
- 支撑/阻力位识别
- 投资者行为研究

### 6. 余额阈值地址统计

#### 6.1 余额 ≥ $1 USD 的地址

**端点**: `/min_1_usd_count`

**描述**: 持有价值至少 1 美元的地址数量。

#### 6.2 余额 ≥ 0.001 币的地址

**端点**: `/min_point_001_count`

**描述**: 持有至少 0.001 个币的地址数量。

#### 6.3 余额 ≥ 0.01 币的地址

**端点**: `/min_point_01_count`

#### 6.4 余额 ≥ 0.1 币的地址

**端点**: `/min_point_1_count`

#### 6.5 余额 ≥ 1 币的地址

**端点**: `/min_1_count`

**示例 - 获取不同余额层级的地址分布**:
```javascript
// JavaScript 示例
const axios = require('axios');

async function getAddressDistribution(asset) {
    const endpoints = [
        'min_point_001_count',
        'min_point_01_count',
        'min_point_1_count',
        'min_1_count',
        'min_10_count',
        'min_100_count',
        'min_1k_count',
        'min_10k_count'
    ];
    
    const results = {};
    
    for (const endpoint of endpoints) {
        const url = `https://api.glassnode.com/v1/metrics/addresses/${endpoint}`;
        const response = await axios.get(url, {
            params: { a: asset, i: '24h' },
            headers: { 'X-Api-Key': 'YOUR_API_KEY' }
        });
        results[endpoint] = response.data;
    }
    
    return results;
}
```

### 7. 新增地址数 (New Addresses)

**端点**: `/new_non_zero_count`

**描述**: 首次接收资金的新地址数量。反映网络增长和新用户采用率。

### 8. 发送/接收地址

#### 8.1 发送地址数

**端点**: `/sending_count`

**描述**: 在指定时间段内发送过交易的地址数量。

#### 8.2 接收地址数

**端点**: `/receiving_count`

**描述**: 在指定时间段内接收过交易的地址数量。

### 9. 零余额地址 (Zero Balance Addresses)

**端点**: `/zero_balance_count`

**描述**: 余额为零的地址总数。可能表示：
- 用户已清空账户
- 临时使用的地址
- 已废弃的地址

### 10. 非零余额地址 (Non-Zero Balance Addresses)

**端点**: `/non_zero_count`

**描述**: 持有任何数量资产的地址总数。

## 高级用例

### 用例 1：网络健康度分析

```python
import requests
import pandas as pd

def analyze_network_health(asset='BTC', days=30):
    base_url = "https://api.glassnode.com/v1/metrics/addresses/"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    
    metrics = {
        'active_addresses': 'active_count',
        'new_addresses': 'new_non_zero_count',
        'accumulation_addresses': 'accumulation_count',
        'addresses_in_profit': 'profit_count'
    }
    
    results = {}
    
    for name, endpoint in metrics.items():
        url = base_url + endpoint
        params = {
            'a': asset,
            'i': '24h',
            's': int(time.time()) - (days * 86400),
            'u': int(time.time())
        }
        
        response = requests.get(url, params=params, headers=headers)
        results[name] = response.json()
    
    # 分析结果
    df = pd.DataFrame(results)
    
    # 计算健康指标
    health_score = calculate_health_score(df)
    
    return {
        'data': df,
        'health_score': health_score,
        'trend': analyze_trend(df)
    }
```

### 用例 2：财富分布分析

```python
def analyze_wealth_distribution(asset='BTC'):
    """分析资产的财富集中度"""
    
    url = "https://api.glassnode.com/v1/metrics/addresses/supply_distribution_relative"
    params = {'a': asset, 'i': '24h'}
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    # 计算基尼系数
    gini_coefficient = calculate_gini(data)
    
    # 识别鲸鱼地址占比
    whale_percentage = data[-1]['v']['10k+']  # >10k 币的地址占比
    
    return {
        'gini_coefficient': gini_coefficient,
        'whale_dominance': whale_percentage,
        'distribution': data
    }
```

### 用例 3：市场情绪指标

```python
def calculate_market_sentiment(asset='BTC'):
    """基于地址盈亏状况计算市场情绪"""
    
    base_url = "https://api.glassnode.com/v1/metrics/addresses/"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    
    # 获取盈利和亏损地址数
    profit_url = base_url + "profit_count"
    loss_url = base_url + "loss_count"
    
    params = {'a': asset, 'i': '24h'}
    
    profit_resp = requests.get(profit_url, params=params, headers=headers)
    loss_resp = requests.get(loss_url, params=params, headers=headers)
    
    profit_count = profit_resp.json()[-1]['v']
    loss_count = loss_resp.json()[-1]['v']
    
    # 计算情绪指数 (0-100)
    sentiment_index = (profit_count / (profit_count + loss_count)) * 100
    
    # 解释情绪
    if sentiment_index > 75:
        sentiment = "极度贪婪"
    elif sentiment_index > 60:
        sentiment = "贪婪"
    elif sentiment_index > 40:
        sentiment = "中性"
    elif sentiment_index > 25:
        sentiment = "恐惧"
    else:
        sentiment = "极度恐惧"
    
    return {
        'index': sentiment_index,
        'sentiment': sentiment,
        'in_profit': profit_count,
        'in_loss': loss_count
    }
```

## 数据解读指南

### 关键指标解释

1. **活跃地址增长**：持续增长表明网络采用率提高
2. **累积地址增加**：表明长期持有者信心增强
3. **新地址激增**：可能预示价格波动或市场事件
4. **盈亏比例变化**：反映市场整体获利状况

### 注意事项

1. **地址 ≠ 用户**：一个用户可能控制多个地址
2. **交易所影响**：大型交易所地址可能扭曲某些指标
3. **时间延迟**：某些指标可能有 10-60 分钟的延迟
4. **数据精度**：历史数据可能经过修正

## 常见问题

### Q1: 如何区分真实用户活动和交易所内部转账？

使用实体调整后的数据（entity-adjusted），这些数据已经过滤了已知的交易所和服务商地址。

### Q2: 为什么活跃地址数会突然下降？

可能原因：
- 网络拥堵导致交易延迟
- 市场横盘导致交易减少
- 节假日或周末效应

### Q3: 如何使用地址数据预测价格？

地址指标通常作为长期趋势指标，而非短期价格预测工具。结合多个指标可提高准确性。

## 最佳实践

1. **组合使用多个指标**：单一指标可能误导，建议综合分析
2. **关注趋势而非绝对值**：趋势变化比绝对数值更有意义
3. **考虑市场周期**：牛熊市的指标解读可能不同
4. **定期更新分析模型**：市场结构在不断演变

---

*本文档提供了 Glassnode Addresses API 的完整使用指南。如需更多技术支持，请访问官方文档或联系技术支持团队。*