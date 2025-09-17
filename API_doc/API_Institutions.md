# Institutions（机构）API 文档

## 概述

Institutions API 提供机构投资者在加密货币市场的活动数据，包括机构持仓、大额交易、托管服务使用情况、ETF 流动等。这些数据帮助了解"聪明钱"的动向和机构采用趋势。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/institutions/`

## 核心端点

### 1. 机构持仓

#### 1.1 机构总持仓

**端点**: `/holdings_sum`

**描述**: 已知机构实体持有的总量。

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/institutions/holdings_sum?a=BTC&i=24h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

#### 1.2 机构持仓变化

**端点**: `/holdings_change`

**描述**: 机构持仓的净变化。

```python
class InstitutionalHoldingsAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/institutions/"
        
    def analyze_institutional_holdings(self, asset='BTC'):
        """分析机构持仓"""
        
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h', 's': int(time.time()) - 90*86400}
        
        # 获取持仓数据
        holdings_sum = requests.get(
            self.base_url + "holdings_sum",
            params=params,
            headers=headers
        ).json()
        
        holdings_change = requests.get(
            self.base_url + "holdings_change",
            params=params,
            headers=headers
        ).json()
        
        # 分析当前状态
        current_holdings = holdings_sum[-1]['v']
        recent_change = sum(d['v'] for d in holdings_change[-30:])  # 30天变化
        
        # 计算持仓趋势
        holdings_trend = self.analyze_holdings_trend(holdings_sum)
        
        # 评估机构情绪
        institutional_sentiment = self.assess_institutional_sentiment(holdings_change)
        
        # 计算机构占比
        total_supply = self.get_total_supply(asset)
        institutional_percentage = (current_holdings / total_supply * 100) if total_supply > 0 else 0
        
        # 识别累积/分配阶段
        accumulation_phase = self.identify_accumulation_phase(holdings_change)
        
        return {
            'current_holdings': {
                'amount': f"{current_holdings:,.0f} {asset}",
                'usd_value': f"${current_holdings * self.get_asset_price(asset):,.0f}",
                'supply_percentage': f"{institutional_percentage:.2f}%"
            },
            'recent_activity': {
                '30d_change': f"{recent_change:,.0f} {asset}",
                'direction': '累积' if recent_change > 0 else '分配',
                'intensity': self.calculate_activity_intensity(recent_change, current_holdings)
            },
            'trend_analysis': holdings_trend,
            'sentiment': institutional_sentiment,
            'accumulation_phase': accumulation_phase,
            'market_impact': self.assess_market_impact(institutional_percentage, recent_change)
        }
    
    def analyze_holdings_trend(self, holdings_data):
        """分析持仓趋势"""
        
        values = [d['v'] for d in holdings_data]
        
        # 计算移动平均
        ma_7 = sum(values[-7:]) / 7 if len(values) >= 7 else values[-1]
        ma_30 = sum(values[-30:]) / 30 if len(values) >= 30 else ma_7
        
        # 判断趋势
        if ma_7 > ma_30 * 1.05:
            trend = "强劲上升"
            signal = "BULLISH"
        elif ma_7 > ma_30:
            trend = "温和上升"
            signal = "SLIGHTLY_BULLISH"
        elif ma_7 < ma_30 * 0.95:
            trend = "快速下降"
            signal = "BEARISH"
        else:
            trend = "横盘整理"
            signal = "NEUTRAL"
        
        # 计算增长率
        if len(values) >= 30:
            growth_rate = (values[-1] - values[-30]) / values[-30] * 100
        else:
            growth_rate = 0
        
        return {
            'direction': trend,
            'signal': signal,
            '30d_growth_rate': f"{growth_rate:.2f}%",
            'momentum': self.calculate_momentum(values)
        }
    
    def assess_institutional_sentiment(self, change_data):
        """评估机构情绪"""
        
        recent_changes = [d['v'] for d in change_data[-7:]]  # 最近7天
        
        # 统计买入/卖出天数
        buy_days = sum(1 for c in recent_changes if c > 0)
        sell_days = sum(1 for c in recent_changes if c < 0)
        
        # 计算净流入
        net_flow = sum(recent_changes)
        
        # 判断情绪
        if buy_days > 5 and net_flow > 0:
            sentiment = "极度看涨"
            confidence = "HIGH"
        elif buy_days > sell_days and net_flow > 0:
            sentiment = "看涨"
            confidence = "MEDIUM"
        elif sell_days > buy_days and net_flow < 0:
            sentiment = "看跌"
            confidence = "MEDIUM"
        elif sell_days > 5 and net_flow < 0:
            sentiment = "极度看跌"
            confidence = "HIGH"
        else:
            sentiment = "中性"
            confidence = "LOW"
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'buy_pressure': buy_days / 7 * 100,
            'sell_pressure': sell_days / 7 * 100,
            '7d_net_flow': net_flow
        }
    
    def identify_accumulation_phase(self, change_data):
        """识别累积/分配阶段"""
        
        # 分析最近30天的数据
        recent_30d = [d['v'] for d in change_data[-30:]] if len(change_data) >= 30 else [d['v'] for d in change_data]
        
        # 计算累积强度
        positive_days = sum(1 for c in recent_30d if c > 0)
        total_accumulation = sum(c for c in recent_30d if c > 0)
        total_distribution = abs(sum(c for c in recent_30d if c < 0))
        
        accumulation_ratio = positive_days / len(recent_30d)
        
        if accumulation_ratio > 0.7 and total_accumulation > total_distribution * 2:
            phase = "强烈累积期"
            description = "机构大量买入，强烈看涨信号"
        elif accumulation_ratio > 0.6:
            phase = "累积期"
            description = "机构净买入，看涨信号"
        elif accumulation_ratio < 0.3:
            phase = "分配期"
            description = "机构净卖出，谨慎信号"
        elif accumulation_ratio < 0.4:
            phase = "轻微分配期"
            description = "机构减持，观望信号"
        else:
            phase = "平衡期"
            description = "机构买卖平衡"
        
        return {
            'phase': phase,
            'description': description,
            'accumulation_ratio': f"{accumulation_ratio*100:.1f}%",
            'net_accumulation': total_accumulation - total_distribution
        }
