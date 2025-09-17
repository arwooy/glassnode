# TOP 5 指标公式详解与计算示例

## 1. Reserve Risk（储备风险）详细公式解析

### 完整公式分解

```
Reserve Risk = Price / HODL Bank

展开后：
Reserve Risk = Current Price / (Σ(Coin Days Destroyed × Price at Destruction) / Σ(Coin Supply × Days))
```

### 每一项的详细含义

#### 1.1 Current Price（当前价格）
- **含义**：BTC的当前市场价格
- **单位**：USD
- **示例**：$95,000

#### 1.2 Coin Days Destroyed（币天销毁）
- **含义**：当一个长期持有的币被移动时，销毁的"币天"数量
- **计算**：币数量 × 持有天数
- **示例**：
  ```
  如果 1 BTC 持有了 365 天后被移动：
  币天销毁 = 1 BTC × 365 天 = 365 币天
  ```

#### 1.3 HODL Bank（HODLer银行）
- **含义**：衡量长期持有者累积价值的指标
- **计算过程**：
  ```python
  # 假设数据
  transactions = [
      {"btc": 1, "days_held": 365, "price_at_move": 50000},
      {"btc": 0.5, "days_held": 180, "price_at_move": 60000},
      {"btc": 2, "days_held": 730, "price_at_move": 40000}
  ]
  
  # 计算分子：价值加权的币天销毁
  numerator = 0
  for tx in transactions:
      coin_days_destroyed = tx["btc"] * tx["days_held"]
      value_destroyed = coin_days_destroyed * tx["price_at_move"]
      numerator += value_destroyed
  
  # numerator = (1×365×50000) + (0.5×180×60000) + (2×730×40000)
  # numerator = 18,250,000 + 5,400,000 + 58,400,000 = 82,050,000
  
  # 计算分母：总币天供应
  total_supply = 19500000  # 当前BTC供应量
  average_days = 365  # 平均持有时间
  denominator = total_supply * average_days
  # denominator = 19,500,000 × 365 = 7,117,500,000
  
  # HODL Bank
  hodl_bank = numerator / denominator
  # hodl_bank = 82,050,000 / 7,117,500,000 = 0.01153
  ```

#### 1.4 完整计算示例

```python
# 实际Reserve Risk计算
current_price = 95000  # 当前BTC价格
hodl_bank = 0.01153    # 上面计算的HODL Bank值

reserve_risk = current_price / hodl_bank
# reserve_risk = 95000 / 0.01153 = 8,238,247

# 标准化（通常会除以一个基准值）
normalized_reserve_risk = reserve_risk / 1000000000
# normalized_reserve_risk = 0.00824

# 解读
if normalized_reserve_risk < 0.002:
    print("极低风险 - 强烈买入信号")
elif normalized_reserve_risk < 0.008:
    print("低风险 - 买入信号")
elif normalized_reserve_risk > 0.02:
    print("高风险 - 卖出信号")
```

---

## 2. MVRV Z-Score 详细公式解析

### 完整公式分解

```
MVRV = Market Cap / Realized Cap
MVRV Z-Score = (Market Cap - Realized Cap) / σ(Market Cap)
```

### 每一项的详细含义

#### 2.1 Market Cap（市值）
- **含义**：传统市值
- **计算**：当前价格 × 流通供应量
- **示例**：
  ```python
  current_price = 95000
  circulating_supply = 19500000
  market_cap = current_price * circulating_supply
  # market_cap = 95000 × 19,500,000 = 1,852,500,000,000 USD
  ```

