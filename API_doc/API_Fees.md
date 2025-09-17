# Fees（手续费）API 文档

## 概述

Fees API 提供区块链网络手续费的全面数据，包括交易费用、Gas 使用情况、矿工收入、以及不同类型交易的费用分析。这些数据对于评估网络使用成本、预测最佳交易时机和分析网络经济至关重要。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/fees/`

## 核心端点

### 1. 基础费用指标

#### 1.1 总手续费

**端点**: `/volume_sum`

**描述**: 支付给矿工/验证者的总手续费。

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/fees/volume_sum?a=BTC&i=24h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

#### 1.2 平均手续费

**端点**: `/volume_mean`

**描述**: 每笔交易的平均手续费。

#### 1.3 中位手续费

**端点**: `/volume_median`

**描述**: 手续费的中位数，更好地反映典型交易成本。

**费用分析系统**:
```python
class FeeAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/fees/"
        
    def analyze_fee_structure(self, asset='BTC'):
        """分析费用结构"""
        
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '1h', 's': int(time.time()) - 24*3600}
        
        # 获取费用数据
        total_fees = self.get_data("volume_sum", params, headers)
        mean_fees = self.get_data("volume_mean", params, headers)
        median_fees = self.get_data("volume_median", params, headers)
        
        # 分析费用分布
        current_mean = mean_fees[-1]['v']
        current_median = median_fees[-1]['v']
        
        # 偏度分析
        skewness = (current_mean - current_median) / current_median if current_median > 0 else 0
        
        if skewness > 0.5:
            distribution = "高度右偏 - 存在高额费用交易"
            congestion = "网络拥堵，部分用户支付高额费用"
        elif skewness > 0.2:
            distribution = "轻微右偏 - 费用分布略不均"
            congestion = "网络略有压力"
        else:
            distribution = "相对均匀 - 费用分布正常"
            congestion = "网络状况良好"
        
        # 24小时费用统计
        total_24h = sum(d['v'] for d in total_fees)
        avg_hourly = total_24h / 24
        
        # 识别高峰时段
        peak_hours = self.identify_peak_hours(total_fees)
        
        return {
            '24h_total_fees': total_24h,
            'current_mean_fee': current_mean,
            'current_median_fee': current_median,
            'fee_distribution': distribution,
            'network_congestion': congestion,
            'peak_hours': peak_hours,
            'optimal_time': self.suggest_optimal_time(total_fees)
        }
    
    def identify_peak_hours(self, hourly_data):
        """识别费用高峰时段"""
        
        fees = [d['v'] for d in hourly_data]
        avg = sum(fees) / len(fees)
        
        peak_hours = []
        for i, fee in enumerate(fees):
            if fee > avg * 1.5:
                peak_hours.append({
                    'hour': i,
                    'fee': fee,
                    'above_avg': f"{(fee/avg - 1) * 100:.1f}%"
                })
        
        return peak_hours
    
    def suggest_optimal_time(self, hourly_data):
        """建议最佳交易时间"""
        
        fees = [d['v'] for d in hourly_data]
        min_fee_hour = fees.index(min(fees))
        
        # 找出费用最低的连续时段
        low_fee_threshold = sorted(fees)[len(fees)//4]  # 最低的25%
        
        low_fee_periods = []
        current_period = []
        
        for i, fee in enumerate(fees):
            if fee <= low_fee_threshold:
                current_period.append(i)
            else:
                if current_period:
                    low_fee_periods.append(current_period)
                    current_period = []
        
        if current_period:
            low_fee_periods.append(current_period)
        
        # 找最长的低费用时段
        if low_fee_periods:
            longest_period = max(low_fee_periods, key=len)
            return {
                'best_hour': min_fee_hour,
                'low_fee_window': f"{longest_period[0]}-{longest_period[-1]} 时",
                'potential_savings': f"{(1 - min(fees)/sum(fees)*len(fees)) * 100:.1f}%"
            }
        
        return {
            'best_hour': min_fee_hour,
            'recommendation': '费用相对稳定，任何时间交易均可'
        }
```

### 2. Gas 相关指标（以太坊）

#### 2.1 Gas 价格（平均）

**端点**: `/gas_price_mean`

**描述**: 平均 Gas 价格（Gwei）。

#### 2.2 Gas 价格（中位数）

**端点**: `/gas_price_median`

**描述**: Gas 价格中位数。

#### 2.3 Gas 使用量

**端点**: `/gas_used_sum`

**描述**: 总 Gas 使用量。

**Gas 优化策略**:
```python
class GasOptimizer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_gas_patterns(self):
        """分析 Gas 模式（以太坊）"""
        
        base_url = "https://api.glassnode.com/v1/metrics/fees/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': 'ETH', 'i': '10m', 's': int(time.time()) - 24*3600}
        
        # 获取 Gas 数据
        gas_price_mean = requests.get(
            base_url + "gas_price_mean",
            params=params,
            headers=headers
        ).json()
        
        gas_used = requests.get(
            base_url + "gas_used_sum",
            params=params,
            headers=headers
        ).json()
        
        # 分析 Gas 价格趋势
        prices = [d['v'] for d in gas_price_mean]
        current_price = prices[-1]
        avg_price = sum(prices) / len(prices)
        
        # 计算 Gas 价格分位数
        sorted_prices = sorted(prices)
        percentile = sum(1 for p in sorted_prices if p < current_price) / len(prices) * 100
        
        # Gas 使用率分析
        usage = [d['v'] for d in gas_used]
        block_gas_limit = 30000000  # 以太坊区块 Gas 限制
        
        utilization = [(u / block_gas_limit) * 100 for u in usage]
        current_utilization = utilization[-1]
        
        # 预测未来 Gas 价格
        prediction = self.predict_gas_price(prices, utilization)
        
        return {
            'current_gas_price': f"{current_price:.2f} Gwei",
            'avg_gas_price_24h': f"{avg_price:.2f} Gwei",
            'price_percentile': f"{percentile:.1f}%",
            'network_utilization': f"{current_utilization:.1f}%",
            'price_trend': self.identify_trend(prices),
            'prediction': prediction,
            'recommendation': self.generate_gas_recommendation(current_price, percentile, current_utilization)
        }
    
    def predict_gas_price(self, prices, utilization):
        """预测 Gas 价格趋势"""
        
        # 简单的线性预测
        recent_prices = prices[-6:]  # 最近1小时
        recent_util = utilization[-6:]
        
        price_trend = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
        util_trend = (recent_util[-1] - recent_util[0]) / max(recent_util[0], 1)
        
        if util_trend > 0.2 and price_trend > 0.1:
            return "预计继续上涨 - 网络压力增加"
        elif util_trend < -0.2 and price_trend < -0.1:
            return "预计继续下降 - 网络压力减少"
        else:
            return "预计保持稳定"
    
    def generate_gas_recommendation(self, current_price, percentile, utilization):
        """生成 Gas 策略建议"""
        
        if percentile > 80 and utilization > 90:
            return {
                'action': 'WAIT',
                'reason': 'Gas 价格处于高位，网络拥堵',
                'suggestion': '建议等待 2-4 小时后再交易'
            }
        elif percentile < 30:
            return {
                'action': 'TRANSACT',
                'reason': 'Gas 价格处于低位',
                'suggestion': '现在是交易的好时机'
            }
        else:
            return {
                'action': 'MONITOR',
                'reason': 'Gas 价格中等',
                'suggestion': '如非紧急，可等待更低价格'
            }
```

### 3. 费用比率指标

#### 3.1 费用比率倍数（FRM）

**端点**: `/fee_ratio_multiple`

**描述**: 矿工收入与交易费用的比率，衡量网络安全性。

```python
def analyze_network_security(asset='BTC'):
    """分析网络安全性（通过 FRM）"""
    
    url = "https://api.glassnode.com/v1/metrics/fees/fee_ratio_multiple"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '24h', 's': int(time.time()) - 90*86400}
    
    response = requests.get(url, params=params, headers=headers)
    frm_data = response.json()
    
    current_frm = frm_data[-1]['v']
    avg_frm = sum(d['v'] for d in frm_data) / len(frm_data)
    
    # FRM 解释
    # FRM = 矿工总收入 / 交易费用
    # 低 FRM 意味着费用占矿工收入比例高，网络更安全
    
    if current_frm < 10:
        security = "极高 - 交易费用提供强大激励"
    elif current_frm < 50:
        security = "高 - 费用收入良好"
    elif current_frm < 100:
        security = "中等 - 主要依赖区块奖励"
    else:
        security = "低 - 高度依赖区块奖励，未来减半可能影响安全"
    
    # 计算费用占比
    fee_percentage = 100 / current_frm if current_frm > 0 else 0
    
    return {
        'current_frm': round(current_frm, 2),
        '90d_avg_frm': round(avg_frm, 2),
        'fee_percentage': f"{fee_percentage:.2f}%",
        'network_security': security,
        'sustainability': assess_fee_sustainability(current_frm, asset)
    }

