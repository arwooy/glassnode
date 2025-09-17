# ETH 2.0（以太坊2.0）API 文档

## 概述

ETH 2.0 API 提供以太坊权益证明（Proof of Stake）网络的全面数据，包括质押（Staking）指标、验证者（Validator）数据、网络参与度、收益率等。这些数据对于理解以太坊 PoS 生态系统和评估质押投资机会至关重要。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/eth2/`

## 核心端点

### 1. 质押基础指标

#### 1.1 总质押量

**端点**: `/staking_total_amount`

**描述**: 质押在信标链（Beacon Chain）上的 ETH 总量。

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/eth2/staking_total_amount?a=ETH&i=24h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

#### 1.2 质押参与率

**端点**: `/staking_participation_rate`

**描述**: 质押的 ETH 占总供应量的百分比。

```python
class ETH2StakingAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/eth2/"
        
    def analyze_staking_metrics(self):
        """分析 ETH 2.0 质押指标"""
        
        headers = {"X-Api-Key": self.api_key}
        params = {'a': 'ETH', 'i': '24h', 's': int(time.time()) - 90*86400}
        
        # 获取质押数据
        total_staked = requests.get(
            self.base_url + "staking_total_amount",
            params=params,
            headers=headers
        ).json()
        
        participation_rate = requests.get(
            self.base_url + "staking_participation_rate",
            params=params,
            headers=headers
        ).json()
        
        # 分析质押趋势
        current_staked = total_staked[-1]['v']
        staked_30d_ago = total_staked[-30]['v'] if len(total_staked) > 30 else total_staked[0]['v']
        
        staking_growth = (current_staked - staked_30d_ago) / staked_30d_ago * 100
        daily_growth_rate = staking_growth / 30
        
        # 计算锁定价值
        eth_price = self.get_eth_price()
        total_value_locked = current_staked * eth_price
        
        # 评估网络安全性
        current_participation = participation_rate[-1]['v']
        security_assessment = self.assess_network_security(current_participation)
        
        # 预测未来质押
        future_projection = self.project_future_staking(current_staked, daily_growth_rate)
        
        return {
            'current_staked': {
                'amount': f"{current_staked:,.0f} ETH",
                'value_usd': f"${total_value_locked:,.0f}",
                'participation_rate': f"{current_participation:.2f}%"
            },
            'growth_metrics': {
                '30d_growth': f"{staking_growth:.2f}%",
                'daily_growth_rate': f"{daily_growth_rate:.3f}%",
                'monthly_new_stake': f"{current_staked - staked_30d_ago:,.0f} ETH"
            },
            'security_assessment': security_assessment,
            'future_projection': future_projection,
            'market_impact': self.analyze_market_impact(current_participation, staking_growth)
        }
    
    def assess_network_security(self, participation_rate):
        """评估网络安全性"""
        
        if participation_rate > 30:
            security = "极高 - 大量 ETH 参与质押，网络非常安全"
            decentralization = "良好"
        elif participation_rate > 20:
            security = "高 - 健康的质押参与度"
            decentralization = "良好"
        elif participation_rate > 10:
            security = "中等 - 基本安全水平"
            decentralization = "需改善"
        else:
            security = "低 - 质押参与度不足"
            decentralization = "需要关注"
        
        return {
            'level': security,
            'decentralization': decentralization,
            'minimum_attack_cost': self.calculate_attack_cost(participation_rate)
        }
    
    def calculate_attack_cost(self, participation_rate):
        """计算攻击成本"""
        
        total_eth_supply = 120000000  # 大约总供应量
        staked_eth = total_eth_supply * participation_rate / 100
        
        # 33% 攻击（影响最终性）
        required_eth = staked_eth * 0.33
        eth_price = self.get_eth_price()
        
        attack_cost = required_eth * eth_price
        
        return {
            '33_percent_attack': f"${attack_cost/1e9:.2f}B",
            'required_eth': f"{required_eth:,.0f} ETH",
            'feasibility': "极低" if attack_cost > 10e9 else "低"
        }
    
    def project_future_staking(self, current, daily_rate):
        """预测未来质押量"""
        
        projections = {}
        
        for days in [30, 90, 180, 365]:
            # 复利增长模型
            future_amount = current * (1 + daily_rate/100) ** days
            projections[f"{days}d"] = {
                'amount': f"{future_amount:,.0f} ETH",
                'growth': f"{(future_amount/current - 1)*100:.1f}%"
            }
        
        return projections
