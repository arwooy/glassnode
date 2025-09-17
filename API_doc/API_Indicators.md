# Indicators（技术指标）API 文档

## 概述

Indicators API 提供各种链上和市场技术指标，包括经典的技术分析指标、链上特有指标、市场情绪指标等。这些指标帮助交易者和投资者做出更明智的决策。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/indicators/`

## 核心端点

### 1. 经典技术指标

#### 1.1 移动平均线（MA）

**端点**: 
- `/ma_simple` - 简单移动平均
- `/ma_exponential` - 指数移动平均

**参数**:
- `length`: 周期长度（如 50, 200）

```python
class TechnicalIndicatorAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/indicators/"
        
    def analyze_moving_averages(self, asset='BTC'):
        """分析移动平均线"""
        
        headers = {"X-Api-Key": self.api_key}
        
        # 获取不同周期的 MA
        ma_periods = [20, 50, 100, 200]
        ma_data = {}
        
        for period in ma_periods:
            params = {
                'a': asset,
                'i': '24h',
                's': int(time.time()) - 365*86400,
                'length': period
            }
            
            # 获取 SMA
            sma = requests.get(
                self.base_url + "ma_simple",
                params=params,
                headers=headers
            ).json()
            
            # 获取 EMA
            ema = requests.get(
                self.base_url + "ma_exponential",
                params=params,
                headers=headers
            ).json()
            
            ma_data[f'MA{period}'] = {
                'sma': sma[-1]['v'] if sma else None,
                'ema': ema[-1]['v'] if ema else None
            }
        
        # 获取当前价格
        current_price = self.get_current_price(asset)
        
        # 分析 MA 信号
        signals = self.analyze_ma_signals(current_price, ma_data)
        
        # 识别趋势
        trend = self.identify_trend_from_ma(current_price, ma_data)
        
        # 计算支撑阻力
        support_resistance = self.calculate_support_resistance(ma_data)
        
        return {
            'current_price': current_price,
            'moving_averages': ma_data,
            'signals': signals,
            'trend': trend,
            'support_resistance': support_resistance,
            'golden_death_cross': self.check_golden_death_cross(ma_data)
        }
    
    def analyze_ma_signals(self, price, ma_data):
        """分析 MA 信号"""
        
        signals = []
        
        # 价格与 MA 关系
        if ma_data.get('MA50') and ma_data.get('MA200'):
            ma50 = ma_data['MA50']['sma']
            ma200 = ma_data['MA200']['sma']
            
            if price > ma50 and price > ma200:
                signals.append({
                    'type': 'BULLISH',
                    'indicator': 'Price above MA50 and MA200',
                    'strength': 'STRONG'
                })
            elif price > ma50 but price < ma200:
                signals.append({
                    'type': 'NEUTRAL',
                    'indicator': 'Price between MA50 and MA200',
                    'strength': 'MEDIUM'
                })
            else:
                signals.append({
                    'type': 'BEARISH',
                    'indicator': 'Price below MA50 and MA200',
                    'strength': 'STRONG'
                })
        
        return signals
    
    def check_golden_death_cross(self, ma_data):
        """检查金叉死叉"""
        
        if not (ma_data.get('MA50') and ma_data.get('MA200')):
            return None
        
        ma50 = ma_data['MA50']['sma']
        ma200 = ma_data['MA200']['sma']
        
        if ma50 > ma200:
            return {
                'type': 'GOLDEN_CROSS',
                'description': 'MA50 在 MA200 上方 - 看涨信号',
                'signal': 'BULLISH'
            }
        else:
            return {
                'type': 'DEATH_CROSS',
                'description': 'MA50 在 MA200 下方 - 看跌信号',
                'signal': 'BEARISH'
            }
