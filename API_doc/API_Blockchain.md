# Blockchain（区块链数据）API 文档

## 概述

Blockchain API 提供区块链网络的基础数据，包括区块信息、UTXO（未花费交易输出）统计、网络性能指标等。这些数据是理解区块链运行状况的基础。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/blockchain/`

## 端点列表

### 1. 区块高度 (Block Height)

**端点**: `/block_height`

**描述**: 主链中已创建并包含的区块总数。这是区块链的基本指标，表示链的长度。

**参数**:
- `a` (必需): 资产代码（BTC, ETH, LTC 等）
- `s` (可选): 开始时间戳
- `u` (可选): 结束时间戳
- `i` (可选): 时间间隔（10m, 1h, 24h）

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/blockchain/block_height?a=BTC" \
  -H "X-Api-Key: YOUR_API_KEY"
```

**示例响应**:
```json
[
  {
    "t": 1614556800,
    "v": 671234
  }
]
```

**用途**:
- 监控区块链增长速度
- 计算区块确认数
- 同步节点状态检查

### 2. 平均出块时间 (Block Interval Mean)

**端点**: `/block_interval_mean`

**描述**: 指定时间段内挖出区块之间的平均时间（秒）。

**计算方法**:
```
平均出块时间 = 时间段总秒数 / 期间产生的区块数
```

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/blockchain/block_interval_mean?a=BTC&i=24h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

**应用场景**:
- 网络拥堵分析
- 难度调整预测
- 交易确认时间估算

### 3. 中位出块时间 (Block Interval Median)

**端点**: `/block_interval_median`

**描述**: 指定时间段内挖出区块之间的中位时间（秒）。比平均值更能反映典型情况。

**与平均值的区别**:
- 中位数不受极端值影响
- 更准确反映"正常"出块时间
- 适用于检测异常出块模式

### 4. 平均区块大小 (Block Size Mean)

**端点**: `/block_size_mean`

**描述**: 时间段内所有区块的平均大小（字节）。

**示例 - 监控区块利用率**:
```python
import requests
import matplotlib.pyplot as plt

def monitor_block_utilization(asset='BTC', days=30):
    url = "https://api.glassnode.com/v1/metrics/blockchain/block_size_mean"
    params = {
        'a': asset,
        'i': '24h',
        's': int(time.time()) - (days * 86400)
    }
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    # 提取时间和大小
    times = [d['t'] for d in data]
    sizes = [d['v'] for d in data]
    
    # 计算利用率（假设最大区块大小为 1MB = 1000000 字节）
    max_block_size = 1000000  # BTC 的区块大小限制
    utilization = [(s / max_block_size) * 100 for s in sizes]
    
    return {
        'average_utilization': sum(utilization) / len(utilization),
        'peak_utilization': max(utilization),
        'data': list(zip(times, utilization))
    }
```

### 5. 区块大小总和 (Block Size Sum)

**端点**: `/block_size_sum`

**描述**: 时间段内所有区块的总大小（字节）。

**用途**:
- 计算链上数据增长率
- 存储需求预测
- 网络吞吐量分析

### 6. 挖出区块数 (Blocks Mined)

**端点**: `/block_count`

**描述**: 指定时间段内创建的区块数量。

**示例 - 计算实际出块率**:
```javascript
async function calculateBlockRate(asset = 'BTC') {
    const url = 'https://api.glassnode.com/v1/metrics/blockchain/block_count';
    const params = {
        a: asset,
        i: '1h'  // 每小时的区块数
    };
    
    const response = await fetch(`${url}?${new URLSearchParams(params)}`, {
        headers: { 'X-Api-Key': 'YOUR_API_KEY' }
    });
    
    const data = await response.json();
    const latestHour = data[data.length - 1];
    
    // BTC 理论上每小时应产生 6 个区块（10分钟一个）
    const expectedBlocks = 6;
    const actualBlocks = latestHour.v;
    const efficiency = (actualBlocks / expectedBlocks) * 100;
    
    return {
        expected: expectedBlocks,
        actual: actualBlocks,
        efficiency: efficiency.toFixed(2) + '%'
    };
}
```

### 7. UTXO 相关指标

#### 7.1 盈利 UTXO 百分比

**端点**: `/utxo_profit_relative`

**描述**: 处于盈利状态的 UTXO 占总 UTXO 的百分比。UTXO 的盈利状态基于创建时的价格与当前价格对比。

**计算逻辑**:
1. 获取每个 UTXO 创建时的价格
2. 与当前价格比较
3. 统计盈利 UTXO 占比