```

### 2. 大额交易监控

#### 2.1 机构级别交易

**端点**: `/large_transactions_count`

**描述**: 大额交易（>$10M）的数量。

```python
class InstitutionalTransactionAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_whale_transactions(self, asset='BTC'):
        """分析鲸鱼交易"""
        
        base_url = "https://api.glassnode.com/v1/metrics/institutions/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '1h', 's': int(time.time()) - 7*86400}
        
        # 获取大额交易数据
        large_tx_count = requests.get(
            base_url + "large_transactions_count",
            params=params,
            headers=headers
        ).json()
        
        # 分析交易模式
        tx_patterns = self.identify_transaction_patterns(large_tx_count)
        
        # 检测异常活动
        anomalies = self.detect_unusual_activity(large_tx_count)
        
        # 评估市场影响
        market_impact = self.assess_transaction_impact(large_tx_count)
        
        # OTC vs 交易所分析
        otc_analysis = self.analyze_otc_activity(large_tx_count)
        
        return {
            'recent_activity': {
                '24h_count': sum(d['v'] for d in large_tx_count[-24:]),
                '7d_total': sum(d['v'] for d in large_tx_count),
                'hourly_average': sum(d['v'] for d in large_tx_count) / len(large_tx_count)
            },
            'patterns': tx_patterns,
            'anomalies': anomalies,
            'market_impact': market_impact,
            'otc_analysis': otc_analysis,
            'trading_signals': self.generate_trading_signals(tx_patterns, anomalies)
        }
    
    def identify_transaction_patterns(self, tx_data):
        """识别交易模式"""
        
        patterns = []
        hourly_counts = [d['v'] for d in tx_data]
        
        # 检测活跃时段
        active_hours = self.find_active_periods(hourly_counts)
        if active_hours:
            patterns.append({
                'type': 'active_periods',
                'description': f"高活跃时段: {active_hours}",
                'implication': '机构交易集中时段'
            })
        
        # 检测累积模式
        if self.detect_accumulation_pattern(hourly_counts):
            patterns.append({
                'type': 'accumulation',
                'description': '持续的大额买入',
                'implication': '机构累积阶段'
            })
        
        # 检测分配模式
        if self.detect_distribution_pattern(hourly_counts):
            patterns.append({
                'type': 'distribution',
                'description': '频繁的大额卖出',
                'implication': '机构获利了结'
            })
        
        return patterns
    
    def detect_unusual_activity(self, tx_data):
        """检测异常活动"""
        
        counts = [d['v'] for d in tx_data]
        mean = sum(counts) / len(counts)
        std_dev = (sum((x - mean) ** 2 for x in counts) / len(counts)) ** 0.5
        
        anomalies = []
        
        for i, count in enumerate(counts):
            if count > mean + 2 * std_dev:
                anomalies.append({
                    'index': i,
                    'count': count,
                    'severity': 'HIGH' if count > mean + 3 * std_dev else 'MEDIUM',
                    'description': f"异常高交易量: {count} (平均: {mean:.1f})"
                })
        
        return anomalies
