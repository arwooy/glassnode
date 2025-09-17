#!/usr/bin/env python3
"""
测试Glassnode多维数据端点
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

API_KEY = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
headers = {"x-key": API_KEY}

def test_distribution_endpoint():
    """测试supply_distribution_relative端点"""
    
    url = "https://grassnoodle.cloud/v1/metrics/addresses/supply_distribution_relative"
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    params = {
        'a': 'BTC',
        's': int(start_date.timestamp()),
        'u': int(end_date.timestamp()),
        'i': '24h'
    }
    
    print("测试 supply_distribution_relative 端点")
    print("-" * 50)
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 成功获取 {len(data)} 条数据\n")
        
        # 查看数据结构
        if data:
            print("第一条数据示例:")
            first = data[0]
            print(f"时间戳 't': {first.get('t')}")
            
            if 'o' in first:
                print(f"数据 'o' 包含的字段:")
                for key, value in first['o'].items():
                    print(f"  {key}: {value:.6f}")
            
            # 转换为DataFrame
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['t'], unit='s')
            df = df.set_index('timestamp')
            
            # 展开o列
            expanded = pd.json_normalize(df['o'])
            expanded.index = df.index
            
            print(f"\n展开后的DataFrame形状: {expanded.shape}")
            print(f"列名: {list(expanded.columns)}")
            
            # 计算集中度指标
            print("\n计算供应集中度指标:")
            
            # 1. 赫芬达尔指数 (HHI)
            hhi_values = []
            for idx, row in expanded.iterrows():
                values = row.values[~pd.isna(row.values)]
                hhi = np.sum(values ** 2)
                hhi_values.append(hhi)
            
            hhi_series = pd.Series(hhi_values, index=expanded.index)
            print(f"HHI 平均值: {hhi_series.mean():.4f}")
            print(f"HHI 标准差: {hhi_series.std():.4f}")
            
            # 2. 基尼系数
            def calculate_gini(values):
                """计算基尼系数"""
                sorted_vals = np.sort(values)
                n = len(values)
                cumsum = np.cumsum(sorted_vals)
                return (2.0 / n) * np.sum((np.arange(1, n + 1) - 1) * sorted_vals) / cumsum[-1] - (n - 1) / n
            
            gini_values = []
            for idx, row in expanded.iterrows():
                values = row.values[~pd.isna(row.values)]
                if len(values) > 0:
                    gini = calculate_gini(values)
                    gini_values.append(gini)
            
            gini_series = pd.Series(gini_values, index=expanded.index[:len(gini_values)])
            print(f"Gini 平均值: {gini_series.mean():.4f}")
            print(f"Gini 标准差: {gini_series.std():.4f}")
            
            # 3. 前1%持有者的份额
            if 'above_100k' in expanded.columns:
                top_1pct = expanded['above_100k']
                print(f"前1%持有者平均份额: {top_1pct.mean():.4f}")
            
            # 返回用于信息增益计算的综合指标
            return hhi_series
            
    else:
        print(f"✗ 错误: {response.status_code}")
        return None

def test_ohlc_endpoint():
    """测试OHLC数据端点"""
    
    url = "https://grassnoodle.cloud/v1/metrics/market/price_usd_ohlc"
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    params = {
        'a': 'BTC',
        's': int(start_date.timestamp()),
        'u': int(end_date.timestamp()),
        'i': '24h'
    }
    
    print("\n测试 price_usd_ohlc 端点")
    print("-" * 50)
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 成功获取 {len(data)} 条数据\n")
        
        if data:
            print("第一条数据示例:")
            first = data[0]
            print(f"时间戳 't': {first.get('t')}")
            
            if 'o' in first:
                print(f"OHLC数据:")
                ohlc = first['o']
                print(f"  开盘 (o): {ohlc.get('o')}")
                print(f"  最高 (h): {ohlc.get('h')}")
                print(f"  最低 (l): {ohlc.get('l')}")
                print(f"  收盘 (c): {ohlc.get('c')}")
            
            # 转换为DataFrame
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['t'], unit='s')
            df = df.set_index('timestamp')
            
            # 展开OHLC数据
            ohlc_df = pd.json_normalize(df['o'])
            ohlc_df.index = df.index
            
            print(f"\nOHLC DataFrame形状: {ohlc_df.shape}")
            print(ohlc_df.head())
            
            # 计算技术指标
            print("\n计算技术指标:")
            
            # 1. 波动率
            ohlc_df['volatility'] = (ohlc_df['h'] - ohlc_df['l']) / ohlc_df['c']
            print(f"平均波动率: {ohlc_df['volatility'].mean():.4f}")
            
            # 2. 价格变化
            ohlc_df['price_change'] = (ohlc_df['c'] - ohlc_df['o']) / ohlc_df['o']
            print(f"平均价格变化: {ohlc_df['price_change'].mean():.4f}")
            
            return ohlc_df['c']  # 返回收盘价用于分析
            
    else:
        print(f"✗ 错误: {response.status_code}")
        return None

def main():
    print("="*60)
    print("测试Glassnode多维数据端点")
    print("="*60)
    print()
    
    # 测试分布数据
    hhi_data = test_distribution_endpoint()
    
    # 测试OHLC数据  
    price_data = test_ohlc_endpoint()
    
    # 如果两个都成功，计算信息增益
    if hhi_data is not None and price_data is not None:
        print("\n" + "="*60)
        print("计算信息增益")
        print("="*60)
        
        # 对齐数据
        common_index = hhi_data.index.intersection(price_data.index)
        hhi_aligned = hhi_data.loc[common_index]
        price_aligned = price_data.loc[common_index]
        
        # 计算价格变化
        price_change = price_aligned.pct_change(7).shift(-7)  # 7天后的价格变化
        
        # 去除NaN
        valid_mask = ~(price_change.isna() | hhi_aligned.isna())
        price_change_clean = price_change[valid_mask]
        hhi_clean = hhi_aligned[valid_mask]
        
        if len(price_change_clean) > 10:
            # 计算相关性
            correlation = hhi_clean.corr(price_change_clean)
            print(f"HHI与7天后价格变化的相关性: {correlation:.4f}")
            
            # 简单的信息增益估算
            from scipy.stats import entropy
            
            # 离散化
            n_bins = 5
            hhi_bins = pd.qcut(hhi_clean, n_bins, labels=False, duplicates='drop')
            price_bins = pd.qcut(price_change_clean, n_bins, labels=False, duplicates='drop')
            
            # 计算熵
            H_price = entropy(np.bincount(price_bins) / len(price_bins))
            
            # 计算条件熵
            H_conditional = 0
            for i in range(n_bins):
                mask = hhi_bins == i
                if mask.sum() > 0:
                    p_hhi = mask.sum() / len(hhi_bins)
                    price_in_bin = price_bins[mask]
                    if len(price_in_bin) > 0:
                        bin_probs = np.bincount(price_in_bin, minlength=n_bins) / len(price_in_bin)
                        h = entropy(bin_probs)
                        H_conditional += p_hhi * h
            
            # 信息增益
            ig = max(0, H_price - H_conditional)
            print(f"信息增益: {ig:.4f}")
            print(f"相对信息增益: {(ig/H_price)*100:.2f}%")

if __name__ == "__main__":
    main()