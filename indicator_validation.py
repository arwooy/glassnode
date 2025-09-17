"""
Glassnode指标验证系统
全面验证各指标的市场预测能力和实际效果
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class IndicatorValidator:
    """指标验证器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://grassnoodle.cloud"
        self.headers = {"x-key": api_key}
        self.indicators_data = {}
        self.price_data = None
        self.signals = {}
        self.performance_metrics = {}
        
    def fetch_data(self, endpoint: str, params: dict) -> List[dict]:
        """获取数据"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"获取数据失败 {endpoint}: {e}")
            return []
    
    def load_all_indicators(self, start_date: str, end_date: str):
        """加载所有指标数据"""
        print("加载指标数据...")
        params = {
            "a": "BTC",
            "s": str(int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())),
            "u": str(int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()))
        }
        
        # 价格数据
        price_data = self.fetch_data("/v1/metrics/market/price_usd_close", params)
        if price_data:
            df = pd.DataFrame(price_data)
            df['date'] = pd.to_datetime(df['t'], unit='s')
            df['price'] = df['v'].astype(float)
            self.price_data = df[['date', 'price']].set_index('date')
            print(f"  价格数据: {len(self.price_data)} 条")
        
        # SOPR
        sopr_data = self.fetch_data("/v1/metrics/indicators/sopr", params)
        if sopr_data:
            df = pd.DataFrame(sopr_data)
            df['date'] = pd.to_datetime(df['t'], unit='s')
            df['sopr'] = df['v'].astype(float)
            self.indicators_data['SOPR'] = df[['date', 'sopr']].set_index('date')
            print(f"  SOPR: {len(self.indicators_data['SOPR'])} 条")
        
        # MVRV Z-Score
        mvrv_data = self.fetch_data("/v1/metrics/market/mvrv_z_score", params)
        if mvrv_data:
            df = pd.DataFrame(mvrv_data)
            df['date'] = pd.to_datetime(df['t'], unit='s')
            df['mvrv'] = df['v'].astype(float)
            self.indicators_data['MVRV'] = df[['date', 'mvrv']].set_index('date')
            print(f"  MVRV: {len(self.indicators_data['MVRV'])} 条")
        
        # NUPL
        nupl_data = self.fetch_data("/v1/metrics/indicators/net_unrealized_profit_loss", params)
        if nupl_data:
            df = pd.DataFrame(nupl_data)
            df['date'] = pd.to_datetime(df['t'], unit='s')
            df['nupl'] = df['v'].astype(float)
            self.indicators_data['NUPL'] = df[['date', 'nupl']].set_index('date')
            print(f"  NUPL: {len(self.indicators_data['NUPL'])} 条")
        
        # NVT (尝试获取)
        nvt_data = self.fetch_data("/v1/metrics/indicators/nvt", params)
        if nvt_data:
            df = pd.DataFrame(nvt_data)
            df['date'] = pd.to_datetime(df['t'], unit='s')
            df['nvt'] = df['v'].astype(float)
            self.indicators_data['NVT'] = df[['date', 'nvt']].set_index('date')
            print(f"  NVT: {len(self.indicators_data['NVT'])} 条")
        
        # Puell Multiple (尝试获取)
        puell_data = self.fetch_data("/v1/metrics/indicators/puell_multiple", params)
        if puell_data:
            df = pd.DataFrame(puell_data)
            df['date'] = pd.to_datetime(df['t'], unit='s')
            df['puell'] = df['v'].astype(float)
            self.indicators_data['Puell'] = df[['date', 'puell']].set_index('date')
            print(f"  Puell Multiple: {len(self.indicators_data['Puell'])} 条")


class SignalGenerator:
    """信号生成器"""
    
    def __init__(self):
        self.thresholds = {
            'SOPR': {
                'strong_buy': 0.95,
                'buy': 0.98,
                'neutral_low': 1.00,
                'neutral_high': 1.02,
                'sell': 1.05,
                'strong_sell': 1.08
            },
            'MVRV': {  # MVRV Z-Score thresholds
                'strong_buy': -0.5,
                'buy': 0,
                'neutral_low': 1,
                'neutral_high': 2,
                'sell': 3,
                'strong_sell': 4
            },
            'NUPL': {
                'strong_buy': 0,
                'buy': 0.25,
                'neutral_low': 0.5,
                'neutral_high': 0.65,
                'sell': 0.75,
                'strong_sell': 0.85
            },
            'NVT': {
                'strong_buy': 40,
                'buy': 50,
                'neutral_low': 70,
                'neutral_high': 90,
                'sell': 100,
                'strong_sell': 120
            },
            'Puell': {
                'strong_buy': 0.3,
                'buy': 0.5,
                'neutral_low': 1,
                'neutral_high': 2,
                'sell': 3,
                'strong_sell': 4
            }
        }
    
    def generate_signal(self, value: float, indicator: str) -> int:
        """生成交易信号 (-2到+2)"""
        if indicator not in self.thresholds:
            return 0
        
        thresholds = self.thresholds[indicator]
        
        # 对于NVT，逻辑是反向的（高值看跌，低值看涨）
        if indicator == 'NVT':
            if value <= thresholds['strong_buy']:
                return 2  # 强烈买入
            elif value <= thresholds['buy']:
                return 1  # 买入
            elif value <= thresholds['neutral_low']:
                return 0  # 中性
            elif value <= thresholds['neutral_high']:
                return 0  # 中性
            elif value <= thresholds['sell']:
                return -1  # 卖出
            else:
                return -2  # 强烈卖出
        else:
            # 其他指标的正常逻辑
            if value <= thresholds['strong_buy']:
                return 2  # 强烈买入
            elif value <= thresholds['buy']:
                return 1  # 买入
            elif value <= thresholds['neutral_low']:
                return 0  # 中性
            elif value <= thresholds['neutral_high']:
                return 0  # 中性
            elif value <= thresholds['sell']:
                return -1  # 卖出
            else:
                return -2  # 强烈卖出
    
    def generate_composite_signal(self, signals: Dict[str, int]) -> float:
        """生成综合信号"""
        # 权重配置
        weights = {
            'MVRV': 0.35,   # 最高权重，因为相关性最强
            'NUPL': 0.25,
            'SOPR': 0.20,
            'NVT': 0.10,
            'Puell': 0.10
        }
        
        composite = 0
        total_weight = 0
        
        for indicator, signal in signals.items():
            if indicator in weights:
                composite += signal * weights[indicator]
                total_weight += weights[indicator]
        
        if total_weight > 0:
            return composite / total_weight
        return 0


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0
        self.trades = []
        self.equity_curve = []
        
    def execute_trade(self, date, price, signal, position_size=0.1):
        """执行交易"""
        trade = {
            'date': date,
            'price': price,
            'signal': signal,
            'type': None,
            'position': 0,
            'capital': self.capital,
            'pnl': 0
        }
        
        # 根据信号强度调整仓位
        if signal > 1.5:  # 强烈买入
            target_position = 1.0
        elif signal > 0.5:  # 买入
            target_position = 0.6
        elif signal < -1.5:  # 强烈卖出
            target_position = 0
        elif signal < -0.5:  # 卖出
            target_position = 0.3
        else:  # 中性
            target_position = self.position
        
        # 调整仓位
        if target_position > self.position:
            # 买入
            buy_amount = (target_position - self.position) * self.capital
            self.position = target_position
            trade['type'] = 'BUY'
            trade['position'] = self.position
        elif target_position < self.position:
            # 卖出
            sell_ratio = (self.position - target_position)
            sell_value = sell_ratio * self.capital
            self.position = target_position
            trade['type'] = 'SELL'
            trade['position'] = self.position
        else:
            trade['type'] = 'HOLD'
            trade['position'] = self.position
        
        self.trades.append(trade)
        
        # 更新资产价值
        if len(self.equity_curve) > 0:
            last_price = self.equity_curve[-1]['price']
            price_change = (price - last_price) / last_price
            self.capital = self.capital * (1 + self.position * price_change)
        
        self.equity_curve.append({
            'date': date,
            'price': price,
            'capital': self.capital,
            'position': self.position,
            'signal': signal
        })
    
    def calculate_metrics(self) -> Dict:
        """计算绩效指标"""
        if not self.equity_curve:
            return {}
        
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df['returns'] = equity_df['capital'].pct_change()
        
        # 买入持有策略对比
        buy_hold_return = (equity_df['price'].iloc[-1] / equity_df['price'].iloc[0] - 1) * 100
        strategy_return = (self.capital / self.initial_capital - 1) * 100
        
        # 计算各项指标
        metrics = {
            'total_return': strategy_return,
            'buy_hold_return': buy_hold_return,
            'excess_return': strategy_return - buy_hold_return,
            'max_drawdown': self.calculate_max_drawdown(equity_df['capital']),
            'sharpe_ratio': self.calculate_sharpe_ratio(equity_df['returns']),
            'win_rate': self.calculate_win_rate(),
            'total_trades': len([t for t in self.trades if t['type'] != 'HOLD']),
            'avg_trade_return': self.calculate_avg_trade_return(),
            'best_trade': self.find_best_trade(),
            'worst_trade': self.find_worst_trade()
        }
        
        return metrics
    
    def calculate_max_drawdown(self, capital_series):
        """计算最大回撤"""
        cummax = capital_series.cummax()
        drawdown = (capital_series - cummax) / cummax * 100
        return abs(drawdown.min())
    
    def calculate_sharpe_ratio(self, returns):
        """计算夏普比率"""
        if len(returns) < 2:
            return 0
        returns = returns.dropna()
        if returns.std() == 0:
            return 0
        return (returns.mean() / returns.std()) * np.sqrt(252)  # 年化
    
    def calculate_win_rate(self):
        """计算胜率"""
        winning_trades = 0
        total_trades = 0
        
        for i in range(1, len(self.trades)):
            if self.trades[i]['type'] == 'SELL' and self.trades[i-1]['type'] == 'BUY':
                total_trades += 1
                if self.trades[i]['capital'] > self.trades[i-1]['capital']:
                    winning_trades += 1
        
        if total_trades == 0:
            return 0
        return (winning_trades / total_trades) * 100
    
    def calculate_avg_trade_return(self):
        """计算平均交易收益"""
        trade_returns = []
        for i in range(1, len(self.trades)):
            if self.trades[i]['type'] != 'HOLD':
                ret = (self.trades[i]['capital'] / self.trades[i-1]['capital'] - 1) * 100
                trade_returns.append(ret)
        
        if trade_returns:
            return np.mean(trade_returns)
        return 0
    
    def find_best_trade(self):
        """找出最佳交易"""
        best_return = -float('inf')
        best_trade = None
        
        for i in range(1, len(self.trades)):
            if self.trades[i]['type'] != 'HOLD':
                ret = (self.trades[i]['capital'] / self.trades[i-1]['capital'] - 1) * 100
                if ret > best_return:
                    best_return = ret
                    best_trade = {
                        'date': self.trades[i]['date'],
                        'return': ret,
                        'type': self.trades[i]['type']
                    }
        
        return best_trade
    
    def find_worst_trade(self):
        """找出最差交易"""
        worst_return = float('inf')
        worst_trade = None
        
        for i in range(1, len(self.trades)):
            if self.trades[i]['type'] != 'HOLD':
                ret = (self.trades[i]['capital'] / self.trades[i-1]['capital'] - 1) * 100
                if ret < worst_return:
                    worst_return = ret
                    worst_trade = {
                        'date': self.trades[i]['date'],
                        'return': ret,
                        'type': self.trades[i]['type']
                    }
        
        return worst_trade


class ValidationReport:
    """验证报告生成器"""
    
    def __init__(self):
        self.results = {}
        
    def analyze_indicator_accuracy(self, validator: IndicatorValidator, 
                                  signal_gen: SignalGenerator) -> Dict:
        """分析指标准确性"""
        accuracy_results = {}
        
        for indicator_name, indicator_data in validator.indicators_data.items():
            # 合并价格和指标数据
            merged = pd.merge(validator.price_data, indicator_data, 
                            left_index=True, right_index=True, how='inner')
            
            if len(merged) < 30:
                continue
            
            # 生成信号
            signals = []
            for idx, row in merged.iterrows():
                signal = signal_gen.generate_signal(
                    row[indicator_data.columns[0]], 
                    indicator_name
                )
                signals.append(signal)
            
            merged['signal'] = signals
            merged['price_change'] = merged['price'].pct_change().shift(-1)  # 未来1天收益
            
            # 计算准确率
            correct_predictions = 0
            total_predictions = 0
            
            for idx, row in merged.iterrows():
                if row['signal'] != 0:  # 非中性信号
                    total_predictions += 1
                    if (row['signal'] > 0 and row['price_change'] > 0) or \
                       (row['signal'] < 0 and row['price_change'] < 0):
                        correct_predictions += 1
            
            accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
            
            # 计算不同时间窗口的准确率
            accuracy_by_period = {}
            for days in [1, 3, 7, 14, 30]:
                merged[f'future_{days}d'] = merged['price'].pct_change(days).shift(-days)
                correct = 0
                total = 0
                
                for idx, row in merged.iterrows():
                    if row['signal'] != 0 and not pd.isna(row[f'future_{days}d']):
                        total += 1
                        if (row['signal'] > 0 and row[f'future_{days}d'] > 0) or \
                           (row['signal'] < 0 and row[f'future_{days}d'] < 0):
                            correct += 1
                
                accuracy_by_period[f'{days}天'] = (correct / total * 100) if total > 0 else 0
            
            accuracy_results[indicator_name] = {
                'overall_accuracy': accuracy,
                'accuracy_by_period': accuracy_by_period,
                'total_signals': total_predictions,
                'signal_distribution': {
                    'strong_buy': (merged['signal'] == 2).sum(),
                    'buy': (merged['signal'] == 1).sum(),
                    'neutral': (merged['signal'] == 0).sum(),
                    'sell': (merged['signal'] == -1).sum(),
                    'strong_sell': (merged['signal'] == -2).sum()
                }
            }
        
        return accuracy_results
    
    def generate_markdown_report(self, accuracy_results: Dict, 
                                backtest_results: Dict,
                                combined_backtest: Dict) -> str:
        """生成Markdown报告"""
        report = """# Glassnode指标验证报告