```

### 3. 托管服务分析

#### 3.1 托管余额

**端点**: `/custody_balance`

**描述**: 机构托管服务中的总余额。

```python
class CustodyAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_custody_services(self, asset='BTC'):
        """分析托管服务"""
        
        base_url = "https://api.glassnode.com/v1/metrics/institutions/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h', 's': int(time.time()) - 90*86400}
        
        # 获取托管数据
        custody_balance = requests.get(
            base_url + "custody_balance",
            params=params,
            headers=headers
        ).json()
        
        # 分析托管趋势
        current_balance = custody_balance[-1]['v']
        balance_30d_ago = custody_balance[-30]['v'] if len(custody_balance) > 30 else custody_balance[0]['v']
        
        growth = (current_balance - balance_30d_ago) / balance_30d_ago * 100 if balance_30d_ago > 0 else 0
        
        # 托管服务提供商分析
        custody_providers = self.analyze_custody_providers()
        
        # 安全性评估
        security_assessment = self.assess_custody_security(current_balance)
        
        # 机构采用率
        adoption_metrics = self.calculate_institutional_adoption(custody_balance)
        
        return {
            'custody_overview': {
                'total_balance': f"{current_balance:,.0f} {asset}",
                'usd_value': f"${current_balance * self.get_asset_price(asset):,.0f}",
                '30d_growth': f"{growth:.2f}%"
            },
            'providers': custody_providers,
            'security': security_assessment,
            'adoption': adoption_metrics,
            'trends': self.analyze_custody_trends(custody_balance)
        }
    
    def analyze_custody_providers(self):
        """分析托管服务提供商"""
        
        # 主要托管商（示例数据）
        providers = {
            'coinbase_custody': {
                'estimated_share': 35,
                'clients': '机构投资者、对冲基金',
                'features': '冷存储、保险、合规'
            },
            'grayscale': {
                'estimated_share': 25,
                'clients': '信托投资者',
                'features': 'GBTC、机构级产品'
            },
            'bakkt': {
                'estimated_share': 15,
                'clients': '传统金融机构',
                'features': '实物交割期货、托管'
            },
            'others': {
                'estimated_share': 25,
                'clients': '多样化',
                'features': '各种服务'
            }
        }
        
        return providers
    
    def assess_custody_security(self, balance):
        """评估托管安全性"""
        
        # 基于余额评估风险
        if balance > 1000000:  # > 100万币
            risk_level = "极高价值目标"
            security_requirement = "最高级别安全措施必需"
        elif balance > 100000:
            risk_level = "高价值目标"
            security_requirement = "企业级安全标准"
        elif balance > 10000:
            risk_level = "中等价值"
            security_requirement = "标准安全措施"
        else:
            risk_level = "低风险"
            security_requirement = "基础安全即可"
        
        return {
            'risk_level': risk_level,
            'security_requirement': security_requirement,
            'recommendations': [
                '多签名钱包',
                '冷存储为主',
                '定期审计',
                '保险覆盖'
            ]
        }