```

#### 1.2 相对强弱指数（RSI）

**端点**: `/rsi`

```python
def analyze_rsi(asset='BTC', period=14):
    """分析 RSI 指标"""
    
    url = "https://api.glassnode.com/v1/metrics/indicators/rsi"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {
        'a': asset,
        'i': '24h',
        's': int(time.time()) - 90*86400,
        'length': period
    }
    
    response = requests.get(url, params=params, headers=headers)
    rsi_data = response.json()
    
    current_rsi = rsi_data[-1]['v']
    
    # RSI 解释
    if current_rsi > 70:
        condition = "超买"
        signal = "SELL"
        description = "市场可能过热，考虑获利了结"
    elif current_rsi < 30:
        condition = "超卖"
        signal = "BUY"
        description = "市场可能超卖，考虑买入机会"
    elif current_rsi > 50:
        condition = "偏强"
        signal = "NEUTRAL_BULLISH"
        description = "市场动能偏向多头"
    else:
        condition = "偏弱"
        signal = "NEUTRAL_BEARISH"
        description = "市场动能偏向空头"
    
    # 检测背离
    divergence = detect_rsi_divergence(rsi_data, asset)
    
    return {
        'current_rsi': round(current_rsi, 2),
        'condition': condition,
        'signal': signal,
        'description': description,
        'divergence': divergence,
        'momentum': assess_momentum(rsi_data)
    }

def detect_rsi_divergence(rsi_data, asset):
    """检测 RSI 背离"""
    
    # 获取价格数据进行对比
    price_data = get_price_data(asset, len(rsi_data))
    
    # 简化的背离检测
    rsi_trend = calculate_trend(rsi_data[-10:])
    price_trend = calculate_trend(price_data[-10:])
    
    if rsi_trend > 0 and price_trend < 0:
        return {
            'type': 'BULLISH_DIVERGENCE',
            'description': 'RSI 上升但价格下降 - 潜在反转信号'
        }
    elif rsi_trend < 0 and price_trend > 0:
        return {
            'type': 'BEARISH_DIVERGENCE',
            'description': 'RSI 下降但价格上升 - 潜在反转信号'
        }
    
    return None
```

### 2. 链上特有指标

#### 2.1 NVT（Network Value to Transactions）

**端点**: `/nvt`

**描述**: 网络价值与交易量的比率，类似于股票的市盈率。

```python
class OnChainIndicatorAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_nvt(self, asset='BTC'):
        """分析 NVT 比率"""
        
        url = "https://api.glassnode.com/v1/metrics/indicators/nvt"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h', 's': int(time.time()) - 180*86400}
        
        response = requests.get(url, params=params, headers=headers)
        nvt_data = response.json()
        
        current_nvt = nvt_data[-1]['v']
        nvt_values = [d['v'] for d in nvt_data]
        
        # 计算历史分位数
        percentile = sum(1 for v in nvt_values if v < current_nvt) / len(nvt_values) * 100
        
        # NVT 解释
        if current_nvt > 100:
            valuation = "极度高估"
            signal = "STRONG_SELL"
            description = "网络价值远超实际使用"
        elif current_nvt > 70:
            valuation = "高估"
            signal = "SELL"
            description = "网络可能被高估"
        elif current_nvt > 40:
            valuation = "合理"
            signal = "NEUTRAL"
            description = "估值在正常范围"
        else:
            valuation = "低估"
            signal = "BUY"
            description = "网络可能被低估"
        
        # NVT Signal（使用移动平均）
        nvt_signal = self.calculate_nvt_signal(nvt_values)
        
        return {
            'current_nvt': round(current_nvt, 2),
            'historical_percentile': f"{percentile:.1f}%",
            'valuation': valuation,
            'signal': signal,
            'description': description,
            'nvt_signal': nvt_signal,
            'trend': self.analyze_nvt_trend(nvt_values)
        }
    
    def calculate_nvt_signal(self, nvt_values):
        """计算 NVT Signal"""
        
        # 使用 90 天移动平均
        if len(nvt_values) < 90:
            return None
        
        ma_90 = sum(nvt_values[-90:]) / 90
        current = nvt_values[-1]
        
        ratio = current / ma_90
        
        if ratio > 1.5:
            return {
                'value': ratio,
                'signal': 'OVERBOUGHT',
                'description': 'NVT 显著高于平均'
            }
        elif ratio < 0.5:
            return {
                'value': ratio,
                'signal': 'OVERSOLD',
                'description': 'NVT 显著低于平均'
            }
        else:
            return {
                'value': ratio,
                'signal': 'NEUTRAL',
                'description': 'NVT 在正常范围'
            }
