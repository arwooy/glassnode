# TOP 5 高信息增益指标详解

## 1. Reserve Risk（储备风险）- 综合得分第1名

### 定义与含义
Reserve Risk是衡量长期持有者信心相对于当前价格的指标，反映了"价格与HODLer信念之间的风险/回报比"。

### 计算公式
```
Reserve Risk = Price / HODL Bank

其中：
HODL Bank = Σ(Coin Days Destroyed × Price at Destruction) / Σ(Coin Supply × Days)

简化形式：
Reserve Risk = Price × Velocity / Opportunity Cost
```

### 核心组成部分
1. **价格（Price）**：当前市场价格
2. **币天销毁（Coin Days Destroyed）**：老币移动时销毁的币天数
3. **机会成本（Opportunity Cost）**：持有而不卖出的累积价值

### 为什么信息增益高？
- **信息增益**: 0.148（平均）
- **30天IG**: 0.283（最高）
- **原因**：
  1. **整合多维信息**：同时考虑价格、时间、持有者行为
  2. **领先性**：长期持有者的行为往往领先市场
  3. **非线性关系**：与价格相关性仅-0.085，但IG高达0.283

### 实际应用
```python
# 信号解读
if reserve_risk < 0.002:
    signal = "强烈买入 - 长期持有者信心极强，价格被低估"
elif reserve_risk < 0.008:
    signal = "买入 - 风险回报比有利"
elif reserve_risk > 0.02:
    signal = "卖出 - 风险过高，可能接近顶部"
```

---

## 2. MVRV Z-Score - 综合得分第2名

### 定义与含义
MVRV Z-Score是MVRV（市值与实现市值比）的标准化版本，消除了长期趋势影响，更准确地识别市场极端状态。

### 计算公式
```
MVRV = Market Cap / Realized Cap

MVRV Z-Score = (Market Cap - Realized Cap) / σ(Market Cap)

展开形式：
Z-Score = (MV - RV) / StdDev(MV over time window)
```

### 核心组成部分
1. **Market Cap（市值）**：当前价格 × 流通供应量
2. **Realized Cap（实现市值）**：每个币最后移动时的价值总和
3. **标准差（σ）**：市值的历史波动率

### 为什么信息增益高？
- **信息增益**: 0.133（平均）
- **7天IG**: 0.110（短期最佳之一）
- **原因**：
  1. **标准化处理**：消除了市场长期上涨趋势的影响
  2. **统计显著性**：Z分数直接反映偏离程度的统计意义
  3. **历史验证**：准确识别了历史上所有主要顶部和底部

### 实际应用
```python
# Z-Score阈值
thresholds = {
    "极度超买": 3.5,    # 历史顶部
    "超买": 2.5,         # 减仓信号
    "中性上": 1.0,       # 温和看涨
    "中性": 0,           # 平衡点
    "超卖": -0.5,        # 加仓信号
    "极度超卖": -1.0     # 历史底部
}

# 历史案例
# 2017年12月: Z-Score = 4.5 → 顶部
# 2018年12月: Z-Score = -0.9 → 底部
# 2021年4月: Z-Score = 3.7 → 顶部
```

---

## 3. NUPL（Net Unrealized Profit/Loss）- 综合得分第3名

### 定义与含义
NUPL衡量整个市场的未实现盈亏状态，反映投资者的整体盈利能力和市场情绪。

### 计算公式
```
NUPL = (Market Cap - Realized Cap) / Market Cap

或者：
NUPL = Σ(UTXOs × (Current Price - Purchase Price)) / Market Cap

相对利润形式：
NUPL = (Unrealized Profit - Unrealized Loss) / Market Cap
```

### 核心组成部分
1. **未实现利润**：所有盈利UTXO的利润总和
2. **未实现亏损**：所有亏损UTXO的损失总和
3. **市值归一化**：使不同时期可比

### 为什么信息增益高？
- **信息增益**: 0.118（平均）
- **互信息**: 0.091（第3高）
- **原因**：
  1. **市场情绪量化**：直接反映投资者盈亏心理
  2. **周期性明显**：清晰的市场周期划分
  3. **极低相关性**：7天相关性仅0.001，但IG=0.105（强非线性）

