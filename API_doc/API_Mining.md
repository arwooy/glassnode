# Mining（挖矿）API 文档

## 概述

Mining API 提供与区块链挖矿相关的全面数据，包括算力、难度、矿工收入、挖矿成本和盈利能力等指标。这些数据对于理解网络安全性、矿工行为和市场供应动态至关重要。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/mining/`

## 核心端点

### 1. 算力和难度

#### 1.1 网络算力（Hash Rate）

**端点**: `/hash_rate_mean`

**描述**: 矿工估计的平均每秒哈希次数。

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/mining/hash_rate_mean?a=BTC&i=24h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

#### 1.2 挖矿难度

**端点**: `/difficulty_latest`

**描述**: 当前挖出一个区块所需的估计哈希次数。

```python
class HashRateAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/mining/"
        
    def analyze_network_hashrate(self, asset='BTC'):
        """分析网络算力"""
        
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h', 's': int(time.time()) - 90*86400}
        
        # 获取算力数据
        hashrate = requests.get(
            self.base_url + "hash_rate_mean",
            params=params,
            headers=headers
        ).json()
        
        # 获取难度数据
        difficulty = requests.get(
            self.base_url + "difficulty_latest",
            params=params,
            headers=headers
        ).json()
        
        # 分析算力趋势
        hr_values = [d['v'] for d in hashrate]
        current_hr = hr_values[-1]
        avg_hr = sum(hr_values) / len(hr_values)
        
        # 计算算力变化
        hr_30d_ago = hr_values[-30] if len(hr_values) > 30 else hr_values[0]
        hr_change = (current_hr - hr_30d_ago) / hr_30d_ago * 100
        
        # 分析难度调整
        diff_values = [d['v'] for d in difficulty]
        current_diff = diff_values[-1]
        
        # 预测下次难度调整
        next_adjustment = self.predict_difficulty_adjustment(hr_values, diff_values)
        
        # 安全性评估
        security_assessment = self.assess_network_security(current_hr, hr_change)
        
        return {
            'current_hashrate': f"{current_hr/1e18:.2f} EH/s",  # Exahash
            '90d_avg_hashrate': f"{avg_hr/1e18:.2f} EH/s",
            '30d_change': f"{hr_change:.2f}%",
            'current_difficulty': current_diff,
            'next_adjustment': next_adjustment,
            'security_assessment': security_assessment,
            'mining_dynamics': self.analyze_mining_dynamics(hr_values, diff_values)
        }
    
    def predict_difficulty_adjustment(self, hashrate, difficulty):
        """预测下次难度调整"""
        
        # 比特币每2016个区块调整一次难度
        # 目标是维持10分钟出块时间
        
        recent_hr = sum(hashrate[-14:]) / 14  # 最近2周平均
        older_hr = sum(hashrate[-28:-14]) / 14  # 前2周平均
        
        hr_change_ratio = recent_hr / older_hr
        
        # 预测调整幅度
        if hr_change_ratio > 1.1:
            adjustment = f"+{(hr_change_ratio - 1) * 100:.1f}%"
            impact = "难度上调，挖矿收益下降"
        elif hr_change_ratio < 0.9:
            adjustment = f"{(hr_change_ratio - 1) * 100:.1f}%"
            impact = "难度下调，挖矿收益上升"
        else:
            adjustment = "±2%以内"
            impact = "难度基本不变"
        
        return {
            'estimated_adjustment': adjustment,
            'impact': impact,
            'blocks_until_adjustment': self.calculate_blocks_to_adjustment()
        }
    
    def assess_network_security(self, hashrate, change):
        """评估网络安全性"""
        
        if hashrate > 400e18:  # 400 EH/s for BTC
            security_level = "极高"
            description = "网络极其安全，51%攻击几乎不可能"
        elif hashrate > 200e18:
            security_level = "高"
            description = "网络安全性强，攻击成本极高"
        elif hashrate > 100e18:
            security_level = "中"
            description = "网络安全，但需关注算力集中度"
        else:
            security_level = "需关注"
            description = "算力相对较低，关注潜在风险"
        
        # 考虑算力变化趋势
        if change < -20:
            description += " | 警告：算力大幅下降"
        elif change > 50:
            description += " | 积极：算力快速增长"
        
        return {
            'level': security_level,
            'description': description,
            'attack_cost_estimate': self.estimate_attack_cost(hashrate)
        }
    
    def estimate_attack_cost(self, hashrate):
        """估算51%攻击成本"""
        
        # 简化计算：需要控制51%算力
        required_hashrate = hashrate * 0.51
        
        # 假设成本（基于ASIC矿机）
        cost_per_th = 50  # 美元/TH
        hardware_cost = (required_hashrate / 1e12) * cost_per_th
        
        # 电力成本（简化）
        electricity_cost_daily = hardware_cost * 0.1  # 日电费约为硬件成本的10%
        
        return {
            'hardware_cost': f"${hardware_cost/1e9:.2f}B",
            'daily_operation_cost': f"${electricity_cost_daily/1e6:.2f}M",
            'feasibility': "极低" if hardware_cost > 1e10 else "低" if hardware_cost > 1e9 else "中"
        }