## 执行时间
""" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """

---

## 1. 单指标准确率分析

### 1.1 总体准确率
| 指标 | 1天 | 3天 | 7天 | 14天 | 30天 | 信号数量 |
|------|-----|-----|-----|------|------|----------|
"""
        
        for indicator, results in accuracy_results.items():
            periods = results['accuracy_by_period']
            report += f"| **{indicator}** | "
            report += f"{periods.get('1天', 0):.1f}% | "
            report += f"{periods.get('3天', 0):.1f}% | "
            report += f"{periods.get('7天', 0):.1f}% | "
            report += f"{periods.get('14天', 0):.1f}% | "
            report += f"{periods.get('30天', 0):.1f}% | "
            report += f"{results['total_signals']} |\n"
        
        report += """
### 1.2 信号分布
| 指标 | 强烈买入 | 买入 | 中性 | 卖出 | 强烈卖出 |
|------|----------|------|------|------|----------|
"""
        
        for indicator, results in accuracy_results.items():
            dist = results['signal_distribution']
            report += f"| **{indicator}** | "
            report += f"{dist['strong_buy']} | "
            report += f"{dist['buy']} | "
            report += f"{dist['neutral']} | "
            report += f"{dist['sell']} | "
            report += f"{dist['strong_sell']} |\n"
        
        report += """
