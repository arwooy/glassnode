# Derivatives（衍生品）API 文档

## 概述

Derivatives API 提供加密货币衍生品市场的全面数据，包括期货（Futures）和期权（Options）的交易量、未平仓合约、清算数据、资金费率等关键指标。这些数据对于理解市场情绪、预测价格走势和风险管理至关重要。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/derivatives/`

**支持的衍生品类型**:
- 永续合约（Perpetual Futures）
- 定期期货（Fixed-term Futures）
- 期权（Options）

**数据来源**: 主要交易所包括 Binance, OKX, Bybit, Deribit, CME 等

## 期货（Futures）端点

### 1. 未平仓合约（Open Interest）

#### 1.1 总未平仓合约

**端点**: `/futures_open_interest_sum`

**描述**: 所有期货合约中的资金总额。反映市场参与度和资金流入。

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/derivatives/futures_open_interest_sum?a=BTC&i=1h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

#### 1.2 现金保证金未平仓合约

**端点**: `/futures_open_interest_cash_margined_sum`

**描述**: 使用美元或稳定币作为保证金的期货合约总价值。

#### 1.3 加密货币保证金未平仓合约

**端点**: `/futures_open_interest_crypto_margined_sum`

**描述**: 使用加密货币（如 BTC）作为保证金的期货合约总价值。

**对比分析示例**:
```python
import requests
import pandas as pd

def analyze_margin_preference(asset='BTC'):
    """分析保证金类型偏好"""
    
    base_url = "https://api.glassnode.com/v1/metrics/derivatives/"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '24h', 's': int(time.time()) - 30*86400}
    
    # 获取两种保证金类型的数据
    cash_margined = requests.get(
        base_url + "futures_open_interest_cash_margined_sum",
        params=params, headers=headers
    ).json()
    
    crypto_margined = requests.get(
        base_url + "futures_open_interest_crypto_margined_sum",
        params=params, headers=headers
    ).json()
    
    # 分析趋势
    analysis = []
    for i in range(len(cash_margined)):
        total = cash_margined[i]['v'] + crypto_margined[i]['v']
        analysis.append({
            'timestamp': cash_margined[i]['t'],
            'cash_margined': cash_margined[i]['v'],
            'crypto_margined': crypto_margined[i]['v'],
            'total': total,
            'cash_ratio': (cash_margined[i]['v'] / total * 100) if total > 0 else 0,
            'crypto_ratio': (crypto_margined[i]['v'] / total * 100) if total > 0 else 0
        })
    
    df = pd.DataFrame(analysis)
    
    # 识别趋势变化
    recent_cash_ratio = df['cash_ratio'].tail(7).mean()
    older_cash_ratio = df['cash_ratio'].head(7).mean()
    
    trend = "转向现金保证金" if recent_cash_ratio > older_cash_ratio else "转向加密保证金"
    
    return {
        'current_preference': '现金保证金' if df['cash_ratio'].iloc[-1] > 50 else '加密保证金',
        'trend': trend,
        'cash_margined_ratio': f"{df['cash_ratio'].iloc[-1]:.2f}%",
        'crypto_margined_ratio': f"{df['crypto_ratio'].iloc[-1]:.2f}%",
        'total_open_interest': df['total'].iloc[-1]
    }
```

#### 1.4 当前未平仓合约

**端点**: `/futures_open_interest_current`

**描述**: 最新的未平仓合约价值，实时反映市场仓位。

### 2. 期货交易量（Volume）

#### 2.1 总交易量

**端点**: `/futures_volume_sum`

**描述**: 所有期货交易所的总交易量。

#### 2.2 买入/卖出交易量

**端点**: 
- `/futures_volume_buy_sum` - 买入交易量
- `/futures_volume_sell_sum` - 卖出交易量

**买卖压力分析**:
```python
def analyze_buy_sell_pressure(asset='BTC', period_hours=24):
    """分析买卖压力"""
    
    base_url = "https://api.glassnode.com/v1/metrics/derivatives/"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {
        'a': asset,
        'i': '1h',
        's': int(time.time()) - period_hours * 3600
    }
    
    # 获取买卖量数据
    buy_volume = requests.get(
        base_url + "futures_volume_buy_sum",
        params=params, headers=headers
    ).json()
    
    sell_volume = requests.get(
        base_url + "futures_volume_sell_sum",
        params=params, headers=headers
    ).json()
    
    # 计算买卖比率
    total_buy = sum(d['v'] for d in buy_volume)
    total_sell = sum(d['v'] for d in sell_volume)
    
    buy_ratio = total_buy / (total_buy + total_sell) * 100
    
    # 计算动量
    recent_buy = sum(d['v'] for d in buy_volume[-6:])  # 最近6小时
    recent_sell = sum(d['v'] for d in sell_volume[-6:])
    momentum = (recent_buy - recent_sell) / (recent_buy + recent_sell) * 100
    
    # 判断市场情绪
    if buy_ratio > 55 and momentum > 10:
        sentiment = "强烈看涨"
    elif buy_ratio > 52:
        sentiment = "温和看涨"
    elif buy_ratio < 45 and momentum < -10:
        sentiment = "强烈看跌"
    elif buy_ratio < 48:
        sentiment = "温和看跌"
    else:
        sentiment = "中性"
    
    return {
        'buy_volume_24h': total_buy,
        'sell_volume_24h': total_sell,
        'buy_ratio': f"{buy_ratio:.2f}%",
        'momentum': f"{momentum:.2f}%",
        'market_sentiment': sentiment
    }
