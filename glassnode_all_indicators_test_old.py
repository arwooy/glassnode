#!/usr/bin/env python3
"""
Glassnode全指标信息增益分析系统
测试所有API端点类别下的指标，计算信息增益并生成综合报告
"""

import os
import json
import time
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy.stats import entropy
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')
API_KEY = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
headers = {
    "x-key": API_KEY
}
class GlassnodeAllIndicatorsAnalyzer:
    """Glassnode全指标分析器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # self.base_url = "https://api.glassnode.com/v1/metrics"
        self.base_url = "https://grassnoodle.cloud/v1/metrics"
        
        # 从JSON配置文件加载端点定义
        self.load_endpoints_config()
            "addresses": {
                "name": "地址分析",
                "endpoints": [
                    # 按API文档精确顺序
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
                    "utxo_sum",
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
                    "block_weight_sum"
                ]
            },
            "derivatives": {
                "name": "衍生品",
                "endpoints": [
                    # Futures - Basis (重要：包括futures_annualized_basis_3m)
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
                    "options_atm_implied_volatility_all",
                    "options_contract_prices",
                    "options_dvol",
                    "options_dvol_bitmex",
                    "options_dvol_bybit",
                    "options_dvol_deribit",
                    "options_dvol_okex",
                    "options_flow_put_call_ratio",
                    "options_gex_1pct",
                    "options_implied_volatility_term_structure",
                    "options_open_interest_distribution",
                    "options_open_interest_put_call_ratio",
                    "options_open_interest_strike_all",
                    "options_open_interest_sum",
                    "options_25d_skew",
                    "options_25d_skew_all",
                    "options_gex",
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
                ]
            },
            "entities": {
                "name": "实体分析",
                "endpoints": [
                    "active",
                    "active_count",
                    "net_growth",
                    "net_growth_count",
                    "new",
                    "new_count",
                    "profit_relative",
                    "receiving_count",
                    "sending_count",
                    "supply_balance_0001_001",
                    "supply_balance_001_01",
                    "supply_balance_01_1",
                    "supply_balance_1_10",
                    "supply_balance_10_100",
                    "supply_balance_100_1k",
                    "supply_balance_1k_10k",
                    "supply_balance_10k_100k",
                    "supply_balance_less_0001",
                    "supply_balance_more_100k",
                    "min_1k_count",
                    "min_10k_count",
                    "min_100k_count"
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
                    "sopr",
                    "sopr_account_based",
                    "sopr_adjusted",
                    "sopr_entity_adjusted",
                    "sopr_less_155_coin_adj",
                    "sopr_more_155_coin_adj",
                    "profit_relative",
                    "loss_relative",
                    "realized_loss",
                    "realized_profit",
                    "realized_profit_loss_ratio",
                    "net_unrealized_profit_loss",
                    "net_unrealized_profit_loss_account_based",
                    "nupl_less_155",
                    "nupl_more_155",
                    "unrealized_loss",
                    "unrealized_profit",
                    "balanced_price_usd",
                    "cvdd",
                    "dormancy",
                    "dormancy_account_based",
                    "average_dormancy",
                    "average_dormancy_supply_adjusted",
                    "liveliness",
                    "vaulted_price",
                    "reserve_risk",
                    "asol",
                    "average_coin_age",
                    "average_spent_output_lifespan",
                    "cdd",
                    "cdd_account_based",
                    "cdd_supply_adjusted",
                    "cdd_supply_adjusted_binary",
                    "cyd_account_based",
                    "cyd_account_based_supply_adjusted",
                    "cyd_supply_adjusted",
                    "hodl_waves",
                    "hodler_net_position_change",
                    "msol",
                    "realized_hodl_ratio",
                    "spent_output_age_bands",
                    "sth_lth_profit_loss_ratio",
                    "lth_net_position_change",
                    "lth_sum_coin_age",
                    "lth_sum_coin_age_usd",
                    "lth_activated_supply",
                    "lth_activated_supply_sum",
                    "lth_supply_loss_sum",
                    "lth_supply_profit_sum",
                    "lth_supply_profit_loss_relative",
                    "sth_net_position_change",
                    "sth_sum_coin_age",
                    "sth_sum_coin_age_usd",
                    "sth_supply_loss_sum",
                    "sth_supply_profit_sum",
                    "sth_supply_profit_loss_relative",
                    "nvt",
                    "nvts",
                    "nvt_entity_adjusted",
                    "velocity",
                    "rhodl_ratio",
                    "hash_ribbon",
                    "difficulty_ribbon",
                    "difficulty_ribbon_compression",
                    "pi_cycle_top",
                    "stock_to_flow_deflection",
                    "stock_to_flow_ratio"
                ]
            },
            "institutions": {
                "name": "机构指标",
                "endpoints": [
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
                    "hash_rate_mean",
                    "hash_rate_migration_absolute",
                    "hash_rate_migration_relative",
                    "hash_price",
                    "hash_price_btc",
                    "hash_price_usd",
                    "miners_revenue_btc",
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
        
        # 用于存储结果
        self.results = {}
        self.failed_endpoints = []
        
    def load_endpoints_config(self):
        """从JSON文件加载端点配置"""
        import os
        config_file = 'glassnode_endpoints_config.json'
        
        # 尝试从当前目录或脚本目录加载
        if os.path.exists(config_file):
            config_path = config_file
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, config_file)
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件 {config_file} 未找到")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.categories = json.load(f)
            
        # 验证配置
        if not self.categories:
            raise ValueError("配置文件为空或格式错误")
            
        print(f"✓ 已加载 {len(self.categories)} 个类别的端点配置")
        total_endpoints = sum(len(cat['endpoints']) for cat in self.categories.values())
        print(f"  总端点数: {total_endpoints}")
        
    def fetch_metric_data(self, category: str, metric: str, 
                         start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """获取单个指标数据"""
        try:
            url = f"{self.base_url}/{category}/{metric}"
            params = {
                'a': 'BTC',
                's': int(start_date.timestamp()),
                'u': int(end_date.timestamp()),
                'i': '24h'
            }
            
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data)
                
                if not df.empty:
                    # 处理时间戳
                    if 't' in df.columns:
                        df['timestamp'] = pd.to_datetime(df['t'], unit='s')
                        df = df.set_index('timestamp')
                    
                    # 处理两种数据格式
                    if 'v' in df.columns:
                        # 单值格式
                        df = df.rename(columns={'v': metric})
                        df = df[[metric]]
                        return df
                    elif 'o' in df.columns:
                        # 多维格式（如supply_distribution_relative）
                        # 将字典展开为多列
                        expanded = pd.json_normalize(df['o'])
                        expanded.index = df.index
                        
                        # 对于分布数据，可以计算一个综合指标
                        # 例如：使用基尼系数或者加权平均
                        if metric == 'supply_distribution_relative':
                            # 计算供应集中度指标
                            expanded[metric] = self.calculate_supply_concentration(expanded)
                        else:
                            # 对于其他多维数据，取第一列或计算均值
                            if not expanded.empty:
                                expanded[metric] = expanded.mean(axis=1)
                        
                        if metric in expanded.columns:
                            return expanded[[metric]]
                        else:
                            print(f"  ⚠ {metric}: 多维数据处理")
                            return pd.DataFrame()
            else:
                print(f"  ✗ {metric}: {response.status_code}")
                self.failed_endpoints.append(f"{category}/{metric}")
                
        except Exception as e:
            print(f"  ✗ {metric}: {str(e)[:50]}")
            self.failed_endpoints.append(f"{category}/{metric}")
            
        return pd.DataFrame()
    
    def calculate_supply_concentration(self, dist_df: pd.DataFrame) -> pd.Series:
        """计算供应集中度指标（基于分布数据）"""
        # 使用加权基尼系数或赫芬达尔指数
        result = []
        
        for idx, row in dist_df.iterrows():
            # 计算赫芬达尔指数 (HHI)
            values = row.values
            # 过滤掉NaN值
            values = values[~pd.isna(values)]
            
            if len(values) > 0:
                # HHI = sum(share^2)
                hhi = np.sum(values ** 2)
                result.append(hhi)
            else:
                result.append(np.nan)
        
        return pd.Series(result, index=dist_df.index)
    
    def calculate_information_gain(self, indicator_data: pd.Series, 
                                  price_data: pd.Series,
                                  horizon_days: int) -> Dict:
        """计算信息增益"""
        try:
            # 准备数据
            df = pd.DataFrame({
                'indicator': indicator_data,
                'price': price_data
            }).dropna()
            
            if len(df) < 100:
                return {}
            
            # 计算未来价格变化
            df['future_price'] = df['price'].shift(-horizon_days)
            df['price_change'] = (df['future_price'] / df['price'] - 1).fillna(0)
            df = df.dropna()
            
            # 离散化
            n_bins = 10
            indicator_bins = pd.qcut(df['indicator'].values, n_bins, 
                                    labels=False, duplicates='drop')
            price_bins = pd.qcut(df['price_change'].values, n_bins, 
                               labels=False, duplicates='drop')
            
            # 计算熵
            H_price = entropy(np.bincount(price_bins) / len(price_bins))
            
            # 计算条件熵
            H_conditional = 0
            for i in range(n_bins):
                mask = indicator_bins == i
                p_indicator = np.sum(mask) / len(indicator_bins)
                
                if p_indicator > 0 and np.sum(mask) > 1:
                    price_in_bin = price_bins[mask]
                    if len(price_in_bin) > 0:
                        bin_probs = np.bincount(price_in_bin, minlength=n_bins) / len(price_in_bin)
                        h = entropy(bin_probs)
                        H_conditional += p_indicator * h
            
            # 信息增益
            ig = max(0, H_price - H_conditional)
            
            # 归一化互信息
            mi = ig
            normalized_mi = mi / H_price if H_price > 0 else 0
            
            # 相关性
            correlation = df['indicator'].corr(df['price_change'])
            
            return {
                'information_gain': ig,
                'normalized_mi': normalized_mi,
                'correlation': correlation,
                'entropy_price': H_price,
                'entropy_conditional': H_conditional,
                'reduction_ratio': ig/H_price if H_price > 0 else 0
            }
            
        except Exception as e:
            return {}
    
    def test_category(self, category_key: str, category_info: Dict,
                     price_data: pd.Series) -> Dict:
        """测试一个类别下的所有指标"""
        print(f"\n{'='*60}")
        print(f"测试类别: {category_info['name']} ({category_key})")
        print(f"端点数量: {len(category_info['endpoints'])}")
        print(f"{'='*60}")
        
        category_results = {}
        successful = 0
        
        for idx, endpoint in enumerate(category_info['endpoints'], 1):
            print(f"\n[{idx}/{len(category_info['endpoints'])}] 测试: {endpoint}")
            
            # 获取数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365*2)  # 2年数据
            
            df = self.fetch_metric_data(category_key, endpoint, start_date, end_date)
            
            if df.empty:
                continue
                
            time.sleep(0.8)  # 避免API限制
            
            # 计算不同时间跨度的信息增益
            horizons = [1, 3, 7, 14, 30]
            endpoint_results = {}
            
            for horizon in horizons:
                ig_result = self.calculate_information_gain(
                    df[endpoint], price_data, horizon
                )
                if ig_result:
                    endpoint_results[f'{horizon}d'] = ig_result
                    
            if endpoint_results:
                # 计算平均信息增益
                avg_ig = np.mean([r['information_gain'] 
                                for r in endpoint_results.values()])
                avg_mi = np.mean([r['normalized_mi'] 
                                for r in endpoint_results.values()])
                
                category_results[endpoint] = {
                    'horizons': endpoint_results,
                    'avg_ig': avg_ig,
                    'avg_mi': avg_mi,
                    'category': category_key
                }
                
                successful += 1
                print(f"  ✓ 平均IG: {avg_ig:.4f}, MI: {avg_mi:.4f}")
        
        print(f"\n类别测试完成: 成功 {successful}/{len(category_info['endpoints'])}")
        return category_results
    
    def run_comprehensive_test(self):
        """运行全面测试"""
        print("\n" + "="*60)
        print("Glassnode 全指标信息增益分析")
        print("="*60)
        
        # 先获取价格数据
        print("\n获取BTC价格数据...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*2)
        
        # 尝试使用正确的价格端点
        price_df = pd.DataFrame()
        price_endpoints = ['price_usd_close', 'close']
        
        for endpoint in price_endpoints:
            price_df = self.fetch_metric_data('market', endpoint,
                                             start_date, end_date)
            if not price_df.empty:
                if endpoint in price_df.columns:
                    price_df = price_df.rename(columns={endpoint: 'price_usd_close'})
                break
        
        if price_df.empty:
            print("错误：无法获取价格数据")
            return
            
        price_data = price_df['price_usd_close']
        print(f"✓ 获取到 {len(price_data)} 天的价格数据")
        
        # 测试每个类别
        all_results = {}
        
        for category_key, category_info in self.categories.items():
            results = self.test_category(category_key, category_info, price_data)
            all_results.update(results)
            
            # 保存中间结果
            self.save_intermediate_results(all_results)
            
            # 避免API限制
            time.sleep(2)
        
        # 生成最终报告
        self.generate_final_report(all_results)
        
    def save_intermediate_results(self, results: Dict):
        """保存中间结果"""
        with open('glassnode_test_intermediate.json', 'w') as f:
            # 转换为可JSON序列化的格式
            json_results = {}
            for key, value in results.items():
                json_results[key] = {
                    'avg_ig': float(value['avg_ig']),
                    'avg_mi': float(value['avg_mi']),
                    'category': value['category']
                }
            json.dump(json_results, f, indent=2)
            
    def generate_final_report(self, all_results: Dict):
        """生成最终报告"""
        print("\n" + "="*60)
        print("最终分析报告")
        print("="*60)
        
        # 按信息增益排序
        sorted_results = sorted(all_results.items(), 
                               key=lambda x: x[1]['avg_ig'],
                               reverse=True)
        
        # Top 20 指标
        print("\n### Top 20 高信息增益指标 ###\n")
        print(f"{'排名':<5} {'指标名称':<40} {'类别':<15} {'平均IG':<10} {'平均MI':<10}")
        print("-" * 80)
        
        for i, (indicator, result) in enumerate(sorted_results[:20], 1):
            category_name = self.categories[result['category']]['name']
            print(f"{i:<5} {indicator:<40} {category_name:<15} "
                  f"{result['avg_ig']:<10.4f} {result['avg_mi']:<10.4f}")
        
        # 按类别统计
        print("\n### 类别统计 ###\n")
        category_stats = {}
        
        for indicator, result in all_results.items():
            cat = result['category']
            if cat not in category_stats:
                category_stats[cat] = {
                    'indicators': [],
                    'avg_igs': []
                }
            category_stats[cat]['indicators'].append(indicator)
            category_stats[cat]['avg_igs'].append(result['avg_ig'])
        
        print(f"{'类别':<20} {'指标数':<10} {'平均IG':<10} {'最高IG指标':<30}")
        print("-" * 70)
        
        for cat, stats in category_stats.items():
            cat_name = self.categories[cat]['name']
            avg_ig = np.mean(stats['avg_igs'])
            best_idx = np.argmax(stats['avg_igs'])
            best_indicator = stats['indicators'][best_idx]
            best_ig = stats['avg_igs'][best_idx]
            
            print(f"{cat_name:<20} {len(stats['indicators']):<10} "
                  f"{avg_ig:<10.4f} {best_indicator} ({best_ig:.4f})")
        
        # 保存完整结果
        self.save_full_results(all_results, sorted_results)
        
        # 统计信息
        print(f"\n### 测试统计 ###")
        print(f"总测试指标数: {len(all_results)}")
        print(f"失败的端点数: {len(self.failed_endpoints)}")
        print(f"平均信息增益: {np.mean([r['avg_ig'] for r in all_results.values()]):.4f}")
        
        if self.failed_endpoints:
            print(f"\n失败的端点:")
            for ep in self.failed_endpoints:
                print(f"  - {ep}")
            if len(self.failed_endpoints) > 10:
                print(f"共 {len(self.failed_endpoints)} 个")
    
    def save_full_results(self, all_results: Dict, sorted_results: List):
        """保存完整结果"""
        # 创建DataFrame
        data = []
        for indicator, result in sorted_results:
            for horizon_key, horizon_data in result['horizons'].items():
                data.append({
                    'indicator': indicator,
                    'category': self.categories[result['category']]['name'],
                    'horizon': horizon_key,
                    'information_gain': horizon_data['information_gain'],
                    'normalized_mi': horizon_data['normalized_mi'],
                    'correlation': horizon_data['correlation'],
                    'reduction_ratio': horizon_data['reduction_ratio']
                })
        
        df = pd.DataFrame(data)
        
        # 保存CSV
        df.to_csv('glassnode_all_indicators_results.csv', index=False)
        print(f"\n结果已保存到 glassnode_all_indicators_results.csv")
        
        # 生成HTML报告
        self.generate_html_report(sorted_results)
    
    def generate_html_report(self, sorted_results: List):
        """生成HTML报告"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Glassnode全指标信息增益分析报告</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        h1 { color: #333; text-align: center; }
        h2 { color: #666; border-bottom: 2px solid #ddd; padding-bottom: 5px; }
        table { width: 100%; border-collapse: collapse; background: white; margin: 20px 0; }
        th { background: #4CAF50; color: white; padding: 12px; text-align: left; }
        td { padding: 10px; border-bottom: 1px solid #ddd; }
        tr:hover { background: #f5f5f5; }
        .top-indicator { background: #fffacd; }
        .category-header { background: #e8f5e9; font-weight: bold; }
        .stats-box { background: white; padding: 20px; margin: 20px 0; border-radius: 5px; 
                     box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric { display: inline-block; margin: 10px 20px; }
        .metric-label { color: #666; font-size: 14px; }
        .metric-value { font-size: 24px; font-weight: bold; color: #4CAF50; }
    </style>
</head>
<body>
    <h1>Glassnode 全指标信息增益分析报告</h1>
    <div class="stats-box">
        <h2>测试概览</h2>
        <div class="metric">
            <div class="metric-label">测试指标总数</div>
            <div class="metric-value">""" + str(len(sorted_results)) + """</div>
        </div>
        <div class="metric">
            <div class="metric-label">平均信息增益</div>
            <div class="metric-value">""" + f"{np.mean([r[1]['avg_ig'] for r in sorted_results]):.4f}" + """</div>
        </div>
        <div class="metric">
            <div class="metric-label">生成时间</div>
            <div class="metric-value">""" + datetime.now().strftime("%Y-%m-%d %H:%M") + """</div>
        </div>
    </div>
    
    <h2>Top 50 高信息增益指标</h2>
    <table>
        <tr>
            <th>排名</th>
            <th>指标</th>
            <th>类别</th>
            <th>平均IG</th>
            <th>平均MI</th>
            <th>1天IG</th>
            <th>7天IG</th>
            <th>30天IG</th>
        </tr>
"""
        
        for i, (indicator, result) in enumerate(sorted_results[:50], 1):
            row_class = 'top-indicator' if i <= 10 else ''
            cat_name = self.categories[result['category']]['name']
            
            ig_1d = result['horizons'].get('1d', {}).get('information_gain', 0)
            ig_7d = result['horizons'].get('7d', {}).get('information_gain', 0)
            ig_30d = result['horizons'].get('30d', {}).get('information_gain', 0)
            
            html += f"""
        <tr class="{row_class}">
            <td>{i}</td>
            <td><b>{indicator}</b></td>
            <td>{cat_name}</td>
            <td>{result['avg_ig']:.4f}</td>
            <td>{result['avg_mi']:.4f}</td>
            <td>{ig_1d:.4f}</td>
            <td>{ig_7d:.4f}</td>
            <td>{ig_30d:.4f}</td>
        </tr>
"""
        
        html += """
    </table>
    
    <h2>按类别分组的完整结果</h2>
"""
        
        # 按类别组织结果
        category_groups = {}
        for indicator, result in sorted_results:
            cat = result['category']
            if cat not in category_groups:
                category_groups[cat] = []
            category_groups[cat].append((indicator, result))
        
        for cat_key, cat_indicators in category_groups.items():
            cat_name = self.categories[cat_key]['name']
            cat_indicators_sorted = sorted(cat_indicators, 
                                          key=lambda x: x[1]['avg_ig'],
                                          reverse=True)
            
            html += f"""
    <h3>{cat_name}</h3>
    <table>
        <tr>
            <th>指标</th>
            <th>平均IG</th>
            <th>平均MI</th>
            <th>1天IG</th>
            <th>7天IG</th>
            <th>30天IG</th>
        </tr>
"""
            
            for indicator, result in cat_indicators_sorted[:20]:  # 每个类别显示前20
                ig_1d = result['horizons'].get('1d', {}).get('information_gain', 0)
                ig_7d = result['horizons'].get('7d', {}).get('information_gain', 0)
                ig_30d = result['horizons'].get('30d', {}).get('information_gain', 0)
                
                html += f"""
        <tr>
            <td>{indicator}</td>
            <td>{result['avg_ig']:.4f}</td>
            <td>{result['avg_mi']:.4f}</td>
            <td>{ig_1d:.4f}</td>
            <td>{ig_7d:.4f}</td>
            <td>{ig_30d:.4f}</td>
        </tr>
"""
            
            html += "</table>\n"
        
        html += """
</body>
</html>
"""
        
        with open('glassnode_all_indicators_report.html', 'w', encoding='utf-8') as f:
            f.write(html)
            
        print(f"HTML报告已保存到 glassnode_all_indicators_report.html")


def main():
    # API密钥
    # api_key = os.getenv('GLASSNODE_API_KEY', 'YOUR_API_KEY_HERE')
    api_key = "myapi_sk_b3fa36048ea022be1c21e626742d4dec"
    # 创建分析器
    analyzer = GlassnodeAllIndicatorsAnalyzer(api_key)
    
    # 运行全面测试
    analyzer.run_comprehensive_test()


if __name__ == "__main__":
    main()