```

### 2. 矿工收入

#### 2.1 区块奖励

**端点**: `/volume_mined_sum`

**描述**: 新挖出的币的总价值。

#### 2.2 手续费收入

**端点**: `/revenue_from_fees`

**描述**: 矿工从交易费用获得的收入。

#### 2.3 总收入

**端点**: `/revenue_sum`

**描述**: 矿工的总收入（区块奖励 + 手续费）。

```python
class MinerRevenueAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_miner_economics(self, asset='BTC'):
        """分析矿工经济学"""
        
        base_url = "https://api.glassnode.com/v1/metrics/mining/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h', 's': int(time.time()) - 30*86400, 'c': 'USD'}
        
        # 获取收入数据
        block_rewards = requests.get(
            base_url + "volume_mined_sum",
            params=params,
            headers=headers
        ).json()
        
        fee_revenue = requests.get(
            base_url + "revenue_from_fees",
            params=params,
            headers=headers
        ).json()
        
        total_revenue = requests.get(
            base_url + "revenue_sum",
            params=params,
            headers=headers
        ).json()
        
        # 分析收入结构
        current_total = total_revenue[-1]['v']
        current_fees = fee_revenue[-1]['v']
        current_block = block_rewards[-1]['v']
        
        fee_percentage = (current_fees / current_total * 100) if current_total > 0 else 0
        
        # 30天统计
        total_30d = sum(d['v'] for d in total_revenue)
        fees_30d = sum(d['v'] for d in fee_revenue)
        blocks_30d = sum(d['v'] for d in block_rewards)
        
        # 盈利能力分析
        profitability = self.calculate_mining_profitability(current_total, asset)
        
        # 减半影响分析（BTC特定）
        halving_impact = self.analyze_halving_impact(asset, fee_percentage)
        
        return {
            'daily_revenue': {
                'total': f"${current_total:,.0f}",
                'block_rewards': f"${current_block:,.0f}",
                'fees': f"${current_fees:,.0f}",
                'fee_percentage': f"{fee_percentage:.2f}%"
            },
            '30d_summary': {
                'total_revenue': f"${total_30d:,.0f}",
                'avg_daily': f"${total_30d/30:,.0f}",
                'fees_ratio': f"{fees_30d/total_30d*100:.2f}%"
            },
            'profitability': profitability,
            'halving_impact': halving_impact,
            'sustainability': self.assess_revenue_sustainability(fee_percentage)
        }
    
    def calculate_mining_profitability(self, daily_revenue, asset):
        """计算挖矿盈利能力"""
        
        # 获取网络算力
        hashrate = self.get_current_hashrate(asset)
        
        # 估算成本（简化模型）
        electricity_cost_per_ph = 50  # 美元/PH/天
        total_ph = hashrate / 1e15  # 转换为 PH
        daily_cost = total_ph * electricity_cost_per_ph
        
        daily_profit = daily_revenue - daily_cost
        profit_margin = (daily_profit / daily_revenue * 100) if daily_revenue > 0 else 0
        
        # 计算回本周期（假设矿机成本）
        hardware_cost_per_ph = 10000  # 美元/PH
        total_hardware_cost = total_ph * hardware_cost_per_ph
        payback_period = total_hardware_cost / daily_profit if daily_profit > 0 else float('inf')
        
        return {
            'daily_profit': f"${daily_profit:,.0f}",
            'profit_margin': f"{profit_margin:.1f}%",
            'payback_period_days': int(payback_period) if payback_period != float('inf') else "∞",
            'profitability_status': self.classify_profitability(profit_margin)
        }
    
    def classify_profitability(self, margin):
        """分类盈利能力"""
        
        if margin > 50:
            return "高盈利 - 挖矿极具吸引力"
        elif margin > 30:
            return "良好盈利 - 健康的挖矿环境"
        elif margin > 10:
            return "微利 - 需要优化成本"
        elif margin > 0:
            return "边际盈利 - 高风险"
        else:
            return "亏损 - 部分矿工可能关机"
    
    def analyze_halving_impact(self, asset, fee_percentage):
        """分析减半影响"""
        
        if asset != 'BTC':
            return "不适用"
        
        # 计算下次减半时间
        current_block = 750000  # 示例
        halving_block = 840000  # 下次减半高度
        blocks_to_halving = halving_block - current_block
        days_to_halving = blocks_to_halving * 10 / 60 / 24
        
        # 评估减半后的可持续性
        if fee_percentage > 30:
            impact = "低影响 - 手续费收入可补偿减半损失"
        elif fee_percentage > 15:
            impact = "中等影响 - 需要价格上涨或费用增加"
        else:
            impact = "高影响 - 严重依赖区块奖励"
        
        return {
            'days_to_halving': int(days_to_halving),
            'current_fee_ratio': f"{fee_percentage:.2f}%",
            'impact_assessment': impact,
            'required_fee_ratio': "建议 >20% 以维持减半后收入"
        }
