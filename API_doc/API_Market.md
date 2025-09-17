# Market（市场指标）API 文档

## 概述

Market API 提供全面的市场分析指标，包括价格、市值、估值模型、市场情绪指标等。这些指标帮助投资者评估市场状态、识别趋势和制定交易策略。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/market/`

## 核心端点

### 1. 价格相关指标

#### 1.1 亚洲时段价格变化

**端点**: `/apac_30d_price_change`

**描述**: 亚太地区交易时段（UTC 00:00-08:00）的30天价格变化。

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/market/apac_30d_price_change?a=BTC" \
  -H "X-Api-Key: YOUR_API_KEY"
```

#### 1.2 欧洲时段价格变化

**端点**: `/emea_30d_price_change`

**描述**: 欧洲、中东和非洲地区交易时段（UTC 08:00-16:00）的30天价格变化。

#### 1.3 美洲时段价格变化

**端点**: `/amer_30d_price_change`

**描述**: 美洲地区交易时段（UTC 16:00-24:00）的30天价格变化。

**地域分析示例**:
```python
def analyze_regional_trading_patterns(asset='BTC'):
    """分析不同地区的交易模式"""
    
    base_url = "https://api.glassnode.com/v1/metrics/market/"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '24h'}
    
    regions = {
        'asia': 'apac_30d_price_change',
        'europe': 'emea_30d_price_change', 
        'americas': 'amer_30d_price_change'
    }
    
    regional_data = {}
    
    for region, endpoint in regions.items():
        response = requests.get(base_url + endpoint, params=params, headers=headers)
        data = response.json()
        regional_data[region] = data[-1]['v'] if data else 0
    
    # 找出最活跃的地区
    most_active = max(regional_data, key=lambda x: abs(regional_data[x]))
    
    # 计算地区间差异
    volatility_diff = max(regional_data.values()) - min(regional_data.values())
    
    return {
        'regional_performance': regional_data,
        'most_active_region': most_active,
        'regional_divergence': f"{volatility_diff:.2f}%",
        'trading_recommendation': generate_regional_strategy(regional_data)
    }

def generate_regional_strategy(regional_data):
    """基于地区差异生成交易策略"""
    
    if regional_data['asia'] > 0 and regional_data['europe'] < 0:
        return "亚洲买入，欧洲卖出 - 考虑时区套利"
    elif abs(max(regional_data.values()) - min(regional_data.values())) > 5:
        return "地区差异大，关注跨时区价格传导"
    else:
        return "地区表现一致，全球趋势明确"
```

### 2. 市值指标

#### 2.1 BTC 主导地位

**端点**: `/btc_dominance`

**描述**: 比特币市值占整个加密货币市场总市值的百分比。

```python
def analyze_btc_dominance_trend():
    """分析 BTC 主导地位趋势"""
    
    url = "https://api.glassnode.com/v1/metrics/market/btc_dominance"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'i': '24h', 's': int(time.time()) - 90*86400}
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    df = pd.DataFrame(data)
    current_dominance = df['v'].iloc[-1]
    
    # 计算趋势
    df['ma7'] = df['v'].rolling(7).mean()
    df['ma30'] = df['v'].rolling(30).mean()
    
    trend = "上升" if df['ma7'].iloc[-1] > df['ma30'].iloc[-1] else "下降"
    
    # 市场阶段判断
    if current_dominance > 60:
        market_phase = "BTC 主导期 - 资金集中于比特币"
    elif current_dominance < 40:
        market_phase = "山寨季 - 资金流向其他加密货币"
    else:
        market_phase = "过渡期 - 市场资金分散"
    
    return {
        'current_dominance': f"{current_dominance:.2f}%",
        'trend': trend,
        'market_phase': market_phase,
        '90d_high': f"{df['v'].max():.2f}%",
        '90d_low': f"{df['v'].min():.2f}%"
    }
```

#### 2.2 市值（Market Cap）

**端点**: `/marketcap_usd`

