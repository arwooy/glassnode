# Mempool（内存池）API 文档

## 概述

Mempool API 提供区块链内存池的实时数据，包括待确认交易、费用估算、拥堵程度等。内存池是所有待处理交易的临时存储区，这些数据对于优化交易时机和费用至关重要。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/mempool/`

## 核心端点

### 1. 内存池大小

#### 1.1 交易数量

**端点**: `/count`

**描述**: 内存池中待确认的交易数量。

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/mempool/count?a=BTC&i=10m" \
  -H "X-Api-Key: YOUR_API_KEY"
```

#### 1.2 内存池大小（字节）

**端点**: `/size`

**描述**: 内存池中所有交易的总大小。

```python
class MempoolAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/mempool/"
        
    def analyze_mempool_congestion(self, asset='BTC'):
        """分析内存池拥堵状况"""
        
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '10m', 's': int(time.time()) - 24*3600}
        
        # 获取内存池数据
        tx_count = requests.get(
            self.base_url + "count",
            params=params,
            headers=headers
        ).json()
        
        mempool_size = requests.get(
            self.base_url + "size",
            params=params,
            headers=headers
        ).json()
        
        # 分析当前状态
        current_count = tx_count[-1]['v']
        current_size = mempool_size[-1]['v']
        
        # 计算平均交易大小
        avg_tx_size = current_size / current_count if current_count > 0 else 0
        
        # 评估拥堵程度
        congestion_level = self.assess_congestion_level(current_count, current_size)
        
        # 预测清空时间
        clearing_time = self.estimate_clearing_time(current_count, current_size)
        
        # 历史对比
        historical_comparison = self.compare_with_history(tx_count, mempool_size)
        
        return {
            'current_status': {
                'transaction_count': current_count,
                'size_bytes': current_size,
                'size_mb': f"{current_size / 1024 / 1024:.2f} MB",
                'avg_tx_size': f"{avg_tx_size:.0f} bytes"
            },
            'congestion_level': congestion_level,
            'clearing_estimate': clearing_time,
            'historical_comparison': historical_comparison,
            'recommendations': self.generate_recommendations(congestion_level)
        }
    
    def assess_congestion_level(self, tx_count, size):
        """评估拥堵程度"""
        
        # 基于交易数量和大小的阈值
        if tx_count > 50000 or size > 50000000:  # 50MB
            level = "严重拥堵"
            score = 90
            description = "交易确认可能严重延迟"
        elif tx_count > 20000 or size > 20000000:
            level = "高度拥堵"
            score = 70
            description = "交易确认时间延长"
        elif tx_count > 5000 or size > 5000000:
            level = "中度拥堵"
            score = 50
            description = "轻微延迟，费用上升"
        elif tx_count > 1000:
            level = "轻微拥堵"
            score = 30
            description = "正常范围，略有积压"
        else:
            level = "畅通"
            score = 10
            description = "内存池空闲，快速确认"
        
        return {
            'level': level,
            'score': score,
            'description': description,
            'impact': self.assess_impact(score)
        }
    
    def estimate_clearing_time(self, tx_count, size):
        """估算内存池清空时间"""
        
        # 假设参数
        block_interval = 600  # 10分钟
        max_block_size = 1000000  # 1MB
        txs_per_block = max_block_size / (size / tx_count) if tx_count > 0 else 2000
        
        blocks_needed = math.ceil(tx_count / txs_per_block)
        time_seconds = blocks_needed * block_interval
        
        if time_seconds < 3600:
            time_str = f"{time_seconds / 60:.0f} 分钟"
        elif time_seconds < 86400:
            time_str = f"{time_seconds / 3600:.1f} 小时"
        else:
            time_str = f"{time_seconds / 86400:.1f} 天"
        
        return {
            'blocks_needed': blocks_needed,
            'estimated_time': time_str,
            'assumptions': '假设无新交易进入且费用足够'
        }
    
    def compare_with_history(self, tx_count_data, size_data):
        """与历史数据对比"""
        
        current_count = tx_count_data[-1]['v']
        current_size = size_data[-1]['v']
        
        # 计算历史平均
        avg_count = sum(d['v'] for d in tx_count_data) / len(tx_count_data)
        avg_size = sum(d['v'] for d in size_data) / len(size_data)
        
        # 计算百分位
        count_values = sorted([d['v'] for d in tx_count_data])
        size_values = sorted([d['v'] for d in size_data])
        
        count_percentile = sum(1 for v in count_values if v < current_count) / len(count_values) * 100
        size_percentile = sum(1 for v in size_values if v < current_size) / len(size_values) * 100
        
        return {
            'vs_average': {
                'count': f"{(current_count / avg_count - 1) * 100:+.1f}%",
                'size': f"{(current_size / avg_size - 1) * 100:+.1f}%"
            },
            'percentiles': {
                'count_percentile': f"{count_percentile:.0f}%",
                'size_percentile': f"{size_percentile:.0f}%"
            },
            'interpretation': self.interpret_comparison(count_percentile, size_percentile)
        }
    
    def interpret_comparison(self, count_pct, size_pct):
        """解释历史对比"""
        
        avg_percentile = (count_pct + size_pct) / 2
        
        if avg_percentile > 90:
            return "历史高位 - 极度拥堵"
        elif avg_percentile > 70:
            return "高于平常 - 较为拥堵"
        elif avg_percentile > 30:
            return "正常范围"
        else:
            return "历史低位 - 非常空闲"
```