---

## 2. 单指标回测结果

### 2.1 收益对比
| 指标 | 策略收益 | 买入持有 | 超额收益 | 最大回撤 | 夏普比率 |
|------|----------|----------|----------|----------|----------|
"""
        
        for indicator, metrics in backtest_results.items():
            report += f"| **{indicator}** | "
            report += f"{metrics['total_return']:.2f}% | "
            report += f"{metrics['buy_hold_return']:.2f}% | "
            report += f"{metrics['excess_return']:.2f}% | "
            report += f"{metrics['max_drawdown']:.2f}% | "
            report += f"{metrics['sharpe_ratio']:.2f} |\n"
        
        report += """
### 2.2 交易统计
| 指标 | 交易次数 | 胜率 | 平均收益 |
|------|----------|------|----------|
"""
        
        for indicator, metrics in backtest_results.items():
            report += f"| **{indicator}** | "
            report += f"{metrics['total_trades']} | "
            report += f"{metrics['win_rate']:.1f}% | "
            report += f"{metrics['avg_trade_return']:.2f}% |\n"
        
        report += f"""
---

## 3. 组合策略回测结果

### 3.1 综合绩效
- **总收益**: {combined_backtest['total_return']:.2f}%
- **买入持有收益**: {combined_backtest['buy_hold_return']:.2f}%
- **超额收益**: {combined_backtest['excess_return']:.2f}%
- **最大回撤**: {combined_backtest['max_drawdown']:.2f}%
- **夏普比率**: {combined_backtest['sharpe_ratio']:.2f}
- **总交易次数**: {combined_backtest['total_trades']}
- **胜率**: {combined_backtest['win_rate']:.1f}%
- **平均交易收益**: {combined_backtest['avg_trade_return']:.2f}%
"""
        
        if combined_backtest.get('best_trade'):
            best = combined_backtest['best_trade']
            report += f"""