def assess_fee_sustainability(frm, asset):
    """评估费用可持续性"""
    
    if asset == 'BTC':
        # 比特币每4年减半
        if frm > 100:
            return "警告：下次减半后可能面临安全挑战"
        elif frm > 50:
            return "注意：需要费用增长以维持减半后的安全性"
        else:
            return "良好：费用收入可支撑网络安全"
    else:
        return "费用模型因币种而异"
```

### 4. 交易类型费用分析

#### 4.1 DeFi 交易费用

**端点**: `/defi_fees_sum`

**描述**: DeFi 协议交易产生的总费用。

#### 4.2 NFT 交易费用

**端点**: `/nft_fees_sum`

**描述**: NFT 相关交易的总费用。

#### 4.3 稳定币转账费用

**端点**: `/stablecoin_fees_sum`

**描述**: 稳定币转账产生的费用。

```python
class TransactionTypeFeeAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_fee_by_type(self):
        """按交易类型分析费用（以太坊）"""
        
        base_url = "https://api.glassnode.com/v1/metrics/fees/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': 'ETH', 'i': '24h', 's': int(time.time()) - 7*86400}
        
        # 获取不同类型的费用数据
        fee_types = {
            'defi': 'defi_fees_sum',
            'nft': 'nft_fees_sum',
            'stablecoin': 'stablecoin_fees_sum',
            'vanilla': 'vanilla_fees_sum'  # 普通转账
        }
        
        fee_data = {}
        total_fees = 0
        
        for tx_type, endpoint in fee_types.items():
            response = requests.get(
                base_url + endpoint,
                params=params,
                headers=headers
            ).json()
            
            week_total = sum(d['v'] for d in response)
            fee_data[tx_type] = {
                'total': week_total,
                'daily_avg': week_total / 7,
                'latest': response[-1]['v']
            }
            total_fees += week_total
        
        # 计算各类型占比
        fee_distribution = {}
        for tx_type, data in fee_data.items():
            percentage = (data['total'] / total_fees * 100) if total_fees > 0 else 0
            fee_distribution[tx_type] = {
                **data,
                'percentage': f"{percentage:.1f}%"
            }
        
        # 识别主导类型
        dominant_type = max(fee_data.keys(), key=lambda x: fee_data[x]['total'])
        
        # 趋势分析
        trends = self.analyze_type_trends(fee_data)
        
        return {
            'fee_distribution': fee_distribution,
            'dominant_type': dominant_type,
            'total_fees_7d': total_fees,
            'trends': trends,
            'insights': self.generate_insights(fee_distribution, dominant_type)
        }
    
    def analyze_type_trends(self, fee_data):
        """分析各类型费用趋势"""
        
        trends = {}
        
        for tx_type, data in fee_data.items():
            # 简化：比较最新值和平均值
            if data['latest'] > data['daily_avg'] * 1.2:
                trends[tx_type] = "上升"
            elif data['latest'] < data['daily_avg'] * 0.8:
                trends[tx_type] = "下降"
            else:
                trends[tx_type] = "稳定"
        
        return trends
    
    def generate_insights(self, distribution, dominant):
        """生成洞察"""
        
        insights = []
        
        if dominant == 'defi':
            insights.append("DeFi 活动是主要的 Gas 消耗者")
        elif dominant == 'nft':
            insights.append("NFT 市场活跃，占据大量网络资源")
        elif dominant == 'stablecoin':
            insights.append("稳定币转账需求强劲")
        
        # 检查 NFT 占比
        nft_pct = float(distribution['nft']['percentage'].strip('%'))
        if nft_pct > 30:
            insights.append("NFT 活动可能导致网络拥堵和高 Gas 费")
        
        # 检查 DeFi 占比
        defi_pct = float(distribution['defi']['percentage'].strip('%'))
        if defi_pct > 40:
            insights.append("DeFi 协议主导网络使用，关注流动性挖矿活动")
        
        return insights