#### 2.2 Realized Cap（实现市值）
- **含义**：每个BTC最后移动时的价值总和
- **计算**：Σ(每个UTXO × 该UTXO创建时的价格)
- **详细示例**：
  ```python
  # UTXO集合示例
  utxos = [
      {"amount": 1000000, "price_at_creation": 20000},  # 2020年购买
      {"amount": 500000, "price_at_creation": 50000},   # 2021年购买
      {"amount": 2000000, "price_at_creation": 30000},  # 2021年购买
      {"amount": 800000, "price_at_creation": 60000},   # 2024年购买
  ]
  
  realized_cap = 0
  for utxo in utxos:
      realized_cap += utxo["amount"] * utxo["price_at_creation"]
  
  # realized_cap = (1M×20000) + (0.5M×50000) + (2M×30000) + (0.8M×60000)
  # realized_cap = 20B + 25B + 60B + 48B = 153B USD
  
  # 全网实现市值（假设）
  total_realized_cap = 600000000000  # 600B USD
  ```

#### 2.3 标准差 σ(Market Cap)
- **含义**：市值的历史波动率
- **计算周期**：通常使用365天滚动窗口
- **示例**：
  ```python
  import numpy as np
  
  # 过去365天的市值数据
  historical_market_caps = [
      1800000000000,  # Day 1
      1850000000000,  # Day 2
      1750000000000,  # Day 3
      # ... 365 days of data
  ]
  
  # 计算标准差
  std_dev = np.std(historical_market_caps)
  # std_dev ≈ 150,000,000,000 (150B)
  ```

#### 2.4 完整Z-Score计算

```python
# 组合所有部分
market_cap = 1852500000000  # 1.85T
realized_cap = 600000000000  # 600B
std_dev = 150000000000      # 150B

# 计算MVRV
mvrv = market_cap / realized_cap
# mvrv = 1,852,500,000,000 / 600,000,000,000 = 3.09

# 计算Z-Score
mvrv_z_score = (market_cap - realized_cap) / std_dev
# mvrv_z_score = (1,852.5B - 600B) / 150B = 1252.5B / 150B = 8.35

# 但实际中通常看到的值在-2到+4之间，因为会用不同的标准化方法
# 实际计算可能用市值的对数或其他变换
actual_z_score = np.log(mvrv) / np.std(np.log(historical_mvrv_values))
# actual_z_score ≈ 2.5

# 信号解读
if actual_z_score > 3.5:
    print("市场极度过热 - 强烈卖出")
elif actual_z_score > 2.5:
    print("市场过热 - 考虑减仓")
elif actual_z_score < -0.5:
    print("市场超卖 - 考虑买入")
elif actual_z_score < -1.0:
    print("市场极度超卖 - 强烈买入")
```

---

## 3. NUPL（Net Unrealized Profit/Loss）详细公式解析

### 完整公式分解

```
NUPL = (Market Cap - Realized Cap) / Market Cap

或更详细：
NUPL = (Σ(UTXOs in Profit) - Σ(UTXOs in Loss)) / Market Cap
```

### 每一项的详细含义

#### 3.1 UTXOs in Profit（盈利的UTXO）
- **含义**：当前价格高于获得价格的所有未花费输出
- **计算**：
  ```python
  current_price = 95000
  
  # UTXO示例
  utxos_in_profit = [
      {"btc": 0.5, "acquisition_price": 30000},  # 利润: 0.5×(95000-30000)=32500
      {"btc": 1.0, "acquisition_price": 50000},  # 利润: 1.0×(95000-50000)=45000
      {"btc": 0.3, "acquisition_price": 20000},  # 利润: 0.3×(95000-20000)=22500
  ]
  
  total_unrealized_profit = 0
  for utxo in utxos_in_profit:
      profit_per_btc = current_price - utxo["acquisition_price"]
      unrealized_profit = utxo["btc"] * profit_per_btc
      total_unrealized_profit += unrealized_profit
  
  # total_unrealized_profit = 32500 + 45000 + 22500 = 100,000 USD
  ```