#### 7.2 UTXO 创建价值（平均）

**端点**: `/utxo_created_value_mean`

**描述**: 新创建 UTXO 的平均价值（原生货币单位）。

#### 7.3 UTXO 创建价值（中位数）

**端点**: `/utxo_created_value_median`

**描述**: 新创建 UTXO 的中位价值。

#### 7.4 UTXO 创建价值（总和）

**端点**: `/utxo_created_value_sum`

**描述**: 时间段内所有新创建 UTXO 的总价值。

**示例 - UTXO 分析仪表板**:
```python
class UTXOAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/blockchain/"
        
    def get_utxo_metrics(self, asset='BTC'):
        metrics = {
            'profit_percentage': 'utxo_profit_relative',
            'created_mean': 'utxo_created_value_mean',
            'created_median': 'utxo_created_value_median',
            'created_sum': 'utxo_created_value_sum',
            'spent_mean': 'utxo_spent_value_mean',
            'spent_median': 'utxo_spent_value_median',
            'spent_sum': 'utxo_spent_value_sum'
        }
        
        results = {}
        headers = {"X-Api-Key": self.api_key}
        
        for name, endpoint in metrics.items():
            url = self.base_url + endpoint
            params = {'a': asset, 'i': '24h'}
            response = requests.get(url, params=params, headers=headers)
            results[name] = response.json()[-1]['v']  # 最新值
        
        return self.analyze_utxo_health(results)
    
    def analyze_utxo_health(self, metrics):
        # 分析 UTXO 集健康度
        health_indicators = {
            'market_sentiment': 'bullish' if metrics['profit_percentage'] > 60 else 'bearish',
            'creation_velocity': metrics['created_sum'] / metrics['created_mean'],
            'spending_pattern': 'high' if metrics['spent_sum'] > metrics['created_sum'] else 'low',
            'median_mean_ratio': metrics['created_median'] / metrics['created_mean']
        }
        
        return {
            'metrics': metrics,
            'analysis': health_indicators
        }
```

#### 7.5 UTXO 总数

**端点**: `/utxo_count`

**描述**: 未花费交易输出的总数量。

**重要性**:
- 反映网络使用复杂度
- 影响节点内存需求
- 交易费用估算基础

#### 7.6 创建的 UTXO 数

**端点**: `/utxo_created_count`

**描述**: 时间段内新创建的 UTXO 数量。

#### 7.7 花费的 UTXO 数

**端点**: `/utxo_spent_count`

**描述**: 时间段内被花费的 UTXO 数量。

#### 7.8 盈利/亏损 UTXO 数

**端点**: 
- `/utxo_profit_count` - 盈利状态的 UTXO 数量
- `/utxo_loss_count` - 亏损状态的 UTXO 数量

### 8. 高级应用案例

#### 案例 1：网络健康监控系统

```python
import pandas as pd
from datetime import datetime, timedelta

class BlockchainHealthMonitor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/blockchain/"
        
    def comprehensive_health_check(self, asset='BTC'):
        """全面的区块链健康检查"""
        
        health_metrics = {}
        
        # 1. 出块稳定性
        block_interval = self.get_metric('block_interval_mean', asset)
        health_metrics['block_stability'] = self.assess_block_stability(block_interval)
        
        # 2. 区块利用率
        block_size = self.get_metric('block_size_mean', asset)
        health_metrics['block_utilization'] = self.assess_utilization(block_size, asset)
        
        # 3. UTXO 集健康度
        utxo_metrics = self.get_utxo_health(asset)
        health_metrics['utxo_health'] = utxo_metrics
        
        # 4. 网络增长
        block_count = self.get_metric('block_count', asset)
        health_metrics['growth_rate'] = self.calculate_growth_rate(block_count)
        
        # 综合评分
        health_metrics['overall_score'] = self.calculate_overall_score(health_metrics)
        
        return health_metrics
    
    def assess_block_stability(self, interval_data):
        """评估出块稳定性"""
        values = [d['v'] for d in interval_data[-30:]]  # 最近30天
        mean_interval = sum(values) / len(values)
        std_dev = pd.Series(values).std()
        
        # BTC 目标是 600 秒（10分钟）
        target_interval = 600
        deviation = abs(mean_interval - target_interval) / target_interval
        
        if deviation < 0.05 and std_dev < 60:
            return {'status': 'excellent', 'score': 95}
        elif deviation < 0.1 and std_dev < 120:
            return {'status': 'good', 'score': 80}
        elif deviation < 0.2 and std_dev < 180:
            return {'status': 'fair', 'score': 60}
        else:
            return {'status': 'poor', 'score': 40}
    
    def get_metric(self, endpoint, asset):
        """获取指标数据"""
        url = self.base_url + endpoint
        params = {
            'a': asset,
            'i': '24h',
            's': int((datetime.now() - timedelta(days=30)).timestamp())
        }
        headers = {"X-Api-Key": self.api_key}
        response = requests.get(url, params=params, headers=headers)
        return response.json()
```