```

### 5. 优先级费用分析

```python
class PriorityFeeAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_priority_fees(self, asset='ETH'):
        """分析优先费（EIP-1559 后）"""
        
        base_url = "https://api.glassnode.com/v1/metrics/fees/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '10m', 's': int(time.time()) - 6*3600}
        
        # 获取基础费和优先费数据
        base_fee = self.get_base_fee(params, headers)
        priority_fee = self.get_priority_fee(params, headers)
        
        # 分析费用结构
        current_base = base_fee[-1]['v']
        current_priority = priority_fee[-1]['v']
        total_fee = current_base + current_priority
        
        # 计算优先费占比
        priority_ratio = current_priority / total_fee * 100 if total_fee > 0 else 0
        
        # 分析网络状态
        if current_base > 100:  # Gwei
            network_state = "极度拥堵"
            urgency = "非紧急交易建议等待"
        elif current_base > 50:
            network_state = "拥堵"
            urgency = "可等待费用下降"
        elif current_base > 20:
            network_state = "正常"
            urgency = "适合常规交易"
        else:
            network_state = "空闲"
            urgency = "理想交易时机"
        
        # 提供费用建议
        fee_suggestions = self.generate_fee_suggestions(
            current_base, 
            current_priority,
            network_state
        )
        
        return {
            'current_base_fee': f"{current_base:.2f} Gwei",
            'current_priority_fee': f"{current_priority:.2f} Gwei",
            'total_fee': f"{total_fee:.2f} Gwei",
            'priority_ratio': f"{priority_ratio:.1f}%",
            'network_state': network_state,
            'urgency_advice': urgency,
            'fee_suggestions': fee_suggestions
        }
    
    def generate_fee_suggestions(self, base_fee, priority_fee, state):
        """生成费用建议"""
        
        suggestions = {
            'slow': {
                'priority_fee': max(1, priority_fee * 0.5),
                'estimated_time': '10-30 分钟',
                'use_case': '非紧急转账'
            },
            'standard': {
                'priority_fee': priority_fee,
                'estimated_time': '3-5 分钟',
                'use_case': '常规交易'
            },
            'fast': {
                'priority_fee': priority_fee * 1.5,
                'estimated_time': '15-30 秒',
                'use_case': '时间敏感交易'
            },
            'instant': {
                'priority_fee': priority_fee * 2,
                'estimated_time': '下一个区块',
                'use_case': '紧急交易、抢购'
            }
        }
        
        # 根据网络状态调整
        if state == "极度拥堵":
            for level in suggestions.values():
                level['priority_fee'] *= 1.5
        
        return suggestions