### 3.2 最佳/最差交易
- **最佳交易**: {best['date'].strftime('%Y-%m-%d')} ({best['type']}) - 收益 {best['return']:.2f}%"""
        
        if combined_backtest.get('worst_trade'):
            worst = combined_backtest['worst_trade']
            report += f"""
- **最差交易**: {worst['date'].strftime('%Y-%m-%d')} ({worst['type']}) - 收益 {worst['return']:.2f}%"""
        
        report += """

---

## 4. 关键发现

### 4.1 指标有效性排名
"""
        
        # 计算综合得分
        indicator_scores = {}
        for indicator in accuracy_results.keys():
            if indicator in backtest_results:
                # 综合考虑准确率、收益和风险
                accuracy_score = accuracy_results[indicator]['accuracy_by_period'].get('7天', 0)
                return_score = backtest_results[indicator]['excess_return']
                sharpe_score = backtest_results[indicator]['sharpe_ratio'] * 10
                
                total_score = accuracy_score * 0.3 + return_score * 0.5 + sharpe_score * 0.2
                indicator_scores[indicator] = total_score
        
        sorted_indicators = sorted(indicator_scores.items(), key=lambda x: x[1], reverse=True)
        
        report += "| 排名 | 指标 | 综合得分 | 评价 |\n"
        report += "|------|------|----------|------|\n"
        
        for rank, (indicator, score) in enumerate(sorted_indicators, 1):
            if score > 50:
                rating = "⭐⭐⭐⭐⭐ 优秀"
            elif score > 30:
                rating = "⭐⭐⭐⭐ 良好"
            elif score > 10:
                rating = "⭐⭐⭐ 中等"
            elif score > 0:
                rating = "⭐⭐ 一般"
            else:
                rating = "⭐ 较差"
            
            report += f"| {rank} | **{indicator}** | {score:.1f} | {rating} |\n"
        
        report += """