### 2. 费用分布

#### 2.1 费率分布

**端点**: `/fee_distribution`

**描述**: 按费率区间分布的交易。

```python
class MempoolFeeAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_fee_distribution(self, asset='BTC'):
        """分析费用分布"""
        
        url = "https://api.glassnode.com/v1/metrics/mempool/fee_distribution"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '10m'}
        
        response = requests.get(url, params=params, headers=headers)
        fee_dist = response.json()[-1]['v']
        
        # 分析费用层级
        fee_tiers = self.categorize_fee_tiers(fee_dist)
        
        # 计算最优费用
        optimal_fees = self.calculate_optimal_fees(fee_dist)
        
        # 费用竞争分析
        competition = self.analyze_fee_competition(fee_dist)
        
        # 预测费用趋势
        fee_trend = self.predict_fee_trend(fee_dist)
        
        return {
            'fee_distribution': fee_tiers,
            'optimal_fees': optimal_fees,
            'competition_analysis': competition,
            'fee_trend': fee_trend,
            'recommendations': self.generate_fee_recommendations(optimal_fees, competition)
        }
    
    def categorize_fee_tiers(self, distribution):
        """分类费用层级"""
        
        tiers = {
            'high_priority': {
                'range': '> 100 sat/vB',
                'count': 0,
                'percentage': 0,
                'use_case': '紧急交易'
            },
            'medium_priority': {
                'range': '50-100 sat/vB',
                'count': 0,
                'percentage': 0,
                'use_case': '标准交易'
            },
            'low_priority': {
                'range': '10-50 sat/vB',
                'count': 0,
                'percentage': 0,
                'use_case': '非紧急交易'
            },
            'minimal': {
                'range': '< 10 sat/vB',
                'count': 0,
                'percentage': 0,
                'use_case': '可等待交易'
            }
        }
        
        total = sum(distribution.values())
        
        for fee_rate, count in distribution.items():
            rate = float(fee_rate)
            percentage = (count / total * 100) if total > 0 else 0
            
            if rate > 100:
                tiers['high_priority']['count'] += count
                tiers['high_priority']['percentage'] += percentage
            elif rate > 50:
                tiers['medium_priority']['count'] += count
                tiers['medium_priority']['percentage'] += percentage
            elif rate > 10:
                tiers['low_priority']['count'] += count
                tiers['low_priority']['percentage'] += percentage
            else:
                tiers['minimal']['count'] += count
                tiers['minimal']['percentage'] += percentage
        
        return tiers
    
    def calculate_optimal_fees(self, distribution):
        """计算最优费用"""
        
        # 排序费率
        sorted_fees = sorted(distribution.items(), key=lambda x: float(x[0]))
        total = sum(v for _, v in sorted_fees)
        
        # 计算累积百分比
        cumulative = 0
        optimal_fees = {}
        
        for fee_rate, count in sorted_fees:
            cumulative += count
            percentage = (cumulative / total * 100) if total > 0 else 0
            
            # 找到不同确认速度的费率
            if percentage >= 10 and 'next_block' not in optimal_fees:
                optimal_fees['next_block'] = {
                    'fee_rate': f"{fee_rate} sat/vB",
                    'confidence': '90%',
                    'est_time': '~10 分钟'
                }
            elif percentage >= 50 and 'fast' not in optimal_fees:
                optimal_fees['fast'] = {
                    'fee_rate': f"{fee_rate} sat/vB",
                    'confidence': '50%',
                    'est_time': '~30 分钟'
                }
            elif percentage >= 80 and 'standard' not in optimal_fees:
                optimal_fees['standard'] = {
                    'fee_rate': f"{fee_rate} sat/vB",
                    'confidence': '20%',
                    'est_time': '~60 分钟'
                }
            elif percentage >= 95 and 'economy' not in optimal_fees:
                optimal_fees['economy'] = {
                    'fee_rate': f"{fee_rate} sat/vB",
                    'confidence': '5%',
                    'est_time': '2+ 小时'
                }
        
        return optimal_fees
    
    def analyze_fee_competition(self, distribution):
        """分析费用竞争"""
        
        # 计算费用集中度
        sorted_fees = sorted(distribution.items(), key=lambda x: -x[1])
        total = sum(v for _, v in sorted_fees)
        
        # 前10%的费率占比
        top_10_percent = int(len(sorted_fees) * 0.1) or 1
        top_fees_count = sum(v for _, v in sorted_fees[:top_10_percent])
        concentration = (top_fees_count / total * 100) if total > 0 else 0
        
        # 评估竞争程度
        if concentration > 50:
            competition = "激烈竞争"
            description = "大量交易集中在高费率"
        elif concentration > 30:
            competition = "中度竞争"
            description = "费率分布相对均匀"
        else:
            competition = "低竞争"
            description = "费率分散，容易确认"
        
        return {
            'level': competition,
            'concentration': f"{concentration:.1f}%",
            'description': description,
            'bidding_pressure': self.assess_bidding_pressure(distribution)
        }
    
    def assess_bidding_pressure(self, distribution):
        """评估出价压力"""
        
        # 计算费率标准差
        fees = []
        for fee_rate, count in distribution.items():
            fees.extend([float(fee_rate)] * count)
        
        if fees:
            mean_fee = sum(fees) / len(fees)
            std_dev = (sum((f - mean_fee) ** 2 for f in fees) / len(fees)) ** 0.5
            cv = std_dev / mean_fee if mean_fee > 0 else 0
            
            if cv > 1:
                return "高波动 - 费用竞标激烈"
            elif cv > 0.5:
                return "中等波动 - 正常竞标"
            else:
                return "低波动 - 稳定费用"
        
        return "无法评估"
```

