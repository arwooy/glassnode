# Transactions（交易数据）API 文档

## 概述

Transactions API 提供区块链交易活动的详细数据，包括交易量、交易计数、转账类型、交易所流动、实体调整后的交易等。这些数据帮助分析网络使用情况、资金流向和市场活动。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/transactions/`

## 核心端点

### 1. 基础交易指标

#### 1.1 交易计数

**端点**: `/count`

**描述**: 区块链上的交易总数。

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/transactions/count?a=BTC&i=24h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

#### 1.2 交易率

**端点**: `/rate`

**描述**: 每秒交易数（TPS）。

```python
def analyze_transaction_activity(asset='BTC'):
    """分析交易活动"""
    
    base_url = "https://api.glassnode.com/v1/metrics/transactions/"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '1h', 's': int(time.time()) - 7*86400}
    
    # 获取交易数据
    tx_count = requests.get(base_url + "count", params=params, headers=headers).json()
    tx_rate = requests.get(base_url + "rate", params=params, headers=headers).json()
    
    # 分析趋势
    current_count = tx_count[-1]['v']
    avg_count = sum(d['v'] for d in tx_count) / len(tx_count)
    current_tps = tx_rate[-1]['v']
    
    # 网络拥堵分析
    if asset == 'BTC':
        max_tps = 7  # 比特币理论最大 TPS
    elif asset == 'ETH':
        max_tps = 15  # 以太坊理论最大 TPS
    else:
        max_tps = 10  # 默认值
    
    congestion_level = (current_tps / max_tps) * 100
    
    return {
        'current_tx_count': current_count,
        '7d_avg_tx_count': round(avg_count),
        'current_tps': round(current_tps, 2),
        'network_congestion': f"{congestion_level:.1f}%",
        'activity_level': classify_activity(current_count, avg_count)
    }

def classify_activity(current, average):
    """分类活动水平"""
    ratio = current / average
    
    if ratio > 1.5:
        return "极高活动"
    elif ratio > 1.2:
        return "高活动"
    elif ratio > 0.8:
        return "正常活动"
    elif ratio > 0.5:
        return "低活动"
    else:
        return "极低活动"
```

### 2. 交易量指标

#### 2.1 总交易量

**端点**: `/volume_sum`

**描述**: 所有交易的总价值。

#### 2.2 平均交易量

**端点**: `/volume_mean`

**描述**: 平均每笔交易的价值。

#### 2.3 中位交易量

**端点**: `/volume_median`

**描述**: 交易价值的中位数。

**交易量分析系统**:
```python
class VolumeAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/transactions/"
        
    def analyze_transaction_volumes(self, asset='BTC', currency='USD'):
        """分析交易量模式"""
        
        headers = {"X-Api-Key": self.api_key}
        params = {
            'a': asset,
            'i': '24h',
            's': int(time.time()) - 30*86400,
            'c': currency
        }
        
        # 获取不同交易量指标
        total_volume = self.get_data("volume_sum", params, headers)
        mean_volume = self.get_data("volume_mean", params, headers)
        median_volume = self.get_data("volume_median", params, headers)
        
        # 分析交易规模分布
        current_mean = mean_volume[-1]['v']
        current_median = median_volume[-1]['v']
        
        # 偏度分析（mean vs median）
        if current_mean > current_median * 2:
            distribution = "高度右偏 - 存在大额交易（鲸鱼活动）"
            whale_activity = "高"
        elif current_mean > current_median * 1.5:
            distribution = "中度右偏 - 一些大额交易"
            whale_activity = "中"
        else:
            distribution = "相对均匀 - 零售主导"
            whale_activity = "低"
        
        # 计算交易量趋势
        volume_trend = self.calculate_trend(total_volume)
        
        return {
            'total_volume_30d': sum(d['v'] for d in total_volume),
            'daily_avg_volume': sum(d['v'] for d in total_volume) / len(total_volume),
            'current_mean_tx': current_mean,
            'current_median_tx': current_median,
            'distribution': distribution,
            'whale_activity': whale_activity,
            'volume_trend': volume_trend,
            'market_phase': self.identify_market_phase(volume_trend, whale_activity)
        }
    
    def calculate_trend(self, data):
        """计算趋势"""
        if len(data) < 7:
            return "数据不足"
        
        recent = sum(d['v'] for d in data[-7:]) / 7
        older = sum(d['v'] for d in data[-14:-7]) / 7
        
        change = (recent - older) / older * 100
        
        if change > 20:
            return f"强劲上升 ({change:.1f}%)"
        elif change > 5:
            return f"温和上升 ({change:.1f}%)"
        elif change < -20:
            return f"强劲下降 ({change:.1f}%)"
        elif change < -5:
            return f"温和下降 ({change:.1f}%)"
        else:
            return f"横盘 ({change:.1f}%)"
    
    def identify_market_phase(self, trend, whale_activity):
        """识别市场阶段"""
        
        if "上升" in trend and whale_activity == "高":
            return "机构积累期"
        elif "上升" in trend and whale_activity == "低":
            return "零售 FOMO 期"
        elif "下降" in trend and whale_activity == "高":
            return "机构分配期"
        elif "下降" in trend and whale_activity == "低":
            return "市场冷淡期"
        else:
            return "整理期"