```

### 3. 矿工行为指标

#### 3.1 矿工流出倍数

**端点**: `/miners_outflow_multiple`

**描述**: 矿工转出量相对于其历史平均的倍数。

#### 3.2 矿工未花费供应

**端点**: `/miners_unspent_supply`

**描述**: 从未移动的挖矿奖励总量。

```python
class MinerBehaviorAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_miner_behavior(self, asset='BTC'):
        """分析矿工行为模式"""
        
        base_url = "https://api.glassnode.com/v1/metrics/mining/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h', 's': int(time.time()) - 90*86400}
        
        # 获取矿工流出数据
        outflow_multiple = requests.get(
            base_url + "miners_outflow_multiple",
            params=params,
            headers=headers
        ).json()
        
        # 获取未花费供应
        unspent_supply = requests.get(
            base_url + "miners_unspent_supply",
            params=params,
            headers=headers
        ).json()
        
        # 分析流出模式
        current_multiple = outflow_multiple[-1]['v']
        avg_multiple = sum(d['v'] for d in outflow_multiple) / len(outflow_multiple)
        
        # 判断矿工情绪
        if current_multiple > 2:
            sentiment = "大量抛售 - 矿工急需现金或看跌"
            signal = "BEARISH"
        elif current_multiple > 1.5:
            sentiment = "增加抛售 - 矿工获利了结"
            signal = "SLIGHTLY_BEARISH"
        elif current_multiple < 0.5:
            sentiment = "囤积 - 矿工看涨未来价格"
            signal = "BULLISH"
        else:
            sentiment = "正常售出 - 覆盖运营成本"
            signal = "NEUTRAL"
        
        # 分析囤积行为
        current_unspent = unspent_supply[-1]['v']
        unspent_change = (unspent_supply[-1]['v'] - unspent_supply[-30]['v']) / unspent_supply[-30]['v'] * 100
        
        hoarding_analysis = self.analyze_hoarding(current_unspent, unspent_change)
        
        # 预测矿工行为
        behavior_prediction = self.predict_miner_behavior(current_multiple, sentiment, asset)
        
        return {
            'outflow_multiple': round(current_multiple, 2),
            'sentiment': sentiment,
            'signal': signal,
            'unspent_supply': current_unspent,
            'unspent_change_30d': f"{unspent_change:.2f}%",
            'hoarding_analysis': hoarding_analysis,
            'behavior_prediction': behavior_prediction,
            'risk_assessment': self.assess_selling_pressure(current_multiple, avg_multiple)
        }
    
    def analyze_hoarding(self, unspent, change):
        """分析囤币行为"""
        
        if change > 5:
            behavior = "积极囤积"
            implication = "矿工预期价格上涨"
        elif change > 0:
            behavior = "轻微囤积"
            implication = "矿工持谨慎乐观态度"
        elif change > -5:
            behavior = "正常流通"
            implication = "矿工维持正常运营"
        else:
            behavior = "释放库存"
            implication = "矿工可能面临财务压力"
        
        return {
            'behavior': behavior,
            'implication': implication,
            'strength': abs(change)
        }
    
    def predict_miner_behavior(self, multiple, sentiment, asset):
        """预测矿工未来行为"""
        
        # 获取当前价格和成本数据
        mining_cost = self.estimate_mining_cost(asset)
        current_price = self.get_current_price(asset)
        
        profit_margin = (current_price - mining_cost) / mining_cost * 100
        
        predictions = []
        
        if profit_margin > 100:
            predictions.append("高盈利环境，预计继续正常售出或轻微囤积")
        elif profit_margin > 30:
            predictions.append("健康盈利，矿工可能增加囤积比例")
        elif profit_margin > 0:
            predictions.append("微利环境，矿工可能增加售出以覆盖成本")
        else:
            predictions.append("亏损环境，弱势矿工可能关机或抛售")
        
        if "抛售" in sentiment:
            predictions.append("当前抛售压力可能持续")
        
        return {
            'short_term': predictions[0] if predictions else "正常运营",
            'factors': {
                'profit_margin': f"{profit_margin:.1f}%",
                'mining_cost': f"${mining_cost:,.0f}",
                'current_price': f"${current_price:,.0f}"
            }
        }
