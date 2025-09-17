# Glassnode API 端点完整列表

基于 https://docs.glassnode.com/basic-api/endpoints 的所有可用端点

## 1. Addresses (地址分析)
- `addresses/active_count` - 活跃地址数
- `addresses/new_non_zero_count` - 新增非零地址数
- `addresses/non_zero_count` - 非零地址总数
- `addresses/min_1_count` - 持有≥1 BTC的地址数
- `addresses/min_10_count` - 持有≥10 BTC的地址数
- `addresses/min_100_count` - 持有≥100 BTC的地址数
- `addresses/min_1k_count` - 持有≥1000 BTC的地址数
- `addresses/min_10k_count` - 持有≥10000 BTC的地址数
- `addresses/receiving_count` - 接收地址数
- `addresses/sending_count` - 发送地址数
- `addresses/accumulation_count` - 积累地址数
- `addresses/profit_count` - 盈利地址数
- `addresses/loss_count` - 亏损地址数

## 2. Blockchain (区块链基础)
- `blockchain/utxo_created_count` - 创建的UTXO数量
- `blockchain/utxo_spent_count` - 花费的UTXO数量
- `blockchain/utxo_count` - UTXO总数
- `blockchain/utxo_total_value` - UTXO总价值
- `blockchain/utxo_mean_value` - UTXO平均价值
- `blockchain/utxo_median_value` - UTXO中位数价值
- `blockchain/block_count` - 区块数量
- `blockchain/block_interval_mean` - 平均出块时间
- `blockchain/block_interval_median` - 中位数出块时间
- `blockchain/block_size_mean` - 平均区块大小
- `blockchain/block_size_sum` - 区块大小总和

## 3. Derivatives (衍生品)
- `derivatives/futures_funding_rate_all` - 期货资金费率（所有）
- `derivatives/futures_funding_rate_perpetual` - 永续期货资金费率
- `derivatives/futures_funding_rate_perpetual_all` - 永续期货资金费率（所有交易所）
- `derivatives/futures_open_interest_sum` - 期货持仓量总和
- `derivatives/futures_open_interest_perpetual_sum` - 永续期货持仓量
- `derivatives/futures_volume_daily_sum` - 期货日交易量
- `derivatives/futures_volume_daily_perpetual_sum` - 永续期货日交易量
- `derivatives/futures_liquidated_volume_long_sum` - 多头清算量
- `derivatives/futures_liquidated_volume_short_sum` - 空头清算量
- `derivatives/options_open_interest_put_call_ratio` - 期权持仓看跌/看涨比率
- `derivatives/options_volume_put_call_ratio` - 期权成交量看跌/看涨比率

## 4. Distribution (分布分析)
- `distribution/exchange_net_position_change` - 交易所净持仓变化
- `distribution/balance_exchanges` - 交易所余额
- `distribution/balance_exchanges_relative` - 交易所相对余额
- `distribution/supply_exchanges` - 交易所供应量
- `distribution/balance_miners` - 矿工余额
- `distribution/balance_miners_change` - 矿工余额变化
- `distribution/gini_coefficient` - 基尼系数
- `distribution/herfindahl_index` - 赫芬达尔指数
- `distribution/supply_llth_035_accounts_relative` - 长期持有者（>0.35年）相对供应
- `distribution/supply_llth_1_accounts_relative` - 长期持有者（>1年）相对供应
- `distribution/balance_1pct_holders` - 前1%持有者余额
- `distribution/balance_01pct_holders` - 前0.1%持有者余额

## 5. Entities (实体分析)
- `entities/sending_entities_count` - 发送实体数量
- `entities/receiving_entities_count` - 接收实体数量
- `entities/active_entities` - 活跃实体
- `entities/new_entities` - 新增实体
- `entities/entities_profit_relative` - 盈利实体比例
- `entities/entities_loss_relative` - 亏损实体比例
- `entities/entities_net_growth_count` - 实体净增长数
- `entities/entities_min_1k_count` - 持有≥1k BTC的实体数
- `entities/entities_min_10k_count` - 持有≥10k BTC的实体数
- `entities/entities_min_100k_count` - 持有≥100k BTC的实体数

## 6. Fees (手续费)
- `fees/fees_total_usd` - 总手续费（美元）
- `fees/fees_total_relative` - 相对总手续费
- `fees/fees_mean_usd` - 平均手续费（美元）
- `fees/fees_median_usd` - 中位数手续费（美元）
- `fees/gas_price_mean` - 平均Gas价格
- `fees/gas_price_median` - 中位数Gas价格
- `fees/gas_used_sum` - 使用的Gas总量
- `fees/gas_limit_tx_mean` - 交易平均Gas限制
- `fees/gas_limit_tx_median` - 交易中位数Gas限制
- `fees/revenue_total` - 总收入
- `fees/revenue_relative` - 相对收入

