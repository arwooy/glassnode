#!/usr/bin/env python3
"""
Glassnode实际可用的端点列表
基于测试结果整理的有效端点
"""

# 成功测试的端点列表
WORKING_ENDPOINTS = {
    "addresses": {
        "name": "地址分析",
        "endpoints": [
            "active_count",              # ✓ 平均IG: 0.0836
            "new_non_zero_count",        # ✓ 平均IG: 0.0963
            "non_zero_count",            # ✓ 平均IG: 0.1434
            "min_1_count",               # ✓ 平均IG: 0.2060
            "min_10_count",              # ✓ 平均IG: 0.1694
            "min_1k_count",              # ✓ 平均IG: 0.1202
            "min_10k_count",             # ✓ 平均IG: 0.1799
            "receiving_count",           # ✓ 平均IG: 0.0769
            "sending_count",             # ✓ 平均IG: 0.0854
            "accumulation_count",        # ✓ 平均IG: 0.2234
            # 需要验证的端点:
            "accumulation_balance",
            "supply_distribution_relative",  # 替代 distribution_count
            "loss_count",
            "profit_count"
        ]
    },
    
    "blockchain": {
        "name": "区块链基础",
        "endpoints": [
            "utxo_created_count",        # ✓ 平均IG: 0.0641
            "utxo_spent_count",          # ✓ 平均IG: 0.0573
            "utxo_count",                # ✓ 平均IG: 0.1598
            "block_count",               # ✓ 平均IG: 0.0630
            "block_interval_median",     # ✓ 平均IG: 0.0564
            "block_size_mean",           # ✓ 平均IG: 0.0664
            "block_size_sum"             # ✓ 平均IG: 0.0666
        ]
    },
    
    "derivatives": {
        "name": "衍生品",
        "endpoints": [
            "futures_funding_rate_perpetual",           # ✓ 平均IG: 0.0762
            "futures_open_interest_sum",                # ✓ 平均IG: 0.1053
            "futures_open_interest_perpetual_sum",      # ✓ 平均IG: 0.0998
            "futures_volume_daily_sum",                 # ✓ 平均IG: 0.0636
            "futures_volume_daily_perpetual_sum",       # ✓ 平均IG: 0.0624
            "futures_liquidated_volume_long_sum",       # ✓ 平均IG: 0.0701
            "futures_liquidated_volume_short_sum",      # ✓ 平均IG: 0.0641
            "options_open_interest_put_call_ratio",     # ✓ 平均IG: 0.0969
            "options_volume_put_call_ratio"             # ✓ 平均IG: 0.0636
        ]
    },
    
    "distribution": {
        "name": "分布分析",
        "endpoints": [
            "exchange_net_position_change",   # ✓ 平均IG: 0.1087
            "balance_exchanges",               # ✓ 平均IG: 0.1553
            "balance_exchanges_relative",      # ✓ 平均IG: 0.1559
            "balance_miners_change",           # ✓ 平均IG: 0.0898
            # 修正的端点名称:
            "balance_exchanges_all",
            "balance_miners_sum",          # 替代 balance_miners
            "gini",                        # 替代 gini_coefficient
            "herfindahl"                   # 替代 herfindahl_index
        ]
    },
    
    "indicators": {
        "name": "核心指标",
        "endpoints": [
            "sopr",                              # ✓ 平均IG: 0.0718
            "sopr_adjusted",                     # ✓ 平均IG: 0.0717
            "reserve_risk",                      # ✓ 平均IG: 0.1726
            "cvdd",                              # ✓ 平均IG: 0.1891
            "net_unrealized_profit_loss",        # ✓ 平均IG: 0.1627
            "nupl_more_155",                     # ✓ 平均IG: 0.1797
            "average_dormancy",                  # ✓ 平均IG: 0.0690
            "liveliness",                        # ✓ 平均IG: 0.1562
            "unrealized_profit",                 # ✓ 平均IG: 0.1547
            "unrealized_loss",                   # ✓ 平均IG: 0.1511
            "realized_profit_loss_ratio",        # ✓ 平均IG: 0.0662
            "nvt",                               # ✓ 平均IG: 0.0692
            "nvts",                              # ✓ 平均IG: 0.1225
            "velocity",                          # ✓ 平均IG: 0.0693
            "rhodl_ratio",                       # ✓ 平均IG: 0.1445
            "balanced_price_usd",                # ✓ 平均IG: 0.1791
            "difficulty_ribbon_compression",     # ✓ 平均IG: 0.1152
            "cdd",                               # ✓ 平均IG: 0.0611
            "cdd_supply_adjusted",               # ✓ 平均IG: 0.0595
            "cdd_supply_adjusted_binary",        # ✓ 平均IG: 0.0000
            "average_dormancy_supply_adjusted",  # ✓ 平均IG: 0.0672
            "hodler_net_position_change",        # ✓ 平均IG: 0.1471
            "cyd_supply_adjusted",               # ✓ 平均IG: 0.2181
            "cyd_account_based",                 # ✓ 平均IG: 0.1603
            "cyd_account_based_supply_adjusted", # ✓ 平均IG: 0.1744
            "dormancy_account_based",            # ✓ 平均IG: 0.0721
            "asol",                              # ✓ 平均IG: 0.0741
            "msol"                               # ✓ 平均IG: 0.0618
        ]
    },
    
    "institutions": {
        "name": "机构指标",
        "endpoints": [
            "purpose_etf_holdings_sum",    # ✓ 平均IG: 0.1643
            "purpose_etf_flows_sum"         # ✓ 平均IG: 0.0484
        ]
    },
    
    "market": {
        "name": "市场数据",
        "endpoints": [
            "price_usd_close",            # ✓ 平均IG: 0.1909
            "marketcap_usd",              # ✓ 平均IG: 0.1876
            "marketcap_realized_usd",     # ✓ 平均IG: 0.1870
            "price_realized_usd",         # ✓ 平均IG: 0.1863
            "mvrv",                       # ✓ 平均IG: 0.1627
            "mvrv_z_score",               # ✓ 平均IG: 0.1591
            "price_drawdown_relative"     # ✓ 平均IG: 0.1654
        ]
    },
    
    "mining": {
        "name": "挖矿数据",
        "endpoints": [
            "hash_rate_mean",             # ✓ 平均IG: 0.0936
            "difficulty_latest",          # ✓ 平均IG: 0.1913
            "revenue_from_fees"           # ✓ 平均IG: 0.0855
        ]
    },
    
    "supply": {
        "name": "供应分析",
        "endpoints": [
            "current",                    # ✓ 平均IG: 0.1891
            "issued",                     # ✓ 平均IG: 0.0797
            "inflation_rate",             # ✓ 平均IG: 0.0806
            "liquid_change",              # ✓ 平均IG: 0.1187
            "active_more_10y"             # ✓ 平均IG: 0.1766
        ]
    },
    
    "transactions": {
        "name": "交易分析",
        "endpoints": [
            "count",                          # ✓ 平均IG: 0.0665
            "rate",                           # ✓ 平均IG: 0.0665
            "transfers_rate",                 # ✓ 平均IG: 0.0686
            "transfers_volume_sum",           # ✓ 平均IG: 0.0588
            "transfers_volume_mean",          # ✓ 平均IG: 0.0650
            "transfers_volume_median",        # ✓ 平均IG: 0.0798
            "transfers_to_exchanges_count",   # ✓ 平均IG: 0.0674
            "transfers_from_exchanges_count"  # ✓ 平均IG: 0.0800
        ]
    }
}