```

### 6. 费用预测模型

```python
class FeePredictionModel:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def predict_fees(self, asset='ETH', horizon_hours=24):
        """预测未来费用"""
        
        # 获取历史数据
        historical_data = self.get_historical_fees(asset, days=30)
        
        # 提取特征
        features = self.extract_features(historical_data)
        
        # 简化的预测模型
        predictions = []
        
        for hour in range(horizon_hours):
            # 基于历史模式的预测
            predicted_fee = self.predict_hour(hour, features)
            predictions.append({
                'hour': hour,
                'predicted_fee': predicted_fee,
                'confidence': self.calculate_confidence(hour)
            })
        
        # 识别最佳交易窗口
        best_windows = self.identify_best_windows(predictions)
        
        return {
            'predictions': predictions,
            'best_windows': best_windows,
            'summary': self.generate_prediction_summary(predictions)
        }
    
    def extract_features(self, data):
        """提取预测特征"""
        
        features = {
            'hourly_pattern': self.extract_hourly_pattern(data),
            'daily_pattern': self.extract_daily_pattern(data),
            'trend': self.extract_trend(data),
            'volatility': self.calculate_volatility(data)
        }
        
        return features
    
    def predict_hour(self, hour, features):
        """预测特定小时的费用"""
        
        # 基础预测值（使用历史平均）
        base_prediction = features['hourly_pattern'][hour % 24]
        
        # 根据趋势调整
        trend_adjustment = features['trend'] * hour
        
        # 加入波动性
        volatility_factor = 1 + (features['volatility'] * random.uniform(-1, 1))
        
        predicted = base_prediction * (1 + trend_adjustment) * volatility_factor
        
        return max(1, predicted)  # 确保费用为正
    
    def identify_best_windows(self, predictions):
        """识别最佳交易窗口"""
        
        # 排序找出费用最低的时段
        sorted_predictions = sorted(predictions, key=lambda x: x['predicted_fee'])
        
        # 返回最佳的3个时段
        best_windows = []
        for pred in sorted_predictions[:3]:
            best_windows.append({
                'hour': pred['hour'],
                'predicted_fee': pred['predicted_fee'],
                'savings': f"{(1 - pred['predicted_fee']/predictions[0]['predicted_fee']) * 100:.1f}%"
            })
        
        return best_windows
