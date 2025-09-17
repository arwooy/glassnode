#!/usr/bin/env python3
"""
修正Glassnode端点名称
根据API文档和测试结果更新端点列表
"""

import requests
import time
from datetime import datetime, timedelta

API_KEY = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
headers = {"x-key": API_KEY}
base_url = "https://grassnoodle.cloud/v1/metrics"

# 可能的端点名称修正映射
ENDPOINT_CORRECTIONS = {
    # Blockchain endpoints
    "blockchain/utxo_total_value": [
        "blockchain/utxo_created_value_sum",
        "blockchain/utxo_value_created_sum", 
        "blockchain/utxo_profit_relative",
    ],
    "blockchain/utxo_mean_value": [
        "blockchain/utxo_created_value_mean",
        "blockchain/utxo_value_created_mean",
        "blockchain/utxo_mean",
    ],
    "blockchain/utxo_median_value": [
        "blockchain/utxo_created_value_median",
        "blockchain/utxo_value_created_median",
        "blockchain/utxo_median",
    ],
    
    # Entities endpoints
    "entities/sending_entities_count": [
        "entities/sending_count",
        "entities/senders_count",
        "entities/active_sending",
    ],
    "entities/receiving_entities_count": [
        "entities/receiving_count",
        "entities/receivers_count",
        "entities/active_receiving",
    ],
    "entities/active_entities": [
        "entities/active",
        "entities/active_count",
        "entities/count",
    ],
    "entities/new_entities": [
        "entities/new",
        "entities/new_count",
        "entities/net_growth",
    ],
    
    # Fees endpoints  
    "fees/fees_total_usd": [
        "fees/volume_sum",
        "fees/fee_total",
        "fees/total_usd",
    ],
    "fees/fees_mean_usd": [
        "fees/volume_mean",
        "fees/fee_mean",
        "fees/mean_usd",
    ],
    
    # Indicators
    "indicators/sopr": [
        "indicators/sopr",
        "indicators/spent_output_profit_ratio",
    ],
    
    # Market
    "market/realized_price_usd": [
        "market/price_realized_usd",
        "market/realized_price",
    ],
    "market/thermocap": [
        "market/thermo_cap",
        "market/thermocap_price",
    ],
    
    # Mining
    "mining/revenue_from_fees": [
        "mining/revenue_fee",
        "mining/fee_revenue",
        "mining/fees_percent",
    ],
    
    # Supply
    "supply/llth": [
        "supply/lth",
        "supply/long_term_holder_supply",
        "supply/hodler_net_position",
    ],
    
    # Transactions
    "transactions/rate": [
        "transactions/transfers_rate",
        "transactions/tx_rate",
    ],
}

def test_endpoint(category, metric):
    """测试单个端点"""
    url = f"{base_url}/{category}/{metric}"
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    params = {
        'a': 'BTC',
        's': int(start_date.timestamp()),
        'u': int(end_date.timestamp()),
        'i': '24h'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        return response.status_code == 200
    except:
        return False

def find_correct_endpoint(failed_endpoint):
    """尝试找到正确的端点名称"""
    print(f"\n测试: {failed_endpoint}")
    
    # 如果在修正映射中
    if failed_endpoint in ENDPOINT_CORRECTIONS:
        alternatives = ENDPOINT_CORRECTIONS[failed_endpoint]
        for alt in alternatives:
            parts = alt.split('/')
            if len(parts) == 2:
                if test_endpoint(parts[0], parts[1]):
                    print(f"  ✓ 找到正确端点: {alt}")
                    return alt
                else:
                    print(f"  ✗ {alt}")
            time.sleep(0.5)
    
    # 尝试一些通用的名称变换
    parts = failed_endpoint.split('/')
    if len(parts) == 2:
        category, metric = parts
        
        # 尝试去掉前缀
        alternatives = []
        if metric.startswith('fees_'):
            alternatives.append(f"{category}/{metric.replace('fees_', '')}")
        if metric.startswith('entities_'):
            alternatives.append(f"{category}/{metric.replace('entities_', '')}")
        if '_usd' in metric:
            alternatives.append(f"{category}/{metric.replace('_usd', '')}")
        
        # 尝试简化名称
        if '_' in metric:
            simplified = metric.split('_')[0]
            alternatives.append(f"{category}/{simplified}")
        
        for alt in alternatives:
            parts = alt.split('/')
            if len(parts) == 2:
                if test_endpoint(parts[0], parts[1]):
                    print(f"  ✓ 找到正确端点: {alt}")
                    return alt
                time.sleep(0.5)
    
    print(f"  ✗ 未找到正确端点")
    return None

def main():
    # 优先测试的失败端点
    priority_failed = [
        "indicators/sopr",
        "market/realized_price_usd",
        "entities/active_entities",
        "fees/fees_total_usd",
        "supply/llth",
        "mining/revenue_from_fees",
        "blockchain/utxo_total_value",
    ]
    
    print("="*60)
    print("查找正确的端点名称")
    print("="*60)
    
    corrections = {}
    
    for endpoint in priority_failed:
        correct = find_correct_endpoint(endpoint)
        if correct:
            corrections[endpoint] = correct
    
    print("\n" + "="*60)
    print("端点修正总结")
    print("="*60)
    
    if corrections:
        print("\n找到的正确端点:")
        for wrong, correct in corrections.items():
            print(f"  {wrong} → {correct}")
    else:
        print("\n未找到任何修正")
    
    # 保存修正结果
    with open('endpoint_corrections.txt', 'w') as f:
        f.write("# Glassnode端点修正\n\n")
        for wrong, correct in corrections.items():
            f.write(f"{wrong} → {correct}\n")

if __name__ == "__main__":
    main()