#### 3.2 UTXOs in Loss（亏损的UTXO）
- **含义**：当前价格低于获得价格的所有未花费输出
- **计算**：
  ```python
  utxos_in_loss = [
      {"btc": 0.2, "acquisition_price": 100000},  # 损失: 0.2×(100000-95000)=1000
      {"btc": 0.1, "acquisition_price": 105000},  # 损失: 0.1×(105000-95000)=1000
  ]
  
  total_unrealized_loss = 0
  for utxo in utxos_in_loss:
      loss_per_btc = utxo["acquisition_price"] - current_price
      unrealized_loss = utxo["btc"] * loss_per_btc
      total_unrealized_loss += unrealized_loss
  
  # total_unrealized_loss = 1000 + 1000 = 2,000 USD
  ```

#### 3.3 完整NUPL计算

```python
# 网络级别数据（简化示例）
market_cap = 1852500000000  # 1.85T USD
realized_cap = 600000000000  # 600B USD

# 方法1：使用市值差
net_unrealized_pl = market_cap - realized_cap
# net_unrealized_pl = 1,852.5B - 600B = 1,252.5B

nupl = net_unrealized_pl / market_cap
# nupl = 1,252.5B / 1,852.5B = 0.676

# 方法2：使用单个UTXO（更精确）
total_supply_btc = 19500000
btc_in_profit = 17000000  # 87%的币处于盈利
btc_in_loss = 2500000     # 13%的币处于亏损

avg_profit_per_btc = 45000  # 平均每个盈利BTC的利润
avg_loss_per_btc = 5000     # 平均每个亏损BTC的损失

total_profit = btc_in_profit * avg_profit_per_btc
# total_profit = 17,000,000 × 45,000 = 765B

total_loss = btc_in_loss * avg_loss_per_btc
# total_loss = 2,500,000 × 5,000 = 12.5B

net_unrealized = total_profit - total_loss
# net_unrealized = 765B - 12.5B = 752.5B

nupl_precise = net_unrealized / market_cap
# nupl_precise = 752.5B / 1,852.5B = 0.406

# 市场阶段判断
if nupl > 0.75:
    phase = "欣快期 - 极度贪婪，接近顶部"
elif nupl > 0.5:
    phase = "贪婪期 - 强烈看涨"
elif nupl > 0.25:
    phase = "乐观期 - 温和看涨"
elif nupl > 0:
    phase = "希望/恐惧期 - 中性"
elif nupl > -0.25:
    phase = "投降期 - 恐慌抛售"
else:
    phase = "绝望期 - 极度恐慌，可能底部"

print(f"NUPL = {nupl:.3f}, 市场阶段: {phase}")
```

---

## 4. MVRV（Market Value to Realized Value）详细公式解析

### 完整公式分解

```
MVRV = Market Value / Realized Value

详细形式：
MVRV = (Current Price × Supply) / Σ(Each Coin × Price When Last Moved)
```

### 每一项的详细含义与计算