### 3. 交易优先级

```python
class TransactionPriorityAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_tx_priorities(self, asset='BTC'):
        """分析交易优先级"""
        
        # 获取内存池数据
        mempool_data = self.get_mempool_snapshot(asset)
        
        # 按优先级分组
        priority_groups = self.group_by_priority(mempool_data)
        
        # 分析 RBF（Replace-By-Fee）交易
        rbf_analysis = self.analyze_rbf_transactions(mempool_data)
        
        # CPFP（Child-Pays-For-Parent）分析
        cpfp_analysis = self.analyze_cpfp_chains(mempool_data)
        
        # 大额交易优先级
        whale_tx_analysis = self.analyze_whale_transactions(mempool_data)
        
        return {
            'priority_distribution': priority_groups,
            'rbf_analysis': rbf_analysis,
            'cpfp_analysis': cpfp_analysis,
            'whale_transactions': whale_tx_analysis,
            'optimization_strategies': self.generate_optimization_strategies(priority_groups)
        }
    
    def group_by_priority(self, mempool_data):
        """按优先级分组交易"""
        
        priority_groups = {
            'urgent': {
                'criteria': '费率 > 100 sat/vB',
                'count': 0,
                'total_size': 0,
                'avg_wait_time': '< 10 分钟'
            },
            'high': {
                'criteria': '50-100 sat/vB',
                'count': 0,
                'total_size': 0,
                'avg_wait_time': '10-30 分钟'
            },
            'medium': {
                'criteria': '20-50 sat/vB',
                'count': 0,
                'total_size': 0,
                'avg_wait_time': '30-60 分钟'
            },
            'low': {
                'criteria': '< 20 sat/vB',
                'count': 0,
                'total_size': 0,
                'avg_wait_time': '> 60 分钟'
            }
        }
        
        # 分类逻辑（示例）
        for tx in mempool_data:
            fee_rate = tx.get('fee_rate', 0)
            size = tx.get('size', 0)
            
            if fee_rate > 100:
                priority_groups['urgent']['count'] += 1
                priority_groups['urgent']['total_size'] += size
            elif fee_rate > 50:
                priority_groups['high']['count'] += 1
                priority_groups['high']['total_size'] += size
            elif fee_rate > 20:
                priority_groups['medium']['count'] += 1
                priority_groups['medium']['total_size'] += size
            else:
                priority_groups['low']['count'] += 1
                priority_groups['low']['total_size'] += size
        
        return priority_groups
    
    def analyze_rbf_transactions(self, mempool_data):
        """分析 RBF 交易"""
        
        rbf_count = 0
        rbf_replacements = []
        
        for tx in mempool_data:
            if tx.get('rbf_enabled', False):
                rbf_count += 1
                
                # 检查是否有替换交易
                if tx.get('replacement_fee'):
                    rbf_replacements.append({
                        'original_fee': tx['original_fee'],
                        'new_fee': tx['replacement_fee'],
                        'increase': f"{(tx['replacement_fee'] / tx['original_fee'] - 1) * 100:.1f}%"
                    })
        
        return {
            'rbf_enabled_count': rbf_count,
            'rbf_percentage': f"{rbf_count / len(mempool_data) * 100:.1f}%" if mempool_data else "0%",
            'replacements': len(rbf_replacements),
            'avg_fee_increase': self.calculate_avg_fee_increase(rbf_replacements),
            'recommendation': "启用 RBF 以便调整费用" if rbf_count < len(mempool_data) * 0.5 else "RBF 使用率良好"
        }
    
    def analyze_cpfp_chains(self, mempool_data):
        """分析 CPFP 链"""
        
        cpfp_chains = []
        
        # 识别父子交易链
        for tx in mempool_data:
            if tx.get('has_children'):
                parent_fee = tx['fee_rate']
                children = tx.get('children', [])
                
                for child in children:
                    if child['fee_rate'] > parent_fee * 1.5:
                        cpfp_chains.append({
                            'parent_fee': parent_fee,
                            'child_fee': child['fee_rate'],
                            'boost_factor': child['fee_rate'] / parent_fee
                        })
        
        return {
            'cpfp_chains_count': len(cpfp_chains),
            'usage_rate': f"{len(cpfp_chains) / len(mempool_data) * 100:.1f}%" if mempool_data else "0%",
            'avg_boost_factor': sum(c['boost_factor'] for c in cpfp_chains) / len(cpfp_chains) if cpfp_chains else 0,
            'effectiveness': self.assess_cpfp_effectiveness(cpfp_chains)
        }
```

