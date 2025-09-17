# Protocols（协议数据）API 详细文档

## 概述

Protocols API 提供各种区块链协议的深度数据分析，包括DeFi协议、Layer 2解决方案、跨链协议、治理协议等的TVL（总锁定价值）、用户活动、治理参与度、代币经济学指标等。这些协议数据对于理解去中心化应用生态系统、评估协议健康度、识别投资机会、分析治理模式和进行协议间比较至关重要。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/protocols/`

**支持的协议类型**:
- DeFi 协议 (Uniswap, Aave, Compound, MakerDAO, Curve, etc.)
- Layer 2 解决方案 (Arbitrum, Optimism, Polygon, etc.)
- 跨链协议 (Bridge protocols)
- 治理协议 (DAO protocols)
- 流动性质押协议 (Lido, Rocket Pool, etc.)
- 衍生品协议 (dYdX, Perpetual Protocol, etc.)

**主要区块链覆盖**:
- Ethereum
- Binance Smart Chain
- Polygon
- Avalanche
- Arbitrum
- Optimism
- Fantom

**数据更新频率**: 
- 实时数据：10分钟
- TVL数据：每小时更新
- 治理数据：每日更新
- 代币指标：实时更新

## 核心端点

### 1. 总锁定价值（TVL）分析

#### 1.1 协议TVL总览

**端点**: `/tvl_total`

**描述**: 获取指定协议的总锁定价值数据，反映协议的资金规模和用户信任度。

**参数**:
- `protocol`: 协议名称（如 uniswap-v3）
- `chain`: 区块链网络（ethereum, polygon, arbitrum等）
- `i`: 时间间隔（1h, 24h, 1w）
- `s`: 开始时间戳
- `currency`: 计价货币（usd, eth, btc）

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/protocols/tvl_total?protocol=uniswap-v3&chain=ethereum&i=24h&s=1609459200" \
  -H "X-Api-Key: YOUR_API_KEY"
```

**示例响应**:
```json
[
  {
    "t": 1726790400,
    "v": {
      "tvl_usd": 4567890123.45,
      "tvl_eth": 1234567.89,
      "tvl_tokens": {
        "USDC": 1500000000,
        "USDT": 1200000000,
        "WETH": 800000000,
        "DAI": 600000000
      },
      "protocol_dominance": 12.5
    }
  }
]
```

#### 1.2 协议TVL排名

**端点**: `/tvl_rankings`

**描述**: 获取按TVL排序的协议排名，了解协议竞争格局。

**参数**:
- `chain`: 区块链网络
- `category`: 协议类别（defi, lending, dex, staking等）
- `limit`: 返回数量限制

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/protocols/tvl_rankings?chain=ethereum&category=defi&limit=20" \
  -H "X-Api-Key: YOUR_API_KEY"
```

### 2. 用户活动分析

#### 2.1 活跃用户数据

**端点**: `/active_users`

**描述**: 获取协议的活跃用户数据，包括日活、周活、月活用户。

**参数**:
- `protocol`: 协议名称
- `chain`: 区块链网络
- `i`: 时间间隔
- `user_type`: 用户类型（unique, new, returning）

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/protocols/active_users?protocol=aave-v2&chain=ethereum&i=24h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

#### 2.2 交易活动数据

**端点**: `/transaction_activity`

**描述**: 获取协议的交易活动数据，包括交易数量、交易量、Gas消耗等。

**参数**:
- `protocol`: 协议名称
- `chain`: 区块链网络
- `activity_type`: 活动类型（swap, deposit, withdraw, borrow, repay）

### 3. 治理指标

#### 3.1 治理参与度

**端点**: `/governance_participation`

**描述**: 获取协议治理的参与度数据，包括提案数量、投票参与率、代币质押率等。

**参数**:
- `protocol`: 协议名称
- `governance_type`: 治理类型（proposal, voting, delegation）
- `i`: 时间间隔

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/protocols/governance_participation?protocol=compound&i=24h" \
  -H "X-Api-Key: YOUR_API_KEY"
```

#### 3.2 治理代币分布

**端点**: `/governance_token_distribution`

**描述**: 获取治理代币的分布情况，分析去中心化程度。

**参数**:
- `protocol`: 协议名称
- `distribution_type`: 分布类型（holder, voting_power, delegation）

### 4. 代币经济学分析

#### 4.1 代币指标

**端点**: `/token_metrics`

**描述**: 获取协议代币的关键指标，包括价格、市值、流通量等。

**参数**:
- `protocol`: 协议名称
- `token_symbol`: 代币符号
- `metrics`: 指标类型（price, market_cap, volume, holders）

#### 4.2 代币流动性分析

**端点**: `/token_liquidity`

**描述**: 分析协议代币的流动性情况，包括DEX流动性、交易深度等。

## Python 实现类