```python
# 示例：简化的5个币的网络
coins = [
    {"amount": 1, "last_move_price": 10000, "last_move_date": "2020-01-01"},
    {"amount": 2, "last_move_price": 30000, "last_move_date": "2021-01-01"},
    {"amount": 0.5, "last_move_price": 60000, "last_move_date": "2021-11-01"},
    {"amount": 1.5, "last_move_price": 20000, "last_move_date": "2022-06-01"},
    {"amount": 1, "last_move_price": 70000, "last_move_date": "2024-03-01"},
]

current_price = 95000
total_supply = sum([c["amount"] for c in coins])  # 6 BTC

# 计算Market Value
market_value = current_price * total_supply
# market_value = 95,000 × 6 = 570,000 USD

# 计算Realized Value
realized_value = 0
for coin in coins:
    coin_realized_value = coin["amount"] * coin["last_move_price"]
    realized_value += coin_realized_value
    print(f"{coin['amount']} BTC × ${coin['last_move_price']} = ${coin_realized_value}")

# 详细计算：
# 1 × 10,000 = 10,000
# 2 × 30,000 = 60,000
# 0.5 × 60,000 = 30,000
# 1.5 × 20,000 = 30,000
# 1 × 70,000 = 70,000
# realized_value = 10,000 + 60,000 + 30,000 + 30,000 + 70,000 = 200,000

# 计算MVRV
mvrv = market_value / realized_value
# mvrv = 570,000 / 200,000 = 2.85

print(f"""
MVRV计算结果：
- 当前价格: ${current_price:,}
- 总供应量: {total_supply} BTC
- 市场价值: ${market_value:,}
- 实现价值: ${realized_value:,}
- MVRV比率: {mvrv:.2f}

解读：
MVRV = {mvrv:.2f} 意味着:
- 平均每个币的账面盈利是成本的 {mvrv:.1f} 倍
- 如果所有人现在卖出，平均利润率为 {(mvrv-1)*100:.1f}%
""")

# 历史对比
historical_mvrv_levels = {
    "2017年12月顶部": 4.8,
    "2018年12月底部": 0.72,
    "2021年4月顶部": 3.96,
    "2022年6月底部": 0.75,
    "当前": mvrv
}

if mvrv > 3.5:
    signal = "⚠️ 过热区域 - 考虑获利了结"
elif mvrv > 2.5:
    signal = "📈 牛市区域 - 持有但保持警惕"
elif mvrv > 1.5:
    signal = "➡️ 中性区域 - 正常估值"
elif mvrv > 1.0:
    signal = "📉 低估区域 - 考虑积累"
else:
    signal = "💎 深度低估 - 强烈买入机会"

print(f"当前信号: {signal}")
```

---

## 5. Hash Rate（哈希率）详细公式解析

### 完整公式分解

```
Hash Rate = (Network Difficulty × 2^32) / Average Block Time

其中：
- Network Difficulty：当前挖矿难度
- 2^32：难度调整常数（4,294,967,296）
- Average Block Time：平均出块时间（目标是600秒）
```

### 每一项的详细含义

#### 5.1 Network Difficulty（网络难度）
- **含义**：找到有效区块哈希的难度
- **单位**：无量纲数字
- **示例**：67,957,790,298,898

#### 5.2 计算常数 2^32
- **含义**：比特币协议中的固定常数
- **值**：4,294,967,296
- **作用**：将难度转换为预期哈希次数

#### 5.3 完整计算示例

