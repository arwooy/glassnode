# Point-In-Time（时点数据）API 详细文档

## 概述

Point-In-Time API 提供特定时间点的区块链和市场状态快照数据，包括历史价格、网络状态、市场指标、持仓分布等在特定时刻的精确数据。这些时点数据对于回测分析、历史研究、合规审计、风险评估和策略验证至关重要，能够准确重现任何历史时刻的市场状况。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/pit/`

**支持的资产**: BTC, ETH, USDT, USDC, LTC, BCH, ADA, DOT 等主要加密资产

**数据类型覆盖**:
- 价格和交易数据
- 网络活动指标  
- 持仓和地址分布
- 交易所数据
- DeFi 协议状态
- 衍生品数据
- 宏观经济指标

**时间精度**: 
- 最小间隔：1分钟
- 最大历史：2010年（比特币）/ 2015年（以太坊）
- 数据完整性：99.9%+

**数据更新频率**: 
- 历史数据：已固化，不变更
- 近期数据：每小时更新完善
- 实时数据：不适用（专门用于历史时点）

## 核心端点

### 1. 价格时点数据

#### 1.1 历史价格快照

**端点**: `/price_snapshot`

**描述**: 获取特定时间点的完整价格信息，包括开高低收价、交易量等。

**参数**:
- `a`: 资产符号（如 BTC）
- `timestamp`: 具体时间戳（Unix时间戳）
- `exchange`: 特定交易所（可选）
- `include_volume`: 是否包含交易量数据

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/pit/price_snapshot?a=BTC&timestamp=1609459200&include_volume=true" \
  -H "X-Api-Key: YOUR_API_KEY"
```

**示例响应**:
```json
{
  "asset": "BTC",
  "timestamp": 1609459200,
  "price_data": {
    "usd_price": 29374.15,
    "volume_24h": 35420189234.67,
    "market_cap": 547892345678.90,
    "circulating_supply": 18628125.0,
    "price_change_24h": 5.67,
    "volatility_30d": 78.45
  },
  "exchange_prices": {
    "binance": 29380.50,
    "coinbase": 29365.75,
    "kraken": 29371.20
  }
}
```

#### 1.2 价格历史区间

**端点**: `/price_range`

**描述**: 获取指定时间范围内每个时点的价格数据。

**参数**:
- `a`: 资产符号
- `start_timestamp`: 开始时间戳
- `end_timestamp`: 结束时间戳
- `interval`: 数据间隔（1m, 5m, 1h, 1d）

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/pit/price_range?a=BTC&start_timestamp=1609459200&end_timestamp=1609545600&interval=1h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

### 2. 网络状态时点数据

#### 2.1 网络活动快照

**端点**: `/network_snapshot`

**描述**: 特定时间点的网络活动状态，包括交易数量、活跃地址、哈希率等。

**参数**:
- `a`: 资产符号
- `timestamp`: 时间戳
- `metrics`: 指定指标列表（可选）

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/pit/network_snapshot?a=BTC&timestamp=1609459200" \
  -H "X-Api-Key: YOUR_API_KEY"
```

#### 2.2 地址分布快照

**端点**: `/address_distribution`

**描述**: 特定时间点的地址持仓分布状况。

**参数**:
- `a`: 资产符号
- `timestamp`: 时间戳
- `balance_tiers`: 余额分层（可选）

### 3. 交易所时点数据

#### 3.1 交易所余额快照

**端点**: `/exchange_balances`

**描述**: 特定时间点各交易所的资产余额情况。

**参数**:
- `a`: 资产符号
- `timestamp`: 时间戳
- `exchange`: 特定交易所过滤器

### 4. 衍生品时点数据

#### 4.1 期货持仓快照

**端点**: `/futures_snapshot`

**描述**: 特定时间点的期货市场状态，包括持仓量、资金费率等。

**参数**:
- `a`: 资产符号
- `timestamp`: 时间戳
- `contract_type`: 合约类型

## Python 实现类

```python
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from dataclasses import dataclass

warnings.filterwarnings('ignore')

@dataclass
class PointInTimeSnapshot:
    """时点数据快照数据类"""
    timestamp: int
    asset: str
    price_data: Dict
    network_data: Dict
    exchange_data: Dict
    market_data: Dict