**描述**: 当前供应量乘以当前美元价格的总市值。

#### 2.3 已实现市值（Realized Cap）

**端点**: `/marketcap_realized_usd`

**描述**: 每个币按其最后移动时的价格计算的总和，反映实际投资成本。

### 3. 估值模型

#### 3.1 MVRV 比率

**端点**: `/mvrv`

**描述**: 市值与已实现市值的比率，衡量持有者的平均盈亏。

**MVRV 分析系统**:
```python
class MVRVAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_mvrv(self, asset='BTC'):
        """全面分析 MVRV 指标"""
        
        url = "https://api.glassnode.com/v1/metrics/market/mvrv"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h', 's': int(time.time()) - 365*86400}
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        df = pd.DataFrame(data)
        df['t'] = pd.to_datetime(df['t'], unit='s')
        
        current_mvrv = df['v'].iloc[-1]
        
        # 计算历史分位数
        percentile = (df['v'] < current_mvrv).sum() / len(df) * 100
        
        # 识别极值区域
        top_threshold = df['v'].quantile(0.9)
        bottom_threshold = df['v'].quantile(0.1)
        
        # 生成交易信号
        signal = self.generate_mvrv_signal(current_mvrv, top_threshold, bottom_threshold)
        
        return {
            'current_mvrv': round(current_mvrv, 3),
            'historical_percentile': f"{percentile:.1f}%",
            'market_valuation': self.interpret_mvrv(current_mvrv),
            'signal': signal,
            'top_zone': round(top_threshold, 3),
            'bottom_zone': round(bottom_threshold, 3)
        }
    
    def interpret_mvrv(self, mvrv):
        """解释 MVRV 值"""
        if mvrv > 3.5:
            return "极度高估 - 历史顶部区域"
        elif mvrv > 2.5:
            return "高估 - 考虑减仓"
        elif mvrv > 1.5:
            return "合理偏高 - 牛市中期"
        elif mvrv > 1:
            return "合理估值 - 持有"
        elif mvrv > 0.8:
            return "低估 - 考虑加仓"
        else:
            return "极度低估 - 历史底部区域"
    
    def generate_mvrv_signal(self, current, top, bottom):
        """生成 MVRV 交易信号"""
        if current > top:
            return {
                'action': 'SELL',
                'confidence': 'HIGH',
                'reason': 'MVRV 处于历史高位'
            }
        elif current < bottom:
            return {
                'action': 'BUY',
                'confidence': 'HIGH',
                'reason': 'MVRV 处于历史低位'
            }
        else:
            return {
                'action': 'HOLD',
                'confidence': 'MEDIUM',
                'reason': 'MVRV 在正常范围'
            }
```

#### 3.2 MVRV Z-Score

**端点**: `/mvrv_z_score`

**描述**: MVRV 的标准化值，帮助识别市场的极端状态。

```python
def analyze_mvrv_zscore(asset='BTC'):
    """分析 MVRV Z-Score"""
    
    url = "https://api.glassnode.com/v1/metrics/market/mvrv_z_score"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '24h'}
    
    response = requests.get(url, params=params, headers=headers)
    zscore = response.json()[-1]['v']
    
    # Z-Score 解释
    if zscore > 7:
        interpretation = "极度过热 - 强烈卖出信号"
        action = "STRONG_SELL"
    elif zscore > 5:
        interpretation = "过热 - 卖出信号"
        action = "SELL"
    elif zscore > 2:
        interpretation = "偏热 - 谨慎看涨"
        action = "CAUTIOUS_BULL"
    elif zscore > -0.5:
        interpretation = "中性区域"
        action = "HOLD"
    elif zscore > -2:
        interpretation = "偏冷 - 逢低买入"
        action = "BUY_DIP"
    else:
        interpretation = "极度超卖 - 强烈买入信号"
        action = "STRONG_BUY"
    
    return {
        'z_score': round(zscore, 3),
        'interpretation': interpretation,
        'action': action,
        'risk_level': abs(zscore) / 10 * 100  # 风险水平 0-100
    }
```