```

### 2. 验证者指标

#### 2.1 活跃验证者数量

**端点**: `/validators_active_count`

**描述**: 当前活跃的验证者数量。

#### 2.2 验证者队列

**端点**: `/validators_queue_entering`

**描述**: 等待激活的验证者队列长度。

#### 2.3 验证者退出

**端点**: `/validators_exiting_count`

**描述**: 正在退出的验证者数量。

```python
class ValidatorAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_validator_dynamics(self):
        """分析验证者动态"""
        
        base_url = "https://api.glassnode.com/v1/metrics/eth2/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': 'ETH', 'i': '24h', 's': int(time.time()) - 30*86400}
        
        # 获取验证者数据
        active_validators = requests.get(
            base_url + "validators_active_count",
            params=params,
            headers=headers
        ).json()
        
        entering_queue = requests.get(
            base_url + "validators_queue_entering",
            params=params,
            headers=headers
        ).json()
        
        exiting_validators = requests.get(
            base_url + "validators_exiting_count",
            params=params,
            headers=headers
        ).json()
        
        # 分析验证者趋势
        current_active = active_validators[-1]['v']
        queue_length = entering_queue[-1]['v']
        exiting_count = exiting_validators[-1]['v']
        
        # 计算网络增长
        net_change = queue_length - exiting_count
        growth_rate = (net_change / current_active * 100) if current_active > 0 else 0
        
        # 估算等待时间
        daily_activation_limit = 1800  # 大约每天激活限制
        queue_wait_days = queue_length / daily_activation_limit if daily_activation_limit > 0 else 0
        
        # 分析退出原因
        exit_analysis = self.analyze_exit_patterns(exiting_validators)
        
        # 验证者分布
        validator_distribution = self.analyze_validator_distribution(current_active)
        
        return {
            'current_status': {
                'active_validators': current_active,
                'entering_queue': queue_length,
                'exiting_validators': exiting_count,
                'net_change': net_change
            },
            'queue_metrics': {
                'wait_time_days': round(queue_wait_days, 1),
                'daily_activations': daily_activation_limit,
                'queue_congestion': self.assess_queue_congestion(queue_length)
            },
            'growth_analysis': {
                'growth_rate': f"{growth_rate:.2f}%",
                'trend': "扩张" if net_change > 0 else "收缩" if net_change < 0 else "稳定"
            },
            'exit_analysis': exit_analysis,
            'distribution': validator_distribution
        }
    
    def analyze_exit_patterns(self, exiting_data):
        """分析验证者退出模式"""
        
        exit_values = [d['v'] for d in exiting_data]
        avg_exits = sum(exit_values) / len(exit_values)
        recent_exits = exit_values[-7:]
        
        # 检测异常退出
        if max(recent_exits) > avg_exits * 3:
            pattern = "异常高退出 - 可能有重大事件"
            risk = "HIGH"
        elif sum(recent_exits) / 7 > avg_exits * 1.5:
            pattern = "退出增加 - 需要关注"
            risk = "MEDIUM"
        else:
            pattern = "正常退出水平"
            risk = "LOW"
        
        return {
            'pattern': pattern,
            'risk_level': risk,
            '7d_avg_exits': sum(recent_exits) / 7,
            '30d_avg_exits': avg_exits
        }
    
    def assess_queue_congestion(self, queue_length):
        """评估队列拥堵程度"""
        
        if queue_length > 50000:
            return "严重拥堵 - 等待时间超过1个月"
        elif queue_length > 20000:
            return "中度拥堵 - 等待时间2-4周"
        elif queue_length > 5000:
            return "轻微拥堵 - 等待时间1周左右"
        else:
            return "流畅 - 快速激活"
    
    def analyze_validator_distribution(self, total_validators):
        """分析验证者分布"""
        
        # 估算不同类型验证者
        eth_per_validator = 32
        
        estimated_distribution = {
            'individual_stakers': {
                'percentage': 30,
                'count': int(total_validators * 0.3),
                'eth_staked': int(total_validators * 0.3 * eth_per_validator)
            },
            'staking_pools': {
                'percentage': 45,
                'count': int(total_validators * 0.45),
                'eth_staked': int(total_validators * 0.45 * eth_per_validator)
            },
            'institutions': {
                'percentage': 25,
                'count': int(total_validators * 0.25),
                'eth_staked': int(total_validators * 0.25 * eth_per_validator)
            }
        }
        
        return estimated_distribution