```

### 4. Thermocap 和市场指标

#### 4.1 Thermocap

**端点**: `/thermocap`

**描述**: 累计矿工收入，代表总安全支出。

#### 4.2 市值/Thermocap 比率

**端点**: `/marketcap_thermocap_ratio`

**描述**: 市值与 Thermocap 的比率，评估相对估值。

```python
def analyze_thermocap_valuation(asset='BTC'):
    """分析 Thermocap 估值"""
    
    base_url = "https://api.glassnode.com/v1/metrics/mining/"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '24h', 's': int(time.time()) - 365*86400}
    
    # 获取 Thermocap 数据
    thermocap = requests.get(
        base_url + "thermocap",
        params=params,
        headers=headers
    ).json()
    
    # 获取市值/Thermocap 比率
    mc_tc_ratio = requests.get(
        base_url + "marketcap_thermocap_ratio",
        params=params,
        headers=headers
    ).json()
    
    current_ratio = mc_tc_ratio[-1]['v']
    
    # 历史分位数
    ratios = [d['v'] for d in mc_tc_ratio]
    percentile = sum(1 for r in ratios if r < current_ratio) / len(ratios) * 100
    
    # 估值判断
    if current_ratio > 10:
        valuation = "极度高估"
        signal = "STRONG_SELL"
    elif current_ratio > 5:
        valuation = "高估"
        signal = "SELL"
    elif current_ratio > 2:
        valuation = "合理偏高"
        signal = "NEUTRAL"
    elif current_ratio > 1:
        valuation = "合理"
        signal = "BUY"
    else:
        valuation = "低估"
        signal = "STRONG_BUY"
    
    return {
        'current_thermocap': thermocap[-1]['v'],
        'mc_tc_ratio': round(current_ratio, 2),
        'historical_percentile': f"{percentile:.1f}%",
        'valuation': valuation,
        'signal': signal,
        'interpretation': interpret_thermocap_ratio(current_ratio)
    }

def interpret_thermocap_ratio(ratio):
    """解释 Thermocap 比率"""
    
    if ratio > 10:
        return "市值远超历史安全支出，可能存在泡沫"
    elif ratio > 5:
        return "市值相对安全支出偏高，注意风险"
    elif ratio > 2:
        return "市值与安全支出比例健康"
    elif ratio > 1:
        return "市值接近历史安全支出，估值合理"
    else:
        return "市值低于历史安全支出，可能被低估"