```

### 3. 交易所流动

#### 3.1 交易所充值

**端点**: `/exchanges_inflow_sum`

**描述**: 流入交易所的总价值。

#### 3.2 交易所提现

**端点**: `/exchanges_outflow_sum`

**描述**: 从交易所流出的总价值。

#### 3.3 交易所净流量

**端点**: `/exchanges_net_flow`

**描述**: 交易所流入减去流出的净值。

**交易所流动分析**:
```python
class ExchangeFlowAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_exchange_flows(self, asset='BTC'):
        """分析交易所资金流动"""
        
        base_url = "https://api.glassnode.com/v1/metrics/transactions/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '1h', 's': int(time.time()) - 24*3600}
        
        # 获取流动数据
        inflow = requests.get(
            base_url + "exchanges_inflow_sum", 
            params=params, 
            headers=headers
        ).json()
        
        outflow = requests.get(
            base_url + "exchanges_outflow_sum", 
            params=params, 
            headers=headers
        ).json()
        
        # 计算净流量
        net_flows = []
        for i in range(len(inflow)):
            net = inflow[i]['v'] - outflow[i]['v']
            net_flows.append({
                'timestamp': inflow[i]['t'],
                'net_flow': net,
                'inflow': inflow[i]['v'],
                'outflow': outflow[i]['v']
            })
        
        # 分析24小时数据
        total_inflow = sum(d['inflow'] for d in net_flows)
        total_outflow = sum(d['outflow'] for d in net_flows)
        net_24h = total_inflow - total_outflow
        
        # 判断市场压力
        if net_24h > 0:
            pressure = "卖压增加" if net_24h > total_outflow * 0.1 else "轻微卖压"
            signal = "BEARISH"
        else:
            pressure = "买压增加" if abs(net_24h) > total_inflow * 0.1 else "轻微买压"
            signal = "BULLISH"
        
        # 检测异常流动
        anomalies = self.detect_anomalies(net_flows)
        
        return {
            '24h_inflow': total_inflow,
            '24h_outflow': total_outflow,
            '24h_net_flow': net_24h,
            'market_pressure': pressure,
            'signal': signal,
            'anomalies': anomalies,
            'recommendation': self.generate_recommendation(net_24h, anomalies)
        }
    
    def detect_anomalies(self, flows):
        """检测异常流动"""
        
        anomalies = []
        
        # 计算标准差
        net_values = [f['net_flow'] for f in flows]
        mean = sum(net_values) / len(net_values)
        std = (sum((x - mean) ** 2 for x in net_values) / len(net_values)) ** 0.5
        
        # 检测异常值（超过2个标准差）
        for flow in flows:
            if abs(flow['net_flow'] - mean) > 2 * std:
                anomalies.append({
                    'timestamp': flow['timestamp'],
                    'net_flow': flow['net_flow'],
                    'type': 'massive_inflow' if flow['net_flow'] > 0 else 'massive_outflow'
                })
        
        return anomalies
    
    def generate_recommendation(self, net_flow, anomalies):
        """生成交易建议"""
        
        if len(anomalies) > 0 and anomalies[-1]['type'] == 'massive_inflow':
            return "警告：大量资金流入交易所，可能有抛售压力"
        elif len(anomalies) > 0 and anomalies[-1]['type'] == 'massive_outflow':
            return "积极信号：大量资金流出交易所，持有意愿强"
        elif net_flow > 0:
            return "谨慎：净流入增加，关注卖压"
        else:
            return "乐观：净流出表明投资者倾向于长期持有"