```

### 3. 质押收益指标

#### 3.1 质押年化收益率（APR）

**端点**: `/staking_apr`

**描述**: 质押的年化收益率。

#### 3.2 验证者收益

**端点**: `/validator_rewards_sum`

**描述**: 验证者获得的总奖励。

```python
class StakingYieldAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_staking_yields(self):
        """分析质押收益"""
        
        base_url = "https://api.glassnode.com/v1/metrics/eth2/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': 'ETH', 'i': '24h', 's': int(time.time()) - 365*86400}
        
        # 获取收益率数据
        apr_data = requests.get(
            base_url + "staking_apr",
            params=params,
            headers=headers
        ).json()
        
        rewards_data = requests.get(
            base_url + "validator_rewards_sum",
            params=params,
            headers=headers
        ).json()
        
        # 分析收益率趋势
        current_apr = apr_data[-1]['v']
        apr_values = [d['v'] for d in apr_data]
        
        # 计算统计数据
        avg_apr = sum(apr_values) / len(apr_values)
        max_apr = max(apr_values)
        min_apr = min(apr_values)
        
        # 计算实际收益（考虑 MEV 和小费）
        real_yield = self.calculate_real_yield(current_apr)
        
        # 与其他投资比较
        yield_comparison = self.compare_yields(current_apr)
        
        # 预测未来收益率
        future_apr = self.predict_future_apr(apr_values)
        
        # 计算复利效应
        compound_returns = self.calculate_compound_returns(current_apr)
        
        return {
            'current_yields': {
                'base_apr': f"{current_apr:.2f}%",
                'real_apr': f"{real_yield:.2f}%",
                'daily_rate': f"{current_apr/365:.4f}%"
            },
            'historical_stats': {
                'avg_apr': f"{avg_apr:.2f}%",
                'max_apr': f"{max_apr:.2f}%",
                'min_apr': f"{min_apr:.2f}%",
                'volatility': f"{self.calculate_volatility(apr_values):.2f}%"
            },
            'yield_comparison': yield_comparison,
            'future_projection': future_apr,
            'compound_returns': compound_returns,
            'risk_adjusted_return': self.calculate_risk_adjusted_return(current_apr, apr_values)
        }
    
    def calculate_real_yield(self, base_apr):
        """计算实际收益（包括 MEV）"""
        
        # MEV 和优先费估算（约占基础收益的 20-30%）
        mev_boost = base_apr * 0.25
        
        # 扣除验证成本（服务器、维护等）
        operational_cost = 0.5  # 0.5% 年成本
        
        real_yield = base_apr + mev_boost - operational_cost
        
        return real_yield
    
    def compare_yields(self, eth_apr):
        """与其他投资产品比较"""
        
        comparisons = {
            'eth_staking': eth_apr,
            'us_treasury_10y': 4.5,  # 示例值
            'sp500_dividend': 1.5,
            'defi_stable_farming': 8.0,
            'btc_holding': 0  # 无收益
        }
        
        eth_premium = eth_apr - comparisons['us_treasury_10y']
        
        return {
            'comparisons': comparisons,
            'risk_premium': f"{eth_premium:.2f}%",
            'attractiveness': self.assess_yield_attractiveness(eth_apr, comparisons)
        }
    
    def assess_yield_attractiveness(self, apr, comparisons):
        """评估收益吸引力"""
        
        if apr > comparisons['defi_stable_farming']:
            return "极具吸引力 - 超过 DeFi 稳定币收益"
        elif apr > comparisons['us_treasury_10y'] + 2:
            return "有吸引力 - 风险溢价合理"
        elif apr > comparisons['us_treasury_10y']:
            return "一般 - 略高于无风险利率"
        else:
            return "较低 - 考虑其他投资选择"
    
    def calculate_compound_returns(self, apr):
        """计算复利回报"""
        
        initial_stake = 32  # ETH
        
        periods = {
            '1_year': 1,
            '2_years': 2,
            '5_years': 5,
            '10_years': 10
        }
        
        compound_returns = {}
        
        for period_name, years in periods.items():
            # 假设收益自动复投
            final_amount = initial_stake * (1 + apr/100) ** years
            total_return = (final_amount - initial_stake) / initial_stake * 100
            
            compound_returns[period_name] = {
                'final_amount': f"{final_amount:.2f} ETH",
                'total_return': f"{total_return:.1f}%",
                'annualized': f"{apr:.2f}%"
            }
        
        return compound_returns