### 4. 内存池趋势分析

```python
class MempoolTrendAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_mempool_trends(self, asset='BTC'):
        """分析内存池趋势"""
        
        # 获取历史数据
        historical_data = self.get_historical_mempool_data(asset, days=7)
        
        # 识别模式
        patterns = self.identify_patterns(historical_data)
        
        # 预测未来趋势
        predictions = self.predict_future_trends(historical_data)
        
        # 周期性分析
        cyclical_analysis = self.analyze_cyclical_patterns(historical_data)
        
        # 异常检测
        anomalies = self.detect_anomalies(historical_data)
        
        return {
            'patterns': patterns,
            'predictions': predictions,
            'cyclical_analysis': cyclical_analysis,
            'anomalies': anomalies,
            'insights': self.generate_insights(patterns, predictions)
        }
    
    def identify_patterns(self, data):
        """识别内存池模式"""
        
        patterns = []
        
        # 检测周末效应
        weekend_pattern = self.detect_weekend_effect(data)
        if weekend_pattern:
            patterns.append(weekend_pattern)
        
        # 检测高峰时段
        peak_hours = self.detect_peak_hours(data)
        if peak_hours:
            patterns.append(peak_hours)
        
        # 检测费用螺旋
        fee_spiral = self.detect_fee_spiral(data)
        if fee_spiral:
            patterns.append(fee_spiral)
        
        return patterns
    
    def detect_weekend_effect(self, data):
        """检测周末效应"""
        
        weekday_avg = 0
        weekend_avg = 0
        weekday_count = 0
        weekend_count = 0
        
        for point in data:
            timestamp = point['timestamp']
            day_of_week = datetime.fromtimestamp(timestamp).weekday()
            
            if day_of_week < 5:  # 周一到周五
                weekday_avg += point['count']
                weekday_count += 1
            else:  # 周末
                weekend_avg += point['count']
                weekend_count += 1
        
        if weekday_count > 0 and weekend_count > 0:
            weekday_avg /= weekday_count
            weekend_avg /= weekend_count
            
            difference = (weekend_avg - weekday_avg) / weekday_avg * 100
            
            if abs(difference) > 20:
                return {
                    'type': 'weekend_effect',
                    'description': f"周末交易量{'增加' if difference > 0 else '减少'} {abs(difference):.1f}%",
                    'weekday_avg': weekday_avg,
                    'weekend_avg': weekend_avg,
                    'trading_tip': '考虑在周末进行非紧急交易' if difference < 0 else '周末可能费用较高'
                }
        
        return None
    
    def predict_future_trends(self, data):
        """预测未来趋势"""
        
        # 简单的线性预测
        recent_data = data[-24:]  # 最近24小时
        
        if len(recent_data) < 2:
            return {'status': '数据不足'}
        
        # 计算趋势
        x = range(len(recent_data))
        y = [d['count'] for d in recent_data]
        
        # 线性回归（简化）
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n
        
        # 预测未来6小时
        predictions = []
        for i in range(6):
            future_hour = n + i
            predicted_count = slope * future_hour + intercept
            predictions.append({
                'hour': i + 1,
                'predicted_count': max(0, int(predicted_count)),
                'trend': 'increasing' if slope > 0 else 'decreasing'
            })
        
        return {
            'next_6_hours': predictions,
            'trend_strength': abs(slope),
            'confidence': self.calculate_prediction_confidence(recent_data)
        }
```