#### 3.3 Delta Cap

**端点**: `/deltacap_usd`

**描述**: 已实现市值与平均市值的差值，衡量资本流入。

```python
def analyze_delta_cap(asset='BTC'):
    """分析 Delta Cap 指标"""
    
    url = "https://api.glassnode.com/v1/metrics/market/deltacap_usd"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '24h', 's': int(time.time()) - 180*86400}
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    df = pd.DataFrame(data)
    
    # 计算变化率
    df['change_rate'] = df['v'].pct_change()
    
    # 识别资本流动趋势
    recent_trend = df['change_rate'].tail(7).mean()
    
    if recent_trend > 0.02:
        capital_flow = "强劲流入"
    elif recent_trend > 0:
        capital_flow = "温和流入"
    elif recent_trend > -0.02:
        capital_flow = "温和流出"
    else:
        capital_flow = "强劲流出"
    
    return {
        'current_delta_cap': f"${df['v'].iloc[-1]/1e9:.2f}B",
        'capital_flow': capital_flow,
        '7d_change': f"{df['change_rate'].tail(7).sum()*100:.2f}%",
        'trend_strength': abs(recent_trend) * 1000
    }
```

### 4. 特殊指标

#### 4.1 HODL Cave

**端点**: `/hodl_cave`

**描述**: 不同持有期的历史收益分析。

```python
def analyze_hodl_returns(asset='BTC'):
    """分析不同持有期的收益"""
    
    url = "https://api.glassnode.com/v1/metrics/market/hodl_cave"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset}
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()[-1]['v']
    
    # 分析不同持有期的收益
    holding_periods = {
        '1_month': data.get('1m', 0),
        '3_months': data.get('3m', 0),
        '6_months': data.get('6m', 0),
        '1_year': data.get('1y', 0),
        '2_years': data.get('2y', 0),
        '3_years': data.get('3y', 0),
        '5_years': data.get('5y', 0)
    }
    
    # 找出最佳持有期
    best_period = max(holding_periods, key=holding_periods.get)
    worst_period = min(holding_periods, key=holding_periods.get)
    
    # 生成持有建议
    if holding_periods['1_month'] < -20:
        suggestion = "短期超卖，可能反弹"
    elif holding_periods['1_year'] > 100:
        suggestion = "长期收益优异，继续持有"
    else:
        suggestion = "正常波动范围"
    
    return {
        'returns_by_period': holding_periods,
        'best_holding_period': best_period,
        'worst_holding_period': worst_period,
        'investment_suggestion': suggestion
    }
```

#### 4.2 股票流量模型（Stock-to-Flow）

**端点**: `/stock_to_flow_ratio`

**描述**: 存量与新增供应的比率，稀缺性指标。

```python
def analyze_stock_to_flow(asset='BTC'):
    """分析 S2F 模型"""
    
    url = "https://api.glassnode.com/v1/metrics/market/stock_to_flow_ratio"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '24h'}
    
    response = requests.get(url, params=params, headers=headers)
    s2f = response.json()[-1]['v']
    
    # S2F 模型价格预测（简化版）
    model_price = s2f ** 3 * 0.18  # 简化的 S2F 模型
    
    # 获取当前价格进行对比
    current_price = get_current_price(asset)
    deviation = (current_price - model_price) / model_price * 100
    
    if deviation > 50:
        valuation = "严重高估"
    elif deviation > 0:
        valuation = "高于模型价格"
    elif deviation > -50:
        valuation = "低于模型价格"
    else:
        valuation = "严重低估"
    
    return {
        'stock_to_flow': round(s2f, 2),
        'model_price': f"${model_price:,.0f}",
        'current_price': f"${current_price:,.0f}",
        'deviation': f"{deviation:.1f}%",
        'valuation': valuation
    }
```

### 5. 综合市场分析