# 高信息增益指标（IG > 0.15）
TOP_IG_ENDPOINTS = [
    ("supply", "cyd_supply_adjusted", 0.2181),
    ("addresses", "accumulation_count", 0.2234),
    ("addresses", "min_1_count", 0.2060),
    ("market", "price_usd_close", 0.1909),
    ("mining", "difficulty_latest", 0.1913),
    ("indicators", "cvdd", 0.1891),
    ("supply", "current", 0.1891),
    ("market", "marketcap_usd", 0.1876),
    ("market", "marketcap_realized_usd", 0.1870),
    ("market", "price_realized_usd", 0.1863),
    ("indicators", "nupl_more_155", 0.1797),
    ("indicators", "balanced_price_usd", 0.1791),
    ("addresses", "min_10k_count", 0.1799),
    ("supply", "active_more_10y", 0.1766),
    ("indicators", "cyd_account_based_supply_adjusted", 0.1744),
    ("indicators", "reserve_risk", 0.1726),
    ("addresses", "min_10_count", 0.1694),
    ("market", "price_drawdown_relative", 0.1654),
    ("institutions", "purpose_etf_holdings_sum", 0.1643),
    ("indicators", "net_unrealized_profit_loss", 0.1627),
    ("market", "mvrv", 0.1627),
    ("indicators", "cyd_account_based", 0.1603),
    ("blockchain", "utxo_count", 0.1598),
    ("market", "mvrv_z_score", 0.1591),
    ("indicators", "liveliness", 0.1562),
    ("distribution", "balance_exchanges_relative", 0.1559),
    ("distribution", "balance_exchanges", 0.1553),
    ("indicators", "unrealized_profit", 0.1547),
    ("indicators", "unrealized_loss", 0.1511)
]

# TOP 5 指标（来自之前的分析）
TOP5_INDICATORS = {
    "reserve_risk": {
        "category": "indicators",
        "avg_ig": 0.1726,
        "30d_ig": 0.283,
        "description": "储备风险 - 长期持有者信心指标"
    },
    "mvrv_z_score": {
        "category": "market",
        "avg_ig": 0.1591,
        "7d_ig": 0.110,
        "description": "MVRV Z分数 - 市场估值指标"
    },
    "net_unrealized_profit_loss": {
        "category": "indicators",
        "avg_ig": 0.1627,
        "mi": 0.091,
        "description": "NUPL - 净未实现盈亏"
    },
    "mvrv": {
        "category": "market",
        "avg_ig": 0.1627,
        "30d_ig": 0.213,
        "description": "MVRV - 市值与实现价值比"
    },
    "hash_rate_mean": {
        "category": "mining",
        "avg_ig": 0.0936,
        "1d_ig": 0.079,
        "description": "哈希率 - 网络算力"
    }
}

def print_summary():
    """打印端点统计摘要"""
    total = 0
    for category, data in WORKING_ENDPOINTS.items():
        count = len(data["endpoints"])
        total += count
        print(f"{data['name']}: {count} 个端点")
    
    print(f"\n总计: {total} 个可用端点")
    print(f"高IG端点 (>0.15): {len(TOP_IG_ENDPOINTS)} 个")
    
    print("\n信息增益最高的前10个指标:")
    for endpoint, _, ig in TOP_IG_ENDPOINTS[:10]:
        print(f"  - {endpoint}: {ig:.4f}")

if __name__ == "__main__":
    print_summary()