```

#### 2.3 永续合约交易量

**端点**: `/futures_volume_perpetual_sum`

**描述**: 永续合约的交易量，这是最活跃的衍生品类型。

#### 2.4 24小时交易量

**端点**: `/futures_volume_24h`

**描述**: 滚动24小时交易量。

### 3. 清算（Liquidations）

#### 3.1 多头清算

**端点**:
- `/futures_liquidations_long_sum` - 多头清算总额
- `/futures_liquidations_long_mean` - 多头清算平均值
- `/futures_liquidations_long_dominance` - 多头清算占比

#### 3.2 空头清算

**端点**:
- `/futures_liquidations_short_sum` - 空头清算总额
- `/futures_liquidations_short_mean` - 空头清算平均值
- `/futures_liquidations_short_dominance` - 空头清算占比

**清算分析系统**:
```python
class LiquidationAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/derivatives/"
        
    def analyze_liquidations(self, asset='BTC', period_days=7):
        """全面分析清算数据"""
        
        headers = {"X-Api-Key": self.api_key}
        params = {
            'a': asset,
            'i': '1h',
            's': int(time.time()) - period_days * 86400
        }
        
        # 获取清算数据
        long_liq = self.get_data("futures_liquidations_long_sum", params, headers)
        short_liq = self.get_data("futures_liquidations_short_sum", params, headers)
        long_dom = self.get_data("futures_liquidations_long_dominance", params, headers)
        
        # 构建分析数据框
        df = pd.DataFrame({
            'timestamp': [d['t'] for d in long_liq],
            'long_liquidations': [d['v'] for d in long_liq],
            'short_liquidations': [d['v'] for d in short_liq],
            'long_dominance': [d['v'] for d in long_dom]
        })
        
        # 识别大规模清算事件
        df['total_liquidations'] = df['long_liquidations'] + df['short_liquidations']
        threshold = df['total_liquidations'].quantile(0.95)  # 95分位数
        
        major_events = df[df['total_liquidations'] > threshold]
        
        # 分析清算模式
        patterns = self.identify_liquidation_patterns(df)
        
        # 预测潜在清算水平
        risk_levels = self.calculate_liquidation_risk_levels(df, asset)
        
        return {
            'summary': {
                'total_long_liquidated': df['long_liquidations'].sum(),
                'total_short_liquidated': df['short_liquidations'].sum(),
                'average_long_dominance': df['long_dominance'].mean(),
                'major_liquidation_events': len(major_events)
            },
            'patterns': patterns,
            'risk_levels': risk_levels,
            'recommendations': self.generate_recommendations(patterns, risk_levels)
        }
    
    def identify_liquidation_patterns(self, df):
        """识别清算模式"""
        
        patterns = []
        
        # 检测级联清算
        df['liq_spike'] = df['total_liquidations'] > df['total_liquidations'].rolling(12).mean() * 3
        cascades = df[df['liq_spike']].index.tolist()
        
        if cascades:
            patterns.append({
                'type': '级联清算',
                'occurrences': len(cascades),
                'risk': '高'
            })
        
        # 检测方向性偏差
        recent_long_dom = df['long_dominance'].tail(24).mean()
        if recent_long_dom > 65:
            patterns.append({
                'type': '空头挤压风险',
                'probability': '中',
                'direction': '上涨'
            })
        elif recent_long_dom < 35:
            patterns.append({
                'type': '多头挤压风险',
                'probability': '中',
                'direction': '下跌'
            })
        
        return patterns
    
    def calculate_liquidation_risk_levels(self, df, asset):
        """计算潜在清算价格水平"""
        
        # 基于历史清算数据估算风险价格
        # 这是简化示例，实际需要更复杂的模型
        
        current_price = self.get_current_price(asset)
        
        # 估算常见杠杆水平的清算价格
        risk_levels = {
            '2x_long': current_price * 0.5,
            '5x_long': current_price * 0.8,
            '10x_long': current_price * 0.9,
            '20x_long': current_price * 0.95,
            '2x_short': current_price * 2,
            '5x_short': current_price * 1.25,
            '10x_short': current_price * 1.11,
            '20x_short': current_price * 1.05
        }
        
        return risk_levels