class PointInTimeAnalyzer:
    """
    Glassnode Point-In-Time API 分析器
    提供时点数据的获取、分析和可视化功能
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/pit/"
        self.headers = {"X-Api-Key": self.api_key}
        
        # 缓存设置
        self.cache = {}
        self.cache_ttl = 3600  # 1小时缓存时间
        
    def get_price_snapshot(self, asset: str, timestamp: int, 
                          include_volume: bool = True) -> Dict:
        """获取价格时点快照"""
        
        cache_key = f"price_{asset}_{timestamp}_{include_volume}"
        
        # 检查缓存
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                return data
        
        url = self.base_url + "price_snapshot"
        params = {
            'a': asset,
            'timestamp': timestamp,
            'include_volume': include_volume
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            # 缓存数据
            self.cache[cache_key] = (time.time(), data)
            
            return self.process_price_snapshot(data, asset, timestamp)
            
        except Exception as e:
            print(f"获取价格快照失败: {e}")
            return {}
    
    def process_price_snapshot(self, data: Dict, asset: str, timestamp: int) -> Dict:
        """处理价格快照数据"""
        
        if not data:
            return {}
        
        processed = {
            'asset': asset,
            'timestamp': timestamp,
            'datetime': pd.to_datetime(timestamp, unit='s'),
            'price_analysis': self.analyze_price_data(data.get('price_data', {})),
            'exchange_analysis': self.analyze_exchange_prices(data.get('exchange_prices', {})),
            'market_context': self.derive_market_context(data),
            'risk_metrics': self.calculate_risk_metrics(data)
        }
        
        return processed
    
    def analyze_price_data(self, price_data: Dict) -> Dict:
        """分析价格数据"""
        
        if not price_data:
            return {}
        
        analysis = {
            'usd_price': price_data.get('usd_price', 0),
            'market_cap': price_data.get('market_cap', 0),
            'volume_24h': price_data.get('volume_24h', 0),
            'price_change_24h': price_data.get('price_change_24h', 0),
            'volatility_assessment': self.assess_volatility(price_data.get('volatility_30d', 0)),
            'volume_analysis': self.analyze_volume_significance(price_data),
            'market_cap_tier': self.classify_market_cap_tier(price_data.get('market_cap', 0))
        }
        
        return analysis
    
    def assess_volatility(self, volatility_30d: float) -> Dict:
        """评估波动率"""
        
        assessment = {
            'volatility_value': volatility_30d,
            'volatility_level': '',
            'risk_category': '',
            'trading_implications': []
        }
        
        if volatility_30d > 100:
            assessment['volatility_level'] = 'extremely_high'
            assessment['risk_category'] = 'high_risk'
            assessment['trading_implications'] = [
                "极高波动性，适合短线交易",
                "风险管理至关重要",
                "可能存在重大市场事件"
            ]
        elif volatility_30d > 70:
            assessment['volatility_level'] = 'high'
            assessment['risk_category'] = 'medium_high_risk'
            assessment['trading_implications'] = [
                "高波动性，注意仓位控制",
                "适合波段交易"
            ]
        elif volatility_30d > 40:
            assessment['volatility_level'] = 'moderate'
            assessment['risk_category'] = 'medium_risk'
            assessment['trading_implications'] = [
                "中等波动性，正常交易环境"
            ]
        elif volatility_30d > 20:
            assessment['volatility_level'] = 'low'
            assessment['risk_category'] = 'low_risk'
            assessment['trading_implications'] = [
                "低波动性，可能处于盘整期"
            ]
        else:
            assessment['volatility_level'] = 'extremely_low'
            assessment['risk_category'] = 'very_low_risk'
            assessment['trading_implications'] = [
                "极低波动性，市场可能过于平静",
                "注意突破性行情"
            ]
        
        return assessment
    
    def analyze_volume_significance(self, price_data: Dict) -> Dict:
        """分析交易量意义"""
        
        volume_24h = price_data.get('volume_24h', 0)
        market_cap = price_data.get('market_cap', 0)
        
        volume_analysis = {
            'volume_24h': volume_24h,
            'volume_to_mcap_ratio': (volume_24h / market_cap) if market_cap > 0 else 0,
            'liquidity_assessment': '',
            'market_activity': ''
        }
        
        vol_mcap_ratio = volume_analysis['volume_to_mcap_ratio']
        
        if vol_mcap_ratio > 0.3:
            volume_analysis['liquidity_assessment'] = 'high_liquidity'
            volume_analysis['market_activity'] = 'very_active'
        elif vol_mcap_ratio > 0.15:
            volume_analysis['liquidity_assessment'] = 'good_liquidity'
            volume_analysis['market_activity'] = 'active'
        elif vol_mcap_ratio > 0.05:
            volume_analysis['liquidity_assessment'] = 'moderate_liquidity'
            volume_analysis['market_activity'] = 'moderate'
        else:
            volume_analysis['liquidity_assessment'] = 'low_liquidity'
            volume_analysis['market_activity'] = 'inactive'
        
        return volume_analysis
    
    def classify_market_cap_tier(self, market_cap: float) -> str:
        """分类市值层级"""
        
        if market_cap > 1000000000000:  # > 1万亿
            return 'mega_cap'
        elif market_cap > 100000000000:  # > 1000亿
            return 'large_cap'
        elif market_cap > 10000000000:   # > 100亿
            return 'mid_cap'
        elif market_cap > 1000000000:    # > 10亿
            return 'small_cap'
        else:
            return 'micro_cap'
    
    def analyze_exchange_prices(self, exchange_prices: Dict) -> Dict:
        """分析交易所价格差异"""
        
        if not exchange_prices:
            return {}
        
        prices = list(exchange_prices.values())
        
        analysis = {
            'price_range': {
                'min_price': min(prices),
                'max_price': max(prices),
                'price_spread': max(prices) - min(prices),
                'spread_percentage': ((max(prices) - min(prices)) / min(prices)) * 100 if min(prices) > 0 else 0
            },
            'arbitrage_opportunities': self.identify_arbitrage_opportunities(exchange_prices),
            'liquidity_concentration': self.analyze_liquidity_concentration(exchange_prices),
            'market_efficiency': self.assess_market_efficiency(exchange_prices)
        }
        
        return analysis
    
    def identify_arbitrage_opportunities(self, exchange_prices: Dict) -> List[Dict]:
        """识别套利机会"""
        
        opportunities = []
        
        if len(exchange_prices) < 2:
            return opportunities
        
        sorted_exchanges = sorted(exchange_prices.items(), key=lambda x: x[1])
        lowest_exchange, lowest_price = sorted_exchanges[0]
        highest_exchange, highest_price = sorted_exchanges[-1]
        
        price_diff = highest_price - lowest_price
        price_diff_pct = (price_diff / lowest_price) * 100 if lowest_price > 0 else 0
        
        if price_diff_pct > 0.5:  # 0.5%阈值
            opportunities.append({
                'type': 'simple_arbitrage',
                'buy_exchange': lowest_exchange,
                'sell_exchange': highest_exchange,
                'buy_price': lowest_price,
                'sell_price': highest_price,
                'profit_potential': price_diff,
                'profit_percentage': price_diff_pct,
                'risk_assessment': self.assess_arbitrage_risk(price_diff_pct)
            })
        
        return opportunities
    
    def assess_arbitrage_risk(self, profit_percentage: float) -> str:
        """评估套利风险"""
        
        if profit_percentage > 3:
            return 'high_profit_high_risk'  # 可能存在流动性或其他问题
        elif profit_percentage > 1:
            return 'moderate_profit_moderate_risk'
        else:
            return 'low_profit_low_risk'
    
    def analyze_liquidity_concentration(self, exchange_prices: Dict) -> Dict:
        """分析流动性集中度"""
        
        # 简化分析，实际需要交易量数据
        return {
            'exchange_count': len(exchange_prices),
            'price_uniformity': self.calculate_price_uniformity(exchange_prices),
            'concentration_score': self.calculate_concentration_score(exchange_prices)
        }
    
    def calculate_price_uniformity(self, exchange_prices: Dict) -> float:
        """计算价格一致性"""
        
        if len(exchange_prices) < 2:
            return 1.0
        
        prices = list(exchange_prices.values())
        mean_price = np.mean(prices)
        std_price = np.std(prices)
        
        # 变异系数的倒数作为一致性指标
        if mean_price > 0:
            cv = std_price / mean_price
            uniformity = 1 / (1 + cv)
        else:
            uniformity = 0
        
        return uniformity
    
    def calculate_concentration_score(self, exchange_prices: Dict) -> float:
        """计算集中度评分"""
        
        # 基于价格分布的集中度
        prices = list(exchange_prices.values())
        
        if len(prices) < 2:
            return 100  # 完全集中
        
        price_range = max(prices) - min(prices)
        mean_price = np.mean(prices)
        
        if mean_price > 0:
            concentration = (1 - price_range / mean_price) * 100
        else:
            concentration = 0
        
        return max(0, min(100, concentration))
    
    def assess_market_efficiency(self, exchange_prices: Dict) -> Dict:
        """评估市场效率"""
        
        uniformity = self.calculate_price_uniformity(exchange_prices)
        
        efficiency = {
            'efficiency_score': uniformity * 100,
            'efficiency_level': '',
            'market_maturity': ''
        }
        
        if uniformity > 0.99:
            efficiency['efficiency_level'] = 'highly_efficient'
            efficiency['market_maturity'] = 'mature'
        elif uniformity > 0.95:
            efficiency['efficiency_level'] = 'efficient'
            efficiency['market_maturity'] = 'developing'
        elif uniformity > 0.90:
            efficiency['efficiency_level'] = 'moderately_efficient'
            efficiency['market_maturity'] = 'emerging'
        else:
            efficiency['efficiency_level'] = 'inefficient'
            efficiency['market_maturity'] = 'early_stage'
        
        return efficiency
    
    def derive_market_context(self, data: Dict) -> Dict:
        """推导市场背景"""
        
        price_data = data.get('price_data', {})
        
        context = {
            'market_phase': self.identify_market_phase(price_data),
            'trend_strength': self.assess_trend_strength(price_data),
            'support_resistance': self.identify_support_resistance_levels(price_data),
            'market_sentiment': self.derive_sentiment_from_metrics(price_data)
        }
        
        return context
    
    def identify_market_phase(self, price_data: Dict) -> str:
        """识别市场阶段"""
        
        price_change_24h = price_data.get('price_change_24h', 0)
        volatility = price_data.get('volatility_30d', 0)
        volume_24h = price_data.get('volume_24h', 0)
        market_cap = price_data.get('market_cap', 0)
        
        # 简化的市场阶段识别
        if price_change_24h > 5 and volatility > 70:
            return 'bull_run'
        elif price_change_24h < -5 and volatility > 70:
            return 'bear_market'
        elif abs(price_change_24h) < 2 and volatility < 30:
            return 'accumulation'
        elif volatility > 80:
            return 'high_volatility'
        else:
            return 'consolidation'
    
    def assess_trend_strength(self, price_data: Dict) -> Dict:
        """评估趋势强度"""
        
        price_change = price_data.get('price_change_24h', 0)
        volatility = price_data.get('volatility_30d', 0)
        
        # 简化的趋势强度评估
        trend_strength = {
            'direction': 'bullish' if price_change > 0 else 'bearish',
            'strength': abs(price_change) / volatility if volatility > 0 else 0,
            'confidence': 'high' if abs(price_change) > volatility * 0.1 else 'low'
        }
        
        return trend_strength
    
    def identify_support_resistance_levels(self, price_data: Dict) -> Dict:
        """识别支撑阻力位"""
        
        current_price = price_data.get('usd_price', 0)
        
        # 简化的支撑阻力位计算
        # 实际应用中需要更多历史数据
        levels = {
            'current_price': current_price,
            'support_levels': [current_price * 0.95, current_price * 0.90],
            'resistance_levels': [current_price * 1.05, current_price * 1.10],
            'confidence': 'estimated'  # 基于有限数据的估算
        }
        
        return levels
    
    def derive_sentiment_from_metrics(self, price_data: Dict) -> Dict:
        """从指标推导情绪"""
        
        price_change = price_data.get('price_change_24h', 0)
        volatility = price_data.get('volatility_30d', 0)
        volume_24h = price_data.get('volume_24h', 0)
        market_cap = price_data.get('market_cap', 0)
        
        sentiment = {
            'primary_sentiment': '',
            'sentiment_strength': 0,
            'contributing_factors': []
        }
        
        # 基于价格变化的情绪
        if price_change > 5:
            sentiment['primary_sentiment'] = 'bullish'
            sentiment['sentiment_strength'] = min(100, price_change * 10)
            sentiment['contributing_factors'].append(f"24小时上涨{price_change:.1f}%")
        elif price_change < -5:
            sentiment['primary_sentiment'] = 'bearish'
            sentiment['sentiment_strength'] = min(100, abs(price_change) * 10)
            sentiment['contributing_factors'].append(f"24小时下跌{abs(price_change):.1f}%")
        else:
            sentiment['primary_sentiment'] = 'neutral'
            sentiment['sentiment_strength'] = 50
        
        # 基于波动率的情绪修正
        if volatility > 80:
            sentiment['contributing_factors'].append("高波动率表明市场不确定性")
            sentiment['sentiment_strength'] *= 0.8  # 降低置信度
        
        return sentiment
    
    def calculate_risk_metrics(self, data: Dict) -> Dict:
        """计算风险指标"""
        
        price_data = data.get('price_data', {})
        
        risk_metrics = {
            'volatility_risk': self.calculate_volatility_risk(price_data),
            'liquidity_risk': self.calculate_liquidity_risk(price_data),
            'concentration_risk': self.calculate_concentration_risk(data),
            'overall_risk_score': 0,
            'risk_level': ''
        }
        
        # 计算综合风险评分
        risk_scores = [
            risk_metrics['volatility_risk'].get('risk_score', 0),
            risk_metrics['liquidity_risk'].get('risk_score', 0),
            risk_metrics['concentration_risk'].get('risk_score', 0)
        ]
        
        risk_metrics['overall_risk_score'] = sum(risk_scores) / len(risk_scores)
        
        # 风险等级
        if risk_metrics['overall_risk_score'] > 75:
            risk_metrics['risk_level'] = 'high'
        elif risk_metrics['overall_risk_score'] > 50:
            risk_metrics['risk_level'] = 'medium'
        elif risk_metrics['overall_risk_score'] > 25:
            risk_metrics['risk_level'] = 'low'
        else:
            risk_metrics['risk_level'] = 'very_low'
        
        return risk_metrics
    
    def calculate_volatility_risk(self, price_data: Dict) -> Dict:
        """计算波动率风险"""
        
        volatility = price_data.get('volatility_30d', 0)
        
        risk = {
            'volatility_value': volatility,
            'risk_score': min(100, volatility),  # 直接使用波动率作为风险评分
            'risk_category': '',
            'implications': []
        }
        
        if volatility > 100:
            risk['risk_category'] = 'extreme'
            risk['implications'] = ["极端波动风险", "可能存在重大事件", "严格风险控制"]
        elif volatility > 70:
            risk['risk_category'] = 'high'
            risk['implications'] = ["高波动风险", "注意仓位管理"]
        elif volatility > 40:
            risk['risk_category'] = 'moderate'
            risk['implications'] = ["中等波动风险", "正常风险管理"]
        else:
            risk['risk_category'] = 'low'
            risk['implications'] = ["低波动风险", "相对稳定"]
        
        return risk
    
    def calculate_liquidity_risk(self, price_data: Dict) -> Dict:
        """计算流动性风险"""
        
        volume_24h = price_data.get('volume_24h', 0)
        market_cap = price_data.get('market_cap', 0)
        
        vol_mcap_ratio = (volume_24h / market_cap) if market_cap > 0 else 0
        
        risk = {
            'volume_to_mcap_ratio': vol_mcap_ratio,
            'risk_score': 0,
            'risk_category': '',
            'implications': []
        }
        
        # 流动性风险与成交量/市值比率成反比
        if vol_mcap_ratio > 0.2:
            risk['risk_score'] = 10
            risk['risk_category'] = 'very_low'
            risk['implications'] = ["流动性充足", "易于交易"]
        elif vol_mcap_ratio > 0.1:
            risk['risk_score'] = 25
            risk['risk_category'] = 'low'
            risk['implications'] = ["流动性良好"]
        elif vol_mcap_ratio > 0.05:
            risk['risk_score'] = 50
            risk['risk_category'] = 'moderate'
            risk['implications'] = ["流动性中等", "注意大额交易影响"]
        elif vol_mcap_ratio > 0.01:
            risk['risk_score'] = 75
            risk['risk_category'] = 'high'
            risk['implications'] = ["流动性较差", "可能存在滑点"]
        else:
            risk['risk_score'] = 90
            risk['risk_category'] = 'very_high'
            risk['implications'] = ["流动性不足", "交易困难", "高滑点风险"]
        
        return risk
    
    def calculate_concentration_risk(self, data: Dict) -> Dict:
        """计算集中度风险"""
        
        exchange_prices = data.get('exchange_prices', {})
        
        risk = {
            'exchange_count': len(exchange_prices),
            'risk_score': 0,
            'risk_category': '',
            'implications': []
        }
        
        # 基于交易所数量评估集中度风险
        exchange_count = len(exchange_prices)
        
        if exchange_count >= 10:
            risk['risk_score'] = 10
            risk['risk_category'] = 'very_low'
            risk['implications'] = ["交易所分散", "降低单点风险"]
        elif exchange_count >= 5:
            risk['risk_score'] = 25
            risk['risk_category'] = 'low'
            risk['implications'] = ["交易所较分散"]
        elif exchange_count >= 3:
            risk['risk_score'] = 50
            risk['risk_category'] = 'moderate'
            risk['implications'] = ["交易所集中度中等"]
        elif exchange_count >= 2:
            risk['risk_score'] = 75
            risk['risk_category'] = 'high'
            risk['implications'] = ["交易所集中", "存在单点风险"]
        else:
            risk['risk_score'] = 90
            risk['risk_category'] = 'very_high'
            risk['implications'] = ["极度集中", "高度依赖单一交易所"]
        
        return risk
    
    def get_network_snapshot(self, asset: str, timestamp: int) -> Dict:
        """获取网络状态快照"""
        
        url = self.base_url + "network_snapshot"
        params = {
            'a': asset,
            'timestamp': timestamp
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            return self.analyze_network_snapshot(data, asset, timestamp)
            
        except Exception as e:
            print(f"获取网络快照失败: {e}")
            return {}
    
    def analyze_network_snapshot(self, data: Dict, asset: str, timestamp: int) -> Dict:
        """分析网络快照数据"""
        
        if not data:
            return {}
        
        network_data = data.get('network_data', {})
        
        analysis = {
            'asset': asset,
            'timestamp': timestamp,
            'datetime': pd.to_datetime(timestamp, unit='s'),
            'network_health': self.assess_network_health(network_data),
            'activity_metrics': self.analyze_network_activity(network_data),
            'security_metrics': self.analyze_network_security(network_data),
            'adoption_indicators': self.analyze_adoption_indicators(network_data)
        }
        
        return analysis
    
    def assess_network_health(self, network_data: Dict) -> Dict:
        """评估网络健康度"""
        
        health = {
            'overall_score': 0,
            'health_level': '',
            'contributing_factors': [],
            'risk_factors': []
        }
        
        # 基于各种网络指标评估健康度
        active_addresses = network_data.get('active_addresses_24h', 0)
        transaction_count = network_data.get('transaction_count_24h', 0)
        hash_rate = network_data.get('hash_rate', 0)
        
        health_scores = []
        
        # 活跃地址评分
        if active_addresses > 100000:
            addr_score = 90
            health['contributing_factors'].append("活跃地址数量充足")
        elif active_addresses > 50000:
            addr_score = 70
        elif active_addresses > 10000:
            addr_score = 50
        else:
            addr_score = 30
            health['risk_factors'].append("活跃地址数量较少")
        
        health_scores.append(addr_score)
        
        # 交易数量评分
        if transaction_count > 200000:
            tx_score = 90
            health['contributing_factors'].append("交易活跃度高")
        elif transaction_count > 100000:
            tx_score = 70
        elif transaction_count > 50000:
            tx_score = 50
        else:
            tx_score = 30
            health['risk_factors'].append("交易活跃度较低")
        
        health_scores.append(tx_score)
        
        # 综合评分
        health['overall_score'] = sum(health_scores) / len(health_scores)
        
        if health['overall_score'] > 80:
            health['health_level'] = 'excellent'
        elif health['overall_score'] > 60:
            health['health_level'] = 'good'
        elif health['overall_score'] > 40:
            health['health_level'] = 'fair'
        else:
            health['health_level'] = 'poor'
        
        return health
    
    def analyze_network_activity(self, network_data: Dict) -> Dict:
        """分析网络活动"""
        
        activity = {
            'transaction_metrics': {
                'count_24h': network_data.get('transaction_count_24h', 0),
                'volume_24h': network_data.get('transaction_volume_24h', 0),
                'avg_transaction_size': 0,
                'activity_level': ''
            },
            'address_metrics': {
                'active_addresses': network_data.get('active_addresses_24h', 0),
                'new_addresses': network_data.get('new_addresses_24h', 0),
                'address_growth_rate': 0
            },
            'usage_patterns': self.analyze_usage_patterns(network_data)
        }
        
        # 计算平均交易大小
        tx_count = activity['transaction_metrics']['count_24h']
        tx_volume = activity['transaction_metrics']['volume_24h']
        
        if tx_count > 0:
            activity['transaction_metrics']['avg_transaction_size'] = tx_volume / tx_count
        
        # 评估活动水平
        if tx_count > 200000:
            activity['transaction_metrics']['activity_level'] = 'very_high'
        elif tx_count > 100000:
            activity['transaction_metrics']['activity_level'] = 'high'
        elif tx_count > 50000:
            activity['transaction_metrics']['activity_level'] = 'moderate'
        else:
            activity['transaction_metrics']['activity_level'] = 'low'
        
        return activity
    
    def analyze_usage_patterns(self, network_data: Dict) -> Dict:
        """分析使用模式"""
        
        patterns = {
            'dominant_use_case': '',
            'user_behavior': '',
            'network_utilization': ''
        }
        
        avg_tx_size = network_data.get('avg_transaction_size', 0)
        
        # 基于平均交易大小推断使用模式
        if avg_tx_size > 10000:  # 大额交易
            patterns['dominant_use_case'] = 'institutional_transfers'
            patterns['user_behavior'] = 'value_storage'
        elif avg_tx_size > 1000:
            patterns['dominant_use_case'] = 'retail_payments'
            patterns['user_behavior'] = 'medium_value_transfers'
        else:
            patterns['dominant_use_case'] = 'micro_payments'
            patterns['user_behavior'] = 'frequent_small_transactions'
        
        return patterns
    
    def analyze_network_security(self, network_data: Dict) -> Dict:
        """分析网络安全性"""
        
        security = {
            'hash_rate': network_data.get('hash_rate', 0),
            'difficulty': network_data.get('difficulty', 0),
            'security_level': '',
            'attack_cost': 0,
            'decentralization_score': 0
        }
        
        hash_rate = security['hash_rate']
        
        # 基于算力评估安全等级
        if hash_rate > 100000000:  # 100 EH/s (比特币级别)
            security['security_level'] = 'maximum'
            security['attack_cost'] = float('inf')  # 攻击成本极高
        elif hash_rate > 10000000:   # 10 EH/s
            security['security_level'] = 'very_high'
            security['attack_cost'] = 1000000000  # 10亿美元
        elif hash_rate > 1000000:    # 1 EH/s
            security['security_level'] = 'high'
            security['attack_cost'] = 100000000   # 1亿美元
        elif hash_rate > 100000:     # 100 PH/s
            security['security_level'] = 'moderate'
            security['attack_cost'] = 10000000    # 1000万美元
        else:
            security['security_level'] = 'low'
            security['attack_cost'] = 1000000     # 100万美元
        
        return security
    
    def analyze_adoption_indicators(self, network_data: Dict) -> Dict:
        """分析采用指标"""
        
        adoption = {
            'user_growth': {
                'new_addresses': network_data.get('new_addresses_24h', 0),
                'active_addresses': network_data.get('active_addresses_24h', 0),
                'growth_rate': 0,
                'adoption_stage': ''
            },
            'ecosystem_development': {
                'transaction_diversity': 0,
                'smart_contract_usage': network_data.get('smart_contract_calls', 0),
                'defi_integration': network_data.get('defi_transactions', 0)
            }
        }
        
        # 评估采用阶段
        active_addresses = adoption['user_growth']['active_addresses']
        
        if active_addresses > 1000000:
            adoption['user_growth']['adoption_stage'] = 'mainstream'
        elif active_addresses > 100000:
            adoption['user_growth']['adoption_stage'] = 'early_majority'
        elif active_addresses > 10000:
            adoption['user_growth']['adoption_stage'] = 'early_adopters'
        else:
            adoption['user_growth']['adoption_stage'] = 'innovators'
        
        return adoption
    
    def get_historical_time_series(self, asset: str, start_timestamp: int, 
                                 end_timestamp: int, interval: str = '1d') -> Dict:
        """获取历史时间序列数据"""
        
        url = self.base_url + "price_range"
        params = {
            'a': asset,
            'start_timestamp': start_timestamp,
            'end_timestamp': end_timestamp,
            'interval': interval
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            return self.analyze_time_series(data, asset, start_timestamp, end_timestamp)
            
        except Exception as e:
            print(f"获取时间序列数据失败: {e}")
            return {}
    
    def analyze_time_series(self, data: List, asset: str, 
                          start_timestamp: int, end_timestamp: int) -> Dict:
        """分析时间序列数据"""
        
        if not data:
            return {}
        
        # 转换为DataFrame
        df = pd.DataFrame(data)
        df['datetime'] = pd.to_datetime(df['t'], unit='s')
        df.set_index('datetime', inplace=True)
        
        analysis = {
            'asset': asset,
            'period': {
                'start': pd.to_datetime(start_timestamp, unit='s'),
                'end': pd.to_datetime(end_timestamp, unit='s'),
                'duration_days': (end_timestamp - start_timestamp) / 86400
            },
            'price_statistics': self.calculate_price_statistics(df),
            'trend_analysis': self.analyze_price_trends(df),
            'volatility_analysis': self.analyze_volatility_patterns(df),
            'return_analysis': self.analyze_returns(df),
            'risk_metrics': self.calculate_time_series_risk_metrics(df)
        }
        
        return analysis
    
    def calculate_price_statistics(self, df: pd.DataFrame) -> Dict:
        """计算价格统计"""
        
        if 'usd_price' not in df.columns:
            return {}
        
        prices = df['usd_price']
        
        stats = {
            'price_range': {
                'min': prices.min(),
                'max': prices.max(),
                'range': prices.max() - prices.min(),
                'range_percentage': ((prices.max() - prices.min()) / prices.min()) * 100 if prices.min() > 0 else 0
            },
            'central_tendency': {
                'mean': prices.mean(),
                'median': prices.median(),
                'mode': prices.mode().iloc[0] if not prices.mode().empty else prices.mean()
            },
            'dispersion': {
                'std': prices.std(),
                'variance': prices.var(),
                'coefficient_of_variation': prices.std() / prices.mean() if prices.mean() > 0 else 0
            },
            'distribution': {
                'skewness': prices.skew(),
                'kurtosis': prices.kurtosis(),
                'distribution_type': self.classify_distribution(prices)
            }
        }
        
        return stats
    
    def classify_distribution(self, prices: pd.Series) -> str:
        """分类价格分布"""
        
        skewness = prices.skew()
        kurtosis = prices.kurtosis()
        
        if abs(skewness) < 0.5 and abs(kurtosis) < 0.5:
            return 'normal'
        elif skewness > 0.5:
            return 'right_skewed'
        elif skewness < -0.5:
            return 'left_skewed'
        elif kurtosis > 3:
            return 'leptokurtic'  # 尖峰分布
        elif kurtosis < -1:
            return 'platykurtic'  # 平峰分布
        else:
            return 'mesokurtic'   # 正态峰度
    
    def analyze_price_trends(self, df: pd.DataFrame) -> Dict:
        """分析价格趋势"""
        
        if 'usd_price' not in df.columns:
            return {}
        
        prices = df['usd_price']
        
        # 计算移动平均线
        df['ma_7'] = prices.rolling(window=7).mean()
        df['ma_30'] = prices.rolling(window=30).mean()
        df['ma_90'] = prices.rolling(window=90).mean()
        
        trends = {
            'short_term_trend': self.identify_trend_direction(prices.tail(7)),
            'medium_term_trend': self.identify_trend_direction(prices.tail(30)),
            'long_term_trend': self.identify_trend_direction(prices.tail(90)),
            'trend_strength': self.calculate_trend_strength(prices),
            'trend_consistency': self.calculate_trend_consistency(prices),
            'support_resistance': self.identify_support_resistance_from_series(prices)
        }
        
        return trends
    
    def identify_trend_direction(self, price_series: pd.Series) -> str:
        """识别趋势方向"""
        
        if len(price_series) < 2:
            return 'undefined'
        
        start_price = price_series.iloc[0]
        end_price = price_series.iloc[-1]
        
        change_pct = ((end_price - start_price) / start_price) * 100 if start_price > 0 else 0
        
        if change_pct > 5:
            return 'strong_uptrend'
        elif change_pct > 1:
            return 'uptrend'
        elif change_pct > -1:
            return 'sideways'
        elif change_pct > -5:
            return 'downtrend'
        else:
            return 'strong_downtrend'
    
    def calculate_trend_strength(self, prices: pd.Series) -> float:
        """计算趋势强度"""
        
        if len(prices) < 10:
            return 0
        
        # 使用线性回归的R²作为趋势强度
        x = np.arange(len(prices))
        y = prices.values
        
        # 计算相关系数
        correlation = np.corrcoef(x, y)[0, 1]
        r_squared = correlation ** 2
        
        return r_squared
    
    def calculate_trend_consistency(self, prices: pd.Series) -> float:
        """计算趋势一致性"""
        
        if len(prices) < 5:
            return 0
        
        # 计算日收益率
        returns = prices.pct_change().dropna()
        
        # 计算同向收益率的比例
        positive_returns = (returns > 0).sum()
        total_returns = len(returns)
        
        consistency = positive_returns / total_returns if total_returns > 0 else 0
        
        # 如果趋势是下降的，计算负收益率的比例
        if prices.iloc[-1] < prices.iloc[0]:
            consistency = 1 - consistency
        
        return consistency
    
    def identify_support_resistance_from_series(self, prices: pd.Series) -> Dict:
        """从价格序列识别支撑阻力位"""
        
        # 简化的支撑阻力位识别
        recent_prices = prices.tail(30)
        
        support_resistance = {
            'support_levels': [
                recent_prices.min(),
                recent_prices.quantile(0.25)
            ],
            'resistance_levels': [
                recent_prices.quantile(0.75),
                recent_prices.max()
            ],
            'current_price': prices.iloc[-1],
            'price_position': self.assess_price_position(prices)
        }
        
        return support_resistance
    
    def assess_price_position(self, prices: pd.Series) -> str:
        """评估价格位置"""
        
        recent_prices = prices.tail(30)
        current_price = prices.iloc[-1]
        
        percentile = (recent_prices < current_price).sum() / len(recent_prices)
        
        if percentile > 0.8:
            return 'near_resistance'
        elif percentile > 0.6:
            return 'upper_range'
        elif percentile > 0.4:
            return 'middle_range'
        elif percentile > 0.2:
            return 'lower_range'
        else:
            return 'near_support'
    
    def analyze_volatility_patterns(self, df: pd.DataFrame) -> Dict:
        """分析波动率模式"""
        
        if 'usd_price' not in df.columns:
            return {}
        
        prices = df['usd_price']
        
        # 计算不同周期的波动率
        returns = prices.pct_change().dropna()
        
        volatility = {
            'realized_volatility': {
                'daily': returns.std() * np.sqrt(365) * 100,  # 年化波动率
                'weekly': returns.rolling(window=7).std().iloc[-1] * np.sqrt(52) * 100 if len(returns) >= 7 else 0,
                'monthly': returns.rolling(window=30).std().iloc[-1] * np.sqrt(12) * 100 if len(returns) >= 30 else 0
            },
            'volatility_clustering': self.detect_volatility_clustering(returns),
            'volatility_regime': self.identify_volatility_regime(returns),
            'garch_effects': self.test_garch_effects(returns)
        }
        
        return volatility
    
    def detect_volatility_clustering(self, returns: pd.Series) -> Dict:
        """检测波动率聚集"""
        
        # 计算绝对收益率的自相关
        abs_returns = returns.abs()
        
        clustering = {
            'autocorrelation_lag1': abs_returns.autocorr(lag=1) if len(abs_returns) > 1 else 0,
            'autocorrelation_lag5': abs_returns.autocorr(lag=5) if len(abs_returns) > 5 else 0,
            'clustering_detected': False,
            'clustering_strength': 'weak'
        }
        
        # 如果自相关系数显著
        if clustering['autocorrelation_lag1'] > 0.3:
            clustering['clustering_detected'] = True
            clustering['clustering_strength'] = 'strong'
        elif clustering['autocorrelation_lag1'] > 0.1:
            clustering['clustering_detected'] = True
            clustering['clustering_strength'] = 'moderate'
        
        return clustering
    
    def identify_volatility_regime(self, returns: pd.Series) -> Dict:
        """识别波动率制度"""
        
        if len(returns) < 30:
            return {'regime': 'insufficient_data'}
        
        # 计算滚动波动率
        rolling_vol = returns.rolling(window=30).std()
        
        # 识别高低波动期
        vol_median = rolling_vol.median()
        current_vol = rolling_vol.iloc[-1]
        
        regime = {
            'current_volatility': current_vol,
            'median_volatility': vol_median,
            'volatility_percentile': (rolling_vol < current_vol).sum() / len(rolling_vol) * 100,
            'regime': 'normal'
        }
        
        if current_vol > vol_median * 1.5:
            regime['regime'] = 'high_volatility'
        elif current_vol < vol_median * 0.5:
            regime['regime'] = 'low_volatility'
        
        return regime
    
    def test_garch_effects(self, returns: pd.Series) -> Dict:
        """测试GARCH效应"""
        
        # 简化的GARCH效应检测
        # 检查收益率平方的自相关性（ARCH效应）
        
        if len(returns) < 20:
            return {'garch_effects': False, 'arch_test': 'insufficient_data'}
        
        squared_returns = returns ** 2
        
        garch = {
            'arch_effect': squared_returns.autocorr(lag=1) > 0.1,
            'autocorrelation_sq': squared_returns.autocorr(lag=1),
            'heteroskedasticity': 'detected' if squared_returns.autocorr(lag=1) > 0.1 else 'not_detected'
        }
        
        return garch
    
    def analyze_returns(self, df: pd.DataFrame) -> Dict:
        """分析收益率"""
        
        if 'usd_price' not in df.columns:
            return {}
        
        prices = df['usd_price']
        returns = prices.pct_change().dropna()
        
        analysis = {
            'return_statistics': {
                'mean_return': returns.mean(),
                'median_return': returns.median(),
                'std_return': returns.std(),
                'skewness': returns.skew(),
                'kurtosis': returns.kurtosis(),
                'sharpe_ratio': self.calculate_sharpe_ratio(returns)
            },
            'extreme_returns': {
                'max_daily_gain': returns.max(),
                'max_daily_loss': returns.min(),
                'days_with_extreme_moves': (returns.abs() > returns.std() * 2).sum(),
                'tail_risk': self.calculate_tail_risk(returns)
            },
            'return_distribution': {
                'positive_days': (returns > 0).sum(),
                'negative_days': (returns < 0).sum(),
                'win_rate': (returns > 0).sum() / len(returns) if len(returns) > 0 else 0
            }
        }
        
        return analysis
    
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """计算夏普比率"""
        
        if len(returns) == 0:
            return 0
        
        excess_return = returns.mean() - risk_free_rate / 365  # 日化无风险利率
        return_std = returns.std()
        
        if return_std == 0:
            return 0
        
        sharpe = (excess_return / return_std) * np.sqrt(365)  # 年化夏普比率
        
        return sharpe
    
    def calculate_tail_risk(self, returns: pd.Series) -> Dict:
        """计算尾部风险"""
        
        if len(returns) < 20:
            return {}
        
        tail_risk = {
            'var_95': returns.quantile(0.05),      # 5% VaR
            'var_99': returns.quantile(0.01),      # 1% VaR
            'cvar_95': returns[returns <= returns.quantile(0.05)].mean(),  # 5% CVaR
            'cvar_99': returns[returns <= returns.quantile(0.01)].mean(),  # 1% CVaR
            'maximum_drawdown': self.calculate_maximum_drawdown(returns)
        }
        
        return tail_risk
    
    def calculate_maximum_drawdown(self, returns: pd.Series) -> float:
        """计算最大回撤"""
        
        if len(returns) == 0:
            return 0
        
        # 计算累积收益
        cumulative = (1 + returns).cumprod()
        
        # 计算滚动最大值
        running_max = cumulative.expanding().max()
        
        # 计算回撤
        drawdown = (cumulative - running_max) / running_max
        
        return drawdown.min()
    
    def calculate_time_series_risk_metrics(self, df: pd.DataFrame) -> Dict:
        """计算时间序列风险指标"""
        
        if 'usd_price' not in df.columns:
            return {}
        
        prices = df['usd_price']
        returns = prices.pct_change().dropna()
        
        risk_metrics = {
            'volatility_metrics': {
                'annualized_volatility': returns.std() * np.sqrt(365) * 100,
                'volatility_regime': self.identify_volatility_regime(returns),
                'volatility_clustering': self.detect_volatility_clustering(returns)
            },
            'downside_risk': {
                'downside_deviation': returns[returns < 0].std() * np.sqrt(365) * 100,
                'sortino_ratio': self.calculate_sortino_ratio(returns),
                'maximum_drawdown': self.calculate_maximum_drawdown(returns)
            },
            'tail_risk': self.calculate_tail_risk(returns),
            'overall_risk_assessment': self.assess_overall_risk(returns)
        }
        
        return risk_metrics
    
    def calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """计算索丁诺比率"""
        
        if len(returns) == 0:
            return 0
        
        excess_return = returns.mean() - risk_free_rate / 365
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0:
            return float('inf') if excess_return > 0 else 0
        
        downside_std = downside_returns.std()
        
        if downside_std == 0:
            return float('inf') if excess_return > 0 else 0
        
        sortino = (excess_return / downside_std) * np.sqrt(365)
        
        return sortino
    
    def assess_overall_risk(self, returns: pd.Series) -> Dict:
        """评估整体风险"""
        
        if len(returns) == 0:
            return {}
        
        volatility = returns.std() * np.sqrt(365) * 100
        max_dd = abs(self.calculate_maximum_drawdown(returns) * 100)
        var_95 = abs(returns.quantile(0.05) * 100)
        
        # 综合风险评分
        risk_components = [
            min(100, volatility),        # 波动率评分
            min(100, max_dd * 2),        # 最大回撤评分（放大2倍）
            min(100, var_95 * 20)        # VaR评分（放大20倍）
        ]
        
        overall_risk_score = sum(risk_components) / len(risk_components)
        
        assessment = {
            'risk_score': overall_risk_score,
            'risk_level': '',
            'key_risks': [],
            'risk_mitigation': []
        }
        
        # 风险等级
        if overall_risk_score > 80:
            assessment['risk_level'] = 'very_high'
            assessment['key_risks'] = ['极高波动率', '大幅回撤风险', '尾部风险显著']
            assessment['risk_mitigation'] = ['严格止损', '小仓位', '短期持有']
        elif overall_risk_score > 60:
            assessment['risk_level'] = 'high'
            assessment['key_risks'] = ['高波动率', '回撤风险']
            assessment['risk_mitigation'] = ['适度止损', '合理仓位']
        elif overall_risk_score > 40:
            assessment['risk_level'] = 'moderate'
            assessment['key_risks'] = ['中等波动率']
            assessment['risk_mitigation'] = ['正常风险管理']
        elif overall_risk_score > 20:
            assessment['risk_level'] = 'low'
            assessment['key_risks'] = ['低风险']
            assessment['risk_mitigation'] = ['标准风险管理']
        else:
            assessment['risk_level'] = 'very_low'
            assessment['key_risks'] = ['极低风险']
            assessment['risk_mitigation'] = ['最小风险管理']
        
        return assessment

    def create_comprehensive_snapshot_report(self, asset: str, timestamp: int) -> Dict:
        """创建综合时点快照报告"""
        
        # 并行获取各类数据
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                'price': executor.submit(self.get_price_snapshot, asset, timestamp),
                'network': executor.submit(self.get_network_snapshot, asset, timestamp),
                # 可以添加更多数据源
            }
            
            results = {}
            for key, future in futures.items():
                try:
                    results[key] = future.result(timeout=30)
                except Exception as e:
                    print(f"获取{key}数据失败: {e}")
                    results[key] = {}
        
        # 创建综合快照
        snapshot = PointInTimeSnapshot(
            timestamp=timestamp,
            asset=asset,
            price_data=results.get('price', {}),
            network_data=results.get('network', {}),
            exchange_data={},  # 从price_data中提取
            market_data={}     # 综合市场数据
        )
        
        # 综合分析报告
        report = {
            'snapshot_info': {
                'asset': asset,
                'timestamp': timestamp,
                'datetime': pd.to_datetime(timestamp, unit='s').isoformat(),
                'data_completeness': self.assess_data_completeness(results)
            },
            'price_analysis': results.get('price', {}),
            'network_analysis': results.get('network', {}),
            'market_summary': self.create_market_summary(results),
            'risk_assessment': self.create_comprehensive_risk_assessment(results),
            'trading_implications': self.derive_trading_implications(results),
            'historical_context': self.provide_historical_context(asset, timestamp)
        }
        
        return report
    
    def assess_data_completeness(self, results: Dict) -> Dict:
        """评估数据完整性"""
        
        completeness = {
            'overall_score': 0,
            'available_data': [],
            'missing_data': [],
            'data_quality': 'good'
        }
        
        expected_data = ['price', 'network']
        available_count = 0
        
        for data_type in expected_data:
            if data_type in results and results[data_type]:
                completeness['available_data'].append(data_type)
                available_count += 1
            else:
                completeness['missing_data'].append(data_type)
        
        completeness['overall_score'] = (available_count / len(expected_data)) * 100
        
        if completeness['overall_score'] > 80:
            completeness['data_quality'] = 'excellent'
        elif completeness['overall_score'] > 60:
            completeness['data_quality'] = 'good'
        elif completeness['overall_score'] > 40:
            completeness['data_quality'] = 'fair'
        else:
            completeness['data_quality'] = 'poor'
        
        return completeness
    
    def create_market_summary(self, results: Dict) -> Dict:
        """创建市场摘要"""
        
        summary = {
            'market_condition': 'unknown',
            'key_metrics': {},
            'notable_events': [],
            'market_sentiment': 'neutral'
        }
        
        price_data = results.get('price', {})
        
        if price_data and 'price_analysis' in price_data:
            price_analysis = price_data['price_analysis']
            
            summary['key_metrics'] = {
                'price': price_analysis.get('usd_price', 0),
                'market_cap': price_analysis.get('market_cap', 0),
                'volume_24h': price_analysis.get('volume_24h', 0),
                'price_change_24h': price_analysis.get('price_change_24h', 0)
            }
            
            # 基于价格变化判断市场条件
            price_change = price_analysis.get('price_change_24h', 0)
            volatility = price_analysis.get('volatility_assessment', {}).get('volatility_value', 0)
            
            if price_change > 10:
                summary['market_condition'] = 'bull_run'
                summary['market_sentiment'] = 'bullish'
            elif price_change < -10:
                summary['market_condition'] = 'bear_market'
                summary['market_sentiment'] = 'bearish'
            elif volatility > 80:
                summary['market_condition'] = 'high_volatility'
                summary['market_sentiment'] = 'uncertain'
            else:
                summary['market_condition'] = 'stable'
                summary['market_sentiment'] = 'neutral'
        
        return summary
    
    def create_comprehensive_risk_assessment(self, results: Dict) -> Dict:
        """创建综合风险评估"""
        
        risk_assessment = {
            'overall_risk_score': 0,
            'risk_level': 'medium',
            'risk_factors': [],
            'risk_mitigation': [],
            'component_risks': {}
        }
        
        risk_scores = []
        
        # 价格风险
        if 'price' in results and 'risk_metrics' in results['price']:
            price_risk = results['price']['risk_metrics']
            price_risk_score = price_risk.get('overall_risk_score', 50)
            risk_scores.append(price_risk_score)
            risk_assessment['component_risks']['price_risk'] = price_risk_score
            
            if price_risk_score > 70:
                risk_assessment['risk_factors'].append("高价格波动风险")
        
        # 网络风险
        if 'network' in results and 'network_health' in results['network']:
            network_health = results['network']['network_health']
            network_risk_score = 100 - network_health.get('overall_score', 50)
            risk_scores.append(network_risk_score)
            risk_assessment['component_risks']['network_risk'] = network_risk_score
            
            if network_risk_score > 70:
                risk_assessment['risk_factors'].append("网络健康度较低")
        
        # 计算综合风险
        if risk_scores:
            risk_assessment['overall_risk_score'] = sum(risk_scores) / len(risk_scores)
        
        # 风险等级
        if risk_assessment['overall_risk_score'] > 75:
            risk_assessment['risk_level'] = 'very_high'
            risk_assessment['risk_mitigation'] = [
                "避免大额投资", "设置严格止损", "密切监控市场"
            ]
        elif risk_assessment['overall_risk_score'] > 50:
            risk_assessment['risk_level'] = 'high'
            risk_assessment['risk_mitigation'] = [
                "控制仓位规模", "设置止损", "分散投资"
            ]
        elif risk_assessment['overall_risk_score'] > 25:
            risk_assessment['risk_level'] = 'medium'
            risk_assessment['risk_mitigation'] = [
                "正常风险管理", "适度仓位"
            ]
        else:
            risk_assessment['risk_level'] = 'low'
            risk_assessment['risk_mitigation'] = [
                "标准风险管理"
            ]
        
        return risk_assessment
    
    def derive_trading_implications(self, results: Dict) -> Dict:
        """推导交易含义"""
        
        implications = {
            'short_term_outlook': 'neutral',
            'recommended_actions': [],
            'entry_exit_levels': {},
            'position_sizing': 'normal',
            'time_horizon': 'medium_term'
        }
        
        price_data = results.get('price', {})
        
        if price_data and 'market_context' in price_data:
            market_context = price_data['market_context']
            
            # 基于市场阶段的建议
            market_phase = market_context.get('market_phase', 'consolidation')
            
            if market_phase == 'bull_run':
                implications['short_term_outlook'] = 'bullish'
                implications['recommended_actions'] = [
                    "考虑逢低买入", "持有现有仓位", "设置移动止损"
                ]
                implications['position_sizing'] = 'aggressive'
            elif market_phase == 'bear_market':
                implications['short_term_outlook'] = 'bearish'
                implications['recommended_actions'] = [
                    "减少仓位", "等待反转信号", "考虑对冲"
                ]
                implications['position_sizing'] = 'conservative'
            elif market_phase == 'high_volatility':
                implications['short_term_outlook'] = 'uncertain'
                implications['recommended_actions'] = [
                    "谨慎交易", "减小仓位", "增加止损"
                ]
                implications['position_sizing'] = 'reduced'
                implications['time_horizon'] = 'short_term'
        
        return implications
    
    def provide_historical_context(self, asset: str, timestamp: int) -> Dict:
        """提供历史背景"""
        
        # 简化的历史背景分析
        date = pd.to_datetime(timestamp, unit='s')
        
        context = {
            'date_analysis': {
                'year': date.year,
                'month': date.month,
                'day_of_week': date.day_name(),
                'quarter': f"Q{date.quarter}"
            },
            'market_events': self.identify_potential_market_events(date),
            'seasonal_patterns': self.analyze_seasonal_patterns(date),
            'macro_environment': self.assess_macro_environment(date)
        }
        
        return context
    
    def identify_potential_market_events(self, date: pd.Timestamp) -> List[str]:
        """识别潜在市场事件"""
        
        events = []
        
        # 基于日期识别重要事件（简化版）
        if date.year == 2020 and date.month == 3:
            events.append("COVID-19 市场恐慌")
        elif date.year == 2021 and date.month in [4, 5]:
            events.append("加密货币牛市高峰")
        elif date.year == 2022 and date.month in [5, 6]:
            events.append("Terra Luna崩盘")
        elif date.year == 2022 and date.month == 11:
            events.append("FTX破产事件")
        
        return events
    
    def analyze_seasonal_patterns(self, date: pd.Timestamp) -> Dict:
        """分析季节性模式"""
        
        patterns = {
            'month_pattern': '',
            'quarter_pattern': '',
            'historical_bias': ''
        }
        
        # 简化的季节性分析
        month = date.month
        
        if month in [1, 2]:
            patterns['month_pattern'] = '年初效应，通常波动较大'
        elif month in [11, 12]:
            patterns['month_pattern'] = '年末效应，可能出现获利了结'
        elif month in [6, 7, 8]:
            patterns['month_pattern'] = '夏季淡季，交易量可能较低'
        else:
            patterns['month_pattern'] = '正常交易月份'
        
        return patterns
    
    def assess_macro_environment(self, date: pd.Timestamp) -> Dict:
        """评估宏观环境"""
        
        macro = {
            'interest_rate_environment': 'normal',
            'inflation_environment': 'normal',
            'risk_sentiment': 'neutral',
            'regulatory_environment': 'normal'
        }
        
        # 基于历史时期的简化评估
        if date.year <= 2021:
            macro['interest_rate_environment'] = 'low_rates'
            macro['risk_sentiment'] = 'risk_on'
        elif date.year >= 2022:
            macro['interest_rate_environment'] = 'rising_rates'
            macro['inflation_environment'] = 'high_inflation'
            macro['risk_sentiment'] = 'risk_off'
        
        return macro

    def visualize_pit_analysis(self, report: Dict, save_path: str = None):
        """可视化时点分析"""
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. 价格和市场指标
        if 'price_analysis' in report and 'price_analysis' in report['price_analysis']:
            ax = axes[0, 0]
            price_analysis = report['price_analysis']['price_analysis']
            
            metrics = ['价格', '市值', '24h交易量']
            values = [
                price_analysis.get('usd_price', 0),
                price_analysis.get('market_cap', 0) / 1e9,  # 转为十亿
                price_analysis.get('volume_24h', 0) / 1e9   # 转为十亿
            ]
            
            ax.bar(metrics, values, color=['blue', 'green', 'orange'])
            ax.set_title("关键市场指标")
            ax.set_ylabel("价值 (USD / 十亿USD)")
        
        # 2. 风险评估雷达图
        if 'risk_assessment' in report and 'component_risks' in report['risk_assessment']:
            ax = axes[0, 1]
            component_risks = report['risk_assessment']['component_risks']
            
            risk_types = list(component_risks.keys())
            risk_scores = list(component_risks.values())
            
            if risk_types:
                angles = np.linspace(0, 2 * np.pi, len(risk_types), endpoint=False)
                risk_scores += risk_scores[:1]
                angles = np.concatenate((angles, [angles[0]]))
                
                ax.plot(angles, risk_scores, 'o-', linewidth=2)
                ax.fill(angles, risk_scores, alpha=0.25)
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(risk_types)
                ax.set_title("风险评估雷达图")
                ax.grid(True)
        
        # 3. 市场情绪和条件
        if 'market_summary' in report:
            ax = axes[1, 0]
            market_summary = report['market_summary']
            
            condition = market_summary.get('market_condition', 'unknown')
            sentiment = market_summary.get('market_sentiment', 'neutral')
            
            # 简单的情绪可视化
            sentiments = ['bearish', 'neutral', 'bullish']
            sentiment_scores = [0, 0, 0]
            
            if sentiment == 'bearish':
                sentiment_scores[0] = 100
            elif sentiment == 'bullish':
                sentiment_scores[2] = 100
            else:
                sentiment_scores[1] = 100
            
            ax.bar(sentiments, sentiment_scores, color=['red', 'gray', 'green'])
            ax.set_title(f"市场情绪 - {condition}")
            ax.set_ylabel("情绪强度")
        
        # 4. 数据完整性
        if 'snapshot_info' in report and 'data_completeness' in report['snapshot_info']:
            ax = axes[1, 1]
            completeness = report['snapshot_info']['data_completeness']
            
            available = len(completeness.get('available_data', []))
            missing = len(completeness.get('missing_data', []))
            
            ax.pie([available, missing], labels=['可用数据', '缺失数据'], 
                   autopct='%1.1f%%', colors=['green', 'red'])
            ax.set_title(f"数据完整性 - {completeness.get('data_quality', 'unknown')}")
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
```

## 数据处理和可视化示例

### 1. 获取特定时点快照

```python
# 初始化分析器
analyzer = PointInTimeAnalyzer(api_key="YOUR_API_KEY")

# 获取2021年牛市高峰期的比特币快照（2021年4月13日）
bull_peak_timestamp = int(datetime(2021, 4, 13, 12, 0, 0).timestamp())
btc_bull_snapshot = analyzer.create_comprehensive_snapshot_report('BTC', bull_peak_timestamp)

print("2021年牛市高峰比特币快照分析:")
print(f"日期: {btc_bull_snapshot['snapshot_info']['datetime']}")

if 'price_analysis' in btc_bull_snapshot:
    price_info = btc_bull_snapshot['price_analysis']['price_analysis']
    print(f"价格: ${price_info.get('usd_price', 0):,.2f}")
    print(f"市值: ${price_info.get('market_cap', 0)/1e9:.1f}B")
    print(f"24h变化: {price_info.get('price_change_24h', 0):+.2f}%")

if 'risk_assessment' in btc_bull_snapshot:
    risk = btc_bull_snapshot['risk_assessment']
    print(f"风险等级: {risk['risk_level']}")
    print(f"风险评分: {risk['overall_risk_score']:.1f}/100")

# 可视化快照
analyzer.visualize_pit_analysis(btc_bull_snapshot, 'btc_bull_peak_snapshot.png')
```

### 2. 历史时间序列分析

```python
def analyze_historical_period(asset='BTC', start_date='2020-03-01', end_date='2020-04-01'):
    """分析历史时期的详细数据"""
    
    start_timestamp = int(pd.to_datetime(start_date).timestamp())
    end_timestamp = int(pd.to_datetime(end_date).timestamp())
    
    # 获取时间序列数据
    time_series = analyzer.get_historical_time_series(
        asset, start_timestamp, end_timestamp, interval='1d'
    )
    
    if not time_series:
        print("无法获取时间序列数据")
        return
    
    print(f"{asset} 历史分析 ({start_date} 到 {end_date}):")
    print(f"分析期间: {time_series['period']['duration_days']:.0f} 天")
    
    # 价格统计
    if 'price_statistics' in time_series:
        stats = time_series['price_statistics']
        
        print(f"\n价格统计:")
        print(f"  最低价: ${stats['price_range']['min']:,.2f}")
        print(f"  最高价: ${stats['price_range']['max']:,.2f}")
        print(f"  价格区间: {stats['price_range']['range_percentage']:.1f}%")
        print(f"  平均价: ${stats['central_tendency']['mean']:,.2f}")
        print(f"  价格波动率: {stats['dispersion']['coefficient_of_variation']:.3f}")
    
    # 趋势分析
    if 'trend_analysis' in time_series:
        trends = time_series['trend_analysis']
        
        print(f"\n趋势分析:")
        print(f"  短期趋势: {trends['short_term_trend']}")
        print(f"  中期趋势: {trends['medium_term_trend']}")
        print(f"  长期趋势: {trends['long_term_trend']}")
        print(f"  趋势强度: {trends['trend_strength']:.3f}")
        print(f"  趋势一致性: {trends['trend_consistency']:.3f}")
    
    # 风险指标
    if 'risk_metrics' in time_series:
        risk = time_series['risk_metrics']
        
        print(f"\n风险分析:")
        vol_metrics = risk['volatility_metrics']
        print(f"  年化波动率: {vol_metrics['annualized_volatility']:.1f}%")
        
        downside = risk['downside_risk']
        print(f"  最大回撤: {abs(downside['maximum_drawdown']*100):.1f}%")
        print(f"  索丁诺比率: {downside['sortino_ratio']:.2f}")
        
        overall = risk['overall_risk_assessment']
        print(f"  整体风险等级: {overall['risk_level']}")
        print(f"  风险评分: {overall['risk_score']:.1f}/100")
    
    # 收益分析
    if 'return_analysis' in time_series:
        returns = time_series['return_analysis']
        
        print(f"\n收益分析:")
        ret_stats = returns['return_statistics']
        print(f"  平均日收益: {ret_stats['mean_return']*100:.3f}%")
        print(f"  夏普比率: {ret_stats['sharpe_ratio']:.2f}")
        
        ret_dist = returns['return_distribution']
        print(f"  胜率: {ret_dist['win_rate']*100:.1f}%")
        
        extreme = returns['extreme_returns']
        print(f"  最大单日涨幅: {extreme['max_daily_gain']*100:.2f}%")
        print(f"  最大单日跌幅: {extreme['max_daily_loss']*100:.2f}%")
    
    return time_series

# 分析COVID-19崩盘期
covid_crash = analyze_historical_period('BTC', '2020-03-01', '2020-04-01')

# 分析2021年牛市期
bull_run = analyze_historical_period('BTC', '2021-01-01', '2021-05-01')
```

### 3. 多时点对比分析

```python
def compare_multiple_timepoints(asset='BTC', timepoints=None):
    """对比多个时点的市场状况"""
    
    if timepoints is None:
        # 定义关键时点
        timepoints = {
            'COVID崩盘': datetime(2020, 3, 12, 12, 0, 0),
            '2020减半': datetime(2020, 5, 11, 12, 0, 0),
            '2021牛市': datetime(2021, 4, 13, 12, 0, 0),
            'Luna崩盘': datetime(2022, 5, 10, 12, 0, 0),
            'FTX破产': datetime(2022, 11, 8, 12, 0, 0)
        }
    
    comparison_data = {}
    
    print(f"{asset} 关键时点对比分析:\n")
    
    for event_name, timestamp_dt in timepoints.items():
        timestamp = int(timestamp_dt.timestamp())
        
        print(f"分析 {event_name} ({timestamp_dt.strftime('%Y-%m-%d')})...")
        
        # 获取时点数据
        snapshot = analyzer.create_comprehensive_snapshot_report(asset, timestamp)
        
        if snapshot and 'price_analysis' in snapshot:
            price_data = snapshot['price_analysis'].get('price_analysis', {})
            risk_data = snapshot.get('risk_assessment', {})
            market_data = snapshot.get('market_summary', {})
            
            comparison_data[event_name] = {
                'date': timestamp_dt.strftime('%Y-%m-%d'),
                'price': price_data.get('usd_price', 0),
                'market_cap': price_data.get('market_cap', 0),
                'volume_24h': price_data.get('volume_24h', 0),
                'price_change_24h': price_data.get('price_change_24h', 0),
                'volatility': price_data.get('volatility_assessment', {}).get('volatility_value', 0),
                'risk_score': risk_data.get('overall_risk_score', 0),
                'risk_level': risk_data.get('risk_level', 'unknown'),
                'market_condition': market_data.get('market_condition', 'unknown'),
                'market_sentiment': market_data.get('market_sentiment', 'neutral')
            }
    
    # 创建对比表格
    df = pd.DataFrame(comparison_data).T
    
    print(f"\n{asset} 关键时点数据对比:")
    print("=" * 80)
    print(f"{'事件':<12} {'日期':<12} {'价格(USD)':<12} {'24h变化%':<10} {'波动率':<8} {'风险等级':<10} {'市场情绪':<10}")
    print("-" * 80)
    
    for event, data in comparison_data.items():
        print(f"{event:<12} {data['date']:<12} {data['price']:>10,.0f} {data['price_change_24h']:>8.1f}% {data['volatility']:>6.1f} {data['risk_level']:<10} {data['market_sentiment']:<10}")
    
    # 可视化对比
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    events = list(comparison_data.keys())
    prices = [comparison_data[event]['price'] for event in events]
    price_changes = [comparison_data[event]['price_change_24h'] for event in events]
    volatilities = [comparison_data[event]['volatility'] for event in events]
    risk_scores = [comparison_data[event]['risk_score'] for event in events]
    
    # 价格对比
    ax1.bar(events, prices, color='blue', alpha=0.7)
    ax1.set_title(f"{asset} 关键时点价格对比")
    ax1.set_ylabel("价格 (USD)")
    ax1.tick_params(axis='x', rotation=45)
    
    # 24小时变化对比
    colors = ['green' if x > 0 else 'red' for x in price_changes]
    ax2.bar(events, price_changes, color=colors, alpha=0.7)
    ax2.set_title("24小时价格变化对比")
    ax2.set_ylabel("变化 (%)")
    ax2.tick_params(axis='x', rotation=45)
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # 波动率对比
    ax3.bar(events, volatilities, color='orange', alpha=0.7)
    ax3.set_title("波动率对比")
    ax3.set_ylabel("波动率 (%)")
    ax3.tick_params(axis='x', rotation=45)
    
    # 风险评分对比
    risk_colors = ['green' if x < 25 else 'yellow' if x < 50 else 'orange' if x < 75 else 'red' for x in risk_scores]
    ax4.bar(events, risk_scores, color=risk_colors, alpha=0.7)
    ax4.set_title("风险评分对比")
    ax4.set_ylabel("风险评分 (0-100)")
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.show()
    
    return comparison_data

# 执行多时点对比分析
btc_comparison = compare_multiple_timepoints('BTC')
```

## 交易策略和市场分析

### 1. 基于历史时点的策略回测

```python
class HistoricalStrategyBacktester:
    """历史策略回测器"""
    
    def __init__(self, analyzer: PointInTimeAnalyzer):
        self.analyzer = analyzer
        
    def backtest_volatility_strategy(self, asset: str, start_date: str, 
                                   end_date: str, volatility_threshold: float = 60) -> Dict:
        """回测基于波动率的交易策略"""
        
        start_timestamp = int(pd.to_datetime(start_date).timestamp())
        end_timestamp = int(pd.to_datetime(end_date).timestamp())
        
        # 获取时间序列数据
        time_series = self.analyzer.get_historical_time_series(
            asset, start_timestamp, end_timestamp, interval='1d'
        )
        
        if not time_series:
            return {}
        
        # 策略逻辑：当波动率超过阈值时，减少仓位
        backtest_results = {
            'strategy_name': 'Volatility-Based Position Sizing',
            'parameters': {'volatility_threshold': volatility_threshold},
            'trades': [],
            'performance_metrics': {},
            'equity_curve': []
        }
        
        # 模拟交易（简化版）
        initial_capital = 10000
        current_capital = initial_capital
        position = 0  # 0=空仓, 1=满仓, 0.5=半仓
        
        # 这里需要实际的价格和波动率数据
        # 由于API限制，使用模拟数据进行演示
        
        dates = pd.date_range(start_date, end_date, freq='D')
        
        for i, date in enumerate(dates):
            timestamp = int(date.timestamp())
            
            # 模拟获取当日数据（实际应该调用API）
            daily_volatility = 50 + np.random.normal(0, 20)  # 模拟波动率
            daily_return = np.random.normal(0, 0.02)         # 模拟日收益率
            
            # 策略逻辑
            if daily_volatility > volatility_threshold:
                target_position = 0.3  # 高波动时减仓
            elif daily_volatility < volatility_threshold * 0.7:
                target_position = 1.0  # 低波动时满仓
            else:
                target_position = 0.7  # 中等波动时正常仓位
            
            # 执行调仓
            if target_position != position:
                trade = {
                    'date': date,
                    'action': 'rebalance',
                    'from_position': position,
                    'to_position': target_position,
                    'volatility': daily_volatility
                }
                backtest_results['trades'].append(trade)
                position = target_position
            
            # 计算当日收益
            daily_pnl = current_capital * position * daily_return
            current_capital += daily_pnl
            
            backtest_results['equity_curve'].append({
                'date': date,
                'capital': current_capital,
                'position': position,
                'volatility': daily_volatility
            })
        
        # 计算绩效指标
        final_capital = current_capital
        total_return = (final_capital - initial_capital) / initial_capital
        
        # 计算年化收益率
        days = len(dates)
        annualized_return = (final_capital / initial_capital) ** (365 / days) - 1
        
        equity_values = [point['capital'] for point in backtest_results['equity_curve']]
        equity_series = pd.Series(equity_values)
        daily_returns = equity_series.pct_change().dropna()
        
        backtest_results['performance_metrics'] = {
            'total_return': total_return * 100,
            'annualized_return': annualized_return * 100,
            'volatility': daily_returns.std() * np.sqrt(365) * 100,
            'sharpe_ratio': (annualized_return - 0.02) / (daily_returns.std() * np.sqrt(365)) if daily_returns.std() > 0 else 0,
            'max_drawdown': self.calculate_max_drawdown(equity_series) * 100,
            'total_trades': len(backtest_results['trades']),
            'final_capital': final_capital
        }
        
        return backtest_results
    
    def calculate_max_drawdown(self, equity_series: pd.Series) -> float:
        """计算最大回撤"""
        
        peak = equity_series.expanding().max()
        drawdown = (equity_series - peak) / peak
        return drawdown.min()
    
    def backtest_sentiment_reversal_strategy(self, asset: str, start_date: str, 
                                           end_date: str) -> Dict:
        """回测情绪逆向策略"""
        
        # 策略逻辑：在极端情绪时进行逆向操作
        backtest_results = {
            'strategy_name': 'Sentiment Reversal Strategy',
            'description': '在极端恐慌时买入，极端贪婪时卖出',
            'trades': [],
            'performance_metrics': {}
        }
        
        # 实现逆向情绪策略的回测逻辑
        # 这里简化实现，实际需要情绪指标数据
        
        return backtest_results
    
    def backtest_multi_timeframe_strategy(self, asset: str, start_date: str, 
                                        end_date: str) -> Dict:
        """回测多时间框架策略"""
        
        # 结合不同时间框架的信号
        backtest_results = {
            'strategy_name': 'Multi-Timeframe Strategy',
            'description': '结合短期、中期和长期信号的综合策略',
            'trades': [],
            'performance_metrics': {}
        }
        
        # 实现多时间框架策略的回测逻辑
        
        return backtest_results

    def compare_strategies(self, strategies_results: List[Dict]) -> Dict:
        """对比多个策略的表现"""
        
        comparison = {
            'strategy_names': [],
            'performance_comparison': {},
            'rankings': {},
            'best_strategy': '',
            'risk_adjusted_best': ''
        }
        
        for strategy in strategies_results:
            name = strategy['strategy_name']
            metrics = strategy.get('performance_metrics', {})
            
            comparison['strategy_names'].append(name)
            comparison['performance_comparison'][name] = metrics
        
        # 按夏普比率排名
        sharpe_ratios = {name: metrics.get('sharpe_ratio', 0) 
                        for name, metrics in comparison['performance_comparison'].items()}
        
        comparison['rankings']['by_sharpe'] = sorted(sharpe_ratios.items(), 
                                                   key=lambda x: x[1], 
                                                   reverse=True)
        
        # 按总收益率排名
        total_returns = {name: metrics.get('total_return', 0) 
                        for name, metrics in comparison['performance_comparison'].items()}
        
        comparison['rankings']['by_return'] = sorted(total_returns.items(), 
                                                   key=lambda x: x[1], 
                                                   reverse=True)
        
        comparison['best_strategy'] = comparison['rankings']['by_return'][0][0]
        comparison['risk_adjusted_best'] = comparison['rankings']['by_sharpe'][0][0]
        
        return comparison

# 使用示例
backtester = HistoricalStrategyBacktester(analyzer)

# 回测波动率策略
volatility_results = backtester.backtest_volatility_strategy(
    'BTC', '2021-01-01', '2021-12-31', volatility_threshold=60
)

print("波动率策略回测结果:")
print(f"总收益率: {volatility_results['performance_metrics']['total_return']:.2f}%")
print(f"年化收益率: {volatility_results['performance_metrics']['annualized_return']:.2f}%")
print(f"夏普比率: {volatility_results['performance_metrics']['sharpe_ratio']:.2f}")
print(f"最大回撤: {volatility_results['performance_metrics']['max_drawdown']:.2f}%")
print(f"交易次数: {volatility_results['performance_metrics']['total_trades']}")

# 可视化回测结果
equity_curve = volatility_results['equity_curve']
dates = [point['date'] for point in equity_curve]
capitals = [point['capital'] for point in equity_curve]
positions = [point['position'] for point in equity_curve]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# 资金曲线
ax1.plot(dates, capitals, 'b-', linewidth=2, label='策略资金曲线')
ax1.axhline(y=10000, color='gray', linestyle='--', alpha=0.5, label='初始资金')
ax1.set_title("波动率策略资金曲线")
ax1.set_ylabel("资金 (USD)")
ax1.legend()
ax1.grid(True, alpha=0.3)

# 仓位变化
ax2.plot(dates, positions, 'r-', linewidth=2, label='仓位比例')
ax2.set_title("仓位变化")
ax2.set_ylabel("仓位比例")
ax2.set_xlabel("日期")
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

### 2. 风险事件影响分析

```python
class RiskEventAnalyzer:
    """风险事件影响分析器"""
    
    def __init__(self, analyzer: PointInTimeAnalyzer):
        self.analyzer = analyzer
        
    def analyze_event_impact(self, asset: str, event_date: str, 
                           pre_days: int = 7, post_days: int = 30) -> Dict:
        """分析特定事件对市场的影响"""
        
        event_dt = pd.to_datetime(event_date)
        pre_start = event_dt - timedelta(days=pre_days)
        post_end = event_dt + timedelta(days=post_days)
        
        # 获取事件前后的数据
        pre_data = self.get_period_data(asset, pre_start, event_dt)
        post_data = self.get_period_data(asset, event_dt, post_end)
        event_snapshot = self.analyzer.get_price_snapshot(
            asset, int(event_dt.timestamp())
        )
        
        analysis = {
            'event_info': {
                'asset': asset,
                'event_date': event_date,
                'analysis_period': f'{pre_days}天前到{post_days}天后'
            },
            'pre_event_analysis': self.analyze_pre_event_conditions(pre_data),
            'event_day_analysis': self.analyze_event_day(event_snapshot),
            'post_event_analysis': self.analyze_post_event_recovery(post_data),
            'impact_assessment': self.assess_overall_impact(pre_data, post_data, event_snapshot),
            'lessons_learned': self.extract_lessons(pre_data, post_data, event_snapshot)
        }
        
        return analysis
    
    def get_period_data(self, asset: str, start_date: pd.Timestamp, 
                       end_date: pd.Timestamp) -> Dict:
        """获取时期数据"""
        
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())
        
        return self.analyzer.get_historical_time_series(
            asset, start_timestamp, end_timestamp, interval='1d'
        )
    
    def analyze_pre_event_conditions(self, pre_data: Dict) -> Dict:
        """分析事件前的市场条件"""
        
        if not pre_data:
            return {'status': 'no_data'}
        
        conditions = {
            'market_state': 'unknown',
            'warning_signs': [],
            'vulnerability_factors': [],
            'strength_indicators': []
        }
        
        # 分析价格趋势
        if 'trend_analysis' in pre_data:
            trend = pre_data['trend_analysis']
            
            if trend.get('short_term_trend') in ['strong_uptrend', 'uptrend']:
                conditions['strength_indicators'].append("上升趋势强劲")
            elif trend.get('short_term_trend') in ['strong_downtrend', 'downtrend']:
                conditions['warning_signs'].append("已处于下降趋势")
        
        # 分析波动率
        if 'volatility_analysis' in pre_data:
            vol_analysis = pre_data['volatility_analysis']
            realized_vol = vol_analysis.get('realized_volatility', {})
            
            if realized_vol.get('daily', 0) > 80:
                conditions['warning_signs'].append("高波动率环境")
                conditions['vulnerability_factors'].append("市场不稳定")
        
        # 分析风险指标
        if 'risk_metrics' in pre_data:
            risk = pre_data['risk_metrics']
            overall_risk = risk.get('overall_risk_assessment', {})
            
            if overall_risk.get('risk_level') in ['high', 'very_high']:
                conditions['vulnerability_factors'].append("整体风险水平较高")
        
        # 综合判断市场状态
        warning_count = len(conditions['warning_signs'])
        vulnerability_count = len(conditions['vulnerability_factors'])
        strength_count = len(conditions['strength_indicators'])
        
        if vulnerability_count > strength_count:
            conditions['market_state'] = 'vulnerable'
        elif strength_count > warning_count:
            conditions['market_state'] = 'strong'
        else:
            conditions['market_state'] = 'neutral'
        
        return conditions
    
    def analyze_event_day(self, event_snapshot: Dict) -> Dict:
        """分析事件当日的市场表现"""
        
        if not event_snapshot:
            return {'status': 'no_data'}
        
        event_analysis = {
            'immediate_impact': 'unknown',
            'market_reaction': [],
            'risk_spike': False,
            'liquidity_impact': 'unknown'
        }
        
        if 'price_analysis' in event_snapshot:
            price_data = event_snapshot['price_analysis']
            
            price_change = price_data.get('price_change_24h', 0)
            
            if price_change < -10:
                event_analysis['immediate_impact'] = 'severe_negative'
                event_analysis['market_reaction'].append(f"价格大跌{abs(price_change):.1f}%")
            elif price_change < -5:
                event_analysis['immediate_impact'] = 'moderate_negative'
                event_analysis['market_reaction'].append(f"价格下跌{abs(price_change):.1f}%")
            elif price_change > 10:
                event_analysis['immediate_impact'] = 'strong_positive'
                event_analysis['market_reaction'].append(f"价格大涨{price_change:.1f}%")
            elif price_change > 5:
                event_analysis['immediate_impact'] = 'moderate_positive'
                event_analysis['market_reaction'].append(f"价格上涨{price_change:.1f}%")
            else:
                event_analysis['immediate_impact'] = 'minimal'
        
        # 分析风险指标
        if 'risk_metrics' in event_snapshot:
            risk = event_snapshot['risk_metrics']
            
            if risk.get('overall_risk_score', 0) > 75:
                event_analysis['risk_spike'] = True
                event_analysis['market_reaction'].append("风险指标飙升")
        
        return event_analysis
    
    def analyze_post_event_recovery(self, post_data: Dict) -> Dict:
        """分析事件后的恢复情况"""
        
        if not post_data:
            return {'status': 'no_data'}
        
        recovery = {
            'recovery_pattern': 'unknown',
            'recovery_speed': 'unknown',
            'new_equilibrium': {},
            'structural_changes': []
        }
        
        # 分析价格恢复
        if 'price_statistics' in post_data:
            price_stats = post_data['price_statistics']
            
            # 简化的恢复分析
            price_range = price_stats['price_range']
            
            if price_range['range_percentage'] > 50:
                recovery['recovery_pattern'] = 'volatile_recovery'
                recovery['recovery_speed'] = 'slow'
            elif price_range['range_percentage'] > 25:
                recovery['recovery_pattern'] = 'gradual_recovery'
                recovery['recovery_speed'] = 'moderate'
            else:
                recovery['recovery_pattern'] = 'stable_recovery'
                recovery['recovery_speed'] = 'fast'
        
        # 分析趋势变化
        if 'trend_analysis' in post_data:
            trend = post_data['trend_analysis']
            
            if trend.get('trend_consistency', 0) < 0.5:
                recovery['structural_changes'].append("趋势一致性降低")
            
            if trend.get('trend_strength', 0) < 0.3:
                recovery['structural_changes'].append("趋势强度减弱")
        
        return recovery
    
    def assess_overall_impact(self, pre_data: Dict, post_data: Dict, 
                            event_snapshot: Dict) -> Dict:
        """评估整体影响"""
        
        impact = {
            'severity_score': 0,
            'impact_level': 'minimal',
            'lasting_effects': [],
            'market_adaptation': 'unknown'
        }
        
        severity_factors = []
        
        # 基于事件当日影响评分
        if event_snapshot and 'price_analysis' in event_snapshot:
            price_change = abs(event_snapshot['price_analysis'].get('price_change_24h', 0))
            severity_factors.append(min(price_change * 2, 100))
        
        # 基于恢复时间评分
        if post_data and 'volatility_analysis' in post_data:
            vol_regime = post_data['volatility_analysis'].get('volatility_regime', {})
            if vol_regime.get('regime') == 'high_volatility':
                severity_factors.append(60)
        
        # 计算综合严重性评分
        if severity_factors:
            impact['severity_score'] = sum(severity_factors) / len(severity_factors)
        
        # 确定影响等级
        if impact['severity_score'] > 80:
            impact['impact_level'] = 'catastrophic'
            impact['lasting_effects'] = [
                "市场结构性改变", "投资者信心长期受损", "监管环境变化"
            ]
        elif impact['severity_score'] > 60:
            impact['impact_level'] = 'severe'
            impact['lasting_effects'] = [
                "短期市场波动加剧", "投资者谨慎情绪上升"
            ]
        elif impact['severity_score'] > 40:
            impact['impact_level'] = 'moderate'
            impact['lasting_effects'] = [
                "临时性市场调整"
            ]
        elif impact['severity_score'] > 20:
            impact['impact_level'] = 'mild'
        else:
            impact['impact_level'] = 'minimal'
        
        return impact
    
    def extract_lessons(self, pre_data: Dict, post_data: Dict, 
                       event_snapshot: Dict) -> List[str]:
        """提取经验教训"""
        
        lessons = []
        
        # 基于事前条件的教训
        if pre_data and 'risk_metrics' in pre_data:
            risk_assessment = pre_data['risk_metrics'].get('overall_risk_assessment', {})
            
            if risk_assessment.get('risk_level') in ['high', 'very_high']:
                lessons.append("高风险环境下应保持谨慎，减少仓位")
        
        # 基于事件影响的教训
        if event_snapshot and 'price_analysis' in event_snapshot:
            price_change = event_snapshot['price_analysis'].get('price_change_24h', 0)
            
            if abs(price_change) > 15:
                lessons.append("黑天鹅事件可能导致极端价格波动")
                lessons.append("设置合理的止损点至关重要")
        
        # 基于恢复情况的教训
        if post_data and 'trend_analysis' in post_data:
            recovery_trend = post_data['trend_analysis'].get('short_term_trend', '')
            
            if recovery_trend in ['uptrend', 'strong_uptrend']:
                lessons.append("市场具有自我修复能力")
                lessons.append("恐慌性抛售后可能存在买入机会")
        
        if not lessons:
            lessons.append("每次市场事件都是学习和改进的机会")
        
        return lessons

# 使用示例
risk_analyzer = RiskEventAnalyzer(analyzer)

# 分析COVID-19崩盘事件
covid_impact = risk_analyzer.analyze_event_impact(
    'BTC', '2020-03-12', pre_days=14, post_days=60
)

print("COVID-19市场崩盘影响分析:")
print(f"事件日期: {covid_impact['event_info']['event_date']}")
print(f"分析期间: {covid_impact['event_info']['analysis_period']}")

if 'impact_assessment' in covid_impact:
    impact = covid_impact['impact_assessment']
    print(f"影响等级: {impact['impact_level']}")
    print(f"严重性评分: {impact['severity_score']:.1f}/100")
    
    if impact['lasting_effects']:
        print("持续影响:")
        for effect in impact['lasting_effects']:
            print(f"  - {effect}")

if 'lessons_learned' in covid_impact:
    print("\n经验教训:")
    for lesson in covid_impact['lessons_learned']:
        print(f"  - {lesson}")

# 分析FTX破产事件
ftx_impact = risk_analyzer.analyze_event_impact(
    'BTC', '2022-11-08', pre_days=7, post_days=30
)

print(f"\nFTX破产事件影响分析:")
print(f"影响等级: {ftx_impact['impact_assessment']['impact_level']}")
```

## 常见问题

### Q1: 时点数据的精确性如何保证？

时点数据的精确性通过以下方式保证：
- **数据快照**: 每个时间点都有完整的数据快照
- **时间戳一致性**: 所有指标使用相同的时间戳
- **数据验证**: 多重验证确保数据准确性
- **历史固化**: 历史数据不会被修改

### Q2: 如何选择合适的分析时间点？

选择分析时间点的考虑因素：
- **重大市场事件**: 政策发布、技术更新、安全事件
- **技术指标信号**: 突破点、支撑阻力位
- **宏观经济事件**: 利率决议、经济数据发布
- **周期性节点**: 减半事件、季度末、年末

### Q3: 历史分析对当前投资的指导意义？

历史分析的指导作用：
- **模式识别**: 发现重复出现的市场模式
- **风险评估**: 了解历史风险水平和分布
- **策略验证**: 通过历史数据验证策略有效性
- **情景分析**: 为未来可能的情况做准备

### Q4: 如何处理数据缺失或异常？

数据处理方法：
- **插值法**: 对短期缺失数据进行合理插值
- **标记异常**: 明确标识数据质量问题
- **多源验证**: 使用多个数据源交叉验证
- **置信度标记**: 为每个数据点提供置信度评级

## 最佳实践

1. **多时点验证**: 不依赖单一时点，进行多时点交叉验证
2. **上下文分析**: 结合当时的市场环境和背景进行分析
3. **定期回顾**: 定期回顾历史分析，验证预测准确性
4. **数据完整性**: 确保分析所需的各类数据完整可用
5. **风险意识**: 历史不代表未来，保持风险意识
6. **策略适应**: 根据历史经验不断调整和优化策略

---

*本文档详细介绍了 Glassnode Point-In-Time API 的使用方法，包括数据获取、分析技术和实际应用案例。时点数据是进行历史研究、策略回测和风险评估的重要工具。*