```

### 4. 网络性能指标

#### 4.1 网络参与率

**端点**: `/network_participation_rate`

**描述**: 验证者的网络参与率，反映网络健康度。

#### 4.2 区块提议成功率

**端点**: `/block_proposal_rate`

**描述**: 成功提议区块的比率。

```python
class NetworkPerformanceAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_network_performance(self):
        """分析网络性能"""
        
        base_url = "https://api.glassnode.com/v1/metrics/eth2/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': 'ETH', 'i': '1h', 's': int(time.time()) - 7*86400}
        
        # 获取性能数据
        participation_rate = self.get_data("network_participation_rate", params, headers)
        proposal_rate = self.get_data("block_proposal_rate", params, headers)
        
        # 分析参与率
        current_participation = participation_rate[-1]['v']
        avg_participation = sum(d['v'] for d in participation_rate) / len(participation_rate)
        
        # 检测网络问题
        network_issues = []
        
        if current_participation < 95:
            network_issues.append("参与率低于理想水平")
        
        if current_participation < 90:
            network_issues.append("警告：参与率过低，可能影响最终性")
        
        # 分析区块提议
        current_proposal_rate = proposal_rate[-1]['v']
        
        # 计算网络效率
        network_efficiency = (current_participation * current_proposal_rate) / 100
        
        # 健康度评分
        health_score = self.calculate_health_score(
            current_participation,
            current_proposal_rate,
            network_issues
        )
        
        return {
            'participation': {
                'current': f"{current_participation:.2f}%",
                '7d_average': f"{avg_participation:.2f}%",
                'status': self.get_participation_status(current_participation)
            },
            'block_proposals': {
                'success_rate': f"{current_proposal_rate:.2f}%",
                'missed_blocks': f"{100 - current_proposal_rate:.2f}%"
            },
            'network_efficiency': f"{network_efficiency:.2f}%",
            'health_score': health_score,
            'issues': network_issues if network_issues else ["网络运行正常"],
            'recommendations': self.generate_performance_recommendations(health_score)
        }
    
    def get_participation_status(self, rate):
        """获取参与率状态"""
        
        if rate >= 99:
            return "优秀 - 网络高度活跃"
        elif rate >= 95:
            return "良好 - 健康参与度"
        elif rate >= 90:
            return "一般 - 基本满足要求"
        elif rate >= 85:
            return "较差 - 需要改善"
        else:
            return "危险 - 网络安全风险"
    
    def calculate_health_score(self, participation, proposal_rate, issues):
        """计算网络健康度评分"""
        
        score = 0
        
        # 参与率评分 (0-50)
        if participation >= 99:
            score += 50
        elif participation >= 95:
            score += 40
        elif participation >= 90:
            score += 25
        else:
            score += max(0, (participation - 80) * 2.5)
        
        # 提议成功率评分 (0-30)
        score += min(30, proposal_rate * 0.3)
        
        # 问题扣分 (0-20)
        score += 20 - (len(issues) * 10)
        
        return min(100, max(0, score))