```

### 4. 资金费率（Funding Rate）

**端点**: `/futures_funding_rate`

**描述**: 永续合约的资金费率，反映多空力量对比和市场情绪。

**资金费率策略**:
```python
def funding_rate_arbitrage_strategy(asset='BTC'):
    """资金费率套利策略分析"""
    
    url = "https://api.glassnode.com/v1/metrics/derivatives/futures_funding_rate"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '1h', 's': int(time.time()) - 7*86400}
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    df = pd.DataFrame(data)
    df['t'] = pd.to_datetime(df['t'], unit='s')
    
    # 计算年化收益率
    df['annualized_rate'] = df['v'] * 3 * 365 * 100  # 假设每8小时结算
    
    # 识别套利机会
    opportunities = []
    
    current_rate = df['annualized_rate'].iloc[-1]
    avg_rate = df['annualized_rate'].mean()
    
    if current_rate > 20:  # 年化 > 20%
        opportunities.append({
            'type': '高资金费率套利',
            'action': '做空永续，做多现货',
            'expected_return': f"{current_rate:.2f}%",
            'risk': '中'
        })
    elif current_rate < -20:  # 年化 < -20%
        opportunities.append({
            'type': '负资金费率套利',
            'action': '做多永续，做空现货',
            'expected_return': f"{abs(current_rate):.2f}%",
            'risk': '中'
        })
    
    # 计算资金费率稳定性
    stability = 1 / (df['annualized_rate'].std() + 1)
    
    return {
        'current_funding_rate': f"{df['v'].iloc[-1]:.4f}%",
        'annualized_return': f"{current_rate:.2f}%",
        '7d_average': f"{avg_rate:.2f}%",
        'stability_score': f"{stability:.2f}",
        'arbitrage_opportunities': opportunities
    }
```

### 5. 杠杆比率（Leverage Ratio）

**端点**: `/futures_leverage_ratio`

**描述**: 平均杠杆使用率，衡量市场风险水平。

```python
def analyze_leverage_risk(asset='BTC'):
    """分析杠杆风险"""
    
    url = "https://api.glassnode.com/v1/metrics/derivatives/futures_leverage_ratio"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '24h', 's': int(time.time()) - 30*86400}
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    current_leverage = data[-1]['v']
    avg_leverage = sum(d['v'] for d in data) / len(data)
    max_leverage = max(d['v'] for d in data)
    
    # 风险评估
    if current_leverage > avg_leverage * 1.2:
        risk_level = "高风险 - 杠杆过度使用"
    elif current_leverage > avg_leverage:
        risk_level = "中等风险 - 杠杆略高"
    else:
        risk_level = "低风险 - 杠杆正常"
    
    return {
        'current_leverage': f"{current_leverage:.2f}x",
        'average_leverage': f"{avg_leverage:.2f}x",
        'max_leverage_30d': f"{max_leverage:.2f}x",
        'risk_assessment': risk_level,
        'deleveraging_probability': 'high' if current_leverage > max_leverage * 0.9 else 'low'
    }
