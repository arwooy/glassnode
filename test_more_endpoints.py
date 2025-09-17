#!/usr/bin/env python3
"""
测试更多失败的端点，找出正确名称
"""

import requests
import time
from datetime import datetime, timedelta

API_KEY = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
headers = {"x-key": API_KEY}
base_url = "https://grassnoodle.cloud/v1/metrics"

def test_endpoint_variations(base_path, variations):
    """测试端点的各种变体"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    params = {
        'a': 'BTC',
        's': int(start_date.timestamp()),
        'u': int(end_date.timestamp()),
        'i': '24h'
    }
    
    for variation in variations:
        url = f"{base_url}/{variation}"
        try:
            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                return variation
            elif response.status_code == 429:
                time.sleep(2)
        except:
            pass
        time.sleep(0.5)
    return None

# 测试各类失败端点的可能变体
test_cases = {
    "distribution/gini": [
        "distribution/gini",
        "distribution/gini_coefficient", 
        "addresses/gini",
        "addresses/gini_coefficient",
    ],
    
    "distribution/herfindahl": [
        "distribution/herfindahl",
        "distribution/herfindahl_index",
        "addresses/herfindahl",
    ],
    
    "distribution/balance_1pct_holders": [
        "distribution/balance_1pct_holders",
        "addresses/balance_1pct_holders",
        "distribution/balance_top_one_pct",
        "addresses/balance_top_1_percent",
    ],
    
    "fees/gas_price_mean": [
        "fees/gas_price_mean",
        "fees/gas_mean",
        "fees/gas_price_average",
    ],
    
    "indicators/profit_relative": [
        "indicators/profit_relative",
        "indicators/relative_profit",
        "indicators/profit_percent",
        "addresses/profit_relative",
    ],
    
    "indicators/loss_relative": [
        "indicators/loss_relative",
        "indicators/relative_loss",
        "indicators/loss_percent",
        "addresses/loss_relative",
    ],
    
    "mining/hash_rate_30d_moving_average": [
        "mining/hash_rate_30d_moving_average",
        "mining/hash_rate_30d",
        "mining/hash_rate_ma30",
        "mining/hashrate_30dma",
    ],
    
    "supply/liquid": [
        "supply/liquid",
        "supply/liquid_supply",
        "supply/liquid_total",
    ],
    
    "supply/profit_total": [
        "supply/profit_total",
        "supply/profit_sum",
        "supply/total_profit",
        "supply/profit_count",
    ],
    
    "transactions/volume_sum": [
        "transactions/volume_sum",
        "transactions/volume_total",
        "transactions/transfer_volume_sum",
        "transactions/transfers_volume_sum",
    ],
    
    "mempool/mempool_count": [
        "mempool/mempool_count",
        "mempool/count",
        "mempool/tx_count",
        "mempool/transaction_count",
    ],
}

print("="*60)
print("测试失败端点的正确名称")
print("="*60)

found_endpoints = {}
not_found = []

for original, variations in test_cases.items():
    print(f"\n测试: {original}")
    correct = test_endpoint_variations(original, variations)
    
    if correct:
        print(f"  ✓ 找到: {correct}")
        found_endpoints[original] = correct
    else:
        print(f"  ✗ 未找到")
        not_found.append(original)

print("\n" + "="*60)
print("测试结果总结")
print("="*60)

print(f"\n成功找到: {len(found_endpoints)}/{len(test_cases)}")

if found_endpoints:
    print("\n正确的端点:")
    for original, correct in found_endpoints.items():
        if original != correct:
            print(f"  {original} → {correct}")
        else:
            print(f"  {original} ✓")

if not_found:
    print(f"\n未找到的端点 ({len(not_found)}):")
    for endpoint in not_found:
        print(f"  - {endpoint}")

# 保存结果
with open('endpoint_test_results.txt', 'w') as f:
    f.write("# 端点测试结果\n\n")
    f.write("## 找到的端点:\n")
    for original, correct in found_endpoints.items():
        f.write(f"{original} → {correct}\n")
    
    f.write("\n## 未找到的端点:\n")
    for endpoint in not_found:
        f.write(f"- {endpoint}\n")