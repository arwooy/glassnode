#!/usr/bin/env python3
"""
Glassnode API 修正后的端点配置
基于实际测试结果的有效端点列表
"""

# 经过验证的有效端点
VERIFIED_ENDPOINTS = {
    "addresses": {
        "name": "地址分析",
        "endpoints": [
            "active_count",              # ✓ 已验证
            "new_non_zero_count",        # ✓ 已验证
            "non_zero_count",            # ✓ 已验证
            "min_1_count",               # ✓ 已验证
            "min_10_count",              # ✓ 已验证
            "min_100_count",             # ✓ 已验证 (有时超时)
            "min_1k_count",              # ✓ 已验证
            "min_10k_count",             # ✓ 已验证
            "receiving_count",           # ✓ 已验证
            "sending_count",             # ✓ 已验证
            "accumulation_count",        # ✓ 已验证
            "supply_distribution_relative", # ✓ 已验证 (返回o字段)
            "profit_relative",           # ✓ 已验证 (原indicators/profit_relative)
            "loss_count",                # ✓ 已验证
            "profit_count"               # ✓ 已验证
        ]
    },
    
    "blockchain": {
        "name": "区块链基础",
        "endpoints": [
            "utxo_created_count",        # ✓ 已验证
            "utxo_spent_count",          # ✓ 已验证
            "utxo_count",                # ✓ 已验证
            "utxo_created_value_sum",    # ✓ 已验证 (原utxo_total_value)
            "utxo_created_value_mean",   # 修正 (原utxo_mean_value)
            "utxo_created_value_median", # 修正 (原utxo_median_value)
            "block_count",               # ✓ 已验证
            "block_interval_median",     # ✓ 已验证
            "block_size_mean",           # ✓ 已验证
            "block_size_sum"             # ✓ 已验证
        ]
    },
    
    "derivatives": {
        "name": "衍生品",
        "endpoints": [
            "futures_funding_rate_perpetual",           # ✓ 已验证
            "futures_funding_rate_perpetual_all",       # ✓ 已验证 (有时超时)
            "futures_open_interest_sum",                # ✓ 已验证
            "futures_open_interest_perpetual_sum",      # ✓ 已验证
            "futures_volume_daily_sum",                 # ✓ 已验证
            "futures_volume_daily_perpetual_sum",       # ✓ 已验证
            "futures_liquidated_volume_long_sum",       # ✓ 已验证
            "futures_liquidated_volume_short_sum",      # ✓ 已验证
            "options_open_interest_put_call_ratio",     # ✓ 已验证
            "options_volume_put_call_ratio"             # ✓ 已验证
        ]
    },
    
    "distribution": {
        "name": "分布分析",
        "endpoints": [
            "exchange_net_position_change",   # ✓ 已验证
            "balance_exchanges",               # ✓ 已验证
            "balance_exchanges_relative",      # ✓ 已验证
            "balance_exchanges_all",           # ✓ 已验证
            "balance_miners_sum",              # ✓ 已验证
            "balance_miners_all",              # ✓ 已验证
            "balance_miners_change",           # ✓ 已验证
            "balance_otc_desks",              # ✓ 已验证
            "balance_mtgox_trustee",          # ✓ 已验证
            "balance_grayscale_trust",        # ✓ 已验证
            "exchange_aggregated_reliance_ratio",      # ✓ 已验证
            "exchange_aggregated_reshuffling_ratio"    # ✓ 已验证
        ]
    },
    
    "entities": {
        "name": "实体分析",
        "endpoints": [
            "active_count",              # ✓ 已验证 (原active_entities)
            # 其他entities端点大多数返回404或429
        ]
    },
    
    "fees": {
        "name": "手续费",
        "endpoints": [
            "volume_sum",                # ✓ 已验证 (原fees_total_usd)
            # 其他fees端点大多不可用（ETH专用）
        ]
    },
    
    "indicators": {
        "name": "核心指标",
        "endpoints": [
            "sopr",                              # ✓ 已验证
            "sopr_adjusted",                     # ✓ 已验证
            "sopr_account_based",                # ✓ 已验证
            "reserve_risk",                      # ✓ 已验证
            "cvdd",                              # ✓ 已验证
            "net_unrealized_profit_loss",        # ✓ 已验证
            "net_unrealized_profit_loss_account_based", # ✓ 已验证
            "nupl_more_155",                     # ✓ 已验证
            "nupl_less_155",                     # ✓ 已验证
            "average_dormancy",                  # ✓ 已验证
            "liveliness",                        # ✓ 已验证
            "unrealized_profit",                 # ✓ 已验证
            "unrealized_loss",                   # ✓ 已验证
            "realized_profit_loss_ratio",        # ✓ 已验证
            "nvt",                               # ✓ 已验证
            "nvts",                              # ✓ 已验证
            "velocity",                          # ✓ 已验证
            "rhodl_ratio",                       # ✓ 已验证
            "balanced_price_usd",                # ✓ 已验证
            "hash_ribbon",                       # ✓ 已验证 (有时超时)
            "difficulty_ribbon_compression",     # ✓ 已验证
            "cdd",                               # ✓ 已验证
            "cdd_supply_adjusted",               # ✓ 已验证
            "cdd_supply_adjusted_binary",        # ✓ 已验证
            "average_dormancy_supply_adjusted",  # ✓ 已验证
            "hodler_net_position_change",        # ✓ 已验证
            "cyd_supply_adjusted",               # ✓ 已验证
            "cyd_account_based",                 # ✓ 已验证
            "cyd_account_based_supply_adjusted", # ✓ 已验证
            "dormancy_account_based",            # ✓ 已验证
            "asol",                              # ✓ 已验证
            "msol",                              # ✓ 已验证
            "pi_cycle_top",                      # ✓ 已验证 (有时超时)
            "stock_to_flow_ratio",               # ✓ 已验证 (有时超时)
            "difficulty_ribbon"                  # ✓ 已验证 (有时超时)
        ]
    },
    
    "institutions": {
        "name": "机构指标",
        "endpoints": [
            "purpose_etf_holdings_sum",    # ✓ 已验证
            "purpose_etf_flows_sum"         # ✓ 已验证
            # 其他机构指标大多不可用或需要高级订阅
        ]
    },
    
    "market": {
        "name": "市场数据",
        "endpoints": [
            "price_usd_close",            # ✓ 已验证
            "price_usd_ohlc",             # ✓ 已验证 (返回o字段)
            "marketcap_usd",              # ✓ 已验证
            "marketcap_realized_usd",     # ✓ 已验证
            "price_realized_usd",         # ✓ 已验证 (原realized_price_usd)
            "mvrv",                       # ✓ 已验证
            "mvrv_z_score",               # ✓ 已验证
            "price_drawdown_relative"     # ✓ 已验证
            # thermocap等端点需要高级订阅
        ]
    },
    
    "mining": {
        "name": "挖矿数据",
        "endpoints": [
            "hash_rate_mean",             # ✓ 已验证
            "difficulty_latest",          # ✓ 已验证
            "revenue_from_fees",          # ✓ 已验证
            "thermocap"                   # ✓ 已验证 (有时429)
            # 其他mining端点大多不可用
        ]
    },
    
    "supply": {
        "name": "供应分析",
        "endpoints": [
            "current",                    # ✓ 已验证
            "issued",                     # ✓ 已验证
            "inflation_rate",             # ✓ 已验证
            "liquid_change",              # ✓ 已验证
            "liquid_illiquid_sum",        # ✓ 已验证 (有时超时)
            "active_more_10y",            # ✓ 已验证
            "profit_sum",                 # ✓ 已验证 (原profit_total)
            "profit_relative"             # ✓ 已验证 (有时429)
            # 其他供应端点大多不可用
        ]
    },
    
    "transactions": {
        "name": "交易分析",
        "endpoints": [
            "count",                          # ✓ 已验证
            "transfers_count",                # ✓ 已验证 (有时429)
            "transfers_rate",                 # ✓ 已验证
            "transfers_volume_sum",           # ✓ 已验证 (原volume_sum)
            "transfers_volume_mean",          # ✓ 已验证
            "transfers_volume_median",        # ✓ 已验证
            "transfers_from_exchanges_count"  # ✓ 已验证
            # transfers_to_exchanges_count等端点不可用
        ]
    }
}