```python
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple
import networkx as nx
from collections import defaultdict
import warnings

warnings.filterwarnings('ignore')

class ProtocolsAnalyzer:
    """
    Glassnode Protocols API 分析器
    提供协议数据的获取、分析和可视化功能
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.glassnode.com/v1/metrics/protocols/"
        self.headers = {"X-Api-Key": self.api_key}
        
        # 协议分类映射
        self.protocol_categories = {
            'dex': ['uniswap-v3', 'uniswap-v2', 'sushiswap', 'curve', 'balancer', 'pancakeswap'],
            'lending': ['aave-v2', 'aave-v3', 'compound', 'cream', 'venus'],
            'staking': ['lido', 'rocket-pool', 'frax', 'stakewise'],
            'derivatives': ['dydx', 'perpetual-protocol', 'synthetix', 'opyn'],
            'yield': ['yearn', 'convex', 'harvest', 'pickle'],
            'bridges': ['multichain', 'hop', 'across', 'connext'],
            'layer2': ['arbitrum', 'optimism', 'polygon', 'avalanche']
        }
        
        # 支持的区块链
        self.supported_chains = [
            'ethereum', 'polygon', 'arbitrum', 'optimism', 
            'avalanche', 'binance-smart-chain', 'fantom'
        ]
        
    def get_protocol_tvl(self, protocol: str, chain: str = 'ethereum', 
                        days: int = 30) -> Dict:
        """获取协议TVL数据"""
        
        url = self.base_url + "tvl_total"
        params = {
            'protocol': protocol,
            'chain': chain,
            'i': '24h',
            's': int((datetime.now() - timedelta(days=days)).timestamp()),
            'u': int(datetime.now().timestamp()),
            'currency': 'usd'
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            return self.analyze_protocol_tvl(data, protocol, chain)
            
        except Exception as e:
            print(f"获取协议TVL数据失败: {e}")
            return {}
    
    def analyze_protocol_tvl(self, data: List, protocol: str, chain: str) -> Dict:
        """分析协议TVL数据"""
        
        if not data:
            return {}
        
        # 转换为DataFrame
        df_data = []
        for entry in data:
            row = {
                'timestamp': pd.to_datetime(entry['t'], unit='s'),
                'tvl_usd': entry['v'].get('tvl_usd', 0),
                'tvl_eth': entry['v'].get('tvl_eth', 0),
                'protocol_dominance': entry['v'].get('protocol_dominance', 0)
            }
            
            # 处理代币构成数据
            tvl_tokens = entry['v'].get('tvl_tokens', {})
            for token, amount in tvl_tokens.items():
                row[f'{token}_tvl'] = amount
            
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df.set_index('timestamp', inplace=True)
        
        # 计算分析指标
        analysis = {
            'protocol': protocol,
            'chain': chain,
            'current_metrics': self.calculate_current_metrics(df),
            'growth_analysis': self.analyze_tvl_growth(df),
            'stability_analysis': self.analyze_tvl_stability(df),
            'token_composition': self.analyze_token_composition(df),
            'market_position': self.assess_market_position(df),
            'risk_assessment': self.assess_protocol_risk(df),
            'future_outlook': self.project_future_outlook(df)
        }
        
        return analysis
    
    def calculate_current_metrics(self, df: pd.DataFrame) -> Dict:
        """计算当前指标"""
        
        if df.empty:
            return {}
        
        current = df.iloc[-1]
        
        metrics = {
            'current_tvl': current['tvl_usd'],
            'current_tvl_eth': current['tvl_eth'],
            'protocol_dominance': current.get('protocol_dominance', 0),
            'tvl_rank_indicator': self.estimate_tvl_rank(current['tvl_usd']),
            'size_category': self.categorize_protocol_size(current['tvl_usd'])
        }
        
        # 计算变化率
        if len(df) >= 7:
            week_ago = df.iloc[-7]['tvl_usd']
            metrics['tvl_change_7d'] = ((current['tvl_usd'] - week_ago) / week_ago * 100) if week_ago > 0 else 0
        
        if len(df) >= 30:
            month_ago = df.iloc[-30]['tvl_usd']
            metrics['tvl_change_30d'] = ((current['tvl_usd'] - month_ago) / month_ago * 100) if month_ago > 0 else 0
        
        return metrics
    
    def estimate_tvl_rank(self, tvl: float) -> str:
        """估算TVL排名区间"""
        
        if tvl > 10000000000:  # > 100亿
            return 'top_5'
        elif tvl > 5000000000:  # > 50亿
            return 'top_10'
        elif tvl > 1000000000:  # > 10亿
            return 'top_20'
        elif tvl > 500000000:   # > 5亿
            return 'top_50'
        elif tvl > 100000000:   # > 1亿
            return 'top_100'
        else:
            return 'below_100'
    
    def categorize_protocol_size(self, tvl: float) -> str:
        """分类协议规模"""
        
        if tvl > 10000000000:
            return 'mega_protocol'
        elif tvl > 1000000000:
            return 'large_protocol'
        elif tvl > 100000000:
            return 'medium_protocol'
        elif tvl > 10000000:
            return 'small_protocol'
        else:
            return 'micro_protocol'
    
    def analyze_tvl_growth(self, df: pd.DataFrame) -> Dict:
        """分析TVL增长"""
        
        if len(df) < 7:
            return {}
        
        tvl_series = df['tvl_usd']
        
        growth = {
            'growth_rates': {
                'daily_avg': tvl_series.pct_change().mean() * 100,
                'weekly_avg': tvl_series.pct_change(periods=7).mean() * 100,
                'monthly_avg': tvl_series.pct_change(periods=30).mean() * 100 if len(df) >= 30 else 0
            },
            'growth_volatility': tvl_series.pct_change().std() * 100,
            'growth_consistency': self.calculate_growth_consistency(tvl_series),
            'growth_phase': self.identify_growth_phase(tvl_series),
            'trend_strength': self.calculate_trend_strength(tvl_series),
            'acceleration': self.calculate_growth_acceleration(tvl_series)
        }
        
        return growth
    
    def calculate_growth_consistency(self, series: pd.Series) -> float:
        """计算增长一致性"""
        
        returns = series.pct_change().dropna()
        
        if len(returns) == 0:
            return 0
        
        # 计算正收益率的比例
        positive_returns = (returns > 0).sum()
        total_returns = len(returns)
        
        consistency = positive_returns / total_returns
        
        return consistency
    
    def identify_growth_phase(self, series: pd.Series) -> str:
        """识别增长阶段"""
        
        if len(series) < 14:
            return 'insufficient_data'
        
        recent_growth = series.pct_change(periods=7).iloc[-1]
        overall_growth = (series.iloc[-1] / series.iloc[0] - 1) if series.iloc[0] > 0 else 0
        
        if recent_growth > 0.2:  # 20%
            return 'rapid_growth'
        elif recent_growth > 0.1:  # 10%
            return 'moderate_growth'
        elif recent_growth > 0:
            return 'slow_growth'
        elif recent_growth > -0.1:  # -10%
            return 'stagnation'
        elif recent_growth > -0.2:  # -20%
            return 'decline'
        else:
            return 'rapid_decline'
    
    def calculate_trend_strength(self, series: pd.Series) -> float:
        """计算趋势强度"""
        
        if len(series) < 10:
            return 0
        
        # 使用线性回归的R²作为趋势强度
        x = np.arange(len(series))
        y = series.values
        
        correlation = np.corrcoef(x, y)[0, 1]
        r_squared = correlation ** 2
        
        return r_squared
    
    def calculate_growth_acceleration(self, series: pd.Series) -> Dict:
        """计算增长加速度"""
        
        if len(series) < 14:
            return {}
        
        # 计算一阶和二阶导数
        first_diff = series.diff()
        second_diff = first_diff.diff()
        
        acceleration = {
            'velocity': first_diff.iloc[-1],  # 最近增长速度
            'acceleration': second_diff.iloc[-1],  # 增长加速度
            'is_accelerating': second_diff.iloc[-1] > 0,
            'momentum_score': self.calculate_momentum_score(first_diff, second_diff)
        }
        
        return acceleration
    
    def calculate_momentum_score(self, first_diff: pd.Series, second_diff: pd.Series) -> float:
        """计算动量评分"""
        
        recent_velocity = first_diff.tail(7).mean()
        recent_acceleration = second_diff.tail(7).mean()
        
        # 标准化动量评分
        momentum = recent_velocity + recent_acceleration * 0.5
        
        return momentum
    
    def analyze_tvl_stability(self, df: pd.DataFrame) -> Dict:
        """分析TVL稳定性"""
        
        if df.empty:
            return {}
        
        tvl_series = df['tvl_usd']
        
        stability = {
            'volatility_metrics': {
                'coefficient_of_variation': tvl_series.std() / tvl_series.mean() if tvl_series.mean() > 0 else 0,
                'volatility_annual': tvl_series.pct_change().std() * np.sqrt(365) * 100,
                'max_drawdown': self.calculate_max_drawdown(tvl_series),
                'var_95': np.percentile(tvl_series.pct_change().dropna() * 100, 5)
            },
            'stability_score': self.calculate_stability_score(tvl_series),
            'risk_level': self.assess_volatility_risk(tvl_series),
            'downside_protection': self.analyze_downside_protection(tvl_series)
        }
        
        return stability
    
    def calculate_max_drawdown(self, series: pd.Series) -> float:
        """计算最大回撤"""
        
        running_max = series.expanding().max()
        drawdown = (series - running_max) / running_max
        
        return drawdown.min()
    
    def calculate_stability_score(self, series: pd.Series) -> float:
        """计算稳定性评分"""
        
        if len(series) < 7:
            return 50  # 默认中等稳定性
        
        # 基于多个指标的综合稳定性评分
        cv = series.std() / series.mean() if series.mean() > 0 else 1
        max_dd = abs(self.calculate_max_drawdown(series))
        volatility = series.pct_change().std()
        
        # 稳定性评分（0-100，100最稳定）
        cv_score = max(0, 100 - cv * 100)
        dd_score = max(0, 100 - max_dd * 200)
        vol_score = max(0, 100 - volatility * 1000)
        
        stability_score = (cv_score + dd_score + vol_score) / 3
        
        return stability_score
    
    def assess_volatility_risk(self, series: pd.Series) -> str:
        """评估波动性风险"""
        
        volatility = series.pct_change().std() * np.sqrt(365)
        
        if volatility > 1.0:  # 100%年化波动率
            return 'very_high'
        elif volatility > 0.5:  # 50%
            return 'high'
        elif volatility > 0.3:  # 30%
            return 'moderate'
        elif volatility > 0.1:  # 10%
            return 'low'
        else:
            return 'very_low'
    
    def analyze_downside_protection(self, series: pd.Series) -> Dict:
        """分析下行保护"""
        
        returns = series.pct_change().dropna()
        
        protection = {
            'negative_return_frequency': (returns < 0).sum() / len(returns) if len(returns) > 0 else 0,
            'average_negative_return': returns[returns < 0].mean() if (returns < 0).any() else 0,
            'worst_single_day': returns.min(),
            'consecutive_decline_max': self.calculate_max_consecutive_declines(returns)
        }
        
        return protection
    
    def calculate_max_consecutive_declines(self, returns: pd.Series) -> int:
        """计算最大连续下跌天数"""
        
        declines = returns < 0
        consecutive = 0
        max_consecutive = 0
        
        for decline in declines:
            if decline:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 0
        
        return max_consecutive
    
    def analyze_token_composition(self, df: pd.DataFrame) -> Dict:
        """分析代币构成"""
        
        if df.empty:
            return {}
        
        # 识别代币列
        token_columns = [col for col in df.columns if col.endswith('_tvl')]
        
        if not token_columns:
            return {'status': 'no_token_data'}
        
        latest_data = df.iloc[-1]
        
        composition = {
            'token_breakdown': {},
            'diversification_score': 0,
            'dominant_token': '',
            'concentration_risk': 'unknown',
            'composition_stability': 0
        }
        
        # 计算代币占比
        total_value = sum(latest_data[col] for col in token_columns if not pd.isna(latest_data[col]))
        
        for col in token_columns:
            token = col.replace('_tvl', '')
            value = latest_data[col] if not pd.isna(latest_data[col]) else 0
            percentage = (value / total_value * 100) if total_value > 0 else 0
            
            composition['token_breakdown'][token] = {
                'value': value,
                'percentage': percentage
            }
        
        # 找出主导代币
        if composition['token_breakdown']:
            composition['dominant_token'] = max(
                composition['token_breakdown'].keys(),
                key=lambda x: composition['token_breakdown'][x]['percentage']
            )
            
            dominant_pct = composition['token_breakdown'][composition['dominant_token']]['percentage']
            
            # 评估集中度风险
            if dominant_pct > 70:
                composition['concentration_risk'] = 'high'
            elif dominant_pct > 50:
                composition['concentration_risk'] = 'moderate'
            else:
                composition['concentration_risk'] = 'low'
        
        # 计算多样化评分
        percentages = [data['percentage'] for data in composition['token_breakdown'].values()]
        if percentages:
            # 使用赫芬达尔指数的反转
            hhi = sum((p/100)**2 for p in percentages)
            composition['diversification_score'] = (1 - hhi) * 100
        
        return composition
    
    def assess_market_position(self, df: pd.DataFrame) -> Dict:
        """评估市场地位"""
        
        if df.empty:
            return {}
        
        current_tvl = df['tvl_usd'].iloc[-1]
        dominance = df.get('protocol_dominance', pd.Series([0])).iloc[-1]
        
        position = {
            'tvl_tier': self.categorize_protocol_size(current_tvl),
            'estimated_rank': self.estimate_tvl_rank(current_tvl),
            'market_dominance': dominance,
            'competitive_position': self.assess_competitive_position(current_tvl, dominance),
            'market_share_trend': self.analyze_market_share_trend(df),
            'growth_vs_market': self.compare_growth_vs_market(df)
        }
        
        return position
    
    def assess_competitive_position(self, tvl: float, dominance: float) -> str:
        """评估竞争地位"""
        
        if dominance > 20:
            return 'market_leader'
        elif dominance > 10:
            return 'major_player'
        elif dominance > 5:
            return 'significant_player'
        elif dominance > 1:
            return 'niche_player'
        else:
            return 'emerging_protocol'
    
    def analyze_market_share_trend(self, df: pd.DataFrame) -> Dict:
        """分析市场份额趋势"""
        
        if 'protocol_dominance' not in df.columns or len(df) < 7:
            return {}
        
        dominance_series = df['protocol_dominance']
        
        trend = {
            'current_share': dominance_series.iloc[-1],
            'share_change_7d': dominance_series.iloc[-1] - dominance_series.iloc[-7] if len(df) >= 7 else 0,
            'share_change_30d': dominance_series.iloc[-1] - dominance_series.iloc[-30] if len(df) >= 30 else 0,
            'trend_direction': self.determine_share_trend(dominance_series),
            'share_volatility': dominance_series.std()
        }
        
        return trend
    
    def determine_share_trend(self, series: pd.Series) -> str:
        """确定份额趋势"""
        
        if len(series) < 14:
            return 'insufficient_data'
        
        recent_avg = series.tail(7).mean()
        earlier_avg = series.head(7).mean()
        
        change = ((recent_avg - earlier_avg) / earlier_avg * 100) if earlier_avg > 0 else 0
        
        if change > 10:
            return 'gaining_share'
        elif change > 2:
            return 'slight_gain'
        elif change > -2:
            return 'stable_share'
        elif change > -10:
            return 'slight_loss'
        else:
            return 'losing_share'
    
    def compare_growth_vs_market(self, df: pd.DataFrame) -> Dict:
        """比较相对市场增长"""
        
        # 简化实现，实际需要整体市场数据
        if len(df) < 30:
            return {}
        
        protocol_growth = ((df['tvl_usd'].iloc[-1] / df['tvl_usd'].iloc[-30]) - 1) * 100
        market_growth = 15  # 假设市场平均增长15%（实际应从市场数据获取）
        
        comparison = {
            'protocol_growth_30d': protocol_growth,
            'estimated_market_growth_30d': market_growth,
            'relative_performance': protocol_growth - market_growth,
            'outperforming_market': protocol_growth > market_growth,
            'performance_category': self.categorize_performance(protocol_growth - market_growth)
        }
        
        return comparison
    
    def categorize_performance(self, relative_performance: float) -> str:
        """分类相对表现"""
        
        if relative_performance > 20:
            return 'significantly_outperforming'
        elif relative_performance > 5:
            return 'outperforming'
        elif relative_performance > -5:
            return 'inline_with_market'
        elif relative_performance > -20:
            return 'underperforming'
        else:
            return 'significantly_underperforming'
    
    def assess_protocol_risk(self, df: pd.DataFrame) -> Dict:
        """评估协议风险"""
        
        if df.empty:
            return {}
        
        risk = {
            'liquidity_risk': self.assess_liquidity_risk(df),
            'concentration_risk': self.assess_concentration_risk(df),
            'volatility_risk': self.assess_volatility_risk_detailed(df),
            'smart_contract_risk': self.assess_smart_contract_risk(),
            'governance_risk': self.assess_governance_risk(),
            'overall_risk_score': 0,
            'risk_level': 'medium'
        }
        
        # 计算综合风险评分
        risk_scores = [
            risk['liquidity_risk'].get('risk_score', 50),
            risk['concentration_risk'].get('risk_score', 50),
            risk['volatility_risk'].get('risk_score', 50),
            risk['smart_contract_risk'].get('risk_score', 50),
            risk['governance_risk'].get('risk_score', 50)
        ]
        
        risk['overall_risk_score'] = sum(risk_scores) / len(risk_scores)
        
        # 确定风险等级
        if risk['overall_risk_score'] > 75:
            risk['risk_level'] = 'very_high'
        elif risk['overall_risk_score'] > 60:
            risk['risk_level'] = 'high'
        elif risk['overall_risk_score'] > 40:
            risk['risk_level'] = 'moderate'
        elif risk['overall_risk_score'] > 25:
            risk['risk_level'] = 'low'
        else:
            risk['risk_level'] = 'very_low'
        
        return risk
    
    def assess_liquidity_risk(self, df: pd.DataFrame) -> Dict:
        """评估流动性风险"""
        
        tvl_series = df['tvl_usd']
        
        # 基于TVL波动性和规模评估流动性风险
        volatility = tvl_series.pct_change().std()
        avg_tvl = tvl_series.mean()
        
        liquidity_risk = {
            'tvl_volatility': volatility,
            'average_tvl': avg_tvl,
            'liquidity_score': self.calculate_liquidity_score(avg_tvl, volatility),
            'risk_score': 0,
            'risk_factors': []
        }
        
        # 流动性风险评分
        if avg_tvl < 10000000:  # < 1000万
            liquidity_risk['risk_score'] += 40
            liquidity_risk['risk_factors'].append("TVL规模较小")
        
        if volatility > 0.1:  # 日波动率 > 10%
            liquidity_risk['risk_score'] += 30
            liquidity_risk['risk_factors'].append("TVL波动性高")
        
        if tvl_series.iloc[-1] < tvl_series.iloc[-7]:  # 最近下降
            liquidity_risk['risk_score'] += 20
            liquidity_risk['risk_factors'].append("TVL最近下降")
        
        liquidity_risk['risk_score'] = min(100, liquidity_risk['risk_score'])
        
        return liquidity_risk
    
    def calculate_liquidity_score(self, tvl: float, volatility: float) -> float:
        """计算流动性评分"""
        
        # 基于TVL规模的评分
        if tvl > 1000000000:  # > 10亿
            size_score = 90
        elif tvl > 100000000:  # > 1亿
            size_score = 70
        elif tvl > 10000000:   # > 1000万
            size_score = 50
        else:
            size_score = 20
        
        # 基于波动性的评分
        volatility_score = max(0, 100 - volatility * 1000)
        
        return (size_score + volatility_score) / 2
    
    def assess_concentration_risk(self, df: pd.DataFrame) -> Dict:
        """评估集中度风险"""
        
        # 基于代币构成分析集中度风险
        token_composition = self.analyze_token_composition(df)
        
        concentration_risk = {
            'diversification_score': token_composition.get('diversification_score', 50),
            'concentration_level': token_composition.get('concentration_risk', 'unknown'),
            'risk_score': 0,
            'risk_factors': []
        }
        
        # 集中度风险评分
        diversification = token_composition.get('diversification_score', 50)
        
        if diversification < 30:
            concentration_risk['risk_score'] = 80
            concentration_risk['risk_factors'].append("代币构成高度集中")
        elif diversification < 50:
            concentration_risk['risk_score'] = 60
            concentration_risk['risk_factors'].append("代币构成中度集中")
        elif diversification < 70:
            concentration_risk['risk_score'] = 40
            concentration_risk['risk_factors'].append("代币构成相对集中")
        else:
            concentration_risk['risk_score'] = 20
            concentration_risk['risk_factors'].append("代币构成多样化")
        
        return concentration_risk
    
    def assess_volatility_risk_detailed(self, df: pd.DataFrame) -> Dict:
        """详细评估波动性风险"""
        
        if df.empty:
            return {}
        
        tvl_series = df['tvl_usd']
        returns = tvl_series.pct_change().dropna()
        
        volatility_risk = {
            'daily_volatility': returns.std(),
            'annualized_volatility': returns.std() * np.sqrt(365),
            'max_drawdown': self.calculate_max_drawdown(tvl_series),
            'var_95': np.percentile(returns, 5) if len(returns) > 0 else 0,
            'risk_score': 0,
            'volatility_regime': 'normal'
        }
        
        # 波动性风险评分
        ann_vol = volatility_risk['annualized_volatility']
        max_dd = abs(volatility_risk['max_drawdown'])
        
        vol_score = min(100, ann_vol * 100)
        dd_score = min(100, max_dd * 200)
        
        volatility_risk['risk_score'] = (vol_score + dd_score) / 2
        
        # 波动性制度
        if ann_vol > 1.0:
            volatility_risk['volatility_regime'] = 'high_volatility'
        elif ann_vol > 0.5:
            volatility_risk['volatility_regime'] = 'elevated_volatility'
        elif ann_vol < 0.1:
            volatility_risk['volatility_regime'] = 'low_volatility'
        
        return volatility_risk
    
    def assess_smart_contract_risk(self) -> Dict:
        """评估智能合约风险"""
        
        # 简化的智能合约风险评估
        # 实际实现需要更多协议特定信息
        
        smart_contract_risk = {
            'audit_status': 'unknown',
            'code_complexity': 'medium',
            'upgrade_mechanism': 'unknown',
            'bug_history': 'unknown',
            'risk_score': 50,  # 默认中等风险
            'risk_factors': ['智能合约固有风险', '需要具体审计信息']
        }
        
        return smart_contract_risk
    
    def assess_governance_risk(self) -> Dict:
        """评估治理风险"""
        
        # 简化的治理风险评估
        governance_risk = {
            'decentralization_level': 'unknown',
            'token_distribution': 'unknown',
            'voting_participation': 'unknown',
            'governance_attacks_risk': 'medium',
            'risk_score': 50,  # 默认中等风险
            'risk_factors': ['治理集中化风险', '需要具体治理数据']
        }
        
        return governance_risk
    
    def project_future_outlook(self, df: pd.DataFrame) -> Dict:
        """项目未来展望"""
        
        if len(df) < 30:
            return {'status': 'insufficient_data_for_projection'}
        
        tvl_series = df['tvl_usd']
        
        outlook = {
            'trend_projection': self.project_trend(tvl_series),
            'growth_potential': self.assess_growth_potential(df),
            'risk_outlook': self.assess_future_risks(df),
            'investment_thesis': self.generate_investment_thesis(df),
            'key_catalysts': self.identify_key_catalysts(),
            'potential_headwinds': self.identify_potential_headwinds()
        }
        
        return outlook
    
    def project_trend(self, series: pd.Series) -> Dict:
        """投射趋势"""
        
        # 简单的线性趋势投射
        x = np.arange(len(series))
        z = np.polyfit(x, series, 1)
        
        # 投射未来30天
        future_x = np.arange(len(series), len(series) + 30)
        projected_values = np.polyval(z, future_x)
        
        projection = {
            'trend_slope': z[0],
            'current_value': series.iloc[-1],
            'projected_30d': projected_values[-1],
            'projected_growth_30d': ((projected_values[-1] / series.iloc[-1]) - 1) * 100 if series.iloc[-1] > 0 else 0,
            'confidence_level': self.calculate_projection_confidence(series)
        }
        
        return projection
    
    def calculate_projection_confidence(self, series: pd.Series) -> str:
        """计算投射置信度"""
        
        # 基于趋势强度和稳定性
        trend_strength = self.calculate_trend_strength(series)
        stability_score = self.calculate_stability_score(series)
        
        confidence_score = (trend_strength * 100 + stability_score) / 2
        
        if confidence_score > 70:
            return 'high'
        elif confidence_score > 50:
            return 'medium'
        else:
            return 'low'
    
    def assess_growth_potential(self, df: pd.DataFrame) -> Dict:
        """评估增长潜力"""
        
        current_tvl = df['tvl_usd'].iloc[-1]
        growth_analysis = self.analyze_tvl_growth(df)
        
        potential = {
            'size_potential': self.assess_size_potential(current_tvl),
            'growth_momentum': growth_analysis.get('growth_phase', 'unknown'),
            'market_opportunity': self.assess_market_opportunity(current_tvl),
            'competitive_advantages': self.identify_competitive_advantages(),
            'growth_score': self.calculate_growth_score(df)
        }
        
        return potential
    
    def assess_size_potential(self, current_tvl: float) -> str:
        """评估规模潜力"""
        
        if current_tvl < 100000000:  # < 1亿
            return 'high_growth_potential'
        elif current_tvl < 1000000000:  # < 10亿
            return 'moderate_growth_potential'
        elif current_tvl < 10000000000:  # < 100亿
            return 'limited_growth_potential'
        else:
            return 'mature_size'
    
    def assess_market_opportunity(self, current_tvl: float) -> str:
        """评估市场机会"""
        
        # 简化的市场机会评估
        total_defi_tvl = 100000000000  # 假设DeFi总TVL为1000亿
        market_share = (current_tvl / total_defi_tvl) * 100
        
        if market_share < 0.1:
            return 'large_opportunity'
        elif market_share < 1:
            return 'moderate_opportunity'
        elif market_share < 5:
            return 'limited_opportunity'
        else:
            return 'saturated_market'
    
    def identify_competitive_advantages(self) -> List[str]:
        """识别竞争优势"""
        
        # 简化实现，实际需要协议特定分析
        return [
            "需要具体协议分析",
            "技术创新",
            "用户体验",
            "代币经济学",
            "团队背景",
            "社区支持"
        ]
    
    def calculate_growth_score(self, df: pd.DataFrame) -> float:
        """计算增长评分"""
        
        growth_analysis = self.analyze_tvl_growth(df)
        stability_analysis = self.analyze_tvl_stability(df)
        
        # 综合增长和稳定性
        growth_rate = growth_analysis.get('growth_rates', {}).get('monthly_avg', 0)
        growth_consistency = growth_analysis.get('growth_consistency', 0)
        stability_score = stability_analysis.get('stability_score', 50)
        
        # 加权评分
        score = (
            min(100, abs(growth_rate) * 2) * 0.4 +  # 增长率
            growth_consistency * 100 * 0.3 +        # 增长一致性
            stability_score * 0.3                   # 稳定性
        )
        
        return score
    
    def assess_future_risks(self, df: pd.DataFrame) -> List[str]:
        """评估未来风险"""
        
        risks = []
        
        current_risk = self.assess_protocol_risk(df)
        
        if current_risk.get('overall_risk_score', 0) > 60:
            risks.append("整体风险水平较高")
        
        # 基于当前趋势的风险
        tvl_series = df['tvl_usd']
        if len(tvl_series) >= 7:
            recent_trend = tvl_series.iloc[-7:].pct_change().mean()
            if recent_trend < -0.05:  # 最近下降趋势
                risks.append("TVL下降趋势可能持续")
        
        # 通用风险
        risks.extend([
            "市场系统性风险",
            "监管政策变化",
            "技术升级风险",
            "竞争加剧风险"
        ])
        
        return risks
    
    def generate_investment_thesis(self, df: pd.DataFrame) -> Dict:
        """生成投资论点"""
        
        current_metrics = self.calculate_current_metrics(df)
        growth_analysis = self.analyze_tvl_growth(df)
        market_position = self.assess_market_position(df)
        
        thesis = {
            'bull_case': [],
            'bear_case': [],
            'base_case': [],
            'key_metrics_to_watch': [],
            'investment_recommendation': 'neutral'
        }
        
        # 看涨论点
        if growth_analysis.get('growth_phase') in ['rapid_growth', 'moderate_growth']:
            thesis['bull_case'].append("强劲的TVL增长趋势")
        
        if current_metrics.get('size_category') in ['large_protocol', 'mega_protocol']:
            thesis['bull_case'].append("已建立市场地位")
        
        if market_position.get('competitive_position') in ['market_leader', 'major_player']:
            thesis['bull_case'].append("竞争优势明显")
        
        # 看跌论点
        risk_assessment = self.assess_protocol_risk(df)
        if risk_assessment.get('overall_risk_score', 0) > 70:
            thesis['bear_case'].append("高风险水平")
        
        if growth_analysis.get('growth_phase') in ['decline', 'rapid_decline']:
            thesis['bear_case'].append("TVL下降趋势")
        
        # 基准情况
        thesis['base_case'] = [
            "继续关注TVL趋势",
            "监控竞争环境变化",
            "评估技术发展进展"
        ]
        
        # 关键指标
        thesis['key_metrics_to_watch'] = [
            "TVL增长率",
            "用户数量变化",
            "市场份额变化",
            "代币价格表现",
            "治理参与度"
        ]
        
        # 投资建议
        bull_points = len(thesis['bull_case'])
        bear_points = len(thesis['bear_case'])
        
        if bull_points > bear_points + 1:
            thesis['investment_recommendation'] = 'bullish'
        elif bear_points > bull_points + 1:
            thesis['investment_recommendation'] = 'bearish'
        else:
            thesis['investment_recommendation'] = 'neutral'
        
        return thesis
    
    def identify_key_catalysts(self) -> List[str]:
        """识别关键催化剂"""
        
        # 通用催化剂，实际需要协议特定分析
        catalysts = [
            "技术升级和新功能发布",
            "新的合作伙伴关系",
            "代币经济学改进",
            "新链部署",
            "机构采用增加",
            "监管明确化",
            "市场整体增长",
            "竞争对手问题"
        ]
        
        return catalysts
    
    def identify_potential_headwinds(self) -> List[str]:
        """识别潜在阻力"""
        
        headwinds = [
            "监管不确定性",
            "技术风险和漏洞",
            "竞争加剧",
            "市场系统性风险",
            "流动性挖矿收益下降",
            "Gas费用上升",
            "用户体验问题",
            "治理争议"
        ]
        
        return headwinds

    def get_protocol_rankings(self, chain: str = 'ethereum', 
                            category: str = 'defi', limit: int = 20) -> Dict:
        """获取协议排名"""
        
        url = self.base_url + "tvl_rankings"
        params = {
            'chain': chain,
            'category': category,
            'limit': limit
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            return self.analyze_protocol_rankings(data, chain, category)
            
        except Exception as e:
            print(f"获取协议排名失败: {e}")
            return {}
    
    def analyze_protocol_rankings(self, data: List, chain: str, category: str) -> Dict:
        """分析协议排名"""
        
        if not data:
            return {}
        
        rankings = {
            'chain': chain,
            'category': category,
            'total_protocols': len(data),
            'rankings': data,
            'market_concentration': self.calculate_market_concentration(data),
            'top_performers': self.identify_top_performers(data),
            'growth_leaders': self.identify_growth_leaders(data),
            'market_insights': self.generate_market_insights(data)
        }
        
        return rankings
    
    def calculate_market_concentration(self, data: List) -> Dict:
        """计算市场集中度"""
        
        if not data:
            return {}
        
        tvl_values = [protocol.get('tvl', 0) for protocol in data]
        total_tvl = sum(tvl_values)
        
        # 计算不同集中度指标
        concentration = {
            'total_tvl': total_tvl,
            'top_3_share': sum(tvl_values[:3]) / total_tvl * 100 if total_tvl > 0 else 0,
            'top_5_share': sum(tvl_values[:5]) / total_tvl * 100 if total_tvl > 0 else 0,
            'top_10_share': sum(tvl_values[:10]) / total_tvl * 100 if total_tvl > 0 else 0,
            'herfindahl_index': sum((tvl / total_tvl) ** 2 for tvl in tvl_values) if total_tvl > 0 else 0,
            'concentration_level': ''
        }
        
        # 评估集中度水平
        if concentration['top_3_share'] > 60:
            concentration['concentration_level'] = 'highly_concentrated'
        elif concentration['top_3_share'] > 40:
            concentration['concentration_level'] = 'moderately_concentrated'
        else:
            concentration['concentration_level'] = 'decentralized'
        
        return concentration
    
    def identify_top_performers(self, data: List) -> List[Dict]:
        """识别顶级表现者"""
        
        # 按TVL排序的前5名
        top_performers = []
        
        for i, protocol in enumerate(data[:5]):
            performer = {
                'rank': i + 1,
                'name': protocol.get('name', 'Unknown'),
                'tvl': protocol.get('tvl', 0),
                'market_share': protocol.get('market_share', 0),
                'category': protocol.get('category', 'Unknown')
            }
            top_performers.append(performer)
        
        return top_performers
    
    def identify_growth_leaders(self, data: List) -> List[Dict]:
        """识别增长领导者"""
        
        # 基于增长率排序（如果有增长数据）
        growth_leaders = []
        
        for protocol in data:
            if 'growth_7d' in protocol or 'growth_30d' in protocol:
                leader = {
                    'name': protocol.get('name', 'Unknown'),
                    'tvl': protocol.get('tvl', 0),
                    'growth_7d': protocol.get('growth_7d', 0),
                    'growth_30d': protocol.get('growth_30d', 0)
                }
                growth_leaders.append(leader)
        
        # 按30天增长率排序
        growth_leaders.sort(key=lambda x: x.get('growth_30d', 0), reverse=True)
        
        return growth_leaders[:5]
    
    def generate_market_insights(self, data: List) -> List[str]:
        """生成市场洞察"""
        
        insights = []
        
        if not data:
            return insights
        
        total_protocols = len(data)
        tvl_values = [protocol.get('tvl', 0) for protocol in data]
        total_tvl = sum(tvl_values)
        
        # 市场规模洞察
        if total_tvl > 100000000000:  # > 1000亿
            insights.append("市场规模超过1000亿美元，已达到显著规模")
        elif total_tvl > 50000000000:  # > 500亿
            insights.append("市场规模超过500亿美元，处于快速发展阶段")
        
        # 集中度洞察
        top_3_tvl = sum(tvl_values[:3])
        top_3_share = (top_3_tvl / total_tvl * 100) if total_tvl > 0 else 0
        
        if top_3_share > 60:
            insights.append("市场高度集中，前三大协议占据主导地位")
        elif top_3_share < 30:
            insights.append("市场相对分散，竞争激烈")
        
        # 协议数量洞察
        if total_protocols > 100:
            insights.append("协议数量众多，生态系统多样化")
        elif total_protocols < 20:
            insights.append("协议数量较少，市场仍在早期阶段")
        
        return insights
    
    def compare_protocols(self, protocols: List[str], chain: str = 'ethereum') -> Dict:
        """比较多个协议"""
        
        comparison_data = {}
        
        for protocol in protocols:
            protocol_data = self.get_protocol_tvl(protocol, chain)
            comparison_data[protocol] = protocol_data
        
        comparison = {
            'protocols': protocols,
            'chain': chain,
            'comparison_data': comparison_data,
            'relative_analysis': self.analyze_relative_performance(comparison_data),
            'ranking': self.rank_protocols(comparison_data),
            'investment_ranking': self.rank_by_investment_potential(comparison_data)
        }
        
        return comparison
    
    def analyze_relative_performance(self, comparison_data: Dict) -> Dict:
        """分析相对表现"""
        
        relative = {
            'tvl_comparison': {},
            'growth_comparison': {},
            'risk_comparison': {},
            'stability_comparison': {}
        }
        
        for protocol, data in comparison_data.items():
            if not data:
                continue
            
            current_metrics = data.get('current_metrics', {})
            growth_analysis = data.get('growth_analysis', {})
            risk_assessment = data.get('risk_assessment', {})
            stability_analysis = data.get('stability_analysis', {})
            
            relative['tvl_comparison'][protocol] = current_metrics.get('current_tvl', 0)
            relative['growth_comparison'][protocol] = growth_analysis.get('growth_rates', {}).get('monthly_avg', 0)
            relative['risk_comparison'][protocol] = risk_assessment.get('overall_risk_score', 50)
            relative['stability_comparison'][protocol] = stability_analysis.get('stability_score', 50)
        
        return relative
    
    def rank_protocols(self, comparison_data: Dict) -> Dict:
        """协议排名"""
        
        rankings = {
            'by_tvl': [],
            'by_growth': [],
            'by_stability': [],
            'by_risk_adjusted_return': []
        }
        
        for protocol, data in comparison_data.items():
            if not data:
                continue
            
            current_metrics = data.get('current_metrics', {})
            growth_analysis = data.get('growth_analysis', {})
            stability_analysis = data.get('stability_analysis', {})
            risk_assessment = data.get('risk_assessment', {})
            
            # TVL排名
            rankings['by_tvl'].append({
                'protocol': protocol,
                'tvl': current_metrics.get('current_tvl', 0)
            })
            
            # 增长排名
            rankings['by_growth'].append({
                'protocol': protocol,
                'growth_rate': growth_analysis.get('growth_rates', {}).get('monthly_avg', 0)
            })
            
            # 稳定性排名
            rankings['by_stability'].append({
                'protocol': protocol,
                'stability_score': stability_analysis.get('stability_score', 0)
            })
            
            # 风险调整收益排名
            growth_rate = growth_analysis.get('growth_rates', {}).get('monthly_avg', 0)
            risk_score = risk_assessment.get('overall_risk_score', 50)
            risk_adjusted = growth_rate / (risk_score / 100) if risk_score > 0 else 0
            
            rankings['by_risk_adjusted_return'].append({
                'protocol': protocol,
                'risk_adjusted_return': risk_adjusted
            })
        
        # 排序
        rankings['by_tvl'].sort(key=lambda x: x['tvl'], reverse=True)
        rankings['by_growth'].sort(key=lambda x: x['growth_rate'], reverse=True)
        rankings['by_stability'].sort(key=lambda x: x['stability_score'], reverse=True)
        rankings['by_risk_adjusted_return'].sort(key=lambda x: x['risk_adjusted_return'], reverse=True)
        
        return rankings
    
    def rank_by_investment_potential(self, comparison_data: Dict) -> List[Dict]:
        """按投资潜力排名"""
        
        investment_scores = []
        
        for protocol, data in comparison_data.items():
            if not data:
                continue
            
            score = self.calculate_investment_score(data)
            
            investment_scores.append({
                'protocol': protocol,
                'investment_score': score,
                'recommendation': self.get_investment_recommendation(score)
            })
        
        investment_scores.sort(key=lambda x: x['investment_score'], reverse=True)
        
        return investment_scores
    
    def calculate_investment_score(self, data: Dict) -> float:
        """计算投资评分"""
        
        current_metrics = data.get('current_metrics', {})
        growth_analysis = data.get('growth_analysis', {})
        stability_analysis = data.get('stability_analysis', {})
        risk_assessment = data.get('risk_assessment', {})
        market_position = data.get('market_position', {})
        
        # 各项评分
        growth_score = min(100, abs(growth_analysis.get('growth_rates', {}).get('monthly_avg', 0)) * 2)
        stability_score = stability_analysis.get('stability_score', 50)
        risk_score = 100 - risk_assessment.get('overall_risk_score', 50)  # 风险越低，评分越高
        
        # 市场地位评分
        tvl = current_metrics.get('current_tvl', 0)
        if tvl > 1000000000:  # > 10亿
            market_score = 90
        elif tvl > 100000000:  # > 1亿
            market_score = 70
        elif tvl > 10000000:   # > 1000万
            market_score = 50
        else:
            market_score = 30
        
        # 加权综合评分
        investment_score = (
            growth_score * 0.3 +
            stability_score * 0.25 +
            risk_score * 0.25 +
            market_score * 0.2
        )
        
        return investment_score
    
    def get_investment_recommendation(self, score: float) -> str:
        """获取投资建议"""
        
        if score > 80:
            return 'strong_buy'
        elif score > 65:
            return 'buy'
        elif score > 50:
            return 'hold'
        elif score > 35:
            return 'weak_hold'
        else:
            return 'avoid'

    def visualize_protocol_analysis(self, analysis: Dict, save_path: str = None):
        """可视化协议分析"""
        
        if not analysis:
            print("无分析数据可用")
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        protocol_name = analysis.get('protocol', 'Unknown')
        
        # 1. TVL趋势（模拟数据）
        ax = axes[0, 0]
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        current_tvl = analysis.get('current_metrics', {}).get('current_tvl', 0)
        
        # 模拟TVL趋势数据
        growth_rate = analysis.get('growth_analysis', {}).get('growth_rates', {}).get('daily_avg', 0) / 100
        tvl_trend = [current_tvl * (1 + growth_rate) ** i for i in range(-29, 1)]
        
        ax.plot(dates, tvl_trend, 'b-', linewidth=2)
        ax.set_title(f"{protocol_name} TVL趋势")
        ax.set_ylabel("TVL (USD)")
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
        
        # 2. 风险评估雷达图
        ax = axes[0, 1]
        risk_assessment = analysis.get('risk_assessment', {})
        
        risk_categories = ['流动性', '集中度', '波动性', '智能合约', '治理']
        risk_scores = [
            100 - risk_assessment.get('liquidity_risk', {}).get('risk_score', 50),
            100 - risk_assessment.get('concentration_risk', {}).get('risk_score', 50),
            100 - risk_assessment.get('volatility_risk', {}).get('risk_score', 50),
            100 - risk_assessment.get('smart_contract_risk', {}).get('risk_score', 50),
            100 - risk_assessment.get('governance_risk', {}).get('risk_score', 50)
        ]
        
        angles = np.linspace(0, 2 * np.pi, len(risk_categories), endpoint=False)
        risk_scores += risk_scores[:1]
        angles = np.concatenate((angles, [angles[0]]))
        
        ax.plot(angles, risk_scores, 'o-', linewidth=2)
        ax.fill(angles, risk_scores, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(risk_categories)
        ax.set_title("风险评估雷达图")
        ax.grid(True)
        
        # 3. 代币构成
        ax = axes[0, 2]
        token_composition = analysis.get('token_composition', {})
        token_breakdown = token_composition.get('token_breakdown', {})
        
        if token_breakdown:
            tokens = list(token_breakdown.keys())[:5]  # 前5大代币
            percentages = [token_breakdown[token]['percentage'] for token in tokens]
            
            ax.pie(percentages, labels=tokens, autopct='%1.1f%%', startangle=90)
            ax.set_title("代币构成分布")
        else:
            ax.text(0.5, 0.5, '无代币构成数据', ha='center', va='center', transform=ax.transAxes)
            ax.set_title("代币构成分布")
        
        # 4. 增长指标
        ax = axes[1, 0]
        growth_analysis = analysis.get('growth_analysis', {})
        growth_rates = growth_analysis.get('growth_rates', {})
        
        periods = ['日平均', '周平均', '月平均']
        rates = [
            growth_rates.get('daily_avg', 0),
            growth_rates.get('weekly_avg', 0),
            growth_rates.get('monthly_avg', 0)
        ]
        
        colors = ['green' if rate > 0 else 'red' for rate in rates]
        bars = ax.bar(periods, rates, color=colors, alpha=0.7)
        ax.set_title("增长率分析")
        ax.set_ylabel("增长率 (%)")
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # 添加数值标签
        for bar, rate in zip(bars, rates):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + (0.01 if height >= 0 else -0.03),
                    f'{rate:.2f}%', ha='center', va='bottom' if height >= 0 else 'top')
        
        # 5. 市场地位
        ax = axes[1, 1]
        market_position = analysis.get('market_position', {})
        current_metrics = analysis.get('current_metrics', {})
        
        metrics = ['TVL排名', '市场份额', '竞争地位', '增长潜力']
        scores = [
            {'top_5': 95, 'top_10': 85, 'top_20': 70, 'top_50': 50, 'top_100': 30, 'below_100': 10}.get(
                current_metrics.get('tvl_rank_indicator', 'below_100'), 10),
            min(100, market_position.get('market_dominance', 0) * 5),
            {'market_leader': 95, 'major_player': 80, 'significant_player': 60, 'niche_player': 40, 'emerging_protocol': 20}.get(
                market_position.get('competitive_position', 'emerging_protocol'), 20),
            analysis.get('future_outlook', {}).get('growth_potential', {}).get('growth_score', 50)
        ]
        
        ax.barh(metrics, scores, color='lightblue', alpha=0.7)
        ax.set_title("市场地位评估")
        ax.set_xlabel("评分 (0-100)")
        
        # 6. 投资评分
        ax = axes[1, 2]
        
        # 计算投资相关评分
        investment_metrics = ['增长性', '稳定性', '安全性', '市场地位', '综合评分']
        
        growth_score = min(100, abs(growth_analysis.get('growth_rates', {}).get('monthly_avg', 0)) * 2)
        stability_score = analysis.get('stability_analysis', {}).get('stability_score', 50)
        safety_score = 100 - risk_assessment.get('overall_risk_score', 50)
        market_score = scores[0]  # 使用TVL排名评分
        overall_score = (growth_score + stability_score + safety_score + market_score) / 4
        
        investment_scores = [growth_score, stability_score, safety_score, market_score, overall_score]
        
        colors = ['red' if score < 40 else 'yellow' if score < 70 else 'green' for score in investment_scores]
        bars = ax.bar(investment_metrics, investment_scores, color=colors, alpha=0.7)
        ax.set_title("投资评分")
        ax.set_ylabel("评分 (0-100)")
        ax.tick_params(axis='x', rotation=45)
        
        # 添加评分标签
        for bar, score in zip(bars, investment_scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{score:.0f}', ha='center', va='bottom')
        
        plt.suptitle(f"{protocol_name} 协议分析报告", fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
```

