"""
Glassnode核心指标分析系统 - 精简版
只使用最重要且稳定可用的指标
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime
import json
import time
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


class GlassnodeCoreAnalyzer:
    """Glassnode核心指标分析器"""
    
    # 核心指标集 - 经过验证可用的
    CORE_METRICS = {
        'market': {
            'price_usd_close': '收盘价',
            'mvrv': 'MVRV比率',
            'mvrv_z_score': 'MVRV Z-Score'
        },
        'indicators': {
            'sopr': 'SOPR',
            'net_unrealized_profit_loss': 'NUPL',
            'puell_multiple': 'Puell倍数',
            'reserve_risk': '储备风险'
        },
        'supply': {
            'profit_relative': '盈利供应占比'
        },
        'addresses': {
            'active_count': '活跃地址数'
        },
        'mining': {
            'hash_rate_mean': '哈希率',
            'difficulty_latest': '挖矿难度'
        },
        'derivatives': {
            'futures_open_interest_sum': '期货持仓',
            'futures_funding_rate_perpetual': '资金费率'
        }
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://grassnoodle.cloud"
        self.headers = {"x-key": api_key}
        self.data_cache = {}
        
    def fetch_metric_safe(self, endpoint: str, params: dict, retry=3):
        """安全获取指标数据，带重试机制"""
        for attempt in range(retry):
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                
                if response.status_code == 429:  # Too Many Requests
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"  ⏳ 限流，等待{wait_time}秒后重试...")
                    time.sleep(wait_time)
                    continue
                    
                response.raise_for_status()
                data = response.json()
                
                # 检查权限
                if isinstance(data, dict) and data.get('type') == 'metric':
                    return None
                
                time.sleep(1)  # 正常请求间隔
                return data
                
            except Exception as e:
                if attempt == retry - 1:
                    print(f"  ❌ 失败: {str(e)[:50]}")
                    return None
                time.sleep(1)
        
        return None
    
    def get_all_core_metrics(self, start_date: str, end_date: str):
        """获取所有核心指标"""
        all_data = {}
        params = {
            "a": "BTC",
            "s": str(int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())),
            "u": str(int(datetime.strptime(end_date, "%Y-%m-%d").timestamp()))
        }
        
        print("\n📊 获取核心指标数据...")
        
        for category, metrics in self.CORE_METRICS.items():
            print(f"\n{category.upper()}:")
            for metric_key, metric_name in metrics.items():
                endpoint = f"/v1/metrics/{category}/{metric_key}"
                print(f"  {metric_name}...", end="")
                
                data = self.fetch_metric_safe(endpoint, params)
                if data:
                    df = pd.DataFrame(data)
                    df['date'] = pd.to_datetime(df['t'], unit='s')
                    df[metric_key] = df['v'].astype(float)
                    df = df[['date', metric_key]].set_index('date')
                    all_data[f"{category}_{metric_key}"] = df
                    print(f" ✅ ({len(df)} 条)")
                else:
                    print(f" ⏩ 跳过")
        
        return all_data
    
    def analyze_market_state(self, price_df: pd.DataFrame):
        """简化的市场状态分析"""
        df = price_df.copy()
        
        # 计算移动平均和收益率
        df['ma_200'] = df['price'].rolling(window=200).mean()
        df['ma_50'] = df['price'].rolling(window=50).mean()
        df['returns_30d'] = df['price'].pct_change(30)
        
        # 简单的市场状态判断
        df['state'] = 'Neutral'
        df.loc[(df['price'] > df['ma_200']) & (df['returns_30d'] > 0.15), 'state'] = 'Bull'
        df.loc[(df['price'] < df['ma_200']) & (df['returns_30d'] < -0.15), 'state'] = 'Bear'
        df.loc[df['returns_30d'] < -0.25, 'state'] = 'Extreme Fear'
        df.loc[df['returns_30d'] > 0.40, 'state'] = 'Extreme Greed'
        
        return df
    
    def generate_signals(self, metrics_data: dict):
        """生成交易信号"""
        signals = []
        
        # MVRV Z-Score信号
        if 'market_mvrv_z_score' in metrics_data:
            mvrv_z = metrics_data['market_mvrv_z_score'].iloc[-1, 0]
            
            if mvrv_z > 3:
                signals.append({
                    'type': 'SELL',
                    'strength': 'Strong',
                    'indicator': 'MVRV Z-Score',
                    'value': round(mvrv_z, 2),
                    'threshold': 3,
                    'reason': '市场极度过热'
                })
            elif mvrv_z < 0:
                signals.append({
                    'type': 'BUY',
                    'strength': 'Strong',
                    'indicator': 'MVRV Z-Score',
                    'value': round(mvrv_z, 2),
                    'threshold': 0,
                    'reason': '市场极度超卖'
                })
        
        # SOPR信号
        if 'indicators_sopr' in metrics_data:
            sopr = metrics_data['indicators_sopr'].iloc[-1, 0]
            sopr_ma7 = metrics_data['indicators_sopr'].iloc[-7:, 0].mean()
            
            if sopr < 0.95:
                signals.append({
                    'type': 'BUY',
                    'strength': 'Medium',
                    'indicator': 'SOPR',
                    'value': round(sopr, 3),
                    'threshold': 0.95,
                    'reason': '投资者恐慌抛售'
                })
            elif sopr > 1.05 and sopr < sopr_ma7:
                signals.append({
                    'type': 'SELL',
                    'strength': 'Medium',
                    'indicator': 'SOPR',
                    'value': round(sopr, 3),
                    'threshold': 1.05,
                    'reason': '获利了结增加'
                })
        
        # NUPL信号
        if 'indicators_net_unrealized_profit_loss' in metrics_data:
            nupl = metrics_data['indicators_net_unrealized_profit_loss'].iloc[-1, 0]
            
            if nupl > 0.7:
                signals.append({
                    'type': 'SELL',
                    'strength': 'Strong',
                    'indicator': 'NUPL',
                    'value': round(nupl, 2),
                    'threshold': 0.7,
                    'reason': '市场贪婪过度'
                })
            elif nupl < 0:
                signals.append({
                    'type': 'BUY',
                    'strength': 'Strong',
                    'indicator': 'NUPL',
                    'value': round(nupl, 2),
                    'threshold': 0,
                    'reason': '市场恐慌阶段'
                })
        
        # Puell Multiple信号
        if 'indicators_puell_multiple' in metrics_data:
            puell = metrics_data['indicators_puell_multiple'].iloc[-1, 0]
            
            if puell < 0.5:
                signals.append({
                    'type': 'BUY',
                    'strength': 'Medium',
                    'indicator': 'Puell Multiple',
                    'value': round(puell, 2),
                    'threshold': 0.5,
                    'reason': '矿工投降，接近底部'
                })
            elif puell > 3:
                signals.append({
                    'type': 'SELL',
                    'strength': 'Medium',
                    'indicator': 'Puell Multiple',
                    'value': round(puell, 2),
                    'threshold': 3,
                    'reason': '矿工收益过高'
                })
        
        return signals
    
    def create_dashboard(self, metrics_data: dict, signals: list, output_file: str = "dashboard.png"):
        """创建可视化仪表板"""
        fig, axes = plt.subplots(3, 2, figsize=(16, 12))
        fig.suptitle('Glassnode 核心指标仪表板', fontsize=16, fontweight='bold')
        
        # 1. 价格走势
        ax1 = axes[0, 0]
        if 'market_price_usd_close' in metrics_data:
            price_df = metrics_data['market_price_usd_close']
            ax1.plot(price_df.index, price_df.values, linewidth=1, color='blue')
            ax1.set_title('BTC价格走势')
            ax1.set_ylabel('价格 (USD)')
            ax1.set_yscale('log')
            ax1.grid(True, alpha=0.3)
        
        # 2. MVRV Z-Score
        ax2 = axes[0, 1]
        if 'market_mvrv_z_score' in metrics_data:
            mvrv_df = metrics_data['market_mvrv_z_score']
            ax2.plot(mvrv_df.index, mvrv_df.values, linewidth=1, color='purple')
            ax2.axhline(y=3, color='red', linestyle='--', alpha=0.5, label='过热线')
            ax2.axhline(y=0, color='green', linestyle='--', alpha=0.5, label='超卖线')
            ax2.fill_between(mvrv_df.index, 0, 3, alpha=0.1, color='gray')
            ax2.set_title('MVRV Z-Score')
            ax2.set_ylabel('Z-Score')
            ax2.legend(loc='upper right')
            ax2.grid(True, alpha=0.3)
        
        # 3. SOPR
        ax3 = axes[1, 0]
        if 'indicators_sopr' in metrics_data:
            sopr_df = metrics_data['indicators_sopr']
            ax3.plot(sopr_df.index, sopr_df.values, linewidth=1, color='orange')
            ax3.axhline(y=1, color='black', linestyle='-', alpha=0.5, label='盈亏平衡')
            ax3.axhline(y=1.05, color='red', linestyle='--', alpha=0.5, label='获利区')
            ax3.axhline(y=0.95, color='green', linestyle='--', alpha=0.5, label='亏损区')
            ax3.set_title('SOPR (支出产出利润率)')
            ax3.set_ylabel('SOPR')
            ax3.legend(loc='upper right')
            ax3.grid(True, alpha=0.3)
        
        # 4. NUPL
        ax4 = axes[1, 1]
        if 'indicators_net_unrealized_profit_loss' in metrics_data:
            nupl_df = metrics_data['indicators_net_unrealized_profit_loss']
            ax4.plot(nupl_df.index, nupl_df.values, linewidth=1, color='green')
            ax4.axhline(y=0.7, color='red', linestyle='--', alpha=0.5, label='贪婪')
            ax4.axhline(y=0.5, color='orange', linestyle='--', alpha=0.5, label='乐观')
            ax4.axhline(y=0, color='blue', linestyle='--', alpha=0.5, label='中性')
            ax4.axhline(y=-0.25, color='purple', linestyle='--', alpha=0.5, label='投降')
            ax4.set_title('NUPL (净未实现损益)')
            ax4.set_ylabel('NUPL')
            ax4.legend(loc='upper right', fontsize=8)
            ax4.grid(True, alpha=0.3)
        
        # 5. 信号汇总
        ax5 = axes[2, 0]
        ax5.axis('off')
        
        # 统计信号
        buy_signals = [s for s in signals if s['type'] == 'BUY']
        sell_signals = [s for s in signals if s['type'] == 'SELL']
        
        signal_text = f"📊 当前信号汇总\n\n"
        signal_text += f"买入信号: {len(buy_signals)} 个\n"
        signal_text += f"卖出信号: {len(sell_signals)} 个\n\n"
        
        if signals:
            signal_text += "具体信号:\n"
            for i, sig in enumerate(signals[:5], 1):  # 最多显示5个
                emoji = "🟢" if sig['type'] == 'BUY' else "🔴"
                signal_text += f"{emoji} {sig['indicator']}: {sig['value']} ({sig['reason']})\n"
        else:
            signal_text += "暂无明确信号"
        
        ax5.text(0.1, 0.5, signal_text, fontsize=11, verticalalignment='center',
                fontfamily='monospace')
        
        # 6. 关键指标表
        ax6 = axes[2, 1]
        ax6.axis('off')
        
        # 获取最新值
        latest_values = []
        for key, df in metrics_data.items():
            if not df.empty:
                name = key.replace('_', ' ').title()
                value = df.iloc[-1, 0]
                if 'price' in key:
                    value_str = f"${value:,.0f}"
                elif 'rate' in key or 'relative' in key:
                    value_str = f"{value:.4f}"
                else:
                    value_str = f"{value:.2f}"
                latest_values.append([name, value_str])
        
        # 创建表格
        if latest_values:
            table = ax6.table(cellText=latest_values[:8],  # 最多显示8个
                            colLabels=['指标', '当前值'],
                            cellLoc='left',
                            loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 1.5)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.show()
        
        return output_file
    
    def generate_report(self, metrics_data: dict, signals: list, market_state: pd.DataFrame):
        """生成分析报告"""
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {},
            'signals': [],
            'metrics': {},
            'market_state': {}
        }
        
        # 市场状态
        current_state = market_state['state'].iloc[-1]
        state_dist = market_state['state'].value_counts(normalize=True).to_dict()
        
        report['market_state'] = {
            'current': current_state,
            'distribution': state_dist
        }
        
        # 信号汇总
        report['signals'] = signals
        buy_count = len([s for s in signals if s['type'] == 'BUY'])
        sell_count = len([s for s in signals if s['type'] == 'SELL'])
        
        # 决策建议
        if buy_count > sell_count and buy_count >= 2:
            report['summary']['recommendation'] = 'BUY'
            report['summary']['confidence'] = 'High' if buy_count >= 3 else 'Medium'
        elif sell_count > buy_count and sell_count >= 2:
            report['summary']['recommendation'] = 'SELL'
            report['summary']['confidence'] = 'High' if sell_count >= 3 else 'Medium'
        else:
            report['summary']['recommendation'] = 'HOLD'
            report['summary']['confidence'] = 'Low'
        
        # 关键指标值
        for key, df in metrics_data.items():
            if not df.empty:
                latest = float(df.iloc[-1, 0])
                mean = float(df.mean().iloc[0])
                std = float(df.std().iloc[0])
                
                report['metrics'][key] = {
                    'latest': latest,
                    'mean': mean,
                    'std': std,
                    'z_score': (latest - mean) / std if std > 0 else 0
                }
        
        return report


def main():
    """主函数"""
    # 配置
    API_KEY = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
    START_DATE = "2023-01-01"  # 更短的时间范围
    END_DATE = "2024-12-31"
    
    print("=" * 60)
    print("🚀 Glassnode核心指标分析系统")
    print("=" * 60)
    print(f"分析周期：{START_DATE} 至 {END_DATE}")
    
    # 初始化分析器
    analyzer = GlassnodeCoreAnalyzer(API_KEY)
    
    # 获取数据
    metrics_data = analyzer.get_all_core_metrics(START_DATE, END_DATE)
    
    if not metrics_data:
        print("\n❌ 无法获取数据，请检查API密钥和网络连接")
        return
    
    print(f"\n✅ 成功获取 {len(metrics_data)} 个指标")
    
    # 分析市场状态
    if 'market_price_usd_close' in metrics_data:
        price_df = metrics_data['market_price_usd_close']
        price_df = price_df.rename(columns={price_df.columns[0]: 'price'})
        market_state = analyzer.analyze_market_state(price_df)
        print(f"📊 当前市场状态: {market_state['state'].iloc[-1]}")
    else:
        market_state = pd.DataFrame()
    
    # 生成信号
    signals = analyzer.generate_signals(metrics_data)
    print(f"\n🎯 生成交易信号: {len(signals)} 个")
    
    # 显示信号
    if signals:
        print("\n当前信号:")
        for sig in signals:
            emoji = "🟢" if sig['type'] == 'BUY' else "🔴"
            print(f"  {emoji} [{sig['type']}] {sig['indicator']}: {sig['value']} - {sig['reason']}")
    
    # 创建可视化
    print("\n📈 生成可视化仪表板...")
    dashboard_file = analyzer.create_dashboard(metrics_data, signals, "glassnode_dashboard.png")
    print(f"✅ 仪表板已保存: {dashboard_file}")
    
    # 生成报告
    report = analyzer.generate_report(metrics_data, signals, market_state)
    
    # 保存报告
    with open('glassnode_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    print(f"✅ 分析报告已保存: glassnode_analysis_report.json")
    
    # 显示建议
    print("\n" + "=" * 60)
    print("💡 投资建议")
    print("=" * 60)
    print(f"推荐操作: {report['summary']['recommendation']}")
    print(f"信心程度: {report['summary']['confidence']}")
    
    # 关键指标摘要
    print("\n📊 关键指标状态:")
    key_metrics = ['market_mvrv_z_score', 'indicators_sopr', 'indicators_net_unrealized_profit_loss']
    for metric in key_metrics:
        if metric in report['metrics']:
            data = report['metrics'][metric]
            name = metric.split('_', 1)[1] if '_' in metric else metric
            z = data['z_score']
            status = "🔴 过高" if z > 2 else "🟢 过低" if z < -2 else "⚪ 正常"
            print(f"  {name}: {data['latest']:.3f} ({status})")
    
    print("\n✅ 分析完成！")


if __name__ == "__main__":
    main()