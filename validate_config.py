#!/usr/bin/env python3
"""
验证Glassnode端点配置文件
"""

import json
import os

def validate_config():
    """验证配置文件完整性和正确性"""
    config_file = 'glassnode_endpoints_config.json'
    
    if not os.path.exists(config_file):
        print(f"❌ 配置文件 {config_file} 不存在")
        return False
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("="*60)
    print("Glassnode 端点配置验证")
    print("="*60)
    
    # 统计信息
    total_endpoints = 0
    categories_info = []
    
    for category, info in config.items():
        if 'name' not in info or 'endpoints' not in info:
            print(f"❌ 类别 {category} 缺少必要字段")
            return False
        
        endpoints_count = len(info['endpoints'])
        total_endpoints += endpoints_count
        categories_info.append((category, info['name'], endpoints_count))
    
    # 打印统计
    print(f"\n✅ 配置文件格式正确")
    print(f"   类别数量: {len(config)}")
    print(f"   总端点数: {total_endpoints}")
    
    print("\n### 类别详情 ###")
    print(f"{'类别ID':<20} {'类别名称':<20} {'端点数量':<10}")
    print("-"*60)
    for cat_id, cat_name, count in sorted(categories_info):
        print(f"{cat_id:<20} {cat_name:<20} {count:<10}")
    
    # 验证关键端点
    print("\n### 关键端点验证 ###")
    key_endpoints = [
        ("addresses", "accumulation_balance"),
        ("addresses", "min_point_1_count"),
        ("derivatives", "futures_annualized_basis_3m"),
        ("market", "price_usd_close"),
        ("indicators", "sopr"),
        ("supply", "current")
    ]
    
    all_valid = True
    for category, endpoint in key_endpoints:
        if category in config and endpoint in config[category]['endpoints']:
            print(f"✅ {category}/{endpoint}")
        else:
            print(f"❌ {category}/{endpoint} - 缺失")
            all_valid = False
    
    if all_valid:
        print("\n✅ 所有关键端点验证通过")
    else:
        print("\n⚠️ 某些关键端点缺失")
    
    # 检查重复端点
    print("\n### 重复端点检查 ###")
    has_duplicates = False
    for category, info in config.items():
        endpoints = info['endpoints']
        unique_endpoints = set(endpoints)
        if len(endpoints) != len(unique_endpoints):
            duplicates = [ep for ep in endpoints if endpoints.count(ep) > 1]
            print(f"⚠️ {category} 类别有重复端点: {set(duplicates)}")
            has_duplicates = True
    
    if not has_duplicates:
        print("✅ 没有发现重复端点")
    
    print("\n" + "="*60)
    print("验证完成")
    print("="*60)
    
    return True

if __name__ == "__main__":
    validate_config()