```

### 7. 实时费用监控

```python
class FeeMonitor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.alert_thresholds = {
            'high_fee': 100,  # Gwei for ETH
            'fee_spike': 2,  # 2x average
            'low_fee': 20  # Gwei for ETH
        }
        
    async def monitor_fees_realtime(self, asset='ETH'):
        """实时监控费用"""
        
        moving_avg = []
        window_size = 6  # 1小时移动平均
        
        while True:
            try:
                # 获取当前费用
                current_fee = await self.get_current_fee(asset)
                
                # 更新移动平均
                moving_avg.append(current_fee)
                if len(moving_avg) > window_size:
                    moving_avg.pop(0)
                
                avg_fee = sum(moving_avg) / len(moving_avg)
                
                # 检查警报条件
                await self.check_alerts(current_fee, avg_fee, asset)
                
                # 生成实时报告
                report = {
                    'timestamp': datetime.now().isoformat(),
                    'current_fee': current_fee,
                    'hourly_avg': avg_fee,
                    'status': self.get_fee_status(current_fee, avg_fee)
                }
                
                print(f"费用监控: {report}")
                
                await asyncio.sleep(600)  # 10分钟检查一次
                
            except Exception as e:
                print(f"监控错误: {e}")
                await asyncio.sleep(60)
    
    async def check_alerts(self, current, average, asset):
        """检查并发送警报"""
        
        # 高费用警报
        if current > self.alert_thresholds['high_fee']:
            await self.send_alert(f"⚠️ 高费用警报: {current} Gwei")
        
        # 费用激增警报
        if current > average * self.alert_thresholds['fee_spike']:
            await self.send_alert(f"📈 费用激增: {current/average:.1f}x 平均值")
        
        # 低费用机会
        if current < self.alert_thresholds['low_fee']:
            await self.send_alert(f"✅ 低费用机会: {current} Gwei")
