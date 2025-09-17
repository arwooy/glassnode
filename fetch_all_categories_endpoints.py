#!/usr/bin/env python3
"""
获取Glassnode API所有类别的完整端点列表
按照API文档的精确顺序
"""

import requests
import time
import json
from datetime import datetime, timedelta

API_KEY = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
headers = {"x-key": API_KEY}
base_url = "https://grassnoodle.cloud/v1/metrics"

# API文档中列出的所有类别（按文档顺序）
CATEGORIES = [
    "addresses",
    "bridges",
    "blockchain", 
    "breakdowns",
    "defi",
    "derivatives",
    "distribution",
    "entities",
    "eth2",
    "fees",
    "indicators",
    "institutions",
    "lightning",
    "market",
    "mempool",
    "mining",
    "options",  # Note: options might be part of derivatives
    "protocols",
    "signals",
    "supply",
    "transactions"
]

# 每个类别的已知端点（将通过测试来验证和补充）
CATEGORY_ENDPOINTS = {
    "addresses": [
        # 基于文档和测试的完整列表
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
        "new_non_zero_count",
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
    
    "bridges": [
        # Bridges endpoints
        "deposits_count",
        "deposits_stacking_90d",
        "deposits_total",
        "deposits_value_sum",
        "withdrawals_count",
        "withdrawals_stacking_90d",
        "withdrawals_total",
        "withdrawals_value_sum"
    ],
    
    "blockchain": [
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
    ],
    
    "breakdowns": [
        # Breakdown metrics
        "exchange_net_position_change",
        "miners_net_position_change",
        "supply_by_type"
    ],
    
    "defi": [
        # DeFi metrics
        "total_value_locked",
        "tvl_ratio",
        "wbtc_supply",
        "wrapped_supply"
    ],
    
    "derivatives": [
        # Comprehensive derivatives list
        "futures_annualized_basis_3m",
        "futures_estimated_leverage_ratio",
        "futures_funding_rate_all",
        "futures_funding_rate_perpetual",
        "futures_funding_rate_perpetual_all",
        "futures_liquidated_volume_long_mean",
        "futures_liquidated_volume_long_relative",
        "futures_liquidated_volume_long_sum",
        "futures_liquidated_volume_long_window_sum",
        "futures_liquidated_volume_short_mean",
        "futures_liquidated_volume_short_relative",
        "futures_liquidated_volume_short_sum",
        "futures_liquidated_volume_short_window_sum",
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
        "futures_term_structure",
        "futures_term_structure_by_exchange",
        "futures_term_structure_relative",
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
        # Options (might be here or separate)
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
    ],
    
    "distribution": [
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
        "exchange_aggregated_reliance_ratio",
        "exchange_aggregated_reshuffling_ratio",
        "exchange_net_position_change",
        "exchange_reliance_ratio",
        "exchange_reshuffling_ratio",
        "exchange_whales_outflow",
        "gini",
        "herfindahl",
        "outflows_mtgox_trustee",
        "proof_of_reserves",
        "proof_of_reserves_all",
        "proof_of_reserves_all_latest",
        "supply_contracts"
    ],
    
    "entities": [
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
    ],
    
    "indicators": [
        "asol",
        "average_coin_age",
        "average_dormancy",
        "average_dormancy_supply_adjusted",
        "average_spent_output_lifespan",
        "balanced_price_usd",
        "bvin",
        "cdd",
        "cdd_account_based",
        "cdd_supply_adjusted",
        "cdd_supply_adjusted_binary",
        "cvdd",
        "cyd_account_based",
        "cyd_account_based_supply_adjusted",
        "cyd_supply_adjusted",
        "difficulty_ribbon",
        "difficulty_ribbon_compression",
        "dormancy",
        "dormancy_account_based",
        "hash_ribbon",
        "hodl_waves",
        "hodler_net_position_change",
        "liveliness",
        "loss_relative",
        "lth_activated_supply",
        "lth_activated_supply_sum",
        "lth_net_position_change",
        "lth_sum_coin_age",
        "lth_sum_coin_age_usd",
        "lth_supply_loss_sum",
        "lth_supply_profit_loss_relative",
        "lth_supply_profit_sum",
        "msol",
        "net_unrealized_profit_loss",
        "net_unrealized_profit_loss_account_based",
        "nupl_less_155",
        "nupl_more_155",
        "nvt",
        "nvt_entity_adjusted",
        "nvts",
        "pi_cycle_top",
        "profit_relative",
        "realized_hodl_ratio",
        "realized_loss",
        "realized_profit",
        "realized_profit_loss_ratio",
        "reserve_risk",
        "rhodl_ratio",
        "sopr",
        "sopr_account_based",
        "sopr_adjusted",
        "sopr_entity_adjusted",
        "sopr_less_155_coin_adj",
        "sopr_more_155_coin_adj",
        "spent_output_age_bands",
        "sth_lth_profit_loss_ratio",
        "sth_net_position_change",
        "sth_sum_coin_age",
        "sth_sum_coin_age_usd",
        "sth_supply_loss_sum",
        "sth_supply_profit_loss_relative",
        "sth_supply_profit_sum",
        "stock_to_flow_deflection",
        "stock_to_flow_ratio",
        "unrealized_loss",
        "unrealized_profit",
        "vaulted_price",
        "velocity"
    ],
    
    "institutions": [
        "acc_1",
        "acc_2",
        "acc_3",
        "acc_4",
        "acc_5",
        "acc_6",
        "btc_2x_fli_supply",
        "btc_2x_fli_supply_net_change",
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
        "purpose_etf_flows_sum",
        "purpose_etf_holdings_sum"
    ],
    
    "lightning": [
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
    ],
    
    "market": [
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
    ],
    
    "mempool": [
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
    ],
    
    "mining": [
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
    ],
    
    "options": [
        # Options might be under derivatives
    ],
    
    "protocols": [
        # Protocol specific metrics
        "lightning_network_capacity",
        "wrapped_supply"
    ],
    
    "signals": [
        # Trading signals
        "exchange_inflow_mean",
        "exchange_outflow_mean",
        "large_transactions_count"
    ],
    
    "supply": [
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
    ],
    
    "transactions": [
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

def test_category_endpoints(category, endpoints):
    """测试一个类别的所有端点"""
    print(f"\n{'='*60}")
    print(f"测试 {category.upper()} 类别端点")
    print(f"{'='*60}")
    
    valid_endpoints = []
    invalid_endpoints = []
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)
    
    params = {
        'a': 'BTC',
        's': int(start_date.timestamp()),
        'u': int(end_date.timestamp()),
        'i': '24h'
    }
    
    for i, endpoint in enumerate(endpoints, 1):
        url = f"{base_url}/{category}/{endpoint}"
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    print(f"✓ [{i:3}] {endpoint}")
                    valid_endpoints.append(endpoint)
                else:
                    print(f"⚠ [{i:3}] {endpoint} - 空数据")
                    valid_endpoints.append(endpoint)
            elif response.status_code == 404:
                print(f"✗ [{i:3}] {endpoint} - 404")
                invalid_endpoints.append(endpoint)
            elif response.status_code == 429:
                print(f"⏸ [{i:3}] {endpoint} - 限流，等待...")
                time.sleep(5)
                # Retry
                response = requests.get(url, params=params, headers=headers, timeout=3)
                if response.status_code == 200:
                    print(f"✓ [{i:3}] {endpoint} (重试成功)")
                    valid_endpoints.append(endpoint)
                else:
                    print(f"✗ [{i:3}] {endpoint} - {response.status_code}")
                    invalid_endpoints.append(endpoint)
            else:
                print(f"? [{i:3}] {endpoint} - {response.status_code}")
                invalid_endpoints.append(endpoint)
                
        except Exception as e:
            print(f"✗ [{i:3}] {endpoint} - 错误: {str(e)[:30]}")
            invalid_endpoints.append(endpoint)
        
        time.sleep(0.8)  # Rate limiting
    
    return valid_endpoints, invalid_endpoints

def main():
    """测试所有类别"""
    all_results = {}
    
    for category in CATEGORIES:
        if category in CATEGORY_ENDPOINTS:
            endpoints = CATEGORY_ENDPOINTS[category]
            if endpoints:
                valid, invalid = test_category_endpoints(category, endpoints)
                all_results[category] = {
                    "valid": valid,
                    "invalid": invalid,
                    "total_tested": len(endpoints),
                    "valid_count": len(valid),
                    "invalid_count": len(invalid)
                }
        else:
            print(f"\n跳过 {category} - 无端点列表")
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    total_valid = 0
    total_invalid = 0
    
    for category, results in all_results.items():
        print(f"\n{category.upper()}:")
        print(f"  有效: {results['valid_count']}")
        print(f"  无效: {results['invalid_count']}")
        print(f"  总计: {results['total_tested']}")
        total_valid += results['valid_count']
        total_invalid += results['invalid_count']
    
    print(f"\n总计:")
    print(f"  有效端点: {total_valid}")
    print(f"  无效端点: {total_invalid}")
    print(f"  总测试数: {total_valid + total_invalid}")
    
    # 保存结果
    with open("all_categories_test_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print("\n结果已保存到 all_categories_test_results.json")
    
    # 生成完整配置
    generate_complete_config(all_results)

def generate_complete_config(results):
    """生成完整的配置文件"""
    config = {}
    
    for category, result in results.items():
        if result['valid']:
            config[category] = result['valid']
    
    with open("glassnode_verified_endpoints.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("验证的端点配置已保存到 glassnode_verified_endpoints.json")

if __name__ == "__main__":
    main()