### 5. 实时监控系统

```python
class MempoolMonitor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.alert_thresholds = {
            'high_congestion': 30000,  # 交易数
            'fee_spike': 100,  # sat/vB
            'size_threshold': 50000000,  # 50MB
            'clearing_time': 3600  # 1小时
        }
        
    async def monitor_mempool_realtime(self, asset='BTC'):
        """实时监控内存池"""
        
        previous_state = None
        
        while True:
            try:
                # 获取当前状态
                current_state = await self.get_current_mempool_state(asset)
                
                # 检查警报条件
                alerts = self.check_alert_conditions(current_state, previous_state)
                
                if alerts:
                    await self.send_alerts(alerts)
                
                # 生成状态报告
                report = self.generate_status_report(current_state, previous_state)
                
                # 更新仪表板
                await self.update_dashboard(report)
                
                previous_state = current_state
                
                await asyncio.sleep(60)  # 每分钟检查
                
            except Exception as e:
                print(f"监控错误: {e}")
                await asyncio.sleep(30)
    
    def check_alert_conditions(self, current, previous):
        """检查警报条件"""
        
        alerts = []
        
        # 拥堵警报
        if current['tx_count'] > self.alert_thresholds['high_congestion']:
            alerts.append({
                'type': 'CONGESTION',
                'severity': 'HIGH',
                'message': f"内存池严重拥堵: {current['tx_count']} 笔交易",
                'action': '考虑延迟交易或提高费用'
            })
        
        # 费用激增警报
        if current['median_fee'] > self.alert_thresholds['fee_spike']:
            alerts.append({
                'type': 'FEE_SPIKE',
                'severity': 'MEDIUM',
                'message': f"费用激增: {current['median_fee']} sat/vB",
                'action': '等待费用下降'
            })
        
        # 快速变化警报
        if previous and abs(current['tx_count'] - previous['tx_count']) / previous['tx_count'] > 0.5:
            alerts.append({
                'type': 'RAPID_CHANGE',
                'severity': 'INFO',
                'message': '内存池快速变化',
                'action': '密切关注'
            })
        
        return alerts
```