# 端点修正映射（原名称 → 正确名称）
ENDPOINT_CORRECTIONS = {
    # Blockchain
    "blockchain/utxo_total_value": "blockchain/utxo_created_value_sum",
    "blockchain/utxo_mean_value": "blockchain/utxo_created_value_mean",
    "blockchain/utxo_median_value": "blockchain/utxo_created_value_median",
    
    # Entities
    "entities/active_entities": "entities/active_count",
    
    # Fees
    "fees/fees_total_usd": "fees/volume_sum",
    
    # Market
    "market/realized_price_usd": "market/price_realized_usd",
    
    # Indicators
    "indicators/profit_relative": "addresses/profit_relative",
    
    # Supply
    "supply/profit_total": "supply/profit_sum",
    
    # Transactions
    "transactions/volume_sum": "transactions/transfers_volume_sum",
}

# 多维数据端点（返回'o'字段而非'v'字段）
MULTIDIM_ENDPOINTS = [
    "addresses/supply_distribution_relative",
    "market/price_usd_ohlc",
    # 可能还有其他HODL waves等端点
]

# 需要高级订阅的端点
PREMIUM_ENDPOINTS = [
    "market/thermocap",
    "market/thermocap_multiple",
    "market/thermocap_price",
    "institutions/grayscale_holdings_sum",
    "institutions/grayscale_flows_sum",
    # 更多机构数据端点
]

# 统计信息
def print_statistics():
    """打印端点统计"""
    total = 0
    for category, data in VERIFIED_ENDPOINTS.items():
        count = len(data["endpoints"])
        total += count
        print(f"{data['name']}: {count} 个端点")
    
    print(f"\n总计: {total} 个验证有效端点")
    print(f"端点修正: {len(ENDPOINT_CORRECTIONS)} 个")
    print(f"多维数据端点: {len(MULTIDIM_ENDPOINTS)} 个")
    print(f"高级订阅端点: {len(PREMIUM_ENDPOINTS)} 个")

if __name__ == "__main__":
    print("="*60)
    print("Glassnode API 端点验证结果")
    print("="*60)
    print()
    print_statistics()