```

### 4. 实体调整交易

#### 4.1 实体调整交易计数

**端点**: `/count_entity_adjusted`

**描述**: 排除同一实体内部转账后的交易数。

#### 4.2 实体调整交易量

**端点**: `/volume_entity_adjusted_sum`

**描述**: 实体间的真实经济交易量。

```python
def analyze_real_economic_activity(asset='BTC'):
    """分析真实经济活动"""
    
    base_url = "https://api.glassnode.com/v1/metrics/transactions/"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '24h', 's': int(time.time()) - 30*86400}
    
    # 获取原始和实体调整后的数据
    raw_count = requests.get(
        base_url + "count", 
        params=params, 
        headers=headers
    ).json()
    
    adjusted_count = requests.get(
        base_url + "count_entity_adjusted", 
        params=params, 
        headers=headers
    ).json()
    
    # 计算真实活动比例
    real_activity_ratio = []
    for i in range(len(raw_count)):
        ratio = adjusted_count[i]['v'] / raw_count[i]['v'] if raw_count[i]['v'] > 0 else 0
        real_activity_ratio.append(ratio)
    
    avg_ratio = sum(real_activity_ratio) / len(real_activity_ratio)
    
    # 解释结果
    if avg_ratio > 0.7:
        interpretation = "高真实活动 - 大部分交易是实体间转账"
    elif avg_ratio > 0.5:
        interpretation = "中等真实活动 - 平衡的内部和外部交易"
    else:
        interpretation = "低真实活动 - 大量内部转账或混币活动"
    
    return {
        'real_activity_ratio': f"{avg_ratio*100:.1f}%",
        'interpretation': interpretation,
        'avg_daily_real_txs': sum(d['v'] for d in adjusted_count) / len(adjusted_count),
        'network_health': "健康" if avg_ratio > 0.6 else "需要关注"
    }
```

### 5. 特定类型交易

#### 5.1 大额交易

**端点**: `/large_volume_sum`

**描述**: 价值超过特定阈值的交易总量。

```python
def analyze_whale_transactions(asset='BTC', threshold=1000000):
    """分析鲸鱼交易"""
    
    url = "https://api.glassnode.com/v1/metrics/transactions/large_volume_sum"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {
        'a': asset,
        'i': '1h',
        's': int(time.time()) - 24*3600,
        'threshold': threshold
    }
    
    response = requests.get(url, params=params, headers=headers)
    large_txs = response.json()
    
    # 分析鲸鱼活动模式
    hourly_volumes = [d['v'] for d in large_txs]
    
    # 识别活跃时段
    active_hours = []
    avg_volume = sum(hourly_volumes) / len(hourly_volumes)
    
    for i, volume in enumerate(hourly_volumes):
        if volume > avg_volume * 1.5:
            active_hours.append(i)
    
    # 判断鲸鱼意图
    recent_6h = sum(hourly_volumes[-6:])
    older_6h = sum(hourly_volumes[-12:-6])
    
    if recent_6h > older_6h * 1.3:
        whale_sentiment = "激增 - 鲸鱼活跃，可能有大动作"
    elif recent_6h < older_6h * 0.7:
        whale_sentiment = "减少 - 鲸鱼观望"
    else:
        whale_sentiment = "稳定 - 正常鲸鱼活动"
    
    return {
        '24h_whale_volume': sum(hourly_volumes),
        'avg_hourly_whale_volume': avg_volume,
        'active_hours': active_hours,
        'whale_sentiment': whale_sentiment,
        'risk_level': assess_whale_risk(hourly_volumes)
    }

