#!/usr/bin/env python3
"""
测试更新后的端点配置
"""

import requests
import time
from datetime import datetime, timedelta

API_KEY = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
headers = {"x-key": API_KEY}
base_url = "https://grassnoodle.cloud/v1/metrics"

# 从更新的配置导入
from glassnode_all_indicators_test import GlassnodeAllIndicatorsAnalyzer

def quick_test_endpoints():
    """快速测试几个关键端点"""
    
    test_endpoints = [
        ("addresses", "active_count"),
        ("addresses", "supply_distribution_relative"),  # 多维数据
        ("blockchain", "utxo_created_value_sum"),       # 修正的端点
        ("indicators", "sopr"),
        ("indicators", "reserve_risk"),
        ("market", "price_usd_close"),
        ("market", "price_usd_ohlc"),                   # 多维数据
        ("supply", "profit_sum"),                       # 修正的端点
        ("transactions", "transfers_volume_sum")        # 修正的端点
    ]
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    params = {
        'a': 'BTC',
        's': int(start_date.timestamp()),
        'u': int(end_date.timestamp()),
        'i': '24h'
    }
    
    print("="*60)
    print("测试关键端点")
    print("="*60)
    
    successful = 0
    failed = []
    
    for category, metric in test_endpoints:
        url = f"{base_url}/{category}/{metric}"
        print(f"\n测试: {category}/{metric}")
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    first = data[0]
                    if 'v' in first:
                        print(f"  ✓ 成功 - 单值数据")
                        successful += 1
                    elif 'o' in first:
                        print(f"  ✓ 成功 - 多维数据")
                        if isinstance(first['o'], dict):
                            print(f"    字段数: {len(first['o'])}")
                        successful += 1
                    else:
                        print(f"  ⚠ 未知数据格式")
                        failed.append(f"{category}/{metric}")
                else:
                    print(f"  ⚠ 空数据")
                    failed.append(f"{category}/{metric}")
            else:
                print(f"  ✗ 错误 {response.status_code}")
                failed.append(f"{category}/{metric}")
                
        except Exception as e:
            print(f"  ✗ 异常: {str(e)[:50]}")
            failed.append(f"{category}/{metric}")
        
        time.sleep(0.5)
    
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"成功: {successful}/{len(test_endpoints)}")
    
    if failed:
        print(f"\n失败的端点:")
        for ep in failed:
            print(f"  - {ep}")
    else:
        print("\n所有测试端点都成功！")

def test_multidim_handling():
    """测试多维数据处理"""
    print("\n" + "="*60)
    print("测试多维数据处理")
    print("="*60)
    
    analyzer = GlassnodeAllIndicatorsAnalyzer(API_KEY)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # 测试supply_distribution_relative
    print("\n测试 supply_distribution_relative:")
    df = analyzer.fetch_metric_data('addresses', 'supply_distribution_relative',
                                   start_date, end_date)
    
    if not df.empty:
        print(f"  ✓ 数据获取成功")
        print(f"  形状: {df.shape}")
        print(f"  列名: {df.columns.tolist()}")
        print(f"  前5个值: {df.iloc[:5, 0].values}")
    else:
        print(f"  ✗ 数据获取失败")
    
    # 测试price_usd_ohlc
    print("\n测试 price_usd_ohlc:")
    df = analyzer.fetch_metric_data('market', 'price_usd_ohlc',
                                   start_date, end_date)
    
    if not df.empty:
        print(f"  ✓ 数据获取成功")
        print(f"  形状: {df.shape}")
        if 'price_usd_ohlc' in df.columns:
            print(f"  前5个值: {df['price_usd_ohlc'].iloc[:5].values}")
    else:
        print(f"  ✗ 数据获取失败")

def main():
    # 快速测试
    quick_test_endpoints()
    
    # 测试多维数据处理
    test_multidim_handling()

if __name__ == "__main__":
    main()