## 数据处理和可视化示例

### 1. 单个协议深度分析

```python
# 初始化分析器
analyzer = ProtocolsAnalyzer(api_key="YOUR_API_KEY")

# 分析Uniswap V3协议
uniswap_analysis = analyzer.get_protocol_tvl('uniswap-v3', 'ethereum', days=60)

print("Uniswap V3 协议分析:")
print(f"当前TVL: ${uniswap_analysis['current_metrics']['current_tvl']:,.2f}")
print(f"协议规模: {uniswap_analysis['current_metrics']['size_category']}")
print(f"市场排名区间: {uniswap_analysis['current_metrics']['tvl_rank_indicator']}")
print(f"增长阶段: {uniswap_analysis['growth_analysis']['growth_phase']}")
print(f"风险等级: {uniswap_analysis['risk_assessment']['risk_level']}")

# 可视化分析
analyzer.visualize_protocol_analysis(uniswap_analysis, 'uniswap_v3_analysis.png')

# 详细投资论点
investment_thesis = uniswap_analysis['future_outlook']['investment_thesis']
print(f"\n投资建议: {investment_thesis['investment_recommendation']}")
print("看涨论点:")
for point in investment_thesis['bull_case']:
    print(f"  + {point}")
print("看跌论点:")
for point in investment_thesis['bear_case']:
    print(f"  - {point}")
```