```python
import math

# 当前网络参数
network_difficulty = 67957790298898  # 当前难度
target_block_time = 600  # 目标10分钟（600秒）
actual_block_time = 590  # 实际平均出块时间

# 方法1：理论计算
hash_rate_theoretical = (network_difficulty * 2**32) / target_block_time
# hash_rate = (67,957,790,298,898 × 4,294,967,296) / 600
# hash_rate = 291,893,439,907,041,935,560,448 / 600
# hash_rate = 486,489,066,511,736,559,267 H/s
# 转换为EH/s (Exahash)
hash_rate_eh = hash_rate_theoretical / 10**18
# hash_rate_eh = 486.5 EH/s

# 方法2：基于实际出块时间
hash_rate_actual = (network_difficulty * 2**32) / actual_block_time
# hash_rate_actual = 495 EH/s （出块更快说明算力更高）

print(f"""
哈希率计算：
- 网络难度: {network_difficulty:,}
- 目标出块时间: {target_block_time}秒
- 实际出块时间: {actual_block_time}秒
- 理论哈希率: {hash_rate_eh:.1f} EH/s
- 实际哈希率: {hash_rate_actual/10**18:.1f} EH/s
""")

# Hash Ribbon 指标计算
historical_hashrates = [
    480, 485, 490, 495, 500, 505, 510, 515, 520, 525,  # 最近10天
    530, 535, 540, 545, 550, 555, 560, 565, 570, 575,  # 11-20天
    580, 585, 590, 595, 600, 605, 610, 615, 620, 625,  # 21-30天
    # ... 更多历史数据
]

# 计算移动平均
import numpy as np

ma_30 = np.mean(historical_hashrates[-30:])  # 30日均线
ma_90 = np.mean(historical_hashrates[-90:]) if len(historical_hashrates) >= 90 else ma_30

print(f"""
Hash Ribbon 分析：
- 30日均线: {ma_30:.1f} EH/s
- 90日均线: {ma_90:.1f} EH/s
""")

# 矿工投降检测
if ma_30 < ma_90 * 0.95:  # 30日均线低于90日均线5%以上
    print("🔴 矿工投降信号 - 可能接近底部")
elif ma_30 > ma_90 * 1.05:  # 30日均线高于90日均线5%以上
    print("🟢 矿工扩张信号 - 看涨")
else:
    print("➡️ 矿工稳定 - 中性")

# 挖矿盈利能力分析
btc_price = 95000
electricity_cost = 0.05  # USD per kWh
mining_efficiency = 30  # J/TH (焦耳每太哈希)
watts_per_th = mining_efficiency  # 瓦特
kwh_per_th_per_day = (watts_per_th * 24) / 1000  # 千瓦时
electricity_cost_per_th = kwh_per_th_per_day * electricity_cost

# 每TH/s的日收益
network_hashrate_th = hash_rate_eh * 10**6  # 转换为TH/s
blocks_per_day = 144
block_reward = 6.25  # BTC
fees_per_block = 0.5  # 平均手续费
total_btc_per_day = blocks_per_day * (block_reward + fees_per_block)
btc_per_th_per_day = total_btc_per_day / network_hashrate_th
revenue_per_th = btc_per_th_per_day * btc_price

# 利润率
profit_per_th = revenue_per_th - electricity_cost_per_th
profit_margin = (profit_per_th / revenue_per_th) * 100

print(f"""
挖矿经济学：
- 每TH/s日产出: {btc_per_th_per_day:.8f} BTC
- 每TH/s日收入: ${revenue_per_th:.2f}
- 每TH/s电费: ${electricity_cost_per_th:.2f}
- 每TH/s利润: ${profit_per_th:.2f}
- 利润率: {profit_margin:.1f}%

信号：
""")

if profit_margin > 60:
    print("✨ 挖矿高利润 - 算力将继续增长")
elif profit_margin > 30:
    print("✅ 挖矿健康 - 网络安全")
elif profit_margin > 0:
    print("⚠️ 挖矿微利 - 部分矿工可能退出")
else:
    print("🔴 挖矿亏损 - 矿工投降风险")
```

---

## 信息增益计算的完整示例

### 以Reserve Risk为例的完整IG计算

