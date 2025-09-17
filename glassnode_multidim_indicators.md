# Glassnode 多维指标处理指南

## 概述

Glassnode API返回两种数据格式：
1. **单值格式** (`'v'` 字段): 大多数指标，如 price, mvrv, sopr 等
2. **多维格式** (`'o'` 字段): 分布类指标，如 supply_distribution_relative, price_usd_ohlc 等

## 多维指标列表

### 1. 供应分布指标
**端点**: `addresses/supply_distribution_relative`

**返回数据结构**:
```json
{
  "t": 1755475200,
  "o": {
    "less_0001": 0.000278,      // <0.001 BTC
    "0001_001": 0.002136,        // 0.001-0.01 BTC
    "001_01": 0.013472,          // 0.01-0.1 BTC
    "01_1": 0.053679,            // 0.1-1 BTC
    "1_10": 0.103612,            // 1-10 BTC
    "10_100": 0.216334,          // 10-100 BTC
    "100_1k": 0.247089,          // 100-1k BTC
    "1k_10k": 0.220562,          // 1k-10k BTC
    "10k_100k": 0.110117,        // 10k-100k BTC
    "above_100k": 0.032721       // >100k BTC
  }
}
```

**处理方法**:
- **赫芬达尔指数(HHI)**: 衡量集中度，HHI = Σ(share²)
- **基尼系数**: 衡量不平等程度
- **Top 1%份额**: above_100k 字段值

**信息增益分析结果**:
- HHI平均值: 0.1835
- 与7天价格变化相关性: 0.1684
- 信息增益: 0.5768 (35.97%相对减少)

### 2. OHLC价格数据
**端点**: `market/price_usd_ohlc`

**返回数据结构**:
```json
{
  "t": 1755475200,
  "o": {
    "o": 117478.93,  // 开盘价
    "h": 117620.34,  // 最高价
    "l": 114750.29,  // 最低价
    "c": 116295.38   // 收盘价
  }
}
```

**衍生指标**:
- **波动率**: (high - low) / close
- **价格变化率**: (close - open) / open
- **真实范围(TR)**: max(h-l, |h-prev_c|, |l-prev_c|)

### 3. UTXO价格分布
**端点**: `blockchain/utxo_realized_price_distribution_percent`

**预期数据结构**: 不同价格区间的UTXO分布

### 4. HODL波
**端点**: `indicators/hodl_waves`

**预期数据结构**: 不同持有时长的供应分布

### 5. 花费输出年龄带
**端点**: `indicators/spent_output_age_band`

**预期数据结构**: 不同年龄段的花费输出分布

## 处理策略

### 1. 通用处理框架

```python
def process_multidim_data(data, metric_name):
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['t'], unit='s')
    df = df.set_index('timestamp')
    
    if 'o' in df.columns:
        # 展开多维数据
        expanded = pd.json_normalize(df['o'])
        expanded.index = df.index
        
        # 根据指标类型计算综合值
        if 'distribution' in metric_name:
            # 计算集中度指标
            return calculate_concentration(expanded)
        elif 'ohlc' in metric_name:
            # 返回收盘价或计算技术指标
            return expanded['c'] if 'c' in expanded else expanded.mean(axis=1)
        else:
            # 默认：计算均值
            return expanded.mean(axis=1)
    else:
        # 单值数据
        return df['v']
```

### 2. 信息增益计算

对于多维数据，关键是将其转换为有意义的单一指标：

1. **分布数据** → 集中度指标（HHI、Gini）
2. **OHLC数据** → 技术指标（RSI、ATR、Bollinger Width）
3. **年龄分布** → 加权平均年龄或分位数

### 3. 最佳实践

1. **保存原始多维数据**: 用于后续深度分析
2. **创建多个衍生指标**: 从不同角度提取信息
3. **时间序列对齐**: 确保与价格数据时间戳匹配
4. **异常值处理**: 多维数据更容易出现异常值

## 性能优化建议

1. **缓存处理结果**: 多维数据处理计算量大
2. **批量请求**: 减少API调用次数
3. **增量更新**: 只获取新数据
4. **并行处理**: 多个指标并行计算

## 实际应用示例

### 供应集中度预警系统

```python
def concentration_alert(hhi_series, threshold=0.2):
    """
    当供应集中度超过阈值时发出预警
    HHI > 0.2 表示高度集中
    """
    if hhi_series.iloc[-1] > threshold:
        change = (hhi_series.iloc[-1] - hhi_series.iloc[-7]) / hhi_series.iloc[-7]
        return {
            'alert': True,
            'hhi': hhi_series.iloc[-1],
            'weekly_change': change,
            'message': f"供应集中度达到 {hhi_series.iloc[-1]:.3f}，周变化 {change*100:.1f}%"
        }
    return {'alert': False}
```

### 价格预测模型输入

```python
def prepare_ml_features(supply_dist, ohlc_data):
    """
    准备机器学习模型的特征
    """
    features = pd.DataFrame()
    
    # 供应分布特征
    features['hhi'] = calculate_hhi(supply_dist)
    features['gini'] = calculate_gini(supply_dist)
    features['top1pct'] = supply_dist['above_100k']
    
    # OHLC技术指标
    features['volatility'] = (ohlc_data['h'] - ohlc_data['l']) / ohlc_data['c']
    features['price_change'] = (ohlc_data['c'] - ohlc_data['o']) / ohlc_data['o']
    features['rsi'] = calculate_rsi(ohlc_data['c'])
    
    return features
```

## 结论

多维数据包含丰富的市场信息：
- **供应分布**: HHI信息增益0.5768，预测能力强
- **OHLC数据**: 提供波动率和趋势信息
- **年龄分布**: 反映市场参与者行为

正确处理这些数据对构建高质量预测模型至关重要。