### 2. 协议对比分析

```python
def comprehensive_protocol_comparison(protocols=['uniswap-v3', 'aave-v2', 'curve'], chain='ethereum'):
    """综合协议对比分析"""
    
    comparison = analyzer.compare_protocols(protocols, chain)
    
    print(f"{chain.title()} 链上协议对比分析:")
    print("="*60)
    
    # 显示排名信息
    rankings = comparison['ranking']
    
    print("TVL排名:")
    for i, item in enumerate(rankings['by_tvl'], 1):
        print(f"  {i}. {item['protocol']}: ${item['tvl']:,.0f}")
    
    print("\n增长率排名:")
    for i, item in enumerate(rankings['by_growth'], 1):
        print(f"  {i}. {item['protocol']}: {item['growth_rate']:+.2f}%/月")
    
    print("\n稳定性排名:")
    for i, item in enumerate(rankings['by_stability'], 1):
        print(f"  {i}. {item['protocol']}: {item['stability_score']:.1f}/100")
    
    print("\n风险调整收益排名:")
    for i, item in enumerate(rankings['by_risk_adjusted_return'], 1):
        print(f"  {i}. {item['protocol']}: {item['risk_adjusted_return']:.2f}")
    
    # 投资潜力排名
    investment_ranking = comparison['investment_ranking']
    print("\n投资潜力排名:")
    for i, item in enumerate(investment_ranking, 1):
        print(f"  {i}. {item['protocol']}: {item['investment_score']:.1f}/100 ({item['recommendation']})")
    
    # 可视化对比
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # TVL对比
    protocols_names = [item['protocol'] for item in rankings['by_tvl']]
    tvl_values = [item['tvl']/1e9 for item in rankings['by_tvl']]  # 转为十亿美元
    
    ax1.bar(protocols_names, tvl_values, color='lightblue', alpha=0.7)
    ax1.set_title("TVL对比 (十亿美元)")
    ax1.set_ylabel("TVL (B$)")
    ax1.tick_params(axis='x', rotation=45)
    
    # 增长率对比
    growth_protocols = [item['protocol'] for item in rankings['by_growth']]
    growth_rates = [item['growth_rate'] for item in rankings['by_growth']]
    colors = ['green' if rate > 0 else 'red' for rate in growth_rates]
    
    ax2.bar(growth_protocols, growth_rates, color=colors, alpha=0.7)
    ax2.set_title("月增长率对比")
    ax2.set_ylabel("增长率 (%)")
    ax2.tick_params(axis='x', rotation=45)
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # 风险-收益散点图
    risk_scores = []
    return_scores = []
    protocol_labels = []
    
    for protocol in protocols:
        data = comparison['comparison_data'].get(protocol, {})
        if data:
            risk = data.get('risk_assessment', {}).get('overall_risk_score', 50)
            growth = data.get('growth_analysis', {}).get('growth_rates', {}).get('monthly_avg', 0)
            
            risk_scores.append(risk)
            return_scores.append(growth)
            protocol_labels.append(protocol)
    
    ax3.scatter(risk_scores, return_scores, s=100, alpha=0.7)
    for i, label in enumerate(protocol_labels):
        ax3.annotate(label, (risk_scores[i], return_scores[i]), 
                    xytext=(5, 5), textcoords='offset points')
    
    ax3.set_xlabel("风险评分")
    ax3.set_ylabel("月增长率 (%)")
    ax3.set_title("风险-收益关系")
    ax3.grid(True, alpha=0.3)
    
    # 综合评分雷达图
    if len(protocols) <= 3:  # 限制显示数量以保持清晰
        categories = ['TVL规模', '增长性', '稳定性', '安全性']
        
        for protocol in protocols:
            data = comparison['comparison_data'].get(protocol, {})
            if data:
                tvl_score = min(100, data.get('current_metrics', {}).get('current_tvl', 0) / 1e9 * 10)
                growth_score = min(100, abs(data.get('growth_analysis', {}).get('growth_rates', {}).get('monthly_avg', 0)) * 2)
                stability_score = data.get('stability_analysis', {}).get('stability_score', 50)
                safety_score = 100 - data.get('risk_assessment', {}).get('overall_risk_score', 50)
                
                values = [tvl_score, growth_score, stability_score, safety_score]
                
                angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)
                values += values[:1]
                angles = np.concatenate((angles, [angles[0]]))
                
                ax4.plot(angles, values, 'o-', linewidth=2, label=protocol)
                ax4.fill(angles, values, alpha=0.1)
        
        ax4.set_xticks(angles[:-1])
        ax4.set_xticklabels(categories)
        ax4.set_title("综合能力雷达图")
        ax4.legend()
        ax4.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    return comparison

# 执行协议对比
comparison_result = comprehensive_protocol_comparison(['uniswap-v3', 'aave-v2', 'curve'])
```