def assess_whale_risk(volumes):
    """评估鲸鱼活动风险"""
    
    # 计算变异系数
    mean = sum(volumes) / len(volumes)
    variance = sum((x - mean) ** 2 for x in volumes) / len(volumes)
    std_dev = variance ** 0.5
    cv = std_dev / mean if mean > 0 else 0
    
    if cv > 1.5:
        return "高风险 - 鲸鱼活动极不稳定"
    elif cv > 1:
        return "中风险 - 鲸鱼活动波动较大"
    else:
        return "低风险 - 鲸鱼活动相对稳定"
```

### 6. DeFi 和智能合约交易

#### 6.1 DeFi 交易量

**端点**: `/defi_volume_sum`

**描述**: DeFi 协议相关的交易量。

#### 6.2 ERC-20 转账

**端点**: `/transfers_erc20_count`

**描述**: ERC-20 代币转账数量。

```python
class DeFiTransactionAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_defi_activity(self, asset='ETH'):
        """分析 DeFi 交易活动"""
        
        if asset != 'ETH':
            return "DeFi 分析主要适用于以太坊"
        
        base_url = "https://api.glassnode.com/v1/metrics/transactions/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h', 's': int(time.time()) - 7*86400}
        
        # 获取 DeFi 和 ERC-20 数据
        defi_volume = requests.get(
            base_url + "defi_volume_sum",
            params=params,
            headers=headers
        ).json()
        
        erc20_transfers = requests.get(
            base_url + "transfers_erc20_count",
            params=params,
            headers=headers
        ).json()
        
        # 分析 DeFi 占比
        total_volume = requests.get(
            base_url + "volume_sum",
            params=params,
            headers=headers
        ).json()
        
        defi_ratios = []
        for i in range(len(defi_volume)):
            if total_volume[i]['v'] > 0:
                ratio = defi_volume[i]['v'] / total_volume[i]['v']
                defi_ratios.append(ratio)
        
        avg_defi_ratio = sum(defi_ratios) / len(defi_ratios) if defi_ratios else 0
        
        # 判断 DeFi 市场状态
        if avg_defi_ratio > 0.3:
            defi_state = "DeFi 热潮 - 高度活跃"
        elif avg_defi_ratio > 0.15:
            defi_state = "DeFi 活跃 - 健康发展"
        elif avg_defi_ratio > 0.05:
            defi_state = "DeFi 温和 - 正常水平"
        else:
            defi_state = "DeFi 冷淡 - 活动较少"
        
        # ERC-20 活动分析
        current_erc20 = erc20_transfers[-1]['v']
        avg_erc20 = sum(d['v'] for d in erc20_transfers) / len(erc20_transfers)
        
        token_activity = "高" if current_erc20 > avg_erc20 * 1.2 else "正常" if current_erc20 > avg_erc20 * 0.8 else "低"
        
        return {
            'defi_volume_7d': sum(d['v'] for d in defi_volume),
            'defi_ratio': f"{avg_defi_ratio*100:.1f}%",
            'defi_state': defi_state,
            'erc20_transfers_7d': sum(d['v'] for d in erc20_transfers),
            'token_activity': token_activity,
            'recommendations': self.generate_defi_recommendations(defi_state, token_activity)
        }
    
    def generate_defi_recommendations(self, defi_state, token_activity):
        """生成 DeFi 相关建议"""
        
        recommendations = []
        
        if "热潮" in defi_state:
            recommendations.append("DeFi 活动过热，注意 gas 费用和协议风险")
        elif "冷淡" in defi_state:
            recommendations.append("DeFi 活动低迷，可能是进入优质项目的好时机")
        
        if token_activity == "高":
            recommendations.append("代币转账活跃，关注热门代币和新项目")
        elif token_activity == "低":
            recommendations.append("代币活动低迷，市场可能处于观望期")
        
        return recommendations