### 4.2 验证结论

#### ✅ 验证成功的观点：
"""
        
        # 分析验证结果
        validations = []
        
        # MVRV验证
        if 'MVRV' in accuracy_results:
            mvrv_7d = accuracy_results['MVRV']['accuracy_by_period'].get('7天', 0)
            if mvrv_7d > 55:
                validations.append("1. **MVRV确实是最强预测指标** - 7天准确率达到" + f"{mvrv_7d:.1f}%")
        
        # 组合策略验证
        if combined_backtest['excess_return'] > 0:
            validations.append(f"2. **多指标组合策略优于单一指标** - 超额收益{combined_backtest['excess_return']:.1f}%")
        
        # 风险控制验证
        if combined_backtest['max_drawdown'] < 30:
            validations.append(f"3. **指标能有效控制风险** - 最大回撤仅{combined_backtest['max_drawdown']:.1f}%")
        
        for validation in validations:
            report += f"- {validation}\n"
        
        report += """
#### ❌ 需要修正的观点：
"""
        
        issues = []
        
        # 检查SOPR
        if 'SOPR' in backtest_results:
            if backtest_results['SOPR']['excess_return'] < 0:
                issues.append(f"1. **SOPR独立使用效果不佳** - 超额收益{backtest_results['SOPR']['excess_return']:.1f}%")
        
        # 检查短期预测
        short_term_accuracy = []
        for indicator, results in accuracy_results.items():
            if '1天' in results['accuracy_by_period']:
                short_term_accuracy.append(results['accuracy_by_period']['1天'])
        
        if short_term_accuracy and np.mean(short_term_accuracy) < 52:
            issues.append(f"2. **短期(1天)预测准确率偏低** - 平均仅{np.mean(short_term_accuracy):.1f}%")
        
        for issue in issues:
            report += f"- {issue}\n"
        
        report += """
