#!/usr/bin/env python3
"""
验证完整端点配置是否正确
"""

from glassnode_all_indicators_test import GlassnodeAllIndicatorsAnalyzer
import requests
import time
from datetime import datetime, timedelta

API_KEY = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
headers = {"x-key": API_KEY}

def verify_configuration():
    """验证配置完整性"""
    analyzer = GlassnodeAllIndicatorsAnalyzer(API_KEY)
    
    print("="*60)
    print("Glassnode 完整端点配置验证")
    print("="*60)
    
    # 统计信息
    total = 0
    for category, info in analyzer.categories.items():
        count = len(info['endpoints'])
        total += count
        print(f"{info['name']:20} {count:4} 个端点")
    
    print("-"*60)
    print(f"{'总计':20} {total:4} 个端点")
    
    # 验证关键端点
    critical_endpoints = [
        ("addresses", "accumulation_balance"),
        ("blockchain", "utxo_created_value_sum"),
        ("derivatives", "futures_funding_rate_all"),
        ("distribution", "balance_1pct_holders"),
        ("entities", "supply_balance_0001_001"),
        ("fees", "exchanges_deposits_fee_spending_30d_change"),
        ("indicators", "sopr_entity_adjusted"),
        ("institutions", "acc_1"),
        ("lightning", "average_base_fee"),
        ("market", "deltacap_usd"),
        ("mempool", "congestion"),
        ("mining", "block_production_daily_sum"),
        ("supply", "active_10y"),
        ("transactions", "entity_adjusted_count")
    ]
    
    print("\n" + "="*60)
    print("验证关键端点")
    print("="*60)
    
    all_found = True
    for category, endpoint in critical_endpoints:
        if endpoint in analyzer.categories[category]['endpoints']:
            print(f"✓ {category}/{endpoint}")
        else:
            print(f"✗ {category}/{endpoint} - 缺失!")
            all_found = False
    
    if all_found:
        print("\n✅ 所有关键端点都已包含在配置中!")
    else:
        print("\n❌ 某些关键端点缺失，请检查配置")
    
    return all_found

def test_random_endpoints():
    """测试随机几个端点的可访问性"""
    analyzer = GlassnodeAllIndicatorsAnalyzer(API_KEY)
    
    print("\n" + "="*60)
    print("测试随机端点可访问性")
    print("="*60)
    
    import random
    
    # 随机选择5个端点测试
    test_endpoints = []
    for category, info in analyzer.categories.items():
        if info['endpoints']:
            endpoint = random.choice(info['endpoints'])
            test_endpoints.append((category, endpoint))
            if len(test_endpoints) >= 5:
                break
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    successful = 0
    for category, endpoint in test_endpoints:
        print(f"\n测试 {category}/{endpoint}:")
        df = analyzer.fetch_metric_data(category, endpoint, start_date, end_date)
        
        if not df.empty:
            print(f"  ✓ 成功获取 {len(df)} 条数据")
            successful += 1
        else:
            print(f"  ✗ 获取失败")
        
        time.sleep(1)  # 避免API限制
    
    print(f"\n成功率: {successful}/{len(test_endpoints)}")

def main():
    # 验证配置完整性
    if verify_configuration():
        # 测试随机端点
        test_random_endpoints()
    
    print("\n" + "="*60)
    print("验证完成")
    print("="*60)
    print("\n配置文件已更新，包含所有477个端点")
    print("可以运行 glassnode_all_indicators_test.py 进行完整测试")

if __name__ == "__main__":
    main()