```

### 7. 跨链桥接交易

#### 7.1 桥接交易量

**端点**: `/bridge_volume`

**描述**: 跨链桥接的交易量。

```python
def analyze_bridge_activity(asset='ETH'):
    """分析跨链桥接活动"""
    
    url = "https://api.glassnode.com/v1/metrics/transactions/bridge_volume"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '24h', 's': int(time.time()) - 30*86400}
    
    response = requests.get(url, params=params, headers=headers)
    bridge_data = response.json()
    
    # 分析桥接趋势
    volumes = [d['v'] for d in bridge_data]
    current = volumes[-1]
    avg_30d = sum(volumes) / len(volumes)
    
    # 计算增长率
    growth = (current - avg_30d) / avg_30d * 100 if avg_30d > 0 else 0
    
    # 判断跨链活动
    if growth > 50:
        activity = "跨链活动激增 - 可能有新的机会或风险"
    elif growth > 20:
        activity = "跨链活动增加 - 生态互联增强"
    elif growth < -20:
        activity = "跨链活动减少 - 可能存在安全担忧"
    else:
        activity = "跨链活动稳定"
    
    return {
        'current_bridge_volume': current,
        '30d_avg_bridge_volume': avg_30d,
        'growth_rate': f"{growth:.1f}%",
        'activity_assessment': activity,
        'risk_warning': "高" if growth > 100 else "中" if growth > 50 else "低"
    }