```

### 5. 流动性质押分析

```python
class LiquidStakingAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_liquid_staking(self):
        """分析流动性质押"""
        
        # 主要流动性质押协议
        protocols = {
            'lido': {'token': 'stETH', 'market_share': 0.32},
            'rocket_pool': {'token': 'rETH', 'market_share': 0.08},
            'frax': {'token': 'frxETH', 'market_share': 0.05},
            'stakewise': {'token': 'sETH2', 'market_share': 0.02}
        }
        
        total_liquid_staked = self.get_liquid_staking_total()
        
        # 分析每个协议
        protocol_analysis = {}
        
        for name, info in protocols.items():
            protocol_tvl = total_liquid_staked * info['market_share']
            
            protocol_analysis[name] = {
                'tvl': f"{protocol_tvl:,.0f} ETH",
                'market_share': f"{info['market_share']*100:.1f}%",
                'token': info['token'],
                'premium_discount': self.get_token_premium(info['token']),
                'risks': self.assess_protocol_risks(name)
            }
        
        # 计算去中心化程度
        decentralization = self.calculate_decentralization(protocols)
        
        return {
            'total_liquid_staked': f"{total_liquid_staked:,.0f} ETH",
            'protocols': protocol_analysis,
            'decentralization': decentralization,
            'market_dynamics': self.analyze_liquid_staking_market(),
            'recommendations': self.generate_liquid_staking_recommendations(protocol_analysis)
        }
    
    def get_token_premium(self, token):
        """获取流动性质押代币溢价/折价"""
        
        # 示例数据
        premiums = {
            'stETH': -0.2,  # 0.2% 折价
            'rETH': 0.1,    # 0.1% 溢价
            'frxETH': -0.15,
            'sETH2': -0.3
        }
        
        premium = premiums.get(token, 0)
        
        if premium > 0:
            return f"+{premium:.2f}% 溢价"
        else:
            return f"{premium:.2f}% 折价"
    
    def assess_protocol_risks(self, protocol):
        """评估协议风险"""
        
        risks = {
            'lido': ["中心化风险", "治理风险"],
            'rocket_pool': ["技术复杂性", "流动性较低"],
            'frax': ["算法风险", "新协议"],
            'stakewise': ["规模较小", "流动性风险"]
        }
        
        return risks.get(protocol, ["未知风险"])
    
    def calculate_decentralization(self, protocols):
        """计算去中心化程度"""
        
        # HHI 指数
        hhi = sum(p['market_share']**2 for p in protocols.values()) * 10000
        
        if hhi > 3000:
            level = "低 - 高度集中"
        elif hhi > 1500:
            level = "中 - 适度集中"
        else:
            level = "高 - 良好分散"
        
        return {
            'hhi_index': round(hhi),
            'level': level,
            'largest_protocol': max(protocols.items(), key=lambda x: x[1]['market_share'])[0]
        }
