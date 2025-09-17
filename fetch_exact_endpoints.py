#!/usr/bin/env python3
"""
从Glassnode API文档获取精确的端点列表
"""

# 这是从API文档页面提取的完整端点列表
# 按照 https://docs.glassnode.com/basic-api/endpoints 的精确顺序

GLASSNODE_EXACT_ENDPOINTS = {
    "addresses": [
        "accumulation_balance",
        "accumulation_count",
        "active_count",
        "active_recurrent_count",
        "count",
        "loss_count",
        "min_point_zero_1_count",
        "min_point_1_count", 
        "min_1_count",
        "min_10_count",
        "min_100_count",
        "min_1k_count",
        "min_10k_count",
        "min_32_count",
        "min_1_usd_count",
        "min_10_usd_count",
        "min_100_usd_count",
        "min_1k_usd_count",
        "min_10k_usd_count",
        "min_100k_usd_count",
        "min_1m_usd_count",
        "min_10m_usd_count",
        "new_count",
        "non_zero_count",
        "profit_count",
        "profit_relative",
        "receiving_count",
        "receiving_from_exchanges_count",
        "sending_count",
        "sending_to_exchanges_count",
        "supply_distribution_relative",
        "zero_balance_count"
    ],
    
    "blockchain": [
        "block_count",
        "block_height", 
        "block_interval_mean",
        "block_interval_median",
        "block_size_mean",
        "block_size_sum",
        "utxo_count",
        "utxo_created_count",
        "utxo_created_value_mean",
        "utxo_created_value_median",
        "utxo_created_value_sum",
        "utxo_loss_count",
        "utxo_mean",
        "utxo_profit_count",
        "utxo_profit_relative",
        "utxo_spent_count",
        "utxo_spent_value_mean",
        "utxo_spent_value_median",
        "utxo_spent_value_sum"
    ],
    
    "derivatives": [
        "futures_annualized_basis_3m",
        "futures_estimated_leverage_ratio",
        "futures_funding_rate_perpetual",
        "futures_funding_rate_perpetual_all",
        "futures_liquidated_volume_long_mean",
        "futures_liquidated_volume_long_relative",
        "futures_liquidated_volume_long_sum",
        "futures_liquidated_volume_short_mean",
        "futures_liquidated_volume_short_relative", 
        "futures_liquidated_volume_short_sum",
        "futures_open_interest_cash_margin_relative",
        "futures_open_interest_crypto_margin_relative",
        "futures_open_interest_crypto_margin_sum",
        "futures_open_interest_latest",
        "futures_open_interest_perpetual_sum",
        "futures_open_interest_sum",
        "futures_open_interest_sum_all",
        "futures_term_structure",
        "futures_term_structure_by_exchange",
        "futures_volume_buy_sum",
        "futures_volume_buy_daily_sum",
        "futures_volume_buy_perpetual_sum", 
        "futures_volume_buy_daily_perpetual_sum",
        "futures_volume_daily_latest",
        "futures_volume_daily_perpetual_sum",
        "futures_volume_daily_sum",
        "futures_volume_daily_sum_all",
        "futures_volume_perpetual_sum",
        "futures_volume_sell_sum",
        "futures_volume_sell_daily_sum",
        "futures_volume_sell_perpetual_sum",
        "futures_volume_sell_daily_perpetual_sum",
        "futures_volume_sum",
        "options_25d_skew_all",
        "options_atm_implied_volatility_all",
        "options_dvol",
        "options_flow_put_call_ratio",
        "options_gex",
        "options_implied_volatility_term_structure",
        "options_open_interest_put_call_ratio",
        "options_open_interest_sum",
        "options_volume_put_call_ratio",
        "options_volume_sum"
    ],
    
    "distribution": [
        "balance_1pct_holders",
        "balance_exchanges",
        "balance_exchanges_all",
        "balance_exchanges_relative",
        "balance_miners_all",
        "balance_miners_change",
        "balance_miners_sum",
        "balance_otc_desks",
        "balance_us_government",
        "exchange_net_position_change",
        "gini",
        "herfindahl", 
        "supply_contracts"
    ],
    
    "entities": [
        "min_001_count",
        "min_01_count",
        "min_1_count",
        "min_10_count",
        "min_100_count",
        "min_1k_count",
        "min_10k_count",
        "net_growth_count",
        "new_count",
        "profit_relative",
        "receiving_count",
        "sending_count",
        "supply_balance_less_001",
        "supply_balance_001_01",
        "supply_balance_01_1",
        "supply_balance_1_10",
        "supply_balance_10_100",
        "supply_balance_100_1k",
        "supply_balance_1k_10k",
        "supply_balance_more_10k"
    ],
    
    "eth2": [
        "staking_deposits_count",
        "staking_phase_0_goal_percent",
        "staking_total_deposits_count",
        "staking_total_value_staked",
        "staking_total_validators_count",
        "staking_validators_count",
        "staking_value_staked_sum"
    ],
    
    "fees": [
        "exchanges_deposits_fee_spending_relative",
        "exchanges_withdrawals_fee_spending_relative",
        "fee_ratio_multiple",
        "gas_limit_tx_mean",
        "gas_limit_tx_median",
        "gas_price_mean",
        "gas_price_median",
        "gas_used_mean",
        "gas_used_sum",
        "revenue_sum",
        "volume_mean",
        "volume_median",
        "volume_sum"
    ],
    
    "indicators": [
        "asol",
        "average_dormancy",
        "average_dormancy_supply_adjusted",
        "balanced_price_usd",
        "bvin",
        "cdd",
        "cdd_supply_adjusted",
        "cdd_supply_adjusted_binary",
        "cvdd",
        "cyd_supply_adjusted",
        "difficulty_ribbon",
        "difficulty_ribbon_compression",
        "dormancy",
        "hash_ribbon",
        "hodl_waves",
        "hodler_net_position_change",
        "liveliness",
        "msol",
        "net_unrealized_profit_loss",
        "nupl_less_155",
        "nupl_more_155",
        "nvt",
        "nvts",
        "pi_cycle_top",
        "realized_loss",
        "realized_profit",
        "realized_profit_loss_ratio",
        "reserve_risk",
        "rhodl_ratio",
        "sopr",
        "sopr_adjusted",
        "sopr_less_155_coin_adj",
        "sopr_more_155_coin_adj",
        "spent_output_age_bands",
        "sth_lth_profit_loss_ratio",
        "stock_to_flow_deflection",
        "stock_to_flow_ratio",
        "unrealized_loss",
        "unrealized_profit",
        "velocity"
    ],
    
    "institutions": [
        "purpose_etf_flows_sum",
        "purpose_etf_holdings_sum"
    ],
    
    "lightning": [
        "average_capacity",
        "average_fee_rate",
        "channel_count",
        "network_capacity",
        "node_count"
    ],
    
    "market": [
        "marketcap_realized_usd",
        "marketcap_usd",
        "mvrv",
        "mvrv_less_155",
        "mvrv_more_155",
        "mvrv_z_score",
        "price_drawdown_relative",
        "price_realized_usd",
        "price_usd_close",
        "price_usd_ohlc"
    ],
    
    "mempool": [
        "count",
        "fees_median",
        "fees_total",
        "size",
        "value_median",
        "value_total"
    ],
    
    "mining": [
        "difficulty_latest",
        "hash_rate_mean",
        "hash_price",
        "miners_revenue_sum",
        "puell_multiple",
        "revenue_from_fees",
        "thermocap"
    ],
    
    "supply": [
        "active_24h",
        "active_1d_1w",
        "active_1w_1m",
        "active_1m_3m",
        "active_3m_6m",
        "active_6m_12m",
        "active_1y_2y",
        "active_2y_3y",
        "active_3y_5y",
        "active_5y_7y",
        "active_7y_10y",
        "active_more_10y",
        "circulating",
        "current",
        "highly_liquid_sum",
        "illiquid_change",
        "illiquid_sum",
        "inflation_rate",
        "issued",
        "liquid_change",
        "liquid_sum",
        "lth_net_position_change",
        "lth_sum",
        "profit_relative",
        "profit_sum",
        "rcap_hodl_waves",
        "revived_more_1y",
        "sth_net_position_change",
        "sth_sum"
    ],
    
    "transactions": [
        "count",
        "rate",
        "transfers_count",
        "transfers_from_exchanges_count",
        "transfers_rate",
        "transfers_to_exchanges_count",
        "transfers_volume_adjusted_mean",
        "transfers_volume_adjusted_median",
        "transfers_volume_adjusted_sum",
        "transfers_volume_exchanges_net",
        "transfers_volume_from_exchanges_mean",
        "transfers_volume_from_exchanges_sum",
        "transfers_volume_mean",
        "transfers_volume_median",
        "transfers_volume_sum",
        "transfers_volume_to_exchanges_mean",
        "transfers_volume_to_exchanges_sum"
    ]
}

def print_statistics():
    """打印统计信息"""
    print("Glassnode API 精确端点统计")
    print("="*60)
    
    total = 0
    for category, endpoints in GLASSNODE_EXACT_ENDPOINTS.items():
        count = len(endpoints)
        total += count
        print(f"{category:20} {count:4} 个端点")
    
    print("-"*60)
    print(f"{'总计':20} {total:4} 个端点")
    
    # 检查特定端点
    print("\n检查特定端点:")
    check_endpoints = [
        ("derivatives", "futures_annualized_basis_3m"),
        ("addresses", "accumulation_balance")
    ]
    
    for category, endpoint in check_endpoints:
        if endpoint in GLASSNODE_EXACT_ENDPOINTS.get(category, []):
            print(f"✓ {category}/{endpoint} 存在")
        else:
            print(f"✗ {category}/{endpoint} 缺失")

if __name__ == "__main__":
    print_statistics()