```python
class MarketAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/market/"
        
    def comprehensive_market_analysis(self, asset='BTC'):
        """综合市场分析"""
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'asset': asset,
            'valuation': {},
            'sentiment': {},
            'trend': {},
            'signals': []
        }
        
        # 估值分析
        analysis['valuation'] = self.valuation_analysis(asset)
        
        # 情绪分析
        analysis['sentiment'] = self.sentiment_analysis(asset)
        
        # 趋势分析
        analysis['trend'] = self.trend_analysis(asset)
        
        # 生成综合信号
        analysis['signals'] = self.generate_signals(analysis)
        
        # 计算综合评分
        analysis['overall_score'] = self.calculate_score(analysis)
        
        return analysis
    
    def valuation_analysis(self, asset):
        """估值分析"""
        
        metrics = {}
        
        # MVRV
        mvrv_data = self.get_metric('mvrv', asset)
        metrics['mvrv'] = {
            'value': mvrv_data[-1]['v'],
            'signal': self.interpret_mvrv_signal(mvrv_data[-1]['v'])
        }
        
        # MVRV Z-Score
        zscore_data = self.get_metric('mvrv_z_score', asset)
        metrics['mvrv_zscore'] = {
            'value': zscore_data[-1]['v'],
            'signal': self.interpret_zscore_signal(zscore_data[-1]['v'])
        }
        
        # Market Cap
        mcap_data = self.get_metric('marketcap_usd', asset)
        metrics['market_cap'] = mcap_data[-1]['v']
        
        return metrics
    
    def sentiment_analysis(self, asset):
        """情绪分析"""
        
        sentiment_score = 0
        factors = []
        
        # 分析各种情绪指标
        # ... 实现细节 ...
        
        return {
            'score': sentiment_score,
            'level': self.get_sentiment_level(sentiment_score),
            'factors': factors
        }
    
    def trend_analysis(self, asset):
        """趋势分析"""
        
        # 获取价格数据
        price_data = self.get_price_data(asset, 90)
        
        # 计算移动平均
        ma20 = self.calculate_ma(price_data, 20)
        ma50 = self.calculate_ma(price_data, 50)
        
        # 判断趋势
        if ma20 > ma50:
            trend = "上升趋势"
            strength = (ma20 - ma50) / ma50 * 100
        else:
            trend = "下降趋势"
            strength = (ma50 - ma20) / ma50 * 100
        
        return {
            'direction': trend,
            'strength': f"{strength:.2f}%",
            'ma20': ma20,
            'ma50': ma50
        }
    
    def generate_signals(self, analysis):
        """生成交易信号"""
        
        signals = []
        
        # 基于估值的信号
        if analysis['valuation']['mvrv']['signal'] == 'BUY':
            signals.append({
                'type': 'valuation',
                'action': 'BUY',
                'reason': 'MVRV 处于低位',
                'confidence': 'HIGH'
            })
        
        # 基于趋势的信号
        if analysis['trend']['direction'] == "上升趋势":
            signals.append({
                'type': 'trend',
                'action': 'BUY',
                'reason': '上升趋势确立',
                'confidence': 'MEDIUM'
            })
        
        return signals
    
    def calculate_score(self, analysis):
        """计算综合评分 (0-100)"""
        
        score = 50  # 基础分
        
        # 估值加分
        if analysis['valuation']['mvrv']['value'] < 1.5:
            score += 20
        elif analysis['valuation']['mvrv']['value'] > 3:
            score -= 20
        
        # 趋势加分
        if analysis['trend']['direction'] == "上升趋势":
            score += 15
        else:
            score -= 15
        
        # 限制在 0-100 范围
        return max(0, min(100, score))
```

### 6. 实时监控和预警

