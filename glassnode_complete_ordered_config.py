#!/usr/bin/env python3
"""
Glassnode API 完整端点配置 - 按API文档精确顺序
基于 https://docs.glassnode.com/basic-api/endpoints
"""

# 完整的端点配置，按API文档顺序排列，包括所有已知端点
GLASSNODE_COMPLETE_ENDPOINTS = {
    "addresses": {
        "name": "地址分析", 
        "endpoints": [
            # 按文档顺序
            "accumulation_balance",
            "accumulation_count",
            "active_count",
            "active_count_with_contracts",
            "active_recurrent_count",
            "activity_retention_rate",
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
        ]
    },
    
    "blockchain": {
        "name": "区块链基础",
        "endpoints": [
            # Block metrics
            "block_count",
            "block_height",
            "block_interval_mean",
            "block_interval_median",
            "block_size_mean",
            "block_size_sum",
            "block_volume_mean",
            "block_volume_median",
            "block_volume_sum",
            "block_weight_mean",
            "block_weight_sum",
            # UTXO metrics
            "utxo_count",
            "utxo_created_count",
            "utxo_created_value_mean",
            "utxo_created_value_median",
            "utxo_created_value_sum",
            "utxo_loss_count",
            "utxo_mean",
            "utxo_median",
            "utxo_profit_count",
            "utxo_profit_relative",
            "utxo_realized_price_distribution_ath",
            "utxo_realized_price_distribution_relative",
            "utxo_spent_count",
            "utxo_spent_value_mean",
            "utxo_spent_value_median",
            "utxo_spent_value_sum",
            "utxo_sum"
        ]
    },
    
    "derivatives": {
        "name": "衍生品",
        "endpoints": [
            # Futures - Basis
            "futures_annualized_basis_3m",
            # Futures - Estimated Leverage
            "futures_estimated_leverage_ratio",
            # Futures - Funding Rates
            "futures_funding_rate_all",
            "futures_funding_rate_perpetual",
            "futures_funding_rate_perpetual_all",
            # Futures - Liquidations
            "futures_liquidated_volume_long_mean",
            "futures_liquidated_volume_long_relative",
            "futures_liquidated_volume_long_sum",
            "futures_liquidated_volume_long_window_sum",
            "futures_liquidated_volume_short_mean",
            "futures_liquidated_volume_short_relative",
            "futures_liquidated_volume_short_sum",
            "futures_liquidated_volume_short_window_sum",
            # Futures - Open Interest
            "futures_open_interest_cash_margin_relative",
            "futures_open_interest_cash_margin_sum",
            "futures_open_interest_crypto_margin_relative",
            "futures_open_interest_crypto_margin_sum",
            "futures_open_interest_current_relative",
            "futures_open_interest_latest",
            "futures_open_interest_liquidation_sum",
            "futures_open_interest_perpetual_sum",
            "futures_open_interest_stablecoin_margin_relative",
            "futures_open_interest_stablecoin_margin_sum",
            "futures_open_interest_sum",
            "futures_open_interest_sum_all",
            # Futures - Term Structure
            "futures_term_structure",
            "futures_term_structure_by_exchange",
            "futures_term_structure_relative",
            # Futures - Volume
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
            # Options
            "options_25d_skew",
            "options_25d_skew_all",
            "options_atm_implied_volatility_all",
            "options_contract_prices",
            "options_dvol",
            "options_dvol_bitmex",
            "options_dvol_bybit",
            "options_dvol_deribit",
            "options_dvol_okex",
            "options_flow_put_call_ratio",
            "options_gex",
            "options_gex_1pct",
            "options_implied_volatility_term_structure",
            "options_open_interest_distribution",
            "options_open_interest_put_call_ratio",
            "options_open_interest_strike_all",
            "options_open_interest_sum",
            "options_skew",
            "options_skew_all",
            "options_volume_daily_sum",
            "options_volume_put_call_ratio",
            "options_volume_put_call_ratio_relative",
            "options_volume_strike_all",
            "options_volume_sum"
        ]
    },
    
    "distribution": {
        "name": "分布分析",
        "endpoints": [
            # Balance metrics
            "balance_1pct_holders",
            "balance_bhutan_government",
            "balance_bitwise",
            "balance_blackrock",
            "balance_cashapp",
            "balance_donald_trump",
            "balance_el_salvador",
            "balance_exchanges",
            "balance_exchanges_all",
            "balance_exchanges_relative",
            "balance_franklin_templeton",
            "balance_german_government",
            "balance_grayscale_trust",
            "balance_luna_foundation_guard",
            "balance_miners_all",
            "balance_miners_change",
            "balance_miners_sum",
            "balance_mtgox_trustee",
            "balance_otc_desks",
            "balance_paypal",
            "balance_revolut",
            "balance_robinhood",
            "balance_tesla",
            "balance_tether_treasury",
            "balance_uk_government",
            "balance_us_government",
            "balance_vaneck",
            "balance_wbtc",
            "balance_wisdomtree",
            # Exchange metrics
            "exchange_aggregated_reliance_ratio",
            "exchange_aggregated_reshuffling_ratio",
            "exchange_net_position_change",
            "exchange_reliance_ratio",
            "exchange_reshuffling_ratio",
            "exchange_whales_outflow",
            # Distribution metrics
            "gini",
            "herfindahl",
            # Other
            "outflows_mtgox_trustee",
            "proof_of_reserves",
            "proof_of_reserves_all",
            "proof_of_reserves_all_latest",
            "supply_contracts"
        ]
    },
    
    "entities": {
        "name": "实体分析",
        "endpoints": [
            "active",
            "active_count",
            "min_001_count",
            "min_01_count",
            "min_1_count",
            "min_10_count",
            "min_100_count",
            "min_1k_count",
            "min_10k_count",
            "min_100k_count",
            "net_growth",
            "net_growth_count",
            "new",
            "new_count",
            "profit_relative",
            "receiving_count",
            "sending_count",
            "supply_balance_less_0001",
            "supply_balance_0001_001",
            "supply_balance_001_01",
            "supply_balance_01_1",
            "supply_balance_1_10",
            "supply_balance_10_100",
            "supply_balance_100_1k",
            "supply_balance_1k_10k",
            "supply_balance_10k_100k",
            "supply_balance_more_100k"
        ]
    },
    
    "eth2": {
        "name": "ETH2.0",
        "endpoints": [
            "staking_deposits_count",
            "staking_phase_0_goal_percent",
            "staking_total_deposits_count",
            "staking_total_value_staked",
            "staking_total_validators_count",
            "staking_validators_count",
            "staking_value_staked_sum"
        ]
    },
    
    "fees": {
        "name": "手续费",
        "endpoints": [
            "exchanges_deposits_fee_spending_30d_change",
            "exchanges_deposits_fee_spending_relative",
            "exchanges_deposits_stacking_90d",
            "exchanges_withdrawals_fee_spending_30d_change",
            "exchanges_withdrawals_fee_spending_relative",
            "exchanges_withdrawals_stacking_90d",
            "fee_ratio_multiple",
            "gas_limit_tx_mean",
            "gas_limit_tx_median",
            "gas_price_mean",
            "gas_price_median",
            "gas_used_mean",
            "gas_used_sum",
            "miners_revenue_fee_percentage_all",
            "revenue_sum",
            "segwit_spending_rate",
            "segwit_spending_sum",
            "segwit_spending_total",
            "segwit_usage_count",
            "segwit_usage_total",
            "volume_mean",
            "volume_median",
            "volume_sum",
            "volume_total"
        ]
    },
    
    "indicators": {
        "name": "核心指标",
        "endpoints": [
            # Supply Dynamics
            "asol",
            "average_coin_age",
            "average_dormancy",
            "average_dormancy_supply_adjusted",
            "average_spent_output_lifespan",
            # Market Value
            "balanced_price_usd",
            "bvin",
            # Coin Days
            "cdd",
            "cdd_account_based",
            "cdd_supply_adjusted",
            "cdd_supply_adjusted_binary",
            "cvdd",
            "cyd_account_based",
            "cyd_account_based_supply_adjusted",
            "cyd_supply_adjusted",
            # Mining Indicators
            "difficulty_ribbon",
            "difficulty_ribbon_compression",
            # Dormancy
            "dormancy",
            "dormancy_account_based",
            # Hash Ribbon
            "hash_ribbon",
            # HODL
            "hodl_waves",
            "hodler_net_position_change",
            # Liveliness
            "liveliness",
            # LTH/STH
            "lth_activated_supply",
            "lth_activated_supply_sum",
            "lth_net_position_change",
            "lth_sum_coin_age",
            "lth_sum_coin_age_usd",
            "lth_supply_loss_sum",
            "lth_supply_profit_loss_relative",
            "lth_supply_profit_sum",
            # MSOL
            "msol",
            # NUPL
            "net_unrealized_profit_loss",
            "net_unrealized_profit_loss_account_based",
            "nupl_less_155",
            "nupl_more_155",
            # NVT
            "nvt",
            "nvt_entity_adjusted",
            "nvts",
            # Pi Cycle
            "pi_cycle_top",
            # Profit/Loss
            "profit_relative",
            "loss_relative",
            "realized_hodl_ratio",
            "realized_loss",
            "realized_profit",
            "realized_profit_loss_ratio",
            # Reserve Risk
            "reserve_risk",
            # RHODL
            "rhodl_ratio",
            # SOPR
            "sopr",
            "sopr_account_based",
            "sopr_adjusted",
            "sopr_entity_adjusted",
            "sopr_less_155_coin_adj",
            "sopr_more_155_coin_adj",
            # Spent Output
            "spent_output_age_bands",
            # STH
            "sth_lth_profit_loss_ratio",
            "sth_net_position_change",
            "sth_sum_coin_age",
            "sth_sum_coin_age_usd",
            "sth_supply_loss_sum",
            "sth_supply_profit_loss_relative",
            "sth_supply_profit_sum",
            # Stock to Flow
            "stock_to_flow_deflection",
            "stock_to_flow_ratio",
            # Unrealized P/L
            "unrealized_loss",
            "unrealized_profit",
            # Other
            "vaulted_price",
            "velocity"
        ]
    },
    
    "institutions": {
        "name": "机构指标",
        "endpoints": [
            # Accumulation Addresses
            "acc_1",
            "acc_2",
            "acc_3",
            "acc_4",
            "acc_5",
            "acc_6",
            # Leveraged Products
            "btc_2x_fli_supply",
            "btc_2x_fli_supply_net_change",
            # ETFs
            "etf_0x21co",
            "etf_21co_flows",
            "etf_21shares",
            "etf_21shares_flows",
            "etf_3iq",
            "etf_3iq_flows",
            "etf_arkb",
            "etf_arkb_flows",
            "etf_bitwise",
            "etf_bitwise_flows",
            "etf_btc",
            "etf_btc_flows",
            "etf_btco",
            "etf_btco_flows",
            "etf_btcw",
            "etf_btcw_flows",
            "etf_brrr",
            "etf_brrr_flows",
            "etf_defi",
            "etf_defi_flows",
            "etf_ezbc",
            "etf_ezbc_flows",
            "etf_fbtc",
            "etf_fbtc_flows",
            "etf_gbtc",
            "etf_gbtc_flows",
            "etf_hodl",
            "etf_hodl_flows",
            "etf_ibit",
            "etf_ibit_flows",
            "etf_qbtc",
            "etf_qbtc_flows",
            # Purpose ETF
            "purpose_etf_flows_sum",
            "purpose_etf_holdings_sum"
        ]
    },
    
    "lightning": {
        "name": "闪电网络",
        "endpoints": [
            "average_base_fee",
            "average_capacity",
            "average_fee_rate",
            "average_size",
            "base_fee_histogram",
            "capacity_histogram",
            "channel_count",
            "channel_size_histogram",
            "fee_rate_histogram",
            "gini_capacity_distribution",
            "gini_channel_distribution",
            "herfindahl_capacity_distribution",
            "herfindahl_channel_distribution",
            "network_capacity",
            "node_connectivity_histogram",
            "node_count"
        ]
    },
    
    "market": {
        "name": "市场数据",
        "endpoints": [
            "close",
            "deltacap_usd",
            "high",
            "low",
            "marketcap_realized_usd",
            "marketcap_thermocap_ratio",
            "marketcap_usd",
            "mvrv",
            "mvrv_account_based",
            "mvrv_less_155",
            "mvrv_more_155",
            "mvrv_z_score",
            "open",
            "price_ath",
            "price_drawdown_relative",
            "price_realized_mean",
            "price_realized_usd",
            "price_usd_close",
            "price_usd_ohlc",
            "realized_cap_hodl_waves",
            "realized_price",
            "thermocap_multiple_4",
            "thermocap_price",
            "thermocap_price_multiple_2",
            "thermocap_price_multiple_4",
            "thermocap_price_multiple_8",
            "thermocap_price_multiple_16",
            "thermocap_price_multiple_32",
            "volume_buyside_usd",
            "volume_sellside_usd"
        ]
    },
    
    "mempool": {
        "name": "内存池",
        "endpoints": [
            "congestion",
            "count",
            "fees_average",
            "fees_average_relative",
            "fees_median",
            "fees_median_relative",
            "fees_total",
            "growth",
            "size",
            "spending_rate",
            "spending_total",
            "spending_value_average",
            "spending_value_median",
            "spending_value_total",
            "value_average",
            "value_median",
            "value_total",
            "vbytes"
        ]
    },
    
    "mining": {
        "name": "挖矿数据",
        "endpoints": [
            "block_production_daily_sum",
            "difficulty_latest",
            "difficulty_mean",
            "hash_price",
            "hash_price_btc",
            "hash_price_usd",
            "hash_rate_mean",
            "hash_rate_migration_absolute",
            "hash_rate_migration_relative",
            "miners_revenue_btc",
            "miners_revenue_sum",
            "miners_revenue_usd",
            "miners_unspent_supply",
            "mining_equipment_price",
            "payout_count",
            "payout_value_mean",
            "payout_value_median",
            "payout_value_sum",
            "puell_multiple",
            "revenue_from_fees",
            "revenue_sum",
            "revenue_unspent",
            "thermocap",
            "thermocap_40",
            "thermocap_ratio_multiple",
            "transaction_fee_per_block_mean",
            "transaction_fee_per_block_sum"
        ]
    },
    
    "supply": {
        "name": "供应分析",
        "endpoints": [
            "active_10y",
            "active_180d",
            "active_1d_1w",
            "active_1m_3m",
            "active_1w_1m",
            "active_1y_2y",
            "active_24h",
            "active_2w_1m",
            "active_2y_3y",
            "active_30d",
            "active_3m_6m",
            "active_3y_5y",
            "active_5y_7y",
            "active_6m_12m",
            "active_7d",
            "active_7y_10y",
            "active_90d",
            "active_more_10y",
            "bridges_deposits_stacking_90d",
            "bridges_deposits_total",
            "bridges_withdrawals_stacking_90d",
            "bridges_withdrawals_total",
            "burned",
            "burned_bridges",
            "circulating",
            "current",
            "highly_liquid_sum",
            "illiquid_change",
            "illiquid_sum",
            "inflation_rate",
            "issued",
            "liquid_change",
            "liquid_illiquid_sum",
            "liquid_sum",
            "lth",
            "lth_net_change",
            "lth_net_position_change",
            "lth_sum",
            "lth_supply_in_profit_sum",
            "minted",
            "minted_blocks",
            "profit_relative",
            "profit_sum",
            "rcap_hodl_waves",
            "revived_more_10y",
            "revived_more_1y",
            "revived_more_2y",
            "revived_more_3y",
            "revived_more_4y",
            "revived_more_5y",
            "shielded",
            "shrimps_sum",
            "sth",
            "sth_net_position_change",
            "sth_sum"
        ]
    },
    
    "transactions": {
        "name": "交易分析",
        "endpoints": [
            "count",
            "entity_adjusted_count",
            "entity_adjusted_rate",
            "entity_adjusted_velocity",
            "fees_per_tx_mean",
            "fees_per_tx_median",
            "payments_count",
            "payments_rate",
            "payments_volume_mean",
            "payments_volume_median",
            "payments_volume_sum",
            "rate",
            "size_mean",
            "size_sum",
            "transfers_count",
            "transfers_from_exchanges_count",
            "transfers_from_exchanges_mean",
            "transfers_from_exchanges_sum",
            "transfers_rate",
            "transfers_to_exchanges_count",
            "transfers_to_exchanges_mean",
            "transfers_to_exchanges_sum",
            "transfers_volume_adjusted_mean",
            "transfers_volume_adjusted_median",
            "transfers_volume_adjusted_sum",
            "transfers_volume_exchanges_net",
            "transfers_volume_from_exchanges_mean",
            "transfers_volume_from_exchanges_sum",
            "transfers_volume_mean",
            "transfers_volume_median",
            "transfers_volume_miners_net",
            "transfers_volume_miners_to_exchanges",
            "transfers_volume_sum",
            "transfers_volume_to_exchanges_mean",
            "transfers_volume_to_exchanges_sum",
            "transfers_volume_whales_to_exchanges_sum"
        ]
    }
}

def print_statistics():
    """打印统计信息"""
    print("Glassnode API 完整端点配置统计")
    print("="*60)
    
    total = 0
    for category, info in GLASSNODE_COMPLETE_ENDPOINTS.items():
        count = len(info["endpoints"])
        total += count
        print(f"{info['name']:20} {count:4} 个端点")
    
    print("-"*60)
    print(f"{'总计':20} {total:4} 个端点")
    
    # 检查特定端点
    print("\n验证关键端点:")
    check_endpoints = [
        ("derivatives", "futures_annualized_basis_3m"),
        ("addresses", "accumulation_balance"),
        ("addresses", "accumulation_count")
    ]
    
    for category, endpoint in check_endpoints:
        if endpoint in GLASSNODE_COMPLETE_ENDPOINTS[category]["endpoints"]:
            print(f"✓ {category}/{endpoint}")
        else:
            print(f"✗ {category}/{endpoint} - 缺失")

if __name__ == "__main__":
    print_statistics()