```

### 4. ETF 和基金流动

#### 4.1 ETF 流入流出

**端点**: `/etf_flows`

**描述**: ETF 产品的资金流动。

```python
class ETFAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_etf_flows(self, asset='BTC'):
        """分析 ETF 资金流动"""
        
        base_url = "https://api.glassnode.com/v1/metrics/institutions/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h', 's': int(time.time()) - 30*86400}
        
        # 获取 ETF 流动数据
        etf_flows = requests.get(
            base_url + "etf_flows",
            params=params,
            headers=headers
        ).json()
        
        # 分析流动趋势
        total_inflows = sum(d['v'] for d in etf_flows if d['v'] > 0)
        total_outflows = abs(sum(d['v'] for d in etf_flows if d['v'] < 0))
        net_flows = total_inflows - total_outflows
        
        # 识别流动模式
        flow_patterns = self.identify_flow_patterns(etf_flows)
        
        # 评估市场情绪
        etf_sentiment = self.assess_etf_sentiment(net_flows, flow_patterns)
        
        # 对价格的影响
        price_impact = self.estimate_price_impact(net_flows)
        
        return {
            'flow_summary': {
                '30d_inflows': f"{total_inflows:,.0f} {asset}",
                '30d_outflows': f"{total_outflows:,.0f} {asset}",
                '30d_net_flows': f"{net_flows:+,.0f} {asset}",
                'flow_ratio': total_inflows / total_outflows if total_outflows > 0 else float('inf')
            },
            'patterns': flow_patterns,
            'sentiment': etf_sentiment,
            'price_impact': price_impact,
            'major_etfs': self.analyze_major_etfs(),
            'recommendations': self.generate_etf_recommendations(net_flows, etf_sentiment)
        }
    
    def identify_flow_patterns(self, flows_data):
        """识别流动模式"""
        
        flows = [d['v'] for d in flows_data]
        patterns = []
        
        # 连续流入/流出
        consecutive_inflows = 0
        consecutive_outflows = 0
        current_streak = 0
        current_direction = None
        
        for flow in flows:
            if flow > 0:
                if current_direction == 'inflow':
                    current_streak += 1
                else:
                    current_direction = 'inflow'
                    current_streak = 1
                consecutive_inflows = max(consecutive_inflows, current_streak)
            elif flow < 0:
                if current_direction == 'outflow':
                    current_streak += 1
                else:
                    current_direction = 'outflow'
                    current_streak = 1
                consecutive_outflows = max(consecutive_outflows, current_streak)
        
        if consecutive_inflows > 5:
            patterns.append({
                'type': 'sustained_inflows',
                'duration': f"{consecutive_inflows} days",
                'implication': '持续的机构兴趣'
            })
        
        if consecutive_outflows > 5:
            patterns.append({
                'type': 'sustained_outflows',
                'duration': f"{consecutive_outflows} days",
                'implication': '机构撤退迹象'
            })
        
        # 波动性分析
        volatility = self.calculate_flow_volatility(flows)
        if volatility > 0.5:
            patterns.append({
                'type': 'high_volatility',
                'description': '流动高度不稳定',
                'implication': '市场不确定性高'
            })
        
        return patterns
    
    def analyze_major_etfs(self):
        """分析主要 ETF 产品"""
        
        major_etfs = {
            'GBTC': {
                'name': 'Grayscale Bitcoin Trust',
                'aum': '$25B',
                'premium_discount': '-15%',
                'status': '申请转换为现货 ETF'
            },
            'BITO': {
                'name': 'ProShares Bitcoin Strategy ETF',
                'aum': '$1.5B',
                'type': '期货 ETF',
                'status': '活跃交易'
            },
            'Spot_ETF': {
                'name': '现货 ETF（待批准）',
                'status': '多个申请待审',
                'potential_impact': '可能带来数百亿美元流入'
            }
        }
        
        return major_etfs
```

### 5. 机构交易策略分析

```python
class InstitutionalStrategyAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_institutional_strategies(self, asset='BTC'):
        """分析机构交易策略"""
        
        # 收集各类数据
        holdings_data = self.get_holdings_data(asset)
        transaction_data = self.get_transaction_data(asset)
        flow_data = self.get_flow_data(asset)
        
        # 识别策略类型
        strategies = self.identify_strategies(holdings_data, transaction_data, flow_data)
        
        # 分析时机选择
        timing_analysis = self.analyze_entry_exit_timing(transaction_data)
        
        # 仓位管理分析
        position_management = self.analyze_position_management(holdings_data)
        
        # 风险管理策略
        risk_strategies = self.analyze_risk_management(holdings_data, transaction_data)
        
        return {
            'identified_strategies': strategies,
            'timing_analysis': timing_analysis,
            'position_management': position_management,
            'risk_strategies': risk_strategies,
            'smart_money_indicators': self.generate_smart_money_indicators(strategies, timing_analysis)
        }
    
    def identify_strategies(self, holdings, transactions, flows):
        """识别机构策略"""
        
        strategies = []
        
        # 买入并持有策略
        if self.detect_buy_and_hold(holdings):
            strategies.append({
                'type': 'buy_and_hold',
                'description': '长期持有策略',
                'characteristics': '低换手率，稳定增持',
                'typical_players': '养老基金、保险公司'
            })
        
        # 动量交易策略
        if self.detect_momentum_trading(transactions):
            strategies.append({
                'type': 'momentum_trading',
                'description': '追涨杀跌策略',
                'characteristics': '在趋势确立后入场',
                'typical_players': '对冲基金、量化基金'
            })
        
        # 套利策略
        if self.detect_arbitrage_activity(transactions, flows):
            strategies.append({
                'type': 'arbitrage',
                'description': '跨市场套利',
                'characteristics': '高频交易，小幅获利',
                'typical_players': '做市商、高频交易公司'
            })
        
        # 价值投资策略
        if self.detect_value_investing(holdings, transactions):
            strategies.append({
                'type': 'value_investing',
                'description': '逢低买入策略',
                'characteristics': '在下跌中累积',
                'typical_players': '价值投资基金'
            })
        
        return strategies
    
    def analyze_entry_exit_timing(self, transactions):
        """分析进出场时机"""
        
        # 分析买入时机
        buy_timing = self.analyze_buy_timing(transactions)
        
        # 分析卖出时机
        sell_timing = self.analyze_sell_timing(transactions)
        
        # 计算时机选择效果
        timing_effectiveness = self.calculate_timing_effectiveness(buy_timing, sell_timing)
        
        return {
            'buy_timing': buy_timing,
            'sell_timing': sell_timing,
            'effectiveness': timing_effectiveness,
            'patterns': {
                'buy_the_dip': self.detect_buy_the_dip_pattern(transactions),
                'sell_the_rally': self.detect_sell_the_rally_pattern(transactions),
                'accumulation_zones': self.identify_accumulation_zones(transactions)
            }
        }
