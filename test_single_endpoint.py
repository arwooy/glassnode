#!/usr/bin/env python3
"""
测试单个Glassnode端点，查看可用的端点
"""

import requests
import os
from datetime import datetime, timedelta

api_key = os.getenv('GLASSNODE_API_KEY', '2lAMxffzOa2lPLbqI6NsBm39Bze')

def test_endpoint(category, metric):
    """测试单个端点"""
    # 使用正确的API域名和格式
    base_url = "https://grassnoodle.cloud"
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # 使用正确的请求格式
    headers = {"x-key": api_key}
    params = {
        "ticker": f"{category}:{metric}",
        "timeframe": "d",
        "from": int(start_date.timestamp()),
        "to": int(end_date.timestamp()),
        "timezone": "Asia/Shanghai"
    }
    
    print(f"\n测试端点: {category}/{metric}")
    print(f"URL: {base_url}")
    
    response = requests.get(base_url, params=params, headers=headers)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"✓ 成功获取 {len(data)} 条数据")
            if len(data) > 0:
                print(f"  示例数据: {data[0]}")
        else:
            print("✗ 返回空数据")
    else:
        print(f"✗ 错误: {response.text[:200]}")
    
    return response.status_code == 200

# 测试各种可能的价格端点
print("="*60)
print("测试Glassnode价格端点")
print("="*60)

test_endpoints = [
    ('market', 'price_usd_close'),
    ('market', 'price_usd'),
    ('market', 'close'),
    ('market', 'price'),
    ('market', 'price_usd_ohlc'),
    ('market', 'marketcap_usd'),
    ('market', 'mvrv')
]

successful = []

for category, metric in test_endpoints:
    if test_endpoint(category, metric):
        successful.append(f"{category}/{metric}")

print("\n" + "="*60)
print(f"成功的端点 ({len(successful)}):")
for ep in successful:
    print(f"  ✓ {ep}")

# 测试一些核心指标端点
print("\n" + "="*60)
print("测试核心指标端点")
print("="*60)

core_indicators = [
    ('indicators', 'sopr'),
    ('indicators', 'reserve_risk'),
    ('indicators', 'nupl'),
    ('market', 'mvrv_z_score'),
    ('mining', 'hash_rate_mean')
]

for category, metric in core_indicators:
    test_endpoint(category, metric)