```

### 8. 综合费用仪表板

```python
class FeeDashboard:
    def __init__(self, api_key):
        self.api_key = api_key
        self.fee_analyzer = FeeAnalyzer(api_key)
        self.gas_optimizer = GasOptimizer(api_key)
        self.prediction_model = FeePredictionModel(api_key)
        
    def generate_comprehensive_report(self, asset='ETH'):
        """生成综合费用报告"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'asset': asset,
            'current_status': {},
            'analysis': {},
            'predictions': {},
            'recommendations': []
        }
        
        # 当前状态
        if asset == 'ETH':
            report['current_status'] = self.gas_optimizer.analyze_gas_patterns()
        else:
            report['current_status'] = self.fee_analyzer.analyze_fee_structure(asset)
        
        # 费用分析
        report['analysis'] = {
            'network_security': analyze_network_security(asset),
            'fee_distribution': self.analyze_fee_distribution(asset),
            'historical_comparison': self.compare_historical(asset)
        }
        
        # 预测
        report['predictions'] = self.prediction_model.predict_fees(asset, 24)
        
        # 生成建议
        report['recommendations'] = self.generate_recommendations(report)
        
        return report
    
    def analyze_fee_distribution(self, asset):
        """分析费用分布"""
        
        # 获取费用数据
        fee_data = self.get_recent_fees(asset, hours=168)  # 7天
        
        # 计算分位数
        fees = sorted([d['v'] for d in fee_data])
        
        percentiles = {
            'p10': fees[int(len(fees) * 0.1)],
            'p25': fees[int(len(fees) * 0.25)],
            'p50': fees[int(len(fees) * 0.5)],
            'p75': fees[int(len(fees) * 0.75)],
            'p90': fees[int(len(fees) * 0.9)]
        }
        
        return {
            'percentiles': percentiles,
            'current_percentile': self.calculate_current_percentile(fees),
            'interpretation': self.interpret_distribution(percentiles)
        }
    
    def generate_recommendations(self, report):
        """生成综合建议"""
        
        recommendations = []
        
        # 基于当前状态的建议
        if 'gas_price' in report['current_status']:
            current_price = float(report['current_status']['current_gas_price'].split()[0])
            
            if current_price > 100:
                recommendations.append({
                    'priority': 'HIGH',
                    'action': '延迟非紧急交易',
                    'reason': 'Gas 价格过高'
                })
            elif current_price < 30:
                recommendations.append({
                    'priority': 'HIGH',
                    'action': '执行计划中的交易',
                    'reason': 'Gas 价格处于低位'
                })
        
        # 基于预测的建议
        if report['predictions']['best_windows']:
            best_hour = report['predictions']['best_windows'][0]['hour']
            recommendations.append({
                'priority': 'MEDIUM',
                'action': f'计划在 {best_hour} 小时后交易',
                'reason': '预测费用将降低'
            })
        
        return recommendations
```

## 常见问题

### Q1: 为什么费用会突然激增？

可能原因：
- 热门 NFT 发售或 IDO
- DeFi 协议的流动性事件
- 网络升级或异常
- 市场剧烈波动导致交易激增

### Q2: 如何优化交易费用？

策略：
- 避开高峰时段（通常是美国工作时间）
- 使用费用预测工具
- 批量处理交易
- 选择适当的优先级

### Q3: EIP-1559 如何影响费用？

- 引入基础费用和优先费
- 费用更可预测
- 部分费用被销毁，减少供应

## 最佳实践

1. **定时交易**：在费用低谷期执行非紧急交易
2. **费用预算**：为重要交易预留足够的费用预算
3. **实时监控**：使用监控工具追踪费用变化
4. **批量优化**：合并多个操作减少总费用

---

*本文档详细介绍了 Glassnode Fees API 的使用方法。费用数据对于优化交易成本和理解网络经济至关重要。*