### 3. 协议生态分析

```python
def analyze_protocol_ecosystem(chain='ethereum', category='defi'):
    """分析协议生态系统"""
    
    # 获取协议排名
    rankings = analyzer.get_protocol_rankings(chain, category, limit=50)
    
    if not rankings:
        print("无法获取协议排名数据")
        return
    
    print(f"{chain.title()} {category.upper()} 生态系统分析:")
    print("="*50)
    
    # 市场集中度分析
    concentration = rankings['market_concentration']
    print(f"总TVL: ${concentration['total_tvl']/1e9:.1f}B")
    print(f"前3大协议份额: {concentration['top_3_share']:.1f}%")
    print(f"前5大协议份额: {concentration['top_5_share']:.1f}%")
    print(f"前10大协议份额: {concentration['top_10_share']:.1f}%")
    print(f"市场集中度: {concentration['concentration_level']}")
    
    # 顶级表现者
    print(f"\n顶级协议 (按TVL):")
    top_performers = rankings['top_performers']
    for performer in top_performers:
        print(f"  {performer['rank']}. {performer['name']}: ${performer['tvl']/1e9:.2f}B ({performer['market_share']:.1f}%)")
    
    # 增长领导者
    growth_leaders = rankings['growth_leaders']
    if growth_leaders:
        print(f"\n增长领导者:")
        for leader in growth_leaders:
            print(f"  {leader['name']}: {leader['growth_30d']:+.1f}% (30天)")
    
    # 市场洞察
    print(f"\n市场洞察:")
    for insight in rankings['market_insights']:
        print(f"  • {insight}")
    
    # 可视化生态系统
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. TVL分布（前20名）
    protocol_data = rankings['rankings'][:20]
    names = [p.get('name', f'Protocol {i}') for i, p in enumerate(protocol_data)]
    tvls = [p.get('tvl', 0)/1e9 for p in protocol_data]
    
    ax1.barh(names, tvls, color='lightblue', alpha=0.7)
    ax1.set_title("前20大协议TVL分布")
    ax1.set_xlabel("TVL (十亿美元)")
    ax1.invert_yaxis()
    
    # 2. 市场份额饼图（前10名）
    top10_names = names[:10]
    top10_tvls = tvls[:10]
    other_tvl = sum(tvls[10:])
    
    if other_tvl > 0:
        pie_names = top10_names + ['其他']
        pie_values = top10_tvls + [other_tvl]
    else:
        pie_names = top10_names
        pie_values = top10_tvls
    
    ax2.pie(pie_values, labels=pie_names, autopct='%1.1f%%', startangle=90)
    ax2.set_title("市场份额分布")
    
    # 3. 协议规模分布
    size_categories = {'巨型(>10B)': 0, '大型(1-10B)': 0, '中型(100M-1B)': 0, '小型(<100M)': 0}
    
    for tvl in [p.get('tvl', 0) for p in protocol_data]:
        if tvl > 10e9:
            size_categories['巨型(>10B)'] += 1
        elif tvl > 1e9:
            size_categories['大型(1-10B)'] += 1
        elif tvl > 100e6:
            size_categories['中型(100M-1B)'] += 1
        else:
            size_categories['小型(<100M)'] += 1
    
    ax3.bar(size_categories.keys(), size_categories.values(), color='lightgreen', alpha=0.7)
    ax3.set_title("协议规模分布")
    ax3.set_ylabel("协议数量")
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. 集中度指标
    concentration_metrics = ['前3大份额', '前5大份额', '前10大份额']
    concentration_values = [
        concentration['top_3_share'],
        concentration['top_5_share'],
        concentration['top_10_share']
    ]
    
    bars = ax4.bar(concentration_metrics, concentration_values, color='orange', alpha=0.7)
    ax4.set_title("市场集中度指标")
    ax4.set_ylabel("市场份额 (%)")
    
    # 添加集中度阈值线
    ax4.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='高集中度阈值')
    ax4.axhline(y=30, color='yellow', linestyle='--', alpha=0.5, label='中等集中度阈值')
    ax4.legend()
    
    # 添加数值标签
    for bar, value in zip(bars, concentration_values):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value:.1f}%', ha='center', va='bottom')
    
    plt.suptitle(f"{chain.title()} {category.upper()} 生态系统分析", fontsize=16)
    plt.tight_layout()
    plt.show()
    
    return rankings

# 分析以太坊DeFi生态
eth_defi_ecosystem = analyze_protocol_ecosystem('ethereum', 'defi')

# 分析Polygon生态
# polygon_ecosystem = analyze_protocol_ecosystem('polygon', 'defi')
```