```

### 8. 综合交易分析仪表板

```python
class TransactionDashboard:
    def __init__(self, api_key):
        self.api_key = api_key
        self.volume_analyzer = VolumeAnalyzer(api_key)
        self.exchange_analyzer = ExchangeFlowAnalyzer(api_key)
        self.defi_analyzer = DeFiTransactionAnalyzer(api_key)
        
    def generate_comprehensive_report(self, asset='BTC'):
        """生成综合交易分析报告"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'asset': asset,
            'network_activity': {},
            'volume_analysis': {},
            'exchange_flows': {},
            'whale_activity': {},
            'signals': []
        }
        
        # 网络活动分析
        report['network_activity'] = analyze_transaction_activity(asset)
        
        # 交易量分析
        report['volume_analysis'] = self.volume_analyzer.analyze_transaction_volumes(asset)
        
        # 交易所流动分析
        report['exchange_flows'] = self.exchange_analyzer.analyze_exchange_flows(asset)
        
        # 鲸鱼活动分析
        report['whale_activity'] = analyze_whale_transactions(asset)
        
        # DeFi 分析（如果是 ETH）
        if asset == 'ETH':
            report['defi_activity'] = self.defi_analyzer.analyze_defi_activity(asset)
        
        # 生成综合信号
        report['signals'] = self.generate_trading_signals(report)
        
        # 计算健康分数
        report['network_health_score'] = self.calculate_health_score(report)
        
        return report
    
    def generate_trading_signals(self, data):
        """基于交易数据生成信号"""
        
        signals = []
        
        # 基于交易所流动的信号
        if data['exchange_flows']['signal'] == 'BULLISH':
            signals.append({
                'type': 'exchange_flow',
                'action': 'BUY',
                'reason': '资金流出交易所，供应减少',
                'confidence': 'HIGH'
            })
        elif data['exchange_flows']['signal'] == 'BEARISH':
            signals.append({
                'type': 'exchange_flow',
                'action': 'SELL',
                'reason': '资金流入交易所，抛压增加',
                'confidence': 'MEDIUM'
            })
        
        # 基于鲸鱼活动的信号
        if "激增" in data['whale_activity']['whale_sentiment']:
            signals.append({
                'type': 'whale_activity',
                'action': 'WATCH',
                'reason': '鲸鱼活动激增，可能有大变动',
                'confidence': 'MEDIUM'
            })
        
        # 基于网络活动的信号
        if data['network_activity']['activity_level'] == "极高活动":
            signals.append({
                'type': 'network_activity',
                'action': 'CAUTION',
                'reason': '网络极度活跃，可能接近局部顶部',
                'confidence': 'LOW'
            })
        
        return signals
    
    def calculate_health_score(self, data):
        """计算网络健康分数"""
        
        score = 50  # 基础分
        
        # 网络活动评分
        activity = data['network_activity']['activity_level']
        if "正常" in activity:
            score += 10
        elif "高" in activity:
            score += 5
        elif "低" in activity:
            score -= 10
        
        # 交易量趋势评分
        volume_trend = data['volume_analysis']['volume_trend']
        if "上升" in volume_trend:
            score += 15
        elif "下降" in volume_trend:
            score -= 15
        
        # 交易所流动评分
        if data['exchange_flows']['signal'] == 'BULLISH':
            score += 20
        elif data['exchange_flows']['signal'] == 'BEARISH':
            score -= 20
        
        # 限制在 0-100 范围
        score = max(0, min(100, score))
        
        # 生成评级
        if score >= 80:
            rating = "优秀"
        elif score >= 60:
            rating = "良好"
        elif score >= 40:
            rating = "一般"
        elif score >= 20:
            rating = "较差"
        else:
            rating = "危险"
        
        return {
            'score': score,
            'rating': rating,
            'interpretation': self.interpret_health_score(score)
        }
    
    def interpret_health_score(self, score):
        """解释健康分数"""
        
        if score >= 80:
            return "网络健康状况优秀，活动活跃且资金流向积极"
        elif score >= 60:
            return "网络健康状况良好，各项指标正常"
        elif score >= 40:
            return "网络健康状况一般，部分指标需要关注"
        elif score >= 20:
            return "网络健康状况较差，多项指标显示问题"
        else:
            return "网络健康状况危险，建议谨慎操作"
```

### 9. 实时监控系统

```python
class TransactionMonitor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.alert_thresholds = {
            'exchange_inflow_spike': 1000,  # BTC
            'whale_tx_threshold': 5000,  # BTC
            'network_congestion': 90,  # 百分比
            'unusual_activity': 2  # 标准差
        }
        
    async def monitor_transactions(self, asset='BTC'):
        """实时监控交易活动"""
        
        while True:
            try:
                # 监控交易所流入
                exchange_flow = await self.check_exchange_flows(asset)
                if exchange_flow > self.alert_thresholds['exchange_inflow_spike']:
                    await self.send_alert(f"⚠️ 大量资金流入交易所: {exchange_flow} {asset}")
                
                # 监控鲸鱼交易
                whale_txs = await self.check_whale_transactions(asset)
                if whale_txs > self.alert_thresholds['whale_tx_threshold']:
                    await self.send_alert(f"🐋 检测到大额交易: {whale_txs} {asset}")
                
                # 监控网络拥堵
                congestion = await self.check_network_congestion(asset)
                if congestion > self.alert_thresholds['network_congestion']:
                    await self.send_alert(f"🚨 网络拥堵严重: {congestion}%")
                
                await asyncio.sleep(300)  # 5分钟检查一次
                
            except Exception as e:
                print(f"监控错误: {e}")
                await asyncio.sleep(60)
    
    async def send_alert(self, message):
        """发送警报"""
        
        print(f"[ALERT] {datetime.now()}: {message}")
        # 可以集成 Telegram、Email 等通知方式
```

## 常见问题

### Q1: 实体调整交易和原始交易有什么区别？

- **原始交易**：包括所有链上交易
- **实体调整**：排除同一实体（如交易所）的内部转账，更准确反映经济活动

### Q2: 如何判断交易所流动的影响？

- **大量流入**：潜在卖压，短期看跌
- **大量流出**：持有意愿强，短期看涨
- **需要结合其他指标综合判断**

### Q3: 鲸鱼交易一定会影响价格吗？

不一定。需要考虑：
- 交易方向（买入/卖出）
- 市场深度
- 其他市场参与者反应

## 最佳实践

1. **多维度分析**：结合交易量、计数、类型等多个维度
2. **关注异常**：异常交易活动往往预示重要变化
3. **区分真实活动**：使用实体调整数据识别真实经济活动
4. **实时监控**：设置关键指标的实时监控和预警

---

*本文档详细介绍了 Glassnode Transactions API 的使用方法。交易数据是理解区块链网络活动和市场动态的核心。*