### 市场状态划分
```python
market_phases = {
    "欣快期（Euphoria）": (0.75, 1.0),      # 极度贪婪，接近顶部
    "贪婪期（Greed）": (0.5, 0.75),         # 强烈看涨
    "乐观期（Optimism）": (0.25, 0.5),      # 温和看涨
    "希望/恐惧（Hope/Fear）": (0, 0.25),    # 中性区域
    "投降期（Capitulation）": (-0.25, 0),    # 恐慌抛售
    "绝望期（Despair）": (-1.0, -0.25)      # 极度恐慌，可能底部
}

# 信息增益来源
# 1. 非线性阈值效应：NUPL跨越关键水平时市场行为突变
# 2. 情绪传导机制：未实现盈亏影响实际交易决策
```

---

## 4. MVRV（Market Value to Realized Value）- 综合得分第4名

### 定义与含义
MVRV是最基础但最重要的链上估值指标，衡量当前市值相对于"成本基础"的倍数。

### 计算公式
```
MVRV = Market Value / Realized Value

展开：
MVRV = (Current Price × Supply) / Σ(UTXO Value at Last Movement)

实际意义：
MVRV = 平均浮盈倍数
```

### 核心组成部分
1. **Market Value**：传统市值
2. **Realized Value**：链上成本基础
3. **比率含义**：平均每个币的账面盈利倍数

### 为什么信息增益高？
- **信息增益**: 0.118（平均）
- **30天IG**: 0.213
- **原因**：
  1. **成本基础追踪**：反映真实的市场成本
  2. **均值回归特性**：长期围绕某个均值波动
  3. **简单但有效**：单一指标包含丰富信息

### 历史关键水平
```python
historical_levels = {
    "2013年顶部": 6.0,
    "2014年底部": 0.85,
    "2017年顶部": 4.8,
    "2018年底部": 0.72,
    "2021年4月顶部": 3.96,
    "2022年6月底部": 0.75,
    
    # 统计阈值
    "强烈卖出": 3.5,
    "卖出考虑": 2.5,
    "中性区间": (1.2, 2.0),
    "买入考虑": 1.0,
    "强烈买入": 0.8
}
```

---

## 5. Hash Rate（哈希率）- 综合得分第5名

### 定义与含义
哈希率衡量比特币网络的总计算能力，反映矿工对网络的长期信心和安全性。

### 计算公式
```
Hash Rate = Number of Hashes per Second

估算方法：
Hash Rate = (Difficulty × 2^32) / Block Time

7天均值：
Hash Rate MA = Average(Daily Hash Rate over 7 days)
```

### 核心组成部分
1. **网络难度（Difficulty）**：挖矿难度
2. **出块时间（Block Time）**：实际出块间隔
3. **算力单位**：EH/s (Exahash per second)

### 为什么信息增益高？
- **信息增益**: 0.128（平均）
- **1天IG**: 0.079（短期最佳）
- **原因**：
  1. **矿工投票**：真金白银的硬件投资
  2. **领先指标**：矿工通常有信息优势
  3. **难度调整机制**：自适应系统的信息传递

### 信号解读
```python
def interpret_hashrate_signal(current_hr, ma_30d, ma_90d, price_ma_30d):
    """
    哈希率信号解读
    """
    # Hash Ribbon指标
    if ma_30d < ma_90d:
        if previous_ma_30d >= previous_ma_90d:
            return "矿工投降开始 - 潜在底部信号"
    
    elif ma_30d > ma_90d:
        if previous_ma_30d <= previous_ma_90d:
            return "矿工投降结束 - 强烈买入信号"
    
    # 哈希率与价格背离
    hr_growth = (current_hr / ma_90d - 1) * 100
    price_growth = (current_price / price_ma_30d - 1) * 100
    
    if hr_growth > price_growth + 20:
        return "哈希率领先价格 - 看涨信号"
    elif hr_growth < price_growth - 20:
        return "哈希率滞后价格 - 谨慎信号"
```

### 特殊之处
```python
# 为什么哈希率有预测能力？
reasons = {
    "1. 矿工成本考量": "矿工基于电费和硬件成本的理性决策",
    "2. 长期承诺": "矿机投资需要6-12个月回本",
    "3. 信息不对称": "大矿工可能掌握更多市场信息",
    "4. 自我实现": "算力增加→网络更安全→价值提升"
}

# 信息增益计算示例（1天）
# H(Price_t+1) = 3.32 bits (价格变化的熵)
# H(Price_t+1|HashRate_t) = 3.241 bits (知道哈希率后的条件熵)
# IG = 3.32 - 3.241 = 0.079 bits
# 减少不确定性 = 0.079/3.32 = 2.4%
```

---

## 信息增益计算详解