```

### 6. 提款（Withdrawals）分析

```python
class WithdrawalAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_withdrawals(self):
        """分析提款情况"""
        
        base_url = "https://api.glassnode.com/v1/metrics/eth2/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': 'ETH', 'i': '24h', 's': int(time.time()) - 30*86400}
        
        # 获取提款数据
        withdrawal_queue = self.get_data("withdrawal_queue_length", params, headers)
        daily_withdrawals = self.get_data("withdrawals_daily_sum", params, headers)
        
        # 分析提款趋势
        current_queue = withdrawal_queue[-1]['v']
        current_daily = daily_withdrawals[-1]['v']
        
        # 计算平均值
        avg_daily = sum(d['v'] for d in daily_withdrawals) / len(daily_withdrawals)
        
        # 提款压力评估
        if current_daily > avg_daily * 2:
            pressure = "高 - 大量提款请求"
            market_impact = "可能造成卖压"
        elif current_daily > avg_daily * 1.5:
            pressure = "中 - 提款增加"
            market_impact = "轻微卖压"
        else:
            pressure = "低 - 正常提款"
            market_impact = "影响有限"
        
        # 计算提款等待时间
        daily_withdrawal_limit = 115200  # ETH per day (approx)
        wait_time_days = current_queue / daily_withdrawal_limit if daily_withdrawal_limit > 0 else 0
        
        return {
            'current_status': {
                'queue_length': f"{current_queue:,.0f} ETH",
                'daily_withdrawals': f"{current_daily:,.0f} ETH",
                'wait_time': f"{wait_time_days:.1f} days"
            },
            'withdrawal_pressure': pressure,
            'market_impact': market_impact,
            'trend_analysis': {
                '30d_avg': f"{avg_daily:,.0f} ETH",
                'current_vs_avg': f"{(current_daily/avg_daily - 1)*100:+.1f}%"
            },
            'recommendations': self.generate_withdrawal_recommendations(pressure, wait_time_days)
        }
    
    def generate_withdrawal_recommendations(self, pressure, wait_time):
        """生成提款相关建议"""
        
        recommendations = []
        
        if pressure == "高":
            recommendations.append("警惕短期卖压，可能影响 ETH 价格")
            recommendations.append("考虑延迟大额买入")
        
        if wait_time > 7:
            recommendations.append("提款队列较长，计划提款需提前准备")
        
        if wait_time < 1:
            recommendations.append("提款快速处理，流动性良好")
        
        return recommendations