```

#### 2.2 SOPR（Spent Output Profit Ratio）

**端点**: `/sopr`

**描述**: 花费输出的盈亏比率，反映市场整体盈亏状况。

```python
def analyze_sopr(asset='BTC'):
    """分析 SOPR 指标"""
    
    url = "https://api.glassnode.com/v1/metrics/indicators/sopr"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {'a': asset, 'i': '24h', 's': int(time.time()) - 90*86400}
    
    response = requests.get(url, params=params, headers=headers)
    sopr_data = response.json()
    
    current_sopr = sopr_data[-1]['v']
    
    # SOPR 解释
    # > 1: 整体盈利
    # = 1: 盈亏平衡
    # < 1: 整体亏损
    
    if current_sopr > 1.05:
        status = "强烈盈利"
        signal = "获利了结压力"
        market_phase = "牛市"
    elif current_sopr > 1:
        status = "轻微盈利"
        signal = "健康市场"
        market_phase = "上升趋势"
    elif current_sopr > 0.98:
        status = "接近平衡"
        signal = "关键支撑"
        market_phase = "整理期"
    else:
        status = "亏损"
        signal = "投降或底部"
        market_phase = "熊市"
    
    # 检测 SOPR 重置
    sopr_reset = detect_sopr_reset(sopr_data)
    
    return {
        'current_sopr': round(current_sopr, 4),
        'status': status,
        'signal': signal,
        'market_phase': market_phase,
        'sopr_reset': sopr_reset,
        'trend_strength': calculate_sopr_trend_strength(sopr_data)
    }

def detect_sopr_reset(sopr_data):
    """检测 SOPR 重置（触及 1.0）"""
    
    recent_values = [d['v'] for d in sopr_data[-7:]]
    
    # 检查是否有接近 1.0 的值
    touches = sum(1 for v in recent_values if 0.98 < v < 1.02)
    
    if touches > 0:
        return {
            'detected': True,
            'description': 'SOPR 触及 1.0 - 可能的支撑/阻力',
            'count': touches
        }
    
    return {
        'detected': False,
        'description': '无 SOPR 重置'
    }
```

### 3. 市场情绪指标

#### 3.1 恐惧贪婪指数

**端点**: `/fear_greed_index`

```python
class SentimentIndicatorAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_fear_greed(self, asset='BTC'):
        """分析恐惧贪婪指数"""
        
        url = "https://api.glassnode.com/v1/metrics/indicators/fear_greed_index"
        headers = {"X-Api-Key": self.api_key}
        params = {'a': asset, 'i': '24h', 's': int(time.time()) - 30*86400}
        
        response = requests.get(url, params=params, headers=headers)
        fg_data = response.json()
        
        current_fg = fg_data[-1]['v']
        
        # 分类情绪
        if current_fg >= 75:
            sentiment = "极度贪婪"
            signal = "STRONG_SELL"
            description = "市场过度乐观，注意风险"
        elif current_fg >= 60:
            sentiment = "贪婪"
            signal = "SELL"
            description = "市场偏向乐观"
        elif current_fg >= 40:
            sentiment = "中性"
            signal = "NEUTRAL"
            description = "市场情绪平衡"
        elif current_fg >= 25:
            sentiment = "恐惧"
            signal = "BUY"
            description = "市场偏向悲观"
        else:
            sentiment = "极度恐惧"
            signal = "STRONG_BUY"
            description = "市场过度悲观，可能是机会"
        
        # 分析情绪变化
        sentiment_trend = self.analyze_sentiment_trend(fg_data)
        
        # 逆向交易信号
        contrarian_signal = self.generate_contrarian_signal(current_fg, sentiment_trend)
        
        return {
            'current_index': current_fg,
            'sentiment': sentiment,
            'signal': signal,
            'description': description,
            'sentiment_trend': sentiment_trend,
            'contrarian_signal': contrarian_signal,
            'historical_extremes': self.find_historical_extremes(fg_data)
        }
    
    def analyze_sentiment_trend(self, data):
        """分析情绪趋势"""
        
        values = [d['v'] for d in data]
        
        # 计算短期和长期平均
        short_avg = sum(values[-7:]) / 7
        long_avg = sum(values) / len(values)
        
        if short_avg > long_avg + 10:
            return {
                'direction': 'improving',
                'strength': 'strong',
                'description': '情绪快速改善'
            }
        elif short_avg > long_avg:
            return {
                'direction': 'improving',
                'strength': 'moderate',
                'description': '情绪逐步改善'
            }
        elif short_avg < long_avg - 10:
            return {
                'direction': 'deteriorating',
                'strength': 'strong',
                'description': '情绪快速恶化'
            }
        else:
            return {
                'direction': 'stable',
                'strength': 'weak',
                'description': '情绪相对稳定'
            }
    
    def generate_contrarian_signal(self, current, trend):
        """生成逆向交易信号"""
        
        signals = []
        
        if current < 20 and trend['direction'] == 'deteriorating':
            signals.append({
                'type': 'CONTRARIAN_BUY',
                'confidence': 'HIGH',
                'reason': '极度恐惧且持续恶化'
            })
        
        if current > 80 and trend['direction'] == 'improving':
            signals.append({
                'type': 'CONTRARIAN_SELL',
                'confidence': 'HIGH',
                'reason': '极度贪婪且持续改善'
            })
        
        return signals