#### 案例 2：UTXO 年龄分析

```python
def analyze_utxo_age_distribution(asset='BTC'):
    """分析 UTXO 年龄分布，识别长期持有模式"""
    
    # 这是一个概念示例，实际需要更详细的 UTXO 数据
    
    age_bands = {
        '1d': {'count': 0, 'value': 0},
        '1w': {'count': 0, 'value': 0},
        '1m': {'count': 0, 'value': 0},
        '3m': {'count': 0, 'value': 0},
        '6m': {'count': 0, 'value': 0},
        '1y': {'count': 0, 'value': 0},
        '2y+': {'count': 0, 'value': 0}
    }
    
    # 基于 UTXO 数据计算分布
    # ... 实际实现需要访问详细的 UTXO 数据 ...
    
    return {
        'distribution': age_bands,
        'hodl_ratio': calculate_hodl_ratio(age_bands),
        'velocity': calculate_velocity(age_bands)
    }
```

#### 案例 3：交易确认时间预测

```python
def predict_confirmation_time(asset='BTC', priority='medium'):
    """基于当前网络状况预测交易确认时间"""
    
    base_url = "https://api.glassnode.com/v1/metrics/blockchain/"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    
    # 获取最近的出块时间
    interval_url = base_url + "block_interval_mean"
    params = {'a': asset, 'i': '1h'}
    response = requests.get(interval_url, params=params, headers=headers)
    recent_interval = response.json()[-1]['v']
    
    # 获取区块大小（判断拥堵程度）
    size_url = base_url + "block_size_mean"
    response = requests.get(size_url, params=params, headers=headers)
    recent_size = response.json()[-1]['v']
    
    # 根据优先级和网络状况估算
    max_block_size = 1000000  # 1MB for BTC
    congestion_level = recent_size / max_block_size
    
    if priority == 'high':
        blocks_to_confirm = 1 if congestion_level < 0.8 else 2
    elif priority == 'medium':
        blocks_to_confirm = 3 if congestion_level < 0.8 else 6
    else:  # low
        blocks_to_confirm = 6 if congestion_level < 0.8 else 12
    
    estimated_time = recent_interval * blocks_to_confirm
    
    return {
        'blocks': blocks_to_confirm,
        'estimated_seconds': estimated_time,
        'estimated_minutes': estimated_time / 60,
        'congestion_level': f"{congestion_level * 100:.1f}%",
        'confidence': 'high' if congestion_level < 0.7 else 'medium'
    }
```

## 数据解读指南

### 关键指标含义

1. **出块时间波动**
   - 正常范围：目标时间 ±20%
   - 异常情况：可能表示算力大幅变化

2. **区块大小趋势**
   - 上升：网络使用增加
   - 接近上限：可能导致费用上涨

3. **UTXO 集增长**
   - 快速增长：活跃使用
   - 缓慢增长：使用模式成熟

### 监控阈值建议

| 指标 | 正常范围 | 警告阈值 | 危险阈值 |
|------|---------|---------|---------|
| 出块时间偏差 | <10% | 10-25% | >25% |
| 区块利用率 | 50-80% | >90% | >95% |
| UTXO 增长率 | 0-10%/月 | >20%/月 | >50%/月 |

## 故障排查

### 常见问题

1. **数据延迟**
   - 原因：区块链同步延迟
   - 解决：使用更短的时间间隔参数

2. **数据缺失**
   - 原因：网络分叉或重组
   - 解决：等待 6 个区块确认

3. **异常值**
   - 原因：孤块或临时分叉
   - 解决：使用中位数而非平均值

## 最佳实践

1. **数据缓存**：历史数据变化少，应适当缓存
2. **批量请求**：合并多个指标请求以减少 API 调用
3. **异常处理**：实现重试机制处理网络错误
4. **数据验证**：交叉验证不同指标的一致性

---

*本文档详细介绍了 Glassnode Blockchain API 的使用方法和应用场景。这些基础数据是理解和分析区块链网络的核心。*