### 基础概念
```python
def information_gain_calculation(indicator, future_price_change):
    """
    信息增益 = H(Y) - H(Y|X)
    
    其中：
    - H(Y) = 目标变量（价格变化）的熵
    - H(Y|X) = 给定指标X后，Y的条件熵
    - IG = 知道X后，Y的不确定性减少量
    """
    
    # Step 1: 计算价格变化的熵
    # 将连续变量离散化为10个区间
    price_bins = discretize(future_price_change, n_bins=10)
    H_price = calculate_entropy(price_bins)
    # 例如：H_price = 3.32 bits（10个等概率区间的最大熵）
    
    # Step 2: 计算条件熵
    # 将指标离散化
    indicator_bins = discretize(indicator, n_bins=10)
    
    # 对每个指标区间，计算对应的价格分布熵
    H_price_given_indicator = 0
    for indicator_value in unique(indicator_bins):
        # 该指标值的概率
        p_indicator = probability(indicator_value)
        
        # 该指标值对应的价格分布
        price_distribution = price_bins[indicator_bins == indicator_value]
        
        # 计算该条件下的熵
        h_conditional = calculate_entropy(price_distribution)
        
        # 加权累加
        H_price_given_indicator += p_indicator * h_conditional
    
    # Step 3: 计算信息增益
    information_gain = H_price - H_price_given_indicator
    
    return {
        "information_gain": information_gain,
        "original_entropy": H_price,
        "conditional_entropy": H_price_given_indicator,
        "reduction_ratio": information_gain / H_price
    }
```

### 综合得分计算
```python
def calculate_composite_score(indicator_results):
    """
    综合得分 = 加权平均的信息度量
    """
    # 权重分配
    weights = {
        "information_gain": 0.3,      # 信息增益
        "mutual_information": 0.3,    # 互信息
        "symmetric_uncertainty": 0.2, # 对称不确定性
        "transfer_entropy": 0.2       # 转移熵
    }
    
    # 计算每个指标的平均值（跨所有时间跨度）
    avg_ig = mean([h["information_gain"] for h in indicator_results])
    avg_mi = mean([h["normalized_mi"] for h in indicator_results])
    avg_su = mean([h["symmetric_uncertainty"] for h in indicator_results])
    avg_te = mean([h["transfer_entropy"] for h in indicator_results])
    
    # 加权求和
    composite_score = (
        avg_ig * weights["information_gain"] +
        avg_mi * weights["mutual_information"] +
        avg_su * weights["symmetric_uncertainty"] +
        avg_te * weights["transfer_entropy"]
    )
    
    return composite_score
```

---

## 关键洞察总结

### 为什么这5个指标信息含量最高？

1. **多维信息整合**
   - Reserve Risk：价格+时间+行为
   - MVRV Z-Score：市值+成本+统计
   - NUPL：盈亏+情绪+比例

2. **非线性关系**
   - 传统相关性低但信息增益高
   - 捕捉阈值效应和状态转换

3. **不同时间尺度**
   - Hash Rate：短期（矿工决策）
   - MVRV/NUPL：中期（市场情绪）
   - Reserve Risk：长期（HODLer行为）

4. **互补信息**
   - 每个指标捕捉市场的不同方面
   - 组合使用可进一步提高预测能力

### 实际应用建议

```python
# 组合策略示例
def combined_signal(reserve_risk, mvrv_z, nupl, mvrv, hashrate_ribbon):
    """
    基于TOP5指标的综合信号
    """
    signals = []
    weights = []
    
    # Reserve Risk (权重最高)
    if reserve_risk < 0.002:
        signals.append(2)  # 强烈买入
        weights.append(0.25)
    elif reserve_risk > 0.02:
        signals.append(-2)  # 强烈卖出
        weights.append(0.25)
    else:
        signals.append(0)
        weights.append(0.25)
    
    # MVRV Z-Score
    if mvrv_z < -0.5:
        signals.append(1.5)
        weights.append(0.20)
    elif mvrv_z > 3:
        signals.append(-1.5)
        weights.append(0.20)
    else:
        signals.append(0)
        weights.append(0.20)
    
    # ... 其他指标类似
    
    # 加权平均
    final_signal = sum(s * w for s, w in zip(signals, weights))
    
    return {
        "signal": final_signal,
        "action": "BUY" if final_signal > 0.5 else "SELL" if final_signal < -0.5 else "HOLD",
        "confidence": abs(final_signal) / 2  # 归一化到0-1
    }
```

这些指标通过捕捉市场的不同维度信息，特别是非线性关系和状态转换，提供了比简单相关性分析更丰富的预测信息。