## 交易策略和市场分析

### 1. 协议投资策略

```python
class ProtocolInvestmentStrategy:
    """协议投资策略"""
    
    def __init__(self, analyzer: ProtocolsAnalyzer):
        self.analyzer = analyzer
        
    def generate_portfolio_recommendations(self, investment_amount: float = 100000, 
                                         risk_tolerance: str = 'moderate') -> Dict:
        """生成投资组合建议"""
        
        # 分析主要协议
        protocols_to_analyze = ['uniswap-v3', 'aave-v2', 'curve', 'lido', 'compound']
        protocol_analysis = {}
        
        for protocol in protocols_to_analyze:
            analysis = self.analyzer.get_protocol_tvl(protocol, 'ethereum')
            if analysis:
                protocol_analysis[protocol] = analysis
        
        # 生成投资组合
        portfolio = {
            'total_investment': investment_amount,
            'risk_tolerance': risk_tolerance,
            'recommended_allocation': {},
            'rationale': {},
            'risk_assessment': {},
            'rebalancing_schedule': 'monthly'
        }
        
        # 计算投资评分
        investment_scores = {}
        for protocol, analysis in protocol_analysis.items():
            score = self.calculate_investment_score(analysis, risk_tolerance)
            investment_scores[protocol] = score
        
        # 根据风险偏好调整配置
        allocation = self.calculate_optimal_allocation(investment_scores, risk_tolerance)
        
        for protocol, weight in allocation.items():
            amount = investment_amount * weight
            portfolio['recommended_allocation'][protocol] = {
                'weight': weight * 100,
                'amount': amount,
                'investment_score': investment_scores.get(protocol, 0)
            }
            
            # 添加投资理由
            analysis = protocol_analysis.get(protocol, {})
            portfolio['rationale'][protocol] = self.generate_investment_rationale(analysis)
        
        # 整体风险评估
        portfolio['risk_assessment'] = self.assess_portfolio_risk(protocol_analysis, allocation)
        
        return portfolio
    
    def calculate_investment_score(self, analysis: Dict, risk_tolerance: str) -> float:
        """计算投资评分"""
        
        if not analysis:
            return 0
        
        # 基础评分
        growth_score = min(100, abs(analysis.get('growth_analysis', {}).get('growth_rates', {}).get('monthly_avg', 0)) * 2)
        stability_score = analysis.get('stability_analysis', {}).get('stability_score', 50)
        market_score = {'mega_protocol': 90, 'large_protocol': 80, 'medium_protocol': 60, 'small_protocol': 40, 'micro_protocol': 20}.get(
            analysis.get('current_metrics', {}).get('size_category', 'micro_protocol'), 20)
        risk_score = 100 - analysis.get('risk_assessment', {}).get('overall_risk_score', 50)
        
        # 根据风险偏好调整权重
        if risk_tolerance == 'conservative':
            weights = {'stability': 0.4, 'market': 0.3, 'risk': 0.2, 'growth': 0.1}
        elif risk_tolerance == 'aggressive':
            weights = {'growth': 0.4, 'market': 0.2, 'stability': 0.2, 'risk': 0.2}
        else:  # moderate
            weights = {'growth': 0.3, 'stability': 0.25, 'market': 0.25, 'risk': 0.2}
        
        investment_score = (
            growth_score * weights['growth'] +
            stability_score * weights['stability'] +
            market_score * weights['market'] +
            risk_score * weights['risk']
        )
        
        return investment_score
    
    def calculate_optimal_allocation(self, scores: Dict, risk_tolerance: str) -> Dict:
        """计算最优资产配置"""
        
        if not scores:
            return {}
        
        # 标准化评分
        total_score = sum(scores.values())
        if total_score == 0:
            # 等权重分配
            equal_weight = 1.0 / len(scores)
            return {protocol: equal_weight for protocol in scores.keys()}
        
        # 基于评分的权重分配
        raw_weights = {protocol: score / total_score for protocol, score in scores.items()}
        
        # 根据风险偏好调整集中度
        if risk_tolerance == 'conservative':
            # 更均匀的分配，降低集中度
            adjustment_factor = 0.7
        elif risk_tolerance == 'aggressive':
            # 更集中的分配，突出高分协议
            adjustment_factor = 1.3
        else:  # moderate
            adjustment_factor = 1.0
        
        # 应用调整因子并重新标准化
        adjusted_weights = {}
        for protocol, weight in raw_weights.items():
            adjusted_weights[protocol] = weight ** adjustment_factor
        
        total_adjusted = sum(adjusted_weights.values())
        final_weights = {protocol: weight / total_adjusted 
                        for protocol, weight in adjusted_weights.items()}
        
        # 限制单一协议的最大权重
        max_weight = {'conservative': 0.3, 'moderate': 0.4, 'aggressive': 0.5}[risk_tolerance]
        
        for protocol in final_weights:
            if final_weights[protocol] > max_weight:
                excess = final_weights[protocol] - max_weight
                final_weights[protocol] = max_weight
                
                # 将超额部分分配给其他协议
                remaining_protocols = [p for p in final_weights.keys() if p != protocol]
                for other_protocol in remaining_protocols:
                    final_weights[other_protocol] += excess / len(remaining_protocols)
        
        return final_weights
    
    def generate_investment_rationale(self, analysis: Dict) -> List[str]:
        """生成投资理由"""
        
        if not analysis:
            return ["缺乏分析数据"]
        
        rationale = []
        
        # 基于增长的理由
        growth_phase = analysis.get('growth_analysis', {}).get('growth_phase', '')
        if growth_phase in ['rapid_growth', 'moderate_growth']:
            rationale.append(f"处于{growth_phase}阶段，发展前景良好")
        
        # 基于市场地位的理由
        size_category = analysis.get('current_metrics', {}).get('size_category', '')
        if size_category in ['mega_protocol', 'large_protocol']:
            rationale.append("市场地位稳固，流动性充足")
        
        # 基于稳定性的理由
        stability_score = analysis.get('stability_analysis', {}).get('stability_score', 0)
        if stability_score > 70:
            rationale.append("TVL稳定性高，波动风险较低")
        
        # 基于风险的理由
        risk_level = analysis.get('risk_assessment', {}).get('risk_level', '')
        if risk_level in ['low', 'very_low']:
            rationale.append("整体风险可控，安全性较高")
        
        # 基于未来展望的理由
        investment_thesis = analysis.get('future_outlook', {}).get('investment_thesis', {})
        recommendation = investment_thesis.get('investment_recommendation', '')
        if recommendation in ['bullish', 'neutral']:
            rationale.append("未来发展前景积极")
        
        if not rationale:
            rationale.append("需要进一步分析该协议的投资价值")
        
        return rationale
    
    def assess_portfolio_risk(self, protocol_analysis: Dict, allocation: Dict) -> Dict:
        """评估投资组合风险"""
        
        portfolio_risk = {
            'weighted_risk_score': 0,
            'risk_level': 'medium',
            'diversification_score': 0,
            'correlation_risk': 'medium',
            'major_risks': [],
            'risk_mitigation': []
        }
        
        # 计算加权风险评分
        total_risk = 0
        total_weight = 0
        
        for protocol, weight in allocation.items():
            analysis = protocol_analysis.get(protocol, {})
            risk_score = analysis.get('risk_assessment', {}).get('overall_risk_score', 50)
            
            total_risk += risk_score * weight
            total_weight += weight
        
        if total_weight > 0:
            portfolio_risk['weighted_risk_score'] = total_risk / total_weight
        
        # 风险等级
        if portfolio_risk['weighted_risk_score'] > 70:
            portfolio_risk['risk_level'] = 'high'
        elif portfolio_risk['weighted_risk_score'] > 50:
            portfolio_risk['risk_level'] = 'medium'
        else:
            portfolio_risk['risk_level'] = 'low'
        
        # 多样化评分
        portfolio_risk['diversification_score'] = self.calculate_diversification_score(allocation)
        
        # 主要风险
        if portfolio_risk['diversification_score'] < 50:
            portfolio_risk['major_risks'].append("投资组合集中度过高")
        
        if portfolio_risk['weighted_risk_score'] > 60:
            portfolio_risk['major_risks'].append("整体风险水平较高")
        
        # 风险缓解建议
        portfolio_risk['risk_mitigation'] = [
            "定期监控协议TVL变化",
            "关注智能合约安全性",
            "分散投资不同类型协议",
            "设置适当的止损策略"
        ]
        
        return portfolio_risk
    
    def calculate_diversification_score(self, allocation: Dict) -> float:
        """计算多样化评分"""
        
        if not allocation:
            return 0
        
        # 使用赫芬达尔指数计算集中度
        hhi = sum(weight ** 2 for weight in allocation.values())
        
        # 转换为多样化评分（0-100）
        diversification_score = (1 - hhi) * 100
        
        return diversification_score
    
    def generate_rebalancing_signals(self, current_portfolio: Dict, 
                                   market_conditions: Dict) -> Dict:
        """生成再平衡信号"""
        
        signals = {
            'rebalancing_needed': False,
            'recommendations': [],
            'urgency': 'low',
            'target_adjustments': {}
        }
        
        # 检查权重偏离
        for protocol, allocation in current_portfolio.get('recommended_allocation', {}).items():
            target_weight = allocation['weight']
            current_weight = allocation.get('current_weight', target_weight)  # 假设当前权重
            
            deviation = abs(current_weight - target_weight)
            
            if deviation > 10:  # 偏离超过10%
                signals['rebalancing_needed'] = True
                signals['recommendations'].append(f"{protocol}: 目标{target_weight:.1f}%, 当前{current_weight:.1f}%")
                
                if deviation > 20:
                    signals['urgency'] = 'high'
                elif deviation > 15:
                    signals['urgency'] = 'medium'
        
        # 基于市场条件的调整建议
        if market_conditions.get('market_trend') == 'bearish':
            signals['recommendations'].append("熊市环境，考虑增加稳定协议权重")
        elif market_conditions.get('market_trend') == 'bullish':
            signals['recommendations'].append("牛市环境，可适度增加成长型协议权重")
        
        return signals

# 使用示例
strategy = ProtocolInvestmentStrategy(analyzer)

# 生成投资组合建议
portfolio_recommendation = strategy.generate_portfolio_recommendations(
    investment_amount=100000, 
    risk_tolerance='moderate'
)

print("协议投资组合建议:")
print(f"总投资金额: ${portfolio_recommendation['total_investment']:,.2f}")
print(f"风险偏好: {portfolio_recommendation['risk_tolerance']}")
print(f"再平衡频率: {portfolio_recommendation['rebalancing_schedule']}")

print("\n推荐配置:")
for protocol, allocation in portfolio_recommendation['recommended_allocation'].items():
    print(f"  {protocol}:")
    print(f"    权重: {allocation['weight']:.1f}%")
    print(f"    金额: ${allocation['amount']:,.2f}")
    print(f"    评分: {allocation['investment_score']:.1f}/100")

print("\n投资理由:")
for protocol, reasons in portfolio_recommendation['rationale'].items():
    print(f"  {protocol}:")
    for reason in reasons:
        print(f"    • {reason}")

# 风险评估
risk_assessment = portfolio_recommendation['risk_assessment']
print(f"\n风险评估:")
print(f"  加权风险评分: {risk_assessment['weighted_risk_score']:.1f}/100")
print(f"  风险等级: {risk_assessment['risk_level']}")
print(f"  多样化评分: {risk_assessment['diversification_score']:.1f}/100")
```