```

### 5. 挖矿池分析

```python
class MiningPoolAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_pool_distribution(self, asset='BTC'):
        """分析矿池分布"""
        
        # 获取矿池数据（示例）
        pool_distribution = self.get_pool_distribution(asset)
        
        # 计算集中度
        top_3_share = sum(pool['hashrate_share'] for pool in pool_distribution[:3])
        top_5_share = sum(pool['hashrate_share'] for pool in pool_distribution[:5])
        
        # HHI指数（赫芬达尔指数）
        hhi = sum(pool['hashrate_share']**2 for pool in pool_distribution) * 10000
        
        # 分析去中心化程度
        if hhi > 2500:
            concentration = "高度集中 - 存在中心化风险"
            risk_level = "HIGH"
        elif hhi > 1500:
            concentration = "中度集中 - 需要关注"
            risk_level = "MEDIUM"
        else:
            concentration = "良好分散 - 去中心化程度高"
            risk_level = "LOW"
        
        # 检测潜在威胁
        threats = []
        if top_3_share > 51:
            threats.append("前3大矿池控制超过51%算力")
        if any(pool['hashrate_share'] > 40 for pool in pool_distribution):
            threats.append("单个矿池接近危险算力水平")
        
        return {
            'top_pools': [
                {
                    'name': pool['name'],
                    'share': f"{pool['hashrate_share']:.1f}%",
                    'blocks_24h': pool['blocks_mined']
                }
                for pool in pool_distribution[:5]
            ],
            'concentration_metrics': {
                'top_3_share': f"{top_3_share:.1f}%",
                'top_5_share': f"{top_5_share:.1f}%",
                'hhi_index': round(hhi),
                'assessment': concentration
            },
            'risk_level': risk_level,
            'threats': threats,
            'recommendations': self.generate_pool_recommendations(hhi, threats)
        }
    
    def generate_pool_recommendations(self, hhi, threats):
        """生成矿池相关建议"""
        
        recommendations = []
        
        if hhi > 2500:
            recommendations.append("建议矿工考虑加入较小矿池以提高去中心化")
        
        if threats:
            recommendations.append("密切关注大矿池动向，防范潜在攻击")
        
        recommendations.append("使用多个矿池分散风险")
        
        return recommendations
```

### 6. 挖矿成本模型

```python
class MiningCostModel:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def calculate_comprehensive_mining_cost(self, asset='BTC'):
        """计算综合挖矿成本"""
        
        # 获取网络数据
        hashrate = self.get_network_hashrate(asset)
        difficulty = self.get_difficulty(asset)
        block_reward = self.get_block_reward(asset)
        
        # 硬件参数（以主流矿机为例）
        miners = {
            'S19_Pro': {
                'hashrate': 110,  # TH/s
                'power': 3250,  # W
                'price': 5000,  # USD
                'efficiency': 29.5  # J/TH
            },
            'S19_XP': {
                'hashrate': 140,
                'power': 3010,
                'price': 8000,
                'efficiency': 21.5
            }
        }
        
        # 计算不同场景的成本
        scenarios = {}
        
        for miner_name, specs in miners.items():
            for electricity_price in [0.03, 0.05, 0.08, 0.12]:  # USD/kWh
                scenario_key = f"{miner_name}_{electricity_price}"
                
                # 日电费
                daily_electricity = specs['power'] * 24 * electricity_price / 1000
                
                # 预期日收益（简化）
                network_hashrate_th = hashrate / 1e12
                miner_share = specs['hashrate'] / network_hashrate_th
                daily_btc = miner_share * block_reward * 144  # 144 blocks/day
                
                # 盈亏平衡价格
                breakeven_price = daily_electricity / daily_btc if daily_btc > 0 else float('inf')
                
                # 考虑硬件折旧（2年）
                daily_depreciation = specs['price'] / 730
                total_daily_cost = daily_electricity + daily_depreciation
                
                full_breakeven = total_daily_cost / daily_btc if daily_btc > 0 else float('inf')
                
                scenarios[scenario_key] = {
                    'miner': miner_name,
                    'electricity_price': f"${electricity_price}/kWh",
                    'breakeven_price': f"${breakeven_price:,.0f}",
                    'full_breakeven': f"${full_breakeven:,.0f}",
                    'daily_cost': f"${total_daily_cost:.2f}",
                    'efficiency': specs['efficiency']
                }
        
        # 找出最优和最差场景
        best_scenario = min(scenarios.items(), 
                          key=lambda x: float(x[1]['full_breakeven'].replace('$', '').replace(',', '')) 
                          if x[1]['full_breakeven'] != '$inf' else float('inf'))
        
        worst_scenario = max(scenarios.items(), 
                           key=lambda x: float(x[1]['full_breakeven'].replace('$', '').replace(',', '')) 
                           if x[1]['full_breakeven'] != '$inf' else 0)
        
        return {
            'cost_scenarios': scenarios,
            'best_case': {
                'scenario': best_scenario[0],
                'details': best_scenario[1]
            },
            'worst_case': {
                'scenario': worst_scenario[0],
                'details': worst_scenario[1]
            },
            'industry_average': self.estimate_industry_average_cost(),
            'profitability_zones': self.define_profitability_zones(scenarios)
        }
    
    def estimate_industry_average_cost(self):
        """估算行业平均成本"""
        
        # 基于全球平均电价和主流矿机效率
        avg_electricity = 0.06  # USD/kWh
        avg_efficiency = 25  # J/TH
        
        # 简化计算
        estimated_cost = 15000  # USD per BTC
        
        return {
            'estimated_cost': f"${estimated_cost:,.0f}",
            'methodology': "基于全球平均电价和主流矿机效率",
            'confidence': "中等"
        }
    
    def define_profitability_zones(self, scenarios):
        """定义盈利区间"""
        
        zones = {
            'highly_profitable': "> $40,000",
            'profitable': "$25,000 - $40,000",
            'marginal': "$18,000 - $25,000",
            'unprofitable': "< $18,000"
        }
        
        return zones