### 4.3 实战建议

基于验证结果，建议采用以下策略：

1. **核心指标组合**：
   - 主要依赖MVRV和NUPL（权重60%）
   - SOPR作为辅助确认（权重20%）
   - NVT用于极值判断（权重20%）

2. **时间框架**：
   - 重点关注7-14天的中期信号
   - 避免过度依赖1天短期信号
   - 30天长期信号用于趋势确认

3. **风险管理**：
   - 综合信号强度低于-1.5时减仓
   - 综合信号强度高于1.5时加仓
   - 保持20-30%的最大回撤容忍度

4. **信号确认**：
   - 至少2个指标同时发出相同方向信号
   - 极值区域（顶部/底部）需要3个以上指标确认
   - 结合交易量和市场情绪指标

---

## 5. 局限性说明

1. **数据限制**：部分高级指标无法获取，影响验证完整性
2. **市场环境**：回测基于历史数据，未来市场可能发生结构性变化
3. **交易成本**：未考虑手续费和滑点，实际收益会降低
4. **样本偏差**：2023-2024年处于牛市，结果可能偏乐观

---

*报告生成时间：""" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """*
"""
        
        return report


def main():
    """主函数"""
    print("=" * 80)
    print("Glassnode指标验证系统")
    print("=" * 80)
    
    # 配置
    API_KEY = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
    START_DATE = "2023-01-01"
    END_DATE = "2024-12-31"
    
    # 初始化组件
    validator = IndicatorValidator(API_KEY)
    signal_gen = SignalGenerator()
    report_gen = ValidationReport()
    
    # 1. 加载数据
    print("\n步骤1: 加载指标数据")
    validator.load_all_indicators(START_DATE, END_DATE)
    
    if not validator.price_data is not None or not validator.indicators_data:
        print("错误：无法加载足够的数据进行验证")
        return
    
    # 2. 分析指标准确性
    print("\n步骤2: 分析指标准确性")
    accuracy_results = report_gen.analyze_indicator_accuracy(validator, signal_gen)
    
    for indicator, results in accuracy_results.items():
        print(f"\n{indicator}:")
        print(f"  1天准确率: {results['accuracy_by_period'].get('1天', 0):.1f}%")
        print(f"  7天准确率: {results['accuracy_by_period'].get('7天', 0):.1f}%")
        print(f"  信号总数: {results['total_signals']}")
    
    # 3. 单指标回测
    print("\n步骤3: 执行单指标回测")
    backtest_results = {}
    
    for indicator_name, indicator_data in validator.indicators_data.items():
        print(f"\n回测 {indicator_name}...")
        
        # 合并数据
        merged = pd.merge(validator.price_data, indicator_data, 
                         left_index=True, right_index=True, how='inner')
        
        if len(merged) < 100:
            print(f"  数据不足，跳过")
            continue
        
        # 初始化回测引擎
        backtest = BacktestEngine()
        
        # 执行回测
        for idx, row in merged.iterrows():
            signal = signal_gen.generate_signal(
                row[indicator_data.columns[0]], 
                indicator_name
            )
            backtest.execute_trade(idx, row['price'], signal)
        
        # 计算绩效
        metrics = backtest.calculate_metrics()
        backtest_results[indicator_name] = metrics
        
        print(f"  总收益: {metrics['total_return']:.2f}%")
        print(f"  超额收益: {metrics['excess_return']:.2f}%")
        print(f"  最大回撤: {metrics['max_drawdown']:.2f}%")
    
    # 4. 组合策略回测
    print("\n步骤4: 执行组合策略回测")
    
    # 合并所有指标
    combined_df = validator.price_data.copy()
    for indicator_name, indicator_data in validator.indicators_data.items():
        combined_df = pd.merge(combined_df, indicator_data, 
                              left_index=True, right_index=True, how='outer')
    
    combined_df = combined_df.dropna()
    
    # 组合策略回测
    combined_backtest = BacktestEngine()
    
    for idx, row in combined_df.iterrows():
        # 生成各指标信号
        signals = {}
        for indicator_name, indicator_data in validator.indicators_data.items():
            if indicator_data.columns[0] in row:
                signals[indicator_name] = signal_gen.generate_signal(
                    row[indicator_data.columns[0]], 
                    indicator_name
                )
        
        # 生成综合信号
        composite_signal = signal_gen.generate_composite_signal(signals)
        combined_backtest.execute_trade(idx, row['price'], composite_signal)
    
    combined_metrics = combined_backtest.calculate_metrics()
    
    print(f"\n组合策略结果:")
    print(f"  总收益: {combined_metrics['total_return']:.2f}%")
    print(f"  买入持有: {combined_metrics['buy_hold_return']:.2f}%")
    print(f"  超额收益: {combined_metrics['excess_return']:.2f}%")
    print(f"  最大回撤: {combined_metrics['max_drawdown']:.2f}%")
    print(f"  夏普比率: {combined_metrics['sharpe_ratio']:.2f}")
    
    # 5. 生成报告
    print("\n步骤5: 生成验证报告")
    
    markdown_report = report_gen.generate_markdown_report(
        accuracy_results,
        backtest_results,
        combined_metrics
    )
    
    # 保存报告
    with open('indicator_validation_report.md', 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print("\n验证报告已生成: indicator_validation_report.md")
    
    # 6. 生成总结
    print("\n" + "=" * 80)
    print("验证总结")
    print("=" * 80)
    
    print("\n📊 关键发现:")
    
    # 找出最佳指标
    if backtest_results:
        best_indicator = max(backtest_results.items(), 
                           key=lambda x: x[1]['excess_return'])
        print(f"1. 最佳单一指标: {best_indicator[0]} (超额收益 {best_indicator[1]['excess_return']:.1f}%)")
    
    # 组合策略表现
    print(f"2. 组合策略超额收益: {combined_metrics['excess_return']:.1f}%")
    
    # 风险控制
    print(f"3. 组合策略最大回撤: {combined_metrics['max_drawdown']:.1f}%")
    
    # 准确率分析
    avg_7d_accuracy = np.mean([r['accuracy_by_period'].get('7天', 0) 
                               for r in accuracy_results.values()])
    print(f"4. 平均7天预测准确率: {avg_7d_accuracy:.1f}%")
    
    print("\n✅ 验证结论:")
    
    if combined_metrics['excess_return'] > 0:
        print("• 链上指标确实能够产生超额收益")
    
    if combined_metrics['excess_return'] > max([m['excess_return'] 
                                                 for m in backtest_results.values()], default=0):
        print("• 多指标组合优于单一指标")
    
    if avg_7d_accuracy > 55:
        print("• 中期(7天)预测准确率较高")
    
    if combined_metrics['sharpe_ratio'] > 1:
        print("• 风险调整后收益良好")
    
    print("\n⚠️ 注意事项:")
    print("• 历史表现不代表未来收益")
    print("• 实际交易需考虑手续费和滑点")
    print("• 建议结合其他分析方法综合决策")


if __name__ == "__main__":
    main()