```

## 期权（Options）端点

### 1. 期权未平仓合约

**端点**: `/options_open_interest`

**描述**: 期权市场的未平仓合约总价值。

### 2. 期权交易量

**端点**: `/options_volume`

**描述**: 期权合约的交易量。

### 3. 隐含波动率（IV）

**端点**: `/options_implied_volatility`

**描述**: 期权市场隐含的未来波动率预期。

**期权分析示例**:
```python
class OptionsAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_options_market(self, asset='BTC'):
        """全面分析期权市场"""
        
        base_url = "https://api.glassnode.com/v1/metrics/derivatives/"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h', 's': int(time.time()) - 30*86400}
        
        # 获取期权数据
        oi_data = self.get_data(base_url + "options_open_interest", params, headers)
        volume_data = self.get_data(base_url + "options_volume", params, headers)
        iv_data = self.get_data(base_url + "options_implied_volatility", params, headers)
        
        # 分析 Put/Call 比率
        pc_ratio = self.calculate_put_call_ratio(asset)
        
        # 分析 IV 趋势
        iv_analysis = self.analyze_iv_trend(iv_data)
        
        # Greeks 分析（如果有数据）
        greeks = self.analyze_greeks(asset)
        
        return {
            'market_size': {
                'open_interest': oi_data[-1]['v'],
                'daily_volume': volume_data[-1]['v'],
                'oi_volume_ratio': oi_data[-1]['v'] / volume_data[-1]['v']
            },
            'volatility': {
                'current_iv': iv_data[-1]['v'],
                'iv_trend': iv_analysis['trend'],
                'iv_percentile': iv_analysis['percentile']
            },
            'sentiment': {
                'put_call_ratio': pc_ratio,
                'market_bias': self.interpret_pc_ratio(pc_ratio)
            },
            'greeks': greeks
        }
    
    def analyze_iv_trend(self, iv_data):
        """分析隐含波动率趋势"""
        
        values = [d['v'] for d in iv_data]
        current_iv = values[-1]
        
        # 计算 IV 百分位
        percentile = sum(1 for v in values if v < current_iv) / len(values) * 100
        
        # 判断趋势
        recent_avg = sum(values[-7:]) / 7
        older_avg = sum(values[-14:-7]) / 7
        
        if recent_avg > older_avg * 1.1:
            trend = "上升"
        elif recent_avg < older_avg * 0.9:
            trend = "下降"
        else:
            trend = "横盘"
        
        return {
            'trend': trend,
            'percentile': percentile,
            'mean_iv': sum(values) / len(values),
            'current_vs_mean': (current_iv / (sum(values) / len(values)) - 1) * 100
        }
    
    def calculate_put_call_ratio(self, asset):
        """计算 Put/Call 比率"""
        # 这里需要更详细的期权数据
        # 简化示例返回
        return 0.85  # 示例值
    
    def interpret_pc_ratio(self, ratio):
        """解释 Put/Call 比率"""
        if ratio > 1.2:
            return "极度看跌"
        elif ratio > 1:
            return "看跌"
        elif ratio < 0.7:
            return "极度看涨"
        elif ratio < 0.9:
            return "看涨"
        else:
            return "中性"
```

### 4. Delta Skew

**端点**: `/options_delta_skew`

**描述**: 期权 Delta 偏斜，反映市场对不同行权价的偏好。

```python
def analyze_delta_skew(asset='BTC'):
    """分析 Delta Skew"""
    
    url = "https://api.glassnode.com/v1/metrics/derivatives/options_delta_skew"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '24h'}
    
    response = requests.get(url, params=params, headers=headers)
    skew = response.json()[-1]['v']
    
    # 解释偏斜
    if skew > 10:
        interpretation = "强烈看涨偏斜 - 市场愿意为上涨保护支付溢价"
    elif skew > 0:
        interpretation = "温和看涨偏斜"
    elif skew < -10:
        interpretation = "强烈看跌偏斜 - 市场愿意为下跌保护支付溢价"
    else:
        interpretation = "温和看跌偏斜"
    
    return {
        'current_skew': skew,
        'interpretation': interpretation,
        'trading_suggestion': generate_skew_strategy(skew)
    }

def generate_skew_strategy(skew):
    """基于 skew 生成交易策略"""
    if abs(skew) > 15:
        return "考虑反向偏斜交易 - 卖出高溢价期权"
    elif abs(skew) < 5:
        return "市场相对平衡，适合进行中性策略"
    else:
        return "跟随市场偏斜方向交易"