```python
class MarketMonitor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.alert_conditions = {
            'mvrv_extreme_high': 3.5,
            'mvrv_extreme_low': 0.8,
            'zscore_extreme': 5,
            'dominance_shift': 5  # 5% 变化
        }
        
    async def monitor_market(self, asset='BTC'):
        """实时监控市场指标"""
        
        last_values = {}
        
        while True:
            try:
                # 检查 MVRV
                mvrv = await self.get_current_mvrv(asset)
                if mvrv > self.alert_conditions['mvrv_extreme_high']:
                    await self.send_alert(f"⚠️ MVRV 极高: {mvrv:.2f}")
                elif mvrv < self.alert_conditions['mvrv_extreme_low']:
                    await self.send_alert(f"🔔 MVRV 极低: {mvrv:.2f}")
                
                # 检查 Z-Score
                zscore = await self.get_current_zscore(asset)
                if abs(zscore) > self.alert_conditions['zscore_extreme']:
                    await self.send_alert(f"⚠️ Z-Score 极值: {zscore:.2f}")
                
                # 检查 BTC 主导地位变化
                if asset == 'BTC':
                    dominance = await self.get_btc_dominance()
                    if 'dominance' in last_values:
                        change = abs(dominance - last_values['dominance'])
                        if change > self.alert_conditions['dominance_shift']:
                            await self.send_alert(f"🔄 BTC 主导地位大幅变化: {change:.2f}%")
                    last_values['dominance'] = dominance
                
                await asyncio.sleep(3600)  # 每小时检查
                
            except Exception as e:
                print(f"监控错误: {e}")
                await asyncio.sleep(300)
```

## 回测框架

```python
class MarketBacktester:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def backtest_mvrv_strategy(self, asset='BTC', start_date=None, end_date=None):
        """回测 MVRV 策略"""
        
        # 获取历史数据
        mvrv_data = self.get_historical_mvrv(asset, start_date, end_date)
        price_data = self.get_historical_price(asset, start_date, end_date)
        
        # 策略参数
        buy_threshold = 1.0
        sell_threshold = 3.0
        
        # 回测逻辑
        trades = []
        position = None
        
        for i in range(len(mvrv_data)):
            mvrv = mvrv_data[i]['v']
            price = price_data[i]['v']
            timestamp = mvrv_data[i]['t']
            
            if position is None and mvrv < buy_threshold:
                # 买入信号
                position = {
                    'type': 'BUY',
                    'price': price,
                    'timestamp': timestamp,
                    'mvrv': mvrv
                }
            elif position and mvrv > sell_threshold:
                # 卖出信号
                trades.append({
                    'buy': position,
                    'sell': {
                        'price': price,
                        'timestamp': timestamp,
                        'mvrv': mvrv
                    },
                    'profit': (price - position['price']) / position['price'] * 100
                })
                position = None
        
        # 计算策略表现
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t['profit'] > 0)
        total_profit = sum(t['profit'] for t in trades)
        
        return {
            'total_trades': total_trades,
            'win_rate': winning_trades / total_trades * 100 if total_trades > 0 else 0,
            'total_return': f"{total_profit:.2f}%",
            'trades': trades,
            'sharpe_ratio': self.calculate_sharpe(trades)
        }
```

## 常见问题

### Q1: MVRV 和 MVRV Z-Score 有什么区别？

- **MVRV**: 原始比率，直接反映市值与实现市值的关系
- **MVRV Z-Score**: 标准化后的值，更容易识别历史极值

### Q2: 如何结合多个市场指标？

建议权重：
- MVRV: 30%
- 趋势指标: 25%
- 市场情绪: 25%
- 技术指标: 20%

### Q3: 地域价格差异说明什么？

- 大差异：可能存在套利机会
- 亚洲领涨：散户主导
- 美洲领涨：机构主导

## 最佳实践

1. **多指标验证**：不依赖单一指标，使用多个指标交叉验证
2. **历史回测**：新策略先进行充分回测
3. **风险管理**：根据市场指标调整仓位大小
4. **定期校准**：市场结构变化，需要定期调整模型参数

---

*本文档详细介绍了 Glassnode Market API 的使用方法。市场指标是评估加密货币市场状态和制定投资策略的核心工具。*