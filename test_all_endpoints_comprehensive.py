#!/usr/bin/env python3
"""
综合测试所有已知的Glassnode端点
确定正确的端点名称和顺序
"""

import requests
import time
from datetime import datetime, timedelta

API_KEY = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
headers = {"x-key": API_KEY}
base_url = "https://grassnoodle.cloud/v1/metrics"

# 所有可能的地址端点（包括各种变体）
ADDRESS_ENDPOINTS_TO_TEST = [
    # Accumulation
    "accumulation_balance",
    "accumulation_count",
    
    # Active
    "active_count",
    "active_count_with_contracts",
    "active_recurrent_count",
    "activity_retention_rate",
    
    # Count
    "count",
    
    # Loss/Profit
    "loss_count",
    "profit_count",
    "profit_relative",
    
    # Min BTC holdings variants
    "min_point_zero_1_count",  # 0.1 BTC
    "min_point_0_1_count",      # Alternative
    "min_point_01_count",       # Alternative
    "min_0_1_count",            # Alternative
    
    "min_point_1_count",        # 1 BTC  
    "min_point_one_count",     # Alternative
    "min_1_count",              # 1 BTC
    "min_10_count",             # 10 BTC
    "min_100_count",            # 100 BTC
    "min_1k_count",             # 1,000 BTC
    "min_10k_count",            # 10,000 BTC
    "min_32_count",             # 32 BTC
    
    # Min USD holdings
    "min_1_usd_count",
    "min_10_usd_count", 
    "min_100_usd_count",
    "min_1k_usd_count",
    "min_10k_usd_count",
    "min_100k_usd_count",
    "min_1m_usd_count",
    "min_10m_usd_count",
    
    # New
    "new_count",
    "new_non_zero_count",
    
    # Non-zero/Zero
    "non_zero_count",
    "zero_balance_count",
    
    # Receiving/Sending
    "receiving_count",
    "receiving_from_exchanges_count",
    "sending_count", 
    "sending_to_exchanges_count",
    
    # Supply distribution
    "supply_distribution_relative",
    
    # Supply balance ranges
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

# Derivatives endpoints to test
DERIVATIVES_ENDPOINTS_TO_TEST = [
    # Futures - Basis
    "futures_annualized_basis",
    "futures_annualized_basis_3m",
    "futures_annualized_rolling_basis",
    "futures_basis",
    "futures_rolling_basis",
    
    # Futures - Estimated Leverage
    "futures_estimated_leverage_ratio",
    "futures_leverage_ratio",
    
    # Futures - Funding
    "futures_funding_rate",
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
    "futures_liquidated_volume_sum",
    "futures_liquidations",
    
    # Futures - Open Interest
    "futures_open_interest_cash_margin_relative",
    "futures_open_interest_cash_margin_sum",
    "futures_open_interest_cash_margin_perpetual_sum",
    "futures_open_interest_crypto_margin_relative",
    "futures_open_interest_crypto_margin_sum",
    "futures_open_interest_crypto_margin_perpetual_sum",
    "futures_open_interest_crypto_margin_relative_perpetual",
    "futures_open_interest_current_relative",
    "futures_open_interest_latest",
    "futures_open_interest_liquidation_sum",
    "futures_open_interest_perpetual_sum",
    "futures_open_interest_perpetual_sum_all",
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
    "options_atm_implied_volatility",
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

def test_endpoints(category, endpoints):
    """测试一个类别的端点"""
    print(f"\n{'='*60}")
    print(f"测试 {category} 端点")
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
    
    for endpoint in endpoints:
        url = f"{base_url}/{category}/{endpoint}"
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    print(f"✓ {endpoint}")
                    valid_endpoints.append(endpoint)
                else:
                    print(f"⚠ {endpoint} - 空数据")
                    valid_endpoints.append(endpoint)  # Still valid but no data
            elif response.status_code == 404:
                print(f"✗ {endpoint} - 不存在")
                invalid_endpoints.append(endpoint)
            else:
                print(f"? {endpoint} - {response.status_code}")
                
        except Exception as e:
            print(f"✗ {endpoint} - 错误: {str(e)[:50]}")
            invalid_endpoints.append(endpoint)
        
        time.sleep(0.5)  # Rate limiting
    
    print(f"\n有效端点: {len(valid_endpoints)}")
    print(f"无效端点: {len(invalid_endpoints)}")
    
    return valid_endpoints, invalid_endpoints

def main():
    # Test addresses
    valid_addr, invalid_addr = test_endpoints("addresses", ADDRESS_ENDPOINTS_TO_TEST)
    
    # Test derivatives
    valid_deriv, invalid_deriv = test_endpoints("derivatives", DERIVATIVES_ENDPOINTS_TO_TEST)
    
    # Print summary
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    print("\n### 有效的地址端点 ###")
    for ep in sorted(valid_addr):
        print(f"  - {ep}")
    
    print("\n### 有效的衍生品端点 ###")
    for ep in sorted(valid_deriv):
        print(f"  - {ep}")
    
    # Save results
    results = {
        "addresses": {
            "valid": valid_addr,
            "invalid": invalid_addr
        },
        "derivatives": {
            "valid": valid_deriv,
            "invalid": invalid_deriv
        }
    }
    
    import json
    with open("endpoint_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n结果已保存到 endpoint_test_results.json")

if __name__ == "__main__":
    main()