```

### 7. 综合仪表板

```python
class ETH2Dashboard:
    def __init__(self, api_key):
        self.api_key = api_key
        self.staking_analyzer = ETH2StakingAnalyzer(api_key)
        self.validator_analyzer = ValidatorAnalyzer(api_key)
        self.yield_analyzer = StakingYieldAnalyzer(api_key)
        self.performance_analyzer = NetworkPerformanceAnalyzer(api_key)
        self.liquid_staking_analyzer = LiquidStakingAnalyzer(api_key)
        self.withdrawal_analyzer = WithdrawalAnalyzer(api_key)
        
    def generate_comprehensive_report(self):
        """生成 ETH 2.0 综合报告"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'network': 'Ethereum 2.0',
            'staking_overview': {},
            'validator_status': {},
            'yield_analysis': {},
            'network_health': {},
            'liquid_staking': {},
            'withdrawals': {},
            'investment_signals': []
        }
        
        # 收集所有数据
        report['staking_overview'] = self.staking_analyzer.analyze_staking_metrics()
        report['validator_status'] = self.validator_analyzer.analyze_validator_dynamics()
        report['yield_analysis'] = self.yield_analyzer.analyze_staking_yields()
        report['network_health'] = self.performance_analyzer.analyze_network_performance()
        report['liquid_staking'] = self.liquid_staking_analyzer.analyze_liquid_staking()
        report['withdrawals'] = self.withdrawal_analyzer.analyze_withdrawals()
        
        # 生成投资信号
        report['investment_signals'] = self.generate_investment_signals(report)
        
        # 计算综合评分
        report['overall_assessment'] = self.calculate_overall_assessment(report)
        
        return report
    
    def generate_investment_signals(self, data):
        """生成投资信号"""
        
        signals = []
        
        # 基于收益率
        current_apr = float(data['yield_analysis']['current_yields']['base_apr'].strip('%'))
        if current_apr > 5:
            signals.append({
                'type': 'YIELD',
                'signal': 'POSITIVE',
                'message': '质押收益率有吸引力',
                'confidence': 'HIGH'
            })
        
        # 基于网络健康度
        health_score = data['network_health']['health_score']
        if health_score > 80:
            signals.append({
                'type': 'NETWORK',
                'signal': 'POSITIVE',
                'message': '网络健康运行',
                'confidence': 'HIGH'
            })
        
        # 基于提款压力
        if data['withdrawals']['withdrawal_pressure'] == "高":
            signals.append({
                'type': 'LIQUIDITY',
                'signal': 'NEGATIVE',
                'message': '提款压力可能造成短期卖压',
                'confidence': 'MEDIUM'
            })
        
        # 基于验证者趋势
        if data['validator_status']['growth_analysis']['trend'] == "扩张":
            signals.append({
                'type': 'ADOPTION',
                'signal': 'POSITIVE',
                'message': '验证者持续增长，采用率提高',
                'confidence': 'HIGH'
            })
        
        return signals
    
    def calculate_overall_assessment(self, data):
        """计算总体评估"""
        
        score = 0
        factors = []
        
        # 收益率因素 (0-25)
        apr = float(data['yield_analysis']['current_yields']['base_apr'].strip('%'))
        if apr > 5:
            score += 20
            factors.append("收益率有吸引力")
        elif apr > 3:
            score += 10
        
        # 网络健康因素 (0-25)
        health = data['network_health']['health_score']
        score += health * 0.25
        if health > 80:
            factors.append("网络健康度优秀")
        
        # 增长因素 (0-25)
        if data['validator_status']['growth_analysis']['trend'] == "扩张":
            score += 20
            factors.append("验证者快速增长")
        elif data['validator_status']['growth_analysis']['trend'] == "稳定":
            score += 10
        
        # 流动性因素 (0-25)
        if data['withdrawals']['withdrawal_pressure'] == "低":
            score += 20
            factors.append("提款压力低")
        elif data['withdrawals']['withdrawal_pressure'] == "中":
            score += 10
        
        # 生成评级
        if score >= 80:
            rating = "优秀"
            recommendation = "强烈推荐参与质押"
        elif score >= 60:
            rating = "良好"
            recommendation = "推荐参与质押"
        elif score >= 40:
            rating = "一般"
            recommendation = "可考虑参与"
        else:
            rating = "较差"
            recommendation = "谨慎参与"
        
        return {
            'score': round(score),
            'rating': rating,
            'key_factors': factors,
            'recommendation': recommendation
        }
```

## 常见问题

### Q1: 质押 ETH 的风险有哪些？

主要风险：
- **罚没风险**：验证者离线或恶意行为可能导致 ETH 被罚没
- **流动性风险**：质押的 ETH 需要等待才能提取
- **技术风险**：软件错误或配置问题
- **市场风险**：ETH 价格波动

### Q2: 如何选择质押方式？

选项对比：
- **自行运行节点**：收益最高，但需要技术能力和 32 ETH
- **质押池**：门槛低，但收益略低且有协议风险
- **中心化交易所**：方便但有托管风险
- **流动性质押**：保持流动性但有智能合约风险

### Q3: 收益率会如何变化？

影响因素：
- 总质押量增加 → 收益率下降
- 网络活动增加 → MEV 收益增加
- 验证者表现 → 影响实际收益

## 最佳实践

1. **分散风险**：不要将所有 ETH 放在一个验证者或协议
2. **监控性能**：定期检查验证者表现和网络健康度
3. **了解税务**：质押奖励可能有税务影响
4. **长期视角**：质押适合长期投资者

---

*本文档详细介绍了 Glassnode ETH 2.0 API 的使用方法。ETH 2.0 数据对于理解以太坊 PoS 生态系统和评估质押机会至关重要。*