### 2. 协议事件驱动策略

```python
class ProtocolEventStrategy:
    """协议事件驱动策略"""
    
    def __init__(self, analyzer: ProtocolsAnalyzer):
        self.analyzer = analyzer
        
    def monitor_protocol_events(self, protocols: List[str]) -> Dict:
        """监控协议事件"""
        
        event_monitoring = {
            'protocols': protocols,
            'detected_events': {},
            'trading_signals': {},
            'alert_level': 'normal'
        }
        
        for protocol in protocols:
            analysis = self.analyzer.get_protocol_tvl(protocol, 'ethereum')
            if analysis:
                events = self.detect_events(analysis, protocol)
                event_monitoring['detected_events'][protocol] = events
                
                signals = self.generate_event_signals(events, analysis)
                event_monitoring['trading_signals'][protocol] = signals
        
        # 确定整体警报级别
        all_signals = [signals for signals in event_monitoring['trading_signals'].values()]
        event_monitoring['alert_level'] = self.determine_alert_level(all_signals)
        
        return event_monitoring
    
    def detect_events(self, analysis: Dict, protocol: str) -> List[Dict]:
        """检测协议事件"""
        
        events = []
        
        if not analysis:
            return events
        
        current_metrics = analysis.get('current_metrics', {})
        growth_analysis = analysis.get('growth_analysis', {})
        risk_assessment = analysis.get('risk_assessment', {})
        
        # TVL异常变化事件
        tvl_change_7d = current_metrics.get('tvl_change_7d', 0)
        if abs(tvl_change_7d) > 30:  # 7天变化超过30%
            events.append({
                'type': 'tvl_anomaly',
                'severity': 'high' if abs(tvl_change_7d) > 50 else 'medium',
                'description': f"TVL 7天变化{tvl_change_7d:+.1f}%",
                'impact': 'negative' if tvl_change_7d < -20 else 'positive'
            })
        
        # 增长阶段变化事件
        growth_phase = growth_analysis.get('growth_phase', '')
        if growth_phase in ['rapid_decline', 'decline']:
            events.append({
                'type': 'growth_deterioration',
                'severity': 'high' if growth_phase == 'rapid_decline' else 'medium',
                'description': f"协议进入{growth_phase}阶段",
                'impact': 'negative'
            })
        elif growth_phase in ['rapid_growth']:
            events.append({
                'type': 'growth_acceleration',
                'severity': 'medium',
                'description': f"协议进入{growth_phase}阶段",
                'impact': 'positive'
            })
        
        # 风险水平变化事件
        risk_level = risk_assessment.get('risk_level', 'medium')
        if risk_level in ['very_high', 'high']:
            events.append({
                'type': 'risk_elevation',
                'severity': 'high' if risk_level == 'very_high' else 'medium',
                'description': f"风险等级上升至{risk_level}",
                'impact': 'negative'
            })
        
        # 代币构成变化事件
        token_composition = analysis.get('token_composition', {})
        concentration_risk = token_composition.get('concentration_risk', 'unknown')
        if concentration_risk == 'high':
            events.append({
                'type': 'concentration_risk',
                'severity': 'medium',
                'description': "代币构成集中度过高",
                'impact': 'negative'
            })
        
        return events
    
    def generate_event_signals(self, events: List[Dict], analysis: Dict) -> Dict:
        """生成事件信号"""
        
        signals = {
            'overall_signal': 'hold',
            'confidence': 'medium',
            'specific_actions': [],
            'time_horizon': 'short_term',
            'position_adjustment': 0  # -1到1，负数减仓，正数加仓
        }
        
        if not events:
            return signals
        
        # 统计事件影响
        positive_impact = sum(1 for event in events if event['impact'] == 'positive')
        negative_impact = sum(1 for event in events if event['impact'] == 'negative')
        high_severity = sum(1 for event in events if event['severity'] == 'high')
        
        # 生成总体信号
        if negative_impact > positive_impact and high_severity > 0:
            signals['overall_signal'] = 'sell'
            signals['position_adjustment'] = -0.5
            signals['specific_actions'].append("考虑减持或清仓")
        elif positive_impact > negative_impact:
            signals['overall_signal'] = 'buy'
            signals['position_adjustment'] = 0.3
            signals['specific_actions'].append("考虑增持")
        elif high_severity > 0:
            signals['overall_signal'] = 'hold_cautious'
            signals['position_adjustment'] = -0.2
            signals['specific_actions'].append("谨慎持有，密切监控")
        
        # 具体行动建议
        for event in events:
            if event['type'] == 'tvl_anomaly' and event['impact'] == 'negative':
                signals['specific_actions'].append("设置紧急止损")
            elif event['type'] == 'growth_acceleration':
                signals['specific_actions'].append("关注后续增长可持续性")
            elif event['type'] == 'risk_elevation':
                signals['specific_actions'].append("评估风险承受能力")
        
        # 置信度评估
        if high_severity >= 2:
            signals['confidence'] = 'high'
        elif len(events) >= 3:
            signals['confidence'] = 'medium'
        else:
            signals['confidence'] = 'low'
        
        return signals
    
    def determine_alert_level(self, all_signals: List[Dict]) -> str:
        """确定警报级别"""
        
        high_risk_signals = sum(1 for signals in all_signals 
                               if signals.get('overall_signal') in ['sell', 'hold_cautious'])
        
        total_signals = len(all_signals)
        
        if total_signals == 0:
            return 'normal'
        
        risk_ratio = high_risk_signals / total_signals
        
        if risk_ratio > 0.7:
            return 'high'
        elif risk_ratio > 0.4:
            return 'medium'
        else:
            return 'normal'
    
    def create_event_dashboard(self, monitoring_result: Dict) -> None:
        """创建事件监控仪表板"""
        
        protocols = monitoring_result['protocols']
        detected_events = monitoring_result['detected_events']
        trading_signals = monitoring_result['trading_signals']
        alert_level = monitoring_result['alert_level']
        
        print("协议事件监控仪表板")
        print("="*50)
        print(f"警报级别: {alert_level.upper()}")
        print(f"监控协议数量: {len(protocols)}")
        
        total_events = sum(len(events) for events in detected_events.values())
        print(f"检测到的事件总数: {total_events}")
        
        print("\n详细事件:")
        for protocol, events in detected_events.items():
            if events:
                print(f"\n{protocol.upper()}:")
                for event in events:
                    severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(event['severity'], "⚪")
                    impact_icon = {"positive": "📈", "negative": "📉", "neutral": "➡️"}.get(event['impact'], "")
                    print(f"  {severity_icon} {impact_icon} {event['description']} ({event['type']})")
                
                # 交易信号
                signal = trading_signals.get(protocol, {})
                signal_icon = {"buy": "🟢", "sell": "🔴", "hold": "🟡", "hold_cautious": "🟠"}.get(signal.get('overall_signal'), "")
                print(f"  📊 交易信号: {signal_icon} {signal.get('overall_signal', 'unknown')} (置信度: {signal.get('confidence', 'unknown')})")
                
                if signal.get('specific_actions'):
                    print(f"  💡 建议行动:")
                    for action in signal['specific_actions']:
                        print(f"     • {action}")
        
        # 没有事件的协议
        protocols_without_events = [p for p in protocols if not detected_events.get(p)]
        if protocols_without_events:
            print(f"\n✅ 无异常事件的协议: {', '.join(protocols_without_events)}")

# 使用示例
event_strategy = ProtocolEventStrategy(analyzer)

# 监控关键协议
monitored_protocols = ['uniswap-v3', 'aave-v2', 'curve', 'lido', 'compound']
monitoring_result = event_strategy.monitor_protocol_events(monitored_protocols)

# 显示监控仪表板
event_strategy.create_event_dashboard(monitoring_result)

# 根据信号执行交易决策
print(f"\n📋 交易决策摘要:")
for protocol, signals in monitoring_result['trading_signals'].items():
    overall_signal = signals.get('overall_signal', 'hold')
    position_adjustment = signals.get('position_adjustment', 0)
    
    if overall_signal != 'hold':
        action = "增持" if position_adjustment > 0 else "减持"
        print(f"  {protocol}: {action} {abs(position_adjustment)*100:.0f}% ({overall_signal})")
```