```

### 4. 波动性指标

#### 4.1 历史波动率

**端点**: `/historical_volatility`

```python
def analyze_volatility(asset='BTC', period=30):
    """分析历史波动率"""
    
    url = "https://api.glassnode.com/v1/metrics/indicators/historical_volatility"
    headers = {"X-Api-Key": "YOUR_API_KEY"}
    params = {
        'a': asset,
        'i': '24h',
        's': int(time.time()) - 365*86400,
        'period': period
    }
    
    response = requests.get(url, params=params, headers=headers)
    volatility_data = response.json()
    
    current_vol = volatility_data[-1]['v']
    vol_values = [d['v'] for d in volatility_data]
    
    # 计算波动率分位数
    percentile = sum(1 for v in vol_values if v < current_vol) / len(vol_values) * 100
    
    # 波动率状态
    if current_vol > 100:
        vol_state = "极高波动"
        trading_env = "高风险高回报"
    elif current_vol > 60:
        vol_state = "高波动"
        trading_env = "活跃交易环境"
    elif current_vol > 30:
        vol_state = "正常波动"
        trading_env = "标准市场条件"
    else:
        vol_state = "低波动"
        trading_env = "平静市场"
    
    # 波动率交易策略
    vol_strategy = generate_volatility_strategy(current_vol, percentile)
    
    return {
        'current_volatility': f"{current_vol:.2f}%",
        'historical_percentile': f"{percentile:.1f}%",
        'volatility_state': vol_state,
        'trading_environment': trading_env,
        'volatility_strategy': vol_strategy,
        'risk_management': calculate_position_sizing(current_vol)
    }

def generate_volatility_strategy(vol, percentile):
    """生成波动率交易策略"""
    
    strategies = []
    
    if percentile > 80:
        strategies.append({
            'strategy': 'VOLATILITY_SELLING',
            'description': '考虑卖出期权或减少杠杆',
            'reason': '波动率处于历史高位'
        })
    elif percentile < 20:
        strategies.append({
            'strategy': 'VOLATILITY_BUYING',
            'description': '考虑买入期权或跨式策略',
            'reason': '波动率处于历史低位'
        })
    
    if vol > 80:
        strategies.append({
            'strategy': 'REDUCE_POSITION',
            'description': '降低仓位规模',
            'reason': '极高波动环境'
        })
    
    return strategies