```

## 高级策略应用

### 1. 综合衍生品仪表板

```python
class DerivativesDashboard:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def generate_comprehensive_report(self, asset='BTC'):
        """生成综合衍生品报告"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'asset': asset,
            'futures': {},
            'options': {},
            'risk_metrics': {},
            'trading_signals': []
        }
        
        # 期货分析
        report['futures'] = {
            'open_interest': self.get_futures_oi(asset),
            'funding_rate': self.get_funding_rate(asset),
            'liquidations': self.get_liquidation_summary(asset),
            'leverage': self.get_leverage_ratio(asset)
        }
        
        # 期权分析
        report['options'] = {
            'implied_volatility': self.get_iv(asset),
            'put_call_ratio': self.get_pc_ratio(asset),
            'delta_skew': self.get_delta_skew(asset)
        }
        
        # 风险指标
        report['risk_metrics'] = self.calculate_risk_metrics(report)
        
        # 生成交易信号
        report['trading_signals'] = self.generate_signals(report)
        
        return report
    
    def calculate_risk_metrics(self, data):
        """计算综合风险指标"""
        
        risk_score = 0
        factors = []
        
        # 杠杆风险
        if data['futures']['leverage'] > 15:
            risk_score += 30
            factors.append("高杠杆风险")
        
        # 资金费率风险
        if abs(data['futures']['funding_rate']) > 0.1:
            risk_score += 20
            factors.append("极端资金费率")
        
        # 波动率风险
        if data['options']['implied_volatility'] > 80:
            risk_score += 25
            factors.append("高波动率环境")
        
        return {
            'overall_risk_score': risk_score,
            'risk_level': self.get_risk_level(risk_score),
            'risk_factors': factors,
            'recommended_position_size': self.calculate_position_size(risk_score)
        }
    
    def generate_signals(self, data):
        """生成交易信号"""
        
        signals = []
        
        # 资金费率套利
        if data['futures']['funding_rate'] > 0.05:
            signals.append({
                'type': 'arbitrage',
                'action': 'short_perpetual_long_spot',
                'confidence': 'high',
                'expected_return': f"{data['futures']['funding_rate'] * 365 * 100:.2f}% APR"
            })
        
        # 波动率交易
        if data['options']['implied_volatility'] < 40:
            signals.append({
                'type': 'volatility',
                'action': 'buy_straddle',
                'confidence': 'medium',
                'rationale': 'IV at low percentile'
            })
        
        return signals
```

### 2. 风险预警系统

```python
class RiskAlertSystem:
    def __init__(self, api_key):
        self.api_key = api_key
        self.alert_thresholds = {
            'liquidation_spike': 1000000000,  # $1B in liquidations
            'funding_extreme': 0.1,  # 0.1% funding rate
            'leverage_high': 20,  # 20x leverage
            'iv_spike': 100  # 100% IV
        }
    
    async def monitor_risks(self, asset='BTC'):
        """实时监控风险指标"""
        
        while True:
            try:
                # 检查各项风险指标
                alerts = []
                
                # 检查清算
                liquidations = await self.check_liquidations(asset)
                if liquidations > self.alert_thresholds['liquidation_spike']:
                    alerts.append(f"⚠️ 大规模清算: ${liquidations/1e9:.2f}B")
                
                # 检查资金费率
                funding = await self.check_funding_rate(asset)
                if abs(funding) > self.alert_thresholds['funding_extreme']:
                    alerts.append(f"⚠️ 极端资金费率: {funding:.4f}%")
                
                # 检查杠杆
                leverage = await self.check_leverage(asset)
                if leverage > self.alert_thresholds['leverage_high']:
                    alerts.append(f"⚠️ 高杠杆风险: {leverage:.2f}x")
                
                # 发送警报
                if alerts:
                    await self.send_alerts(alerts)
                
                await asyncio.sleep(300)  # 5分钟检查一次
                
            except Exception as e:
                print(f"Error in risk monitoring: {e}")
                await asyncio.sleep(60)
```

## 数据解读指南

### 关键指标解释

1. **未平仓合约（OI）**
   - 上升 + 价格上涨 = 新多头进场，看涨
   - 上升 + 价格下跌 = 新空头进场，看跌
   - 下降 + 价格上涨 = 空头平仓，短期看涨
   - 下降 + 价格下跌 = 多头平仓，短期看跌

2. **资金费率**
   - 正值 = 多头付费给空头，多头情绪强
   - 负值 = 空头付费给多头，空头情绪强
   - 极端值 = 潜在反转信号

3. **清算数据**
   - 大规模多头清算 = 可能触发进一步下跌
   - 大规模空头清算 = 可能触发进一步上涨
   - 双向清算 = 高波动环境

4. **隐含波动率**
   - IV 上升 = 市场预期波动增加
   - IV 下降 = 市场预期趋于平静
   - IV 极值 = 重大事件预期

## 常见问题

### Q1: 如何判断市场是否过度杠杆化？

观察以下指标：
- 杠杆比率 > 15x
- 资金费率绝对值 > 0.05%
- 清算量激增
- OI/市值比例过高

### Q2: 期货和期权数据哪个更重要？

两者互补：
- 期货：短期方向和情绪
- 期权：中长期预期和尾部风险

### Q3: 如何利用衍生品数据进行现货交易？

- 使用资金费率判断短期顶底
- 观察清算水平设置止损
- 利用期权 IV 判断入场时机

## 最佳实践

1. **多维度分析**：结合多个衍生品指标，避免单一指标误导
2. **关注极值**：极端数据往往预示转折点
3. **风险管理**：根据衍生品数据调整仓位和杠杆
4. **套利机会**：寻找期现、跨期、跨市场套利机会

---

*本文档详细介绍了 Glassnode Derivatives API 的使用方法。衍生品数据是理解市场结构和预测价格走势的关键工具。*