## 7. Indicators (核心指标)
- `indicators/sopr` - SOPR（花费输出利润率）
- `indicators/sopr_adjusted` - 调整后SOPR
- `indicators/reserve_risk` - 储备风险
- `indicators/cvdd` - CVDD（累积价值销毁天数）
- `indicators/net_unrealized_profit_loss` - NUPL（净未实现盈亏）
- `indicators/nupl_more_155` - NUPL（>155美元）
- `indicators/nupl_more_1k` - NUPL（>1k美元）
- `indicators/nupl_more_10k` - NUPL（>10k美元）
- `indicators/average_dormancy` - 平均休眠期
- `indicators/liveliness` - 活跃度
- `indicators/unrealized_profit` - 未实现利润
- `indicators/unrealized_loss` - 未实现亏损
- `indicators/profit_relative` - 相对利润
- `indicators/loss_relative` - 相对亏损
- `indicators/realized_profit_loss_ratio` - 已实现盈亏比
- `indicators/stock_to_flow_ratio` - 库存流量比
- `indicators/nvt` - NVT比率
- `indicators/nvts` - NVT信号
- `indicators/velocity` - 流通速度
- `indicators/rhodl_ratio` - RHODL比率
- `indicators/balanced_price_usd` - 平衡价格
- `indicators/hash_ribbon` - 哈希丝带
- `indicators/difficulty_ribbon` - 难度丝带
- `indicators/difficulty_ribbon_compression` - 难度丝带压缩
- `indicators/nvt_90d_percentile` - NVT 90天百分位
- `indicators/cdd` - 币天销毁
- `indicators/cdd_supply_adjusted` - 供应调整币天销毁
- `indicators/average_dormancy_supply_adjusted` - 供应调整平均休眠期
- `indicators/spent_output_age_band` - 花费输出年龄带
- `indicators/hodl_waves` - HODL波
- `indicators/realized_hodl_ratio` - 实现HODL比率
- `indicators/hodler_net_position_change` - HODLer净持仓变化
- `indicators/coin_years_destroyed` - 币年销毁
- `indicators/cyd_adjusted` - 调整币年销毁
- `indicators/cyd_supply_adjusted` - 供应调整币年销毁
- `indicators/dormancy` - 休眠期
- `indicators/asol` - 平均花费输出寿命
- `indicators/msol` - 中位数花费输出寿命
- `indicators/average_spent_output_lifespan` - 平均花费输出生命周期
- `indicators/cointime_destroyed` - 币时间销毁
- `indicators/pi_cycle_top` - Pi周期顶部

## 8. Institutions (机构指标)
- `institutions/purpose_etf_holdings_sum` - Purpose ETF持仓总和
- `institutions/purpose_etf_flows_sum` - Purpose ETF流入流出
- `institutions/qbtc_holdings_sum` - QBTC持仓总和
- `institutions/qbtc_flows_sum` - QBTC流入流出
- `institutions/grayscale_holdings_sum` - Grayscale持仓总和
- `institutions/grayscale_flows_sum` - Grayscale流入流出
- `institutions/btc_anchored_ust` - BTC锚定UST
- `institutions/btc_anchored_dai` - BTC锚定DAI
- `institutions/btc_anchored_pax` - BTC锚定PAX
- `institutions/btc_anchored_usdc` - BTC锚定USDC
- `institutions/btc_anchored_aggregate` - BTC锚定聚合

## 9. Market (市场数据)
- `market/price_usd_close` - 收盘价（美元）
- `market/price_usd_ohlc` - OHLC价格
- `market/marketcap_usd` - 市值（美元）
- `market/marketcap_realized_usd` - 实现市值（美元）
- `market/price_realized_usd` - 实现价格（美元）
- `market/mvrv` - MVRV比率
- `market/mvrv_z_score` - MVRV Z分数
- `market/price_drawdown_relative` - 相对价格回撤
- `market/price_ath` - 历史最高价
- `market/price_ath_drawdown` - ATH回撤
- `market/realized_price_usd` - 实现价格
- `market/realized_market_cap` - 实现市值
- `market/thermocap` - 热力学市值
- `market/thermocap_multiple` - 热力学倍数
- `market/thermocap_price` - 热力学价格
- `market/realized_profits` - 已实现利润
- `market/realized_losses` - 已实现亏损

## 10. Mempool (内存池)
- `mempool/mempool_count` - 内存池交易数
- `mempool/mempool_size` - 内存池大小
- `mempool/mempool_gas` - 内存池Gas
- `mempool/mempool_fees_sum` - 内存池手续费总和
- `mempool/mempool_fees_mean` - 内存池平均手续费
- `mempool/mempool_fees_median` - 内存池中位数手续费

## 11. Mining (挖矿数据)
- `mining/hash_rate_mean` - 平均哈希率
- `mining/hash_rate_30d_moving_average` - 30天移动平均哈希率
- `mining/difficulty_latest` - 最新难度
- `mining/revenue_miner` - 矿工收入
- `mining/revenue_from_fees` - 手续费收入
- `mining/mining_revenue_total` - 挖矿总收入
- `mining/thermocap` - 热力学市值
- `mining/thermocap_multiple` - 热力学倍数
- `mining/puell_multiple` - Puell倍数
- `mining/production_total` - 总产量
- `mining/production_miner_revenue_ratio` - 产量收入比