### 6. 综合仪表板

```python
class MempoolDashboard:
    def __init__(self, api_key):
        self.api_key = api_key
        self.analyzer = MempoolAnalyzer(api_key)
        self.fee_analyzer = MempoolFeeAnalyzer(api_key)
        self.priority_analyzer = TransactionPriorityAnalyzer(api_key)
        self.trend_analyzer = MempoolTrendAnalyzer(api_key)
        self.monitor = MempoolMonitor(api_key)
        
    def generate_comprehensive_report(self, asset='BTC'):
        """生成内存池综合报告"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'asset': asset,
            'congestion_analysis': {},
            'fee_analysis': {},
            'priority_analysis': {},
            'trend_analysis': {},
            'recommendations': [],
            'action_items': []
        }
        
        # 收集所有分析数据
        report['congestion_analysis'] = self.analyzer.analyze_mempool_congestion(asset)
        report['fee_analysis'] = self.fee_analyzer.analyze_fee_distribution(asset)
        report['priority_analysis'] = self.priority_analyzer.analyze_tx_priorities(asset)
        report['trend_analysis'] = self.trend_analyzer.analyze_mempool_trends(asset)
        
        # 生成综合建议
        report['recommendations'] = self.generate_recommendations(report)
        
        # 生成行动项
        report['action_items'] = self.generate_action_items(report)
        
        # 计算总体评分
        report['overall_assessment'] = self.calculate_overall_assessment(report)
        
        return report
    
    def generate_recommendations(self, data):
        """生成综合建议"""
        
        recommendations = []
        
        # 基于拥堵程度
        congestion_score = data['congestion_analysis']['congestion_level']['score']
        
        if congestion_score > 70:
            recommendations.append({
                'priority': 'HIGH',
                'type': 'TIMING',
                'recommendation': '延迟非紧急交易至少 2-4 小时',
                'reason': '当前内存池严重拥堵'
            })
        elif congestion_score < 30:
            recommendations.append({
                'priority': 'HIGH',
                'type': 'OPPORTUNITY',
                'recommendation': '立即执行计划中的交易',
                'reason': '内存池空闲，费用低'
            })
        
        # 基于费用分析
        optimal_fees = data['fee_analysis']['optimal_fees']
        
        if 'economy' in optimal_fees:
            economy_fee = float(optimal_fees['economy']['fee_rate'].split()[0])
            if economy_fee < 5:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'type': 'COST_SAVING',
                    'recommendation': f"使用 {economy_fee} sat/vB 的经济费率",
                    'reason': '可节省 50% 以上费用'
                })
        
        # 基于趋势
        if data['trend_analysis']['predictions']['trend_strength'] > 100:
            trend = data['trend_analysis']['predictions']['next_6_hours'][0]['trend']
            recommendations.append({
                'priority': 'MEDIUM',
                'type': 'TREND',
                'recommendation': f"预计未来拥堵将{'增加' if trend == 'increasing' else '减少'}",
                'reason': '基于历史趋势分析'
            })
        
        return recommendations
    
    def generate_action_items(self, data):
        """生成行动项"""
        
        actions = []
        
        congestion_level = data['congestion_analysis']['congestion_level']['level']
        
        # 紧急交易
        if congestion_level == "严重拥堵":
            actions.append({
                'action': 'URGENT_TX',
                'steps': [
                    '使用 RBF 启用交易',
                    f"设置费率 > {data['fee_analysis']['optimal_fees'].get('next_block', {}).get('fee_rate', '100 sat/vB')}",
                    '考虑使用加速服务'
                ]
            })
        
        # 常规交易
        elif congestion_level in ["轻微拥堵", "畅通"]:
            actions.append({
                'action': 'REGULAR_TX',
                'steps': [
                    '使用标准费率',
                    '批量处理多个交易',
                    '考虑使用 SegWit 减少大小'
                ]
            })
        
        # 优化建议
        if data['priority_analysis']['rbf_analysis']['rbf_percentage'] < 30:
            actions.append({
                'action': 'ENABLE_RBF',
                'steps': [
                    '在钱包中启用 RBF',
                    '为所有交易默认启用',
                    '保留调整费用的灵活性'
                ]
            })
        
        return actions
    
    def calculate_overall_assessment(self, data):
        """计算总体评估"""
        
        score = 100  # 起始分
        
        # 根据拥堵程度扣分
        congestion_score = data['congestion_analysis']['congestion_level']['score']
        score -= congestion_score * 0.5
        
        # 根据费用水平扣分
        if 'next_block' in data['fee_analysis']['optimal_fees']:
            fee = float(data['fee_analysis']['optimal_fees']['next_block']['fee_rate'].split()[0])
            if fee > 100:
                score -= 20
            elif fee > 50:
                score -= 10
        
        # 根据趋势调整
        trend = data['trend_analysis']['predictions'].get('next_6_hours', [{}])[0].get('trend')
        if trend == 'increasing':
            score -= 10
        elif trend == 'decreasing':
            score += 10
        
        # 生成评级
        if score >= 80:
            rating = "优秀"
            description = "理想的交易时机"
        elif score >= 60:
            rating = "良好"
            description = "适合常规交易"
        elif score >= 40:
            rating = "一般"
            description = "可接受但不理想"
        elif score >= 20:
            rating = "较差"
            description = "建议等待"
        else:
            rating = "糟糕"
            description = "强烈建议延迟交易"
        
        return {
            'score': max(0, min(100, score)),
            'rating': rating,
            'description': description,
            'best_action': self.determine_best_action(score)
        }
    
    def determine_best_action(self, score):
        """确定最佳行动"""
        
        if score >= 80:
            return "立即执行所有计划交易"
        elif score >= 60:
            return "执行重要交易，延迟其他"
        elif score >= 40:
            return "仅执行紧急交易"
        else:
            return "延迟所有非关键交易"
```

## 常见问题

### Q1: 内存池大小如何影响交易确认？

影响：
- **大内存池**：竞争激烈，需要更高费用
- **小内存池**：快速确认，低费用
- **清空时间**：决定等待策略

### Q2: 如何选择合适的交易费用？

策略：
- **紧急交易**：使用高于中位数 50% 的费率
- **标准交易**：使用中位数费率
- **可等待**：使用最低 10% 分位费率

### Q3: RBF 和 CPFP 有什么区别？

区别：
- **RBF**：发送方可以提高自己交易的费用
- **CPFP**：接收方通过子交易提高父交易优先级
- **使用场景**：RBF 更灵活，CPFP 用于无 RBF 的交易

## 最佳实践

1. **监控内存池**：定期检查拥堵状况
2. **灵活费用策略**：根据紧急程度调整
3. **使用 RBF**：保留调整费用的选项
4. **批量交易**：减少总体费用

---

*本文档详细介绍了 Glassnode Mempool API 的使用方法。内存池数据是优化交易时机和费用的关键。*