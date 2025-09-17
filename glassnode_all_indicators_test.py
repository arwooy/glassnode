#!/usr/bin/env python3
"""
Glassnode全指标信息增益分析系统
测试所有API端点类别下的指标，计算信息增益并生成综合报告
"""

import os
import json
import time
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy.stats import entropy
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

API_KEY = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
headers = {
    "x-key": API_KEY
}

class GlassnodeAllIndicatorsAnalyzer:
    """Glassnode全指标分析器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # self.base_url = "https://api.glassnode.com/v1/metrics"
        self.base_url = "https://grassnoodle.cloud/v1/metrics"
        
        # 从JSON配置文件加载端点定义
        self.load_endpoints_config()
        
        # 用于存储结果
        self.results = {}
        self.failed_endpoints = []
        
    def load_endpoints_config(self):
        """从JSON文件加载端点配置"""
        config_file = 'glassnode_endpoints_config.json'
        
        # 尝试从当前目录或脚本目录加载
        if os.path.exists(config_file):
            config_path = config_file
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, config_file)
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件 {config_file} 未找到")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.categories = json.load(f)
            
        # 验证配置
        if not self.categories:
            raise ValueError("配置文件为空或格式错误")
            
        print(f"✓ 已加载 {len(self.categories)} 个类别的端点配置")
        total_endpoints = sum(len(cat['endpoints']) for cat in self.categories.values())
        print(f"  总端点数: {total_endpoints}")
        
    def fetch_metric_data(self, category: str, metric: str, 
                         start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """获取单个指标数据"""
        try:
            url = f"{self.base_url}/{category}/{metric}"
            params = {
                'a': 'BTC',
                's': int(start_date.timestamp()),
                'u': int(end_date.timestamp()),
                'i': '24h'
            }
            
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data)
                
                if not df.empty:
                    # 处理时间戳
                    if 't' in df.columns:
                        df['timestamp'] = pd.to_datetime(df['t'], unit='s')
                        df = df.set_index('timestamp')
                    
                    # 处理两种数据格式
                    if 'v' in df.columns:
                        # 单值格式
                        df = df.rename(columns={'v': metric})
                        df = df[[metric]]
                        return df
                    elif 'o' in df.columns:
                        # 多维格式（如supply_distribution_relative）
                        # 将字典展开为多列
                        expanded = pd.json_normalize(df['o'])
                        expanded.index = df.index
                        
                        # 对于分布数据，可以计算一个综合指标
                        # 例如：使用基尼系数或者加权平均
                        if metric == 'supply_distribution_relative':
                            # 计算供应集中度指标
                            expanded[metric] = self.calculate_supply_concentration(expanded)
                        else:
                            # 对于其他多维数据，取第一列或计算均值
                            if not expanded.empty:
                                expanded[metric] = expanded.mean(axis=1)
                        
                        if metric in expanded.columns:
                            return expanded[[metric]]
                        else:
                            print(f"  ⚠ {metric}: 多维数据处理")
                            return pd.DataFrame()
            else:
                print(f"  ✗ {metric}: {response.status_code}")
                self.failed_endpoints.append(f"{category}/{metric}")
                
        except Exception as e:
            print(f"  ✗ {metric}: {str(e)[:50]}")
            self.failed_endpoints.append(f"{category}/{metric}")
            
        return pd.DataFrame()
    
    def calculate_supply_concentration(self, dist_df: pd.DataFrame) -> pd.Series:
        """计算供应集中度指标（基于分布数据）"""
        # 使用加权基尼系数或赫芬达尔指数
        result = []
        
        for idx, row in dist_df.iterrows():
            # 计算赫芬达尔指数 (HHI)
            values = row.values
            # 过滤掉NaN值
            values = values[~pd.isna(values)]
            
            if len(values) > 0:
                # HHI = sum(share^2)
                hhi = np.sum(values ** 2)
                result.append(hhi)
            else:
                result.append(np.nan)
        
        return pd.Series(result, index=dist_df.index)
    
    def calculate_information_gain(self, indicator_data: pd.Series, 
                                  price_data: pd.Series,
                                  horizon_days: int) -> Dict:
        """计算信息增益"""
        try:
            # 准备数据
            df = pd.DataFrame({
                'indicator': indicator_data,
                'price': price_data
            }).dropna()
            
            if len(df) < 100:
                return {}
            
            # 计算未来价格变化
            df['future_price'] = df['price'].shift(-horizon_days)
            df['price_change'] = (df['future_price'] / df['price'] - 1).fillna(0)
            df = df.dropna()
            
            # 离散化
            n_bins = 10
            indicator_bins = pd.qcut(df['indicator'].values, n_bins, 
                                    labels=False, duplicates='drop')
            price_bins = pd.qcut(df['price_change'].values, n_bins, 
                               labels=False, duplicates='drop')
            
            # 计算熵
            H_price = entropy(np.bincount(price_bins) / len(price_bins))
            
            # 计算条件熵
            H_conditional = 0
            for i in range(n_bins):
                mask = indicator_bins == i
                p_indicator = np.sum(mask) / len(indicator_bins)
                
                if p_indicator > 0 and np.sum(mask) > 1:
                    price_in_bin = price_bins[mask]
                    if len(price_in_bin) > 0:
                        bin_probs = np.bincount(price_in_bin, minlength=n_bins) / len(price_in_bin)
                        h = entropy(bin_probs)
                        H_conditional += p_indicator * h
            
            # 信息增益
            ig = max(0, H_price - H_conditional)
            
            # 归一化互信息
            mi = ig
            normalized_mi = mi / H_price if H_price > 0 else 0
            
            # 相关性
            correlation = df['indicator'].corr(df['price_change'])
            
            return {
                'information_gain': ig,
                'normalized_mi': normalized_mi,
                'correlation': correlation,
                'entropy_price': H_price,
                'entropy_conditional': H_conditional,
                'reduction_ratio': ig/H_price if H_price > 0 else 0
            }
            
        except Exception as e:
            return {}
    
    def test_category(self, category_key: str, category_info: Dict,
                     price_data: pd.Series) -> Dict:
        """测试一个类别下的所有指标"""
        print(f"\n{'='*60}")
        print(f"测试类别: {category_info['name']} ({category_key})")
        print(f"端点数量: {len(category_info['endpoints'])}")
        print(f"{'='*60}")
        
        category_results = {}
        successful = 0
        
        for idx, endpoint in enumerate(category_info['endpoints'], 1):
            print(f"\n[{idx}/{len(category_info['endpoints'])}] 测试: {endpoint}")
            
            # 获取数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365*2)  # 2年数据
            
            df = self.fetch_metric_data(category_key, endpoint, start_date, end_date)
            
            if df.empty:
                continue
                
            time.sleep(0.8)  # 避免API限制
            
            # 计算不同时间跨度的信息增益
            horizons = [1, 3, 7, 14, 30]
            endpoint_results = {}
            
            for horizon in horizons:
                ig_result = self.calculate_information_gain(
                    df[endpoint], price_data, horizon
                )
                if ig_result:
                    endpoint_results[f'{horizon}d'] = ig_result
                    
            if endpoint_results:
                # 计算平均信息增益
                avg_ig = np.mean([r['information_gain'] 
                                for r in endpoint_results.values()])
                avg_mi = np.mean([r['normalized_mi'] 
                                for r in endpoint_results.values()])
                
                category_results[endpoint] = {
                    'horizons': endpoint_results,
                    'avg_ig': avg_ig,
                    'avg_mi': avg_mi,
                    'category': category_key
                }
                
                successful += 1
                print(f"  ✓ 平均IG: {avg_ig:.4f}, MI: {avg_mi:.4f}")
        
        print(f"\n类别测试完成: 成功 {successful}/{len(category_info['endpoints'])}")
        return category_results
    
    def run_comprehensive_test(self):
        """运行全面测试"""
        print("\n" + "="*60)
        print("Glassnode 全指标信息增益分析")
        print("="*60)
        
        # 先获取价格数据
        print("\n获取BTC价格数据...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*2)
        
        # 尝试使用正确的价格端点
        price_df = pd.DataFrame()
        price_endpoints = ['price_usd_close', 'close']
        
        for endpoint in price_endpoints:
            price_df = self.fetch_metric_data('market', endpoint,
                                             start_date, end_date)
            if not price_df.empty:
                if endpoint in price_df.columns:
                    price_df = price_df.rename(columns={endpoint: 'price_usd_close'})
                break
        
        if price_df.empty:
            print("错误：无法获取价格数据")
            return
            
        price_data = price_df['price_usd_close']
        print(f"✓ 获取到 {len(price_data)} 天的价格数据")
        
        # 测试每个类别
        all_results = {}
        
        for category_key, category_info in self.categories.items():
            results = self.test_category(category_key, category_info, price_data)
            all_results.update(results)
            
            # 保存中间结果
            self.save_intermediate_results(all_results)
            
            # 避免API限制
            time.sleep(2)
        
        # 生成最终报告
        self.generate_final_report(all_results)
        
    def save_intermediate_results(self, results: Dict):
        """保存中间结果"""
        with open('glassnode_test_intermediate.json', 'w') as f:
            # 转换为可JSON序列化的格式
            json_results = {}
            for key, value in results.items():
                json_results[key] = {
                    'avg_ig': float(value['avg_ig']),
                    'avg_mi': float(value['avg_mi']),
                    'category': value['category']
                }
            json.dump(json_results, f, indent=2)
            
    def generate_final_report(self, all_results: Dict):
        """生成最终报告"""
        print("\n" + "="*60)
        print("最终分析报告")
        print("="*60)
        
        # 按信息增益排序
        sorted_results = sorted(all_results.items(), 
                               key=lambda x: x[1]['avg_ig'],
                               reverse=True)
        
        # Top 20 指标
        print("\n### Top 20 高信息增益指标 ###\n")
        print(f"{'排名':<5} {'指标名称':<40} {'类别':<15} {'平均IG':<10} {'平均MI':<10}")
        print("-" * 80)
        
        for i, (indicator, result) in enumerate(sorted_results[:20], 1):
            category_name = self.categories[result['category']]['name']
            print(f"{i:<5} {indicator:<40} {category_name:<15} "
                  f"{result['avg_ig']:<10.4f} {result['avg_mi']:<10.4f}")
        
        # 按类别统计
        print("\n### 类别统计 ###\n")
        category_stats = {}
        
        for indicator, result in all_results.items():
            cat = result['category']
            if cat not in category_stats:
                category_stats[cat] = {
                    'indicators': [],
                    'avg_igs': []
                }
            category_stats[cat]['indicators'].append(indicator)
            category_stats[cat]['avg_igs'].append(result['avg_ig'])
        
        print(f"{'类别':<20} {'指标数':<10} {'平均IG':<10} {'最高IG指标':<30}")
        print("-" * 70)
        
        for cat, stats in category_stats.items():
            cat_name = self.categories[cat]['name']
            avg_ig = np.mean(stats['avg_igs'])
            best_idx = np.argmax(stats['avg_igs'])
            best_indicator = stats['indicators'][best_idx]
            best_ig = stats['avg_igs'][best_idx]
            
            print(f"{cat_name:<20} {len(stats['indicators']):<10} "
                  f"{avg_ig:<10.4f} {best_indicator} ({best_ig:.4f})")
        
        # 保存完整结果
        self.save_full_results(all_results, sorted_results)
        
        # 统计信息
        print(f"\n### 测试统计 ###")
        print(f"总测试指标数: {len(all_results)}")
        print(f"失败的端点数: {len(self.failed_endpoints)}")
        print(f"平均信息增益: {np.mean([r['avg_ig'] for r in all_results.values()]):.4f}")
        
        if self.failed_endpoints:
            print(f"\n失败的端点:")
            for ep in self.failed_endpoints[:10]:
                print(f"  - {ep}")
            if len(self.failed_endpoints) > 10:
                print(f"  ... 共 {len(self.failed_endpoints)} 个")
    
    def save_full_results(self, all_results: Dict, sorted_results: List):
        """保存完整结果"""
        # 创建DataFrame
        data = []
        for indicator, result in sorted_results:
            for horizon_key, horizon_data in result['horizons'].items():
                data.append({
                    'indicator': indicator,
                    'category': self.categories[result['category']]['name'],
                    'horizon': horizon_key,
                    'information_gain': horizon_data['information_gain'],
                    'normalized_mi': horizon_data['normalized_mi'],
                    'correlation': horizon_data['correlation'],
                    'reduction_ratio': horizon_data['reduction_ratio']
                })
        
        df = pd.DataFrame(data)
        
        # 保存CSV
        df.to_csv('glassnode_all_indicators_results.csv', index=False)
        print(f"\n结果已保存到 glassnode_all_indicators_results.csv")
        
        # 生成HTML报告
        self.generate_html_report(sorted_results)
    
    def generate_html_report(self, sorted_results: List):
        """生成HTML报告"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Glassnode全指标信息增益分析报告</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        h1 { color: #333; text-align: center; }
        h2 { color: #666; border-bottom: 2px solid #ddd; padding-bottom: 5px; }
        table { width: 100%; border-collapse: collapse; background: white; margin: 20px 0; }
        th { background: #4CAF50; color: white; padding: 12px; text-align: left; }
        td { padding: 10px; border-bottom: 1px solid #ddd; }
        tr:hover { background: #f5f5f5; }
        .top-indicator { background: #fffacd; }
        .category-header { background: #e8f5e9; font-weight: bold; }
        .stats-box { background: white; padding: 20px; margin: 20px 0; border-radius: 5px; 
                     box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric { display: inline-block; margin: 10px 20px; }
        .metric-label { color: #666; font-size: 14px; }
        .metric-value { font-size: 24px; font-weight: bold; color: #4CAF50; }
    </style>
</head>
<body>
    <h1>Glassnode 全指标信息增益分析报告</h1>
    <div class="stats-box">
        <h2>测试概览</h2>
        <div class="metric">
            <div class="metric-label">测试指标总数</div>
            <div class="metric-value">""" + str(len(sorted_results)) + """</div>
        </div>
        <div class="metric">
            <div class="metric-label">平均信息增益</div>
            <div class="metric-value">""" + f"{np.mean([r[1]['avg_ig'] for r in sorted_results]):.4f}" + """</div>
        </div>
        <div class="metric">
            <div class="metric-label">生成时间</div>
            <div class="metric-value">""" + datetime.now().strftime("%Y-%m-%d %H:%M") + """</div>
        </div>
    </div>
    
    <h2>Top 50 高信息增益指标</h2>
    <table>
        <tr>
            <th>排名</th>
            <th>指标</th>
            <th>类别</th>
            <th>平均IG</th>
            <th>平均MI</th>
            <th>1天IG</th>
            <th>7天IG</th>
            <th>30天IG</th>
        </tr>
"""
        
        for i, (indicator, result) in enumerate(sorted_results[:50], 1):
            row_class = 'top-indicator' if i <= 10 else ''
            cat_name = self.categories[result['category']]['name']
            
            ig_1d = result['horizons'].get('1d', {}).get('information_gain', 0)
            ig_7d = result['horizons'].get('7d', {}).get('information_gain', 0)
            ig_30d = result['horizons'].get('30d', {}).get('information_gain', 0)
            
            html += f"""
        <tr class="{row_class}">
            <td>{i}</td>
            <td><b>{indicator}</b></td>
            <td>{cat_name}</td>
            <td>{result['avg_ig']:.4f}</td>
            <td>{result['avg_mi']:.4f}</td>
            <td>{ig_1d:.4f}</td>
            <td>{ig_7d:.4f}</td>
            <td>{ig_30d:.4f}</td>
        </tr>
"""
        
        html += """
    </table>
</body>
</html>
"""
        
        with open('glassnode_all_indicators_report.html', 'w', encoding='utf-8') as f:
            f.write(html)
            
        print(f"HTML报告已保存到 glassnode_all_indicators_report.html")


def main():
    # API密钥
    api_key = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
    
    # 创建分析器
    analyzer = GlassnodeAllIndicatorsAnalyzer(api_key)
    
    # 运行全面测试
    analyzer.run_comprehensive_test()


if __name__ == "__main__":
    main()