```

### 5. 动量指标

#### 5.1 MACD

**端点**: `/macd`

```python
class MomentumIndicatorAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def analyze_macd(self, asset='BTC'):
        """分析 MACD 指标"""
        
        url = "https://api.glassnode.com/v1/metrics/indicators/macd"
        headers = {"X-Api-Key": self.api_key}
        params = {
            'a': asset,
            'i': '24h',
            's': int(time.time()) - 180*86400,
            'fast': 12,
            'slow': 26,
            'signal': 9
        }
        
        response = requests.get(url, params=params, headers=headers)
        macd_data = response.json()
        
        current = macd_data[-1]['v']
        
        # MACD 组成部分
        macd_line = current['macd']
        signal_line = current['signal']
        histogram = current['histogram']
        
        # 分析 MACD 信号
        if macd_line > signal_line and histogram > 0:
            trend = "看涨"
            signal = "BUY"
            strength = "强" if histogram > 0.02 else "弱"
        elif macd_line < signal_line and histogram < 0:
            trend = "看跌"
            signal = "SELL"
            strength = "强" if histogram < -0.02 else "弱"
        else:
            trend = "中性"
            signal = "NEUTRAL"
            strength = "无"
        
        # 检测交叉
        crossover = self.detect_macd_crossover(macd_data)
        
        # 动量分析
        momentum = self.analyze_momentum(histogram, macd_data)
        
        return {
            'macd_line': round(macd_line, 4),
            'signal_line': round(signal_line, 4),
            'histogram': round(histogram, 4),
            'trend': trend,
            'signal': signal,
            'strength': strength,
            'crossover': crossover,
            'momentum': momentum
        }
    
    def detect_macd_crossover(self, data):
        """检测 MACD 交叉"""
        
        if len(data) < 2:
            return None
        
        prev = data[-2]['v']
        curr = data[-1]['v']
        
        # 金叉：MACD 上穿信号线
        if prev['macd'] <= prev['signal'] and curr['macd'] > curr['signal']:
            return {
                'type': 'GOLDEN_CROSS',
                'signal': 'BULLISH',
                'description': 'MACD 金叉 - 买入信号'
            }
        
        # 死叉：MACD 下穿信号线
        elif prev['macd'] >= prev['signal'] and curr['macd'] < curr['signal']:
            return {
                'type': 'DEATH_CROSS',
                'signal': 'BEARISH',
                'description': 'MACD 死叉 - 卖出信号'
            }
        
        return None