## 12. Supply (供应分析)
- `supply/current` - 当前供应量
- `supply/issued` - 已发行量
- `supply/inflation_rate` - 通胀率
- `supply/burned` - 销毁量
- `supply/burned_rate` - 销毁率
- `supply/liquid` - 流动供应
- `supply/liquid_change` - 流动供应变化
- `supply/liquid_illiquid_sum` - 流动+非流动总和
- `supply/liquid_illiquid_ratio` - 流动/非流动比率
- `supply/llth` - 长期持有者供应
- `supply/loss_total` - 总亏损供应
- `supply/profit_total` - 总盈利供应
- `supply/profit_relative` - 相对盈利供应
- `supply/active_more_24h` - 活跃>24小时
- `supply/active_more_1m_less_3m` - 活跃1-3月
- `supply/active_more_3m_less_6m` - 活跃3-6月
- `supply/active_more_6m_less_12m` - 活跃6-12月
- `supply/active_more_1y_less_2y` - 活跃1-2年
- `supply/active_more_2y_less_3y` - 活跃2-3年
- `supply/active_more_3y_less_5y` - 活跃3-5年
- `supply/active_more_5y_less_7y` - 活跃5-7年
- `supply/active_more_7y_less_10y` - 活跃7-10年
- `supply/active_more_10y` - 活跃>10年

## 13. Transactions (交易分析)
- `transactions/count` - 交易数量
- `transactions/rate` - 交易速率
- `transactions/volume_sum` - 交易量总和
- `transactions/volume_mean` - 平均交易量
- `transactions/volume_median` - 中位数交易量
- `transactions/volume_total` - 总交易量
- `transactions/transfers_count` - 转账数量
- `transactions/transfers_rate` - 转账速率
- `transactions/transfers_volume_sum` - 转账量总和
- `transactions/transfers_volume_mean` - 平均转账量
- `transactions/transfers_volume_median` - 中位数转账量
- `transactions/transfers_to_exchanges_count` - 转入交易所数量
- `transactions/transfers_from_exchanges_count` - 转出交易所数量

## 14. ETH 2.0
- `eth2/staking_total_validators_count` - 总验证者数量
- `eth2/staking_total_deposits_count` - 总存款数量
- `eth2/staking_total_value_staked` - 总质押价值
- `eth2/staking_phase_0_goal_percent` - Phase 0目标百分比
- `eth2/staking_validators_effectiveness` - 验证者有效性
- `eth2/staking_total_volume_sum` - 总质押量

## 15. DeFi
- `defi/total_value_locked` - 总锁定价值(TVL)
- `defi/lending_deposits_sum` - 借贷存款总和
- `defi/lending_borrows_sum` - 借贷借款总和
- `defi/dex_volume_sum` - DEX交易量总和
- `defi/stablecoin_supply_sum` - 稳定币供应总和

## 16. Lightning (闪电网络)
- `lightning/network_capacity_sum` - 网络容量总和
- `lightning/node_count` - 节点数量
- `lightning/channel_count` - 通道数量
- `lightning/average_channel_size` - 平均通道大小
- `lightning/median_channel_size` - 中位数通道大小

## 17. Options (期权)
- `options/open_interest_sum` - 持仓量总和
- `options/volume_sum` - 成交量总和
- `options/put_call_ratio` - 看跌看涨比率
- `options/implied_volatility` - 隐含波动率
- `options/25d_skew` - 25Delta偏斜

## 18. Signals (信号)
- `signals/bitcoin_hash_ribbon_recovery` - 比特币哈希丝带恢复
- `signals/exchange_whale_ratio` - 交易所鲸鱼比率
- `signals/dormancy_flow` - 休眠流
- `signals/entity_adjusted_dormancy_flow` - 实体调整休眠流

## 19. Protocols (协议)
- `protocols/uniswap_v2_liquidity` - Uniswap V2流动性
- `protocols/uniswap_v3_liquidity` - Uniswap V3流动性
- `protocols/sushiswap_liquidity` - SushiSwap流动性
- `protocols/balancer_liquidity` - Balancer流动性

## 使用说明

每个端点的完整URL格式为：
```
https://api.glassnode.com/v1/metrics/{category}/{metric}
```

参数：
- `a`: 资产符号（如 'BTC', 'ETH'）
- `s`: 开始时间（Unix时间戳）
- `u`: 结束时间（Unix时间戳）  
- `i`: 时间间隔（'24h', '1h', '10m'等）
- `f`: 格式（'JSON', 'CSV'）
- `api_key`: API密钥

示例请求：
```bash
curl "https://api.glassnode.com/v1/metrics/indicators/sopr?a=BTC&s=1614556800&u=1614643200&i=24h&api_key=YOUR_KEY"
```