```

### 7. 实时挖矿监控

```python
class MiningMonitor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.alert_thresholds = {
            'hashrate_drop': -10,  # 10% drop
            'difficulty_spike': 10,  # 10% increase
            'miner_outflow': 2,  # 2x normal
            'profitability_threshold': 10  # 10% margin
        }
        
    async def monitor_mining_metrics(self, asset='BTC'):
        """实时监控挖矿指标"""
        
        last_metrics = {}
        
        while True:
            try:
                current_metrics = await self.get_current_metrics(asset)
                
                # 检查算力变化
                if 'hashrate' in last_metrics:
                    hr_change = (current_metrics['hashrate'] - last_metrics['hashrate']) / last_metrics['hashrate'] * 100
                    
                    if hr_change < self.alert_thresholds['hashrate_drop']:
                        await self.send_alert(f"⚠️ 算力大幅下降: {hr_change:.1f}%")
                
                # 检查矿工流出
                if current_metrics['miner_outflow'] > self.alert_thresholds['miner_outflow']:
                    await self.send_alert(f"🚨 矿工大量抛售: {current_metrics['miner_outflow']}x 正常水平")
                
                # 检查盈利能力
                if current_metrics['profit_margin'] < self.alert_thresholds['profitability_threshold']:
                    await self.send_alert(f"💸 挖矿盈利能力低: {current_metrics['profit_margin']:.1f}%")
                
                last_metrics = current_metrics
                
                await asyncio.sleep(3600)  # 每小时检查
                
            except Exception as e:
                print(f"监控错误: {e}")
                await asyncio.sleep(300)