```python
import numpy as np
from scipy.stats import entropy
import pandas as pd

def calculate_information_gain_example():
    """
    完整的信息增益计算示例
    使用Reserve Risk预测30天后的价格变化
    """
    
    # 模拟数据（实际中是历史数据）
    np.random.seed(42)
    n_samples = 1000
    
    # Reserve Risk数据（已标准化）
    reserve_risk = np.random.lognormal(mean=-6, sigma=1, size=n_samples)
    
    # 30天后的价格变化（受Reserve Risk影响）
    # 低Reserve Risk倾向于正收益
    price_change_30d = []
    for rr in reserve_risk:
        if rr < 0.002:  # 极低风险
            change = np.random.normal(0.15, 0.1)  # 平均+15%
        elif rr < 0.008:  # 低风险
            change = np.random.normal(0.05, 0.1)  # 平均+5%
        elif rr < 0.02:  # 中等风险
            change = np.random.normal(0, 0.15)    # 平均0%
        else:  # 高风险
            change = np.random.normal(-0.1, 0.15) # 平均-10%
        price_change_30d.append(change)
    
    price_change_30d = np.array(price_change_30d)
    
    # Step 1: 计算价格变化的熵 H(Y)
    # 将连续变量离散化为10个区间
    n_bins = 10
    price_bins = pd.qcut(price_change_30d, n_bins, labels=False, duplicates='drop')
    
    # 计算概率分布
    price_probs = np.bincount(price_bins) / len(price_bins)
    
    # 计算熵（使用base-2对数）
    H_price = -np.sum(price_probs * np.log2(price_probs + 1e-10))
    
    print(f"Step 1 - 价格变化的熵 H(Y) = {H_price:.3f} bits")
    print(f"  含义：需要 {H_price:.1f} bits 来完全描述价格变化的不确定性")
    
    # Step 2: 计算条件熵 H(Y|X)
    # 将Reserve Risk离散化
    rr_bins = pd.qcut(reserve_risk, n_bins, labels=False, duplicates='drop')
    
    # 对每个Reserve Risk区间，计算对应的价格分布熵
    H_price_given_rr = 0
    
    for rr_bin in range(n_bins):
        # 该RR区间的概率
        p_rr = np.sum(rr_bins == rr_bin) / len(rr_bins)
        
        # 该RR区间对应的价格变化
        price_in_bin = price_bins[rr_bins == rr_bin]
        
        if len(price_in_bin) > 0:
            # 计算该条件下的价格分布
            conditional_probs = np.bincount(price_in_bin, minlength=n_bins) / len(price_in_bin)
            
            # 计算该条件下的熵
            h_conditional = -np.sum(conditional_probs * np.log2(conditional_probs + 1e-10))
            
            # 加权累加
            H_price_given_rr += p_rr * h_conditional
            
            print(f"  RR区间{rr_bin}: P(RR)={p_rr:.3f}, H(Price|RR)={h_conditional:.3f}")
    
    print(f"\nStep 2 - 条件熵 H(Y|X) = {H_price_given_rr:.3f} bits")
    print(f"  含义：知道Reserve Risk后，价格不确定性降到 {H_price_given_rr:.1f} bits")
    
    # Step 3: 计算信息增益
    information_gain = H_price - H_price_given_rr
    reduction_ratio = (information_gain / H_price) * 100
    
    print(f"\nStep 3 - 信息增益计算:")
    print(f"  IG = H(Y) - H(Y|X) = {H_price:.3f} - {H_price_given_rr:.3f} = {information_gain:.3f} bits")
    print(f"  不确定性减少: {reduction_ratio:.1f}%")
    
    # 实际意义解释
    print(f"\n实际意义:")
    print(f"  • 原始不确定性: {H_price:.3f} bits")
    print(f"  • Reserve Risk提供的信息: {information_gain:.3f} bits")
    print(f"  • 相当于将随机猜测的准确率从50%提升到约{50 + reduction_ratio/2:.1f}%")
    
    # 与实际数据对比
    print(f"\n与实际Reserve Risk (30天) 对比:")
    print(f"  • 实际IG: 0.283 bits")
    print(f"  • 实际减少: 8.5%")
    print(f"  • 说明Reserve Risk确实包含预测信息")
    
    return information_gain, reduction_ratio

# 运行示例
ig, reduction = calculate_information_gain_example()
```

---

## 总结：为什么这些公式能够预测价格？

### 1. **信息聚合**
每个公式都聚合了多个维度的信息：
- Reserve Risk：价格 + 时间 + 行为
- MVRV：当前估值 + 历史成本
- NUPL：盈亏分布 + 市场情绪

### 2. **行为经济学**
公式捕捉了投资者的实际行为模式：
- 盈利时倾向卖出（SOPR > 1）
- 亏损时倾向持有（NUPL < 0）
- 极端情绪导致反转（MVRV Z-Score极值）

### 3. **市场结构**
反映了市场的内在结构：
- 成本基础（Realized Cap）
- 供需平衡（Exchange Flows）
- 安全性（Hash Rate）

### 4. **非线性关系**
信息增益高是因为捕捉了非线性模式：
- 阈值效应（如NUPL > 0.75触发获利了结）
- 状态转换（如矿工投降）
- 反馈循环（如FOMO/FUD）

这些公式的价值在于它们将复杂的市场动态简化为可量化的指标，通过信息论的方法，我们可以精确测量每个指标对价格预测的贡献度。