```

### 6. 综合仪表板

```python
class InstitutionalDashboard:
    def __init__(self, api_key):
        self.api_key = api_key
        self.holdings_analyzer = InstitutionalHoldingsAnalyzer(api_key)
        self.transaction_analyzer = InstitutionalTransactionAnalyzer(api_key)
        self.custody_analyzer = CustodyAnalyzer(api_key)
        self.etf_analyzer = ETFAnalyzer(api_key)
        self.strategy_analyzer = InstitutionalStrategyAnalyzer(api_key)
        
    def generate_comprehensive_report(self, asset='BTC'):
        """生成机构活动综合报告"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'asset': asset,
            'holdings_analysis': {},
            'transaction_activity': {},
            'custody_services': {},
            'etf_flows': {},
            'strategies': {},
            'market_signals': [],
            'recommendations': []
        }
        
        # 收集各项分析
        report['holdings_analysis'] = self.holdings_analyzer.analyze_institutional_holdings(asset)
        report['transaction_activity'] = self.transaction_analyzer.analyze_whale_transactions(asset)
        report['custody_services'] = self.custody_analyzer.analyze_custody_services(asset)
        report['etf_flows'] = self.etf_analyzer.analyze_etf_flows(asset)
        report['strategies'] = self.strategy_analyzer.analyze_institutional_strategies(asset)
        
        # 生成市场信号
        report['market_signals'] = self.generate_market_signals(report)
        
        # 生成投资建议
        report['recommendations'] = self.generate_recommendations(report)
        
        # 计算机构情绪指数
        report['institutional_sentiment_index'] = self.calculate_sentiment_index(report)
        
        # 生成执行摘要
        report['executive_summary'] = self.generate_executive_summary(report)
        
        return report
    
    def generate_market_signals(self, data):
        """生成市场信号"""
        
        signals = []
        
        # 基于持仓变化
        if data['holdings_analysis']['accumulation_phase']['phase'] == "强烈累积期":
            signals.append({
                'type': 'ACCUMULATION',
                'strength': 'STRONG',
                'message': '机构强烈累积，看涨信号',
                'confidence': 'HIGH'
            })
        
        # 基于 ETF 流动
        if data['etf_flows']['flow_summary']['30d_net_flows'] > 0:
            signals.append({
                'type': 'ETF_INFLOWS',
                'strength': 'POSITIVE',
                'message': 'ETF 净流入，散户兴趣增加',
                'confidence': 'MEDIUM'
            })
        
        # 基于大额交易
        if data['transaction_activity']['recent_activity']['24h_count'] > 100:
            signals.append({
                'type': 'HIGH_ACTIVITY',
                'strength': 'SIGNIFICANT',
                'message': '大额交易活跃，可能有重要动作',
                'confidence': 'MEDIUM'
            })
        
        # 基于托管增长
        custody_growth = float(data['custody_services']['custody_overview']['30d_growth'].strip('%'))
        if custody_growth > 10:
            signals.append({
                'type': 'CUSTODY_GROWTH',
                'strength': 'POSITIVE',
                'message': '托管余额快速增长，机构采用加速',
                'confidence': 'HIGH'
            })
        
        return signals
    
    def calculate_sentiment_index(self, data):
        """计算机构情绪指数"""
        
        score = 50  # 基础分
        
        # 持仓因素 (±30分)
        if data['holdings_analysis']['sentiment']['sentiment'] == "极度看涨":
            score += 30
        elif data['holdings_analysis']['sentiment']['sentiment'] == "看涨":
            score += 15
        elif data['holdings_analysis']['sentiment']['sentiment'] == "看跌":
            score -= 15
        elif data['holdings_analysis']['sentiment']['sentiment'] == "极度看跌":
            score -= 30
        
        # ETF 流动因素 (±20分)
        net_flows = data['etf_flows']['flow_summary']['30d_net_flows']
        if net_flows > 0:
            score += min(20, abs(net_flows) / 1000)  # 简化计算
        else:
            score -= min(20, abs(net_flows) / 1000)
        
        # 交易活动因素 (±15分)
        if 'accumulation' in [p['type'] for p in data['transaction_activity']['patterns']]:
            score += 15
        elif 'distribution' in [p['type'] for p in data['transaction_activity']['patterns']]:
            score -= 15
        
        # 托管增长因素 (±15分)
        custody_growth = float(data['custody_services']['custody_overview']['30d_growth'].strip('%'))
        score += min(15, max(-15, custody_growth * 0.5))
        
        # 确保在 0-100 范围内
        score = max(0, min(100, score))
        
        # 生成情绪等级
        if score >= 80:
            level = "极度乐观"
        elif score >= 65:
            level = "乐观"
        elif score >= 50:
            level = "中性偏多"
        elif score >= 35:
            level = "中性偏空"
        elif score >= 20:
            level = "悲观"
        else:
            level = "极度悲观"
        
        return {
            'index': score,
            'level': level,
            'interpretation': self.interpret_sentiment(score)
        }
    
    def interpret_sentiment(self, score):
        """解释情绪指数"""
        
        if score >= 80:
            return "机构极度看好，可能接近局部顶部"
        elif score >= 65:
            return "机构看涨，趋势向好"
        elif score >= 50:
            return "机构态度积极，但谨慎"
        elif score >= 35:
            return "机构观望，市场不确定"
        elif score >= 20:
            return "机构看空，注意风险"
        else:
            return "机构极度悲观，可能接近底部"
    
    def generate_recommendations(self, data):
        """生成投资建议"""
        
        recommendations = []
        
        sentiment_score = data['institutional_sentiment_index']['index']
        
        if sentiment_score >= 70:
            recommendations.append({
                'action': 'FOLLOW_SMART_MONEY',
                'description': '跟随机构建仓',
                'risk': 'MEDIUM',
                'timeframe': '中长期'
            })
        elif sentiment_score <= 30:
            recommendations.append({
                'action': 'CONTRARIAN_BUY',
                'description': '逆向买入机会',
                'risk': 'HIGH',
                'timeframe': '长期'
            })
        
        # 基于 ETF 流动
        if data['etf_flows']['sentiment']['level'] == "强烈流入":
            recommendations.append({
                'action': 'MOMENTUM_TRADE',
                'description': '利用 ETF 流入动能',
                'risk': 'MEDIUM',
                'timeframe': '短中期'
            })
        
        # 基于策略分析
        if 'buy_and_hold' in [s['type'] for s in data['strategies']['identified_strategies']]:
            recommendations.append({
                'action': 'LONG_TERM_HOLD',
                'description': '机构采用长期策略，适合定投',
                'risk': 'LOW',
                'timeframe': '长期'
            })
        
        return recommendations
```

## 常见问题

### Q1: 机构数据的可靠性如何？

可靠性因素：
- **链上数据**：高可靠性，可验证
- **托管数据**：依赖服务商报告
- **ETF 数据**：公开披露，较可靠
- **需要综合多源验证**

### Q2: 如何解读机构行为？

关键点：
- **累积期**：通常预示上涨
- **分配期**：可能接近顶部
- **横盘期**：等待方向选择
- **需结合其他指标**

### Q3: 散户如何利用机构数据？

策略：
- **跟随策略**：跟随机构建仓
- **逆向策略**：在机构恐慌时买入
- **避险策略**：机构撤退时减仓

## 最佳实践

1. **多维度验证**：不依赖单一数据源
2. **关注变化**：变化比绝对值重要
3. **理解动机**：分析机构行为背后原因
4. **风险管理**：机构也会犯错

---

*本文档详细介绍了 Glassnode Institutions API 的使用方法。机构数据是理解"聪明钱"动向的关键。*