```

### 6. 综合指标分析

```python
class IndicatorsDashboard:
    def __init__(self, api_key):
        self.api_key = api_key
        self.technical = TechnicalIndicatorAnalyzer(api_key)
        self.onchain = OnChainIndicatorAnalyzer(api_key)
        self.sentiment = SentimentIndicatorAnalyzer(api_key)
        self.momentum = MomentumIndicatorAnalyzer(api_key)
        
    def generate_comprehensive_analysis(self, asset='BTC'):
        """生成综合指标分析"""
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'asset': asset,
            'technical_indicators': {},
            'onchain_indicators': {},
            'sentiment_indicators': {},
            'composite_signals': [],
            'trading_recommendations': []
        }
        
        # 收集所有指标数据
        analysis['technical_indicators'] = {
            'moving_averages': self.technical.analyze_moving_averages(asset),
            'rsi': analyze_rsi(asset),
            'macd': self.momentum.analyze_macd(asset),
            'volatility': analyze_volatility(asset)
        }
        
        analysis['onchain_indicators'] = {
            'nvt': self.onchain.analyze_nvt(asset),
            'sopr': analyze_sopr(asset)
        }
        
        analysis['sentiment_indicators'] = {
            'fear_greed': self.sentiment.analyze_fear_greed(asset)
        }
        
        # 生成综合信号
        analysis['composite_signals'] = self.generate_composite_signals(analysis)
        
        # 生成交易建议
        analysis['trading_recommendations'] = self.generate_recommendations(analysis)
        
        # 计算信号强度
        analysis['signal_strength'] = self.calculate_signal_strength(analysis)
        
        return analysis
    
    def generate_composite_signals(self, data):
        """生成综合信号"""
        
        signals = []
        bullish_count = 0
        bearish_count = 0
        
        # 技术指标信号
        if data['technical_indicators']['rsi']['signal'] == 'BUY':
            bullish_count += 1
        elif data['technical_indicators']['rsi']['signal'] == 'SELL':
            bearish_count += 1
        
        if data['technical_indicators']['macd']['signal'] == 'BUY':
            bullish_count += 1
        elif data['technical_indicators']['macd']['signal'] == 'SELL':
            bearish_count += 1
        
        # 链上指标信号
        if data['onchain_indicators']['nvt']['signal'] in ['BUY', 'STRONG_BUY']:
            bullish_count += 1
        elif data['onchain_indicators']['nvt']['signal'] in ['SELL', 'STRONG_SELL']:
            bearish_count += 1
        
        # 情绪指标信号
        if data['sentiment_indicators']['fear_greed']['signal'] in ['BUY', 'STRONG_BUY']:
            bullish_count += 1
        elif data['sentiment_indicators']['fear_greed']['signal'] in ['SELL', 'STRONG_SELL']:
            bearish_count += 1
        
        # 生成综合信号
        total_signals = bullish_count + bearish_count
        
        if total_signals > 0:
            bullish_ratio = bullish_count / total_signals
            
            if bullish_ratio > 0.7:
                signals.append({
                    'direction': 'STRONG_BUY',
                    'confidence': 'HIGH',
                    'bullish_signals': bullish_count,
                    'bearish_signals': bearish_count
                })
            elif bullish_ratio > 0.5:
                signals.append({
                    'direction': 'BUY',
                    'confidence': 'MEDIUM',
                    'bullish_signals': bullish_count,
                    'bearish_signals': bearish_count
                })
            elif bullish_ratio < 0.3:
                signals.append({
                    'direction': 'STRONG_SELL',
                    'confidence': 'HIGH',
                    'bullish_signals': bullish_count,
                    'bearish_signals': bearish_count
                })
            elif bullish_ratio < 0.5:
                signals.append({
                    'direction': 'SELL',
                    'confidence': 'MEDIUM',
                    'bullish_signals': bullish_count,
                    'bearish_signals': bearish_count
                })
            else:
                signals.append({
                    'direction': 'NEUTRAL',
                    'confidence': 'LOW',
                    'bullish_signals': bullish_count,
                    'bearish_signals': bearish_count
                })
        
        return signals
    
    def calculate_signal_strength(self, analysis):
        """计算信号强度"""
        
        if not analysis['composite_signals']:
            return 0
        
        signal = analysis['composite_signals'][0]
        
        # 基础强度
        if signal['direction'] in ['STRONG_BUY', 'STRONG_SELL']:
            base_strength = 80
        elif signal['direction'] in ['BUY', 'SELL']:
            base_strength = 60
        else:
            base_strength = 30
        
        # 根据信号一致性调整
        total_signals = signal['bullish_signals'] + signal['bearish_signals']
        consensus = max(signal['bullish_signals'], signal['bearish_signals']) / total_signals
        
        final_strength = base_strength * consensus
        
        return round(final_strength)
```

## 常见问题

### Q1: 技术指标在加密货币市场的有效性如何？

加密市场特点：
- 24/7 交易，无收盘价概念
- 高波动性影响传统指标
- 链上指标提供额外维度
- 建议结合多种指标使用

### Q2: 如何选择合适的指标组合？

推荐组合：
- **趋势跟踪**：MA + MACD + ADX
- **反转交易**：RSI + SOPR + 恐惧贪婪指数
- **价值投资**：NVT + MVRV + Thermocap

### Q3: 指标出现矛盾信号怎么办？

处理方法：
1. 确定主要交易风格（趋势/反转）
2. 设置指标权重
3. 等待更明确信号
4. 降低仓位规模

## 最佳实践

1. **多指标验证**：不依赖单一指标
2. **考虑市场环境**：牛熊市指标表现不同
3. **动态调整参数**：根据市场条件优化
4. **结合基本面**：技术指标配合基本面分析

---

*本文档详细介绍了 Glassnode Indicators API 的使用方法。技术指标是制定交易策略的重要工具。*