## 常见问题

### Q1: 协议TVL数据的可靠性如何？

协议TVL数据的可靠性考虑：
- **数据来源**: 直接从区块链获取，确保准确性
- **计算方法**: 实时计算锁定资产的美元价值
- **价格更新**: 使用多个价格源的聚合数据
- **异常处理**: 自动识别和过滤异常数据

### Q2: 如何比较不同链上的协议？

跨链协议比较要点：
- **TVL标准化**: 统一使用美元计价
- **Gas费用考虑**: 不同链的使用成本差异
- **安全性评估**: 各链的安全性和成熟度
- **生态系统**: 开发者活跃度和用户基础

### Q3: 协议风险如何评估？

协议风险评估维度：
- **智能合约风险**: 代码审计、漏洞历史
- **流动性风险**: TVL稳定性、提取能力
- **治理风险**: 去中心化程度、治理攻击风险
- **市场风险**: 代币价格波动、相关性风险

### Q4: 如何识别协议投资机会？

投资机会识别方法：
- **基本面分析**: TVL增长、用户增长、收入增长
- **技术分析**: 代币价格趋势、技术指标
- **相对估值**: 与同类协议的估值比较
- **催化剂识别**: 技术升级、合作伙伴、新产品

## 最佳实践

1. **多维度评估**: 结合TVL、用户数、收入等多个指标
2. **风险管理**: 分散投资不同类型和链上的协议
3. **持续监控**: 定期跟踪协议发展和市场变化
4. **事件驱动**: 关注技术升级、治理变化等重要事件
5. **相对分析**: 与同类协议和整体市场进行比较
6. **长期视角**: 关注协议的长期发展潜力和可持续性

---

*本文档详细介绍了 Glassnode Protocols API 的使用方法，包括数据获取、分析技术和实际应用案例。协议数据是理解DeFi生态系统和制定协议投资策略的重要工具。*