```

### 8. 综合挖矿仪表板

```python
class MiningDashboard:
    def __init__(self, api_key):
        self.api_key = api_key
        self.hashrate_analyzer = HashRateAnalyzer(api_key)
        self.revenue_analyzer = MinerRevenueAnalyzer(api_key)
        self.behavior_analyzer = MinerBehaviorAnalyzer(api_key)
        self.cost_model = MiningCostModel(api_key)
        
    def generate_comprehensive_report(self, asset='BTC'):
        """生成综合挖矿报告"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'asset': asset,
            'network_metrics': {},
            'economics': {},
            'behavior': {},
            'market_impact': {},
            'recommendations': []
        }
        
        # 网络指标
        report['network_metrics'] = self.hashrate_analyzer.analyze_network_hashrate(asset)
        
        # 经济指标
        report['economics'] = {
            'revenue': self.revenue_analyzer.analyze_miner_economics(asset),
            'costs': self.cost_model.calculate_comprehensive_mining_cost(asset),
            'thermocap': analyze_thermocap_valuation(asset)
        }
        
        # 矿工行为
        report['behavior'] = self.behavior_analyzer.analyze_miner_behavior(asset)
        
        # 市场影响评估
        report['market_impact'] = self.assess_market_impact(report)
        
        # 生成建议
        report['recommendations'] = self.generate_recommendations(report)
        
        return report
    
    def assess_market_impact(self, data):
        """评估对市场的影响"""
        
        impact_score = 50  # 基础分
        factors = []
        
        # 矿工抛售压力
        if data['behavior']['signal'] == 'BEARISH':
            impact_score -= 20
            factors.append("矿工抛售增加供应压力")
        elif data['behavior']['signal'] == 'BULLISH':
            impact_score += 15
            factors.append("矿工囤积减少市场供应")
        
        # 网络安全性
        if "极高" in data['network_metrics']['security_assessment']['level']:
            impact_score += 10
            factors.append("网络安全性强，增加信心")
        
        # 挖矿盈利能力
        if "高盈利" in data['economics']['revenue']['profitability']['profitability_status']:
            impact_score += 10
            factors.append("挖矿盈利良好，吸引更多算力")
        elif "亏损" in data['economics']['revenue']['profitability']['profitability_status']:
            impact_score -= 15
            factors.append("挖矿亏损可能导致抛售")
        
        # 生成评级
        if impact_score >= 70:
            rating = "积极"
        elif impact_score >= 50:
            rating = "中性"
        else:
            rating = "消极"
        
        return {
            'score': impact_score,
            'rating': rating,
            'factors': factors
        }
    
    def generate_recommendations(self, report):
        """生成投资建议"""
        
        recommendations = []
        
        # 基于矿工行为
        if report['behavior']['signal'] == 'BEARISH':
            recommendations.append({
                'type': 'CAUTION',
                'message': '矿工抛售压力大，短期谨慎',
                'action': '等待抛压缓解'
            })
        
        # 基于网络安全
        if "需关注" in report['network_metrics']['security_assessment']['level']:
            recommendations.append({
                'type': 'RISK',
                'message': '网络算力相对较低',
                'action': '关注潜在安全风险'
            })
        
        # 基于挖矿经济
        margin = report['economics']['revenue']['profitability'].get('profit_margin', '0%')
        if float(margin.strip('%')) < 20:
            recommendations.append({
                'type': 'OPPORTUNITY',
                'message': '挖矿利润率低，可能接近底部',
                'action': '考虑逢低建仓'
            })
        
        # 基于估值
        if report['economics']['thermocap']['signal'] == 'STRONG_BUY':
            recommendations.append({
                'type': 'OPPORTUNITY',
                'message': 'Thermocap 指标显示低估',
                'action': '积极配置'
            })
        
        return recommendations
```

## 常见问题

### Q1: 算力下降意味着什么？

算力下降可能因为：
- 价格下跌导致挖矿无利可图
- 电力成本上升
- 政策限制
- 设备更新换代

影响：
- 短期可能降低网络安全性
- 难度调整后其他矿工收益增加

### Q2: 如何判断挖矿是否仍然有利可图？

关键因素：
- 电力成本（最重要）
- 硬件效率
- 币价
- 网络难度

一般来说，电价低于 $0.05/kWh 的地区挖矿仍有竞争力。

### Q3: 矿工抛售对价格的影响有多大？

- 日常抛售：已被市场消化，影响有限
- 异常抛售（>2x正常）：短期负面影响
- 长期囤积后抛售：可能造成较大压力

## 最佳实践

1. **综合分析**：结合算力、收入、成本等多维度数据
2. **关注趋势**：趋势变化比绝对值更重要
3. **风险评估**：定期评估网络安全性和中心化风险
4. **成本监控**：跟踪挖矿盈亏平衡点

---

*本文档详细介绍了 Glassnode Mining API 的使用方法。挖矿数据是理解网络安全、供应动态和市场结构的关键。*