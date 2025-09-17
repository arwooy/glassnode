# Glassnode API 综合文档

## 概述

Glassnode API 提供了全面的区块链和加密货币市场数据访问接口。API 涵盖了从基础链上数据到高级市场分析的各个方面，支持超过 200 种加密货币资产。

## API 基础信息

### 基础 URL
```
https://api.glassnode.com/v1/metrics/
```

### 认证方式
- **API Key 认证**：所有接口都需要有效的 API Key
- 在请求头中添加：`X-Api-Key: YOUR_API_KEY`

### 通用参数

| 参数 | 别名 | 类型 | 必需 | 说明 | 示例 |
|-----|------|------|------|------|------|
| `asset` | `a` | string | 是 | 资产标识符 | BTC, ETH |
| `since` | `s` | integer | 否 | 开始时间（Unix 时间戳） | 1614556800 |
| `until` | `u` | integer | 否 | 结束时间（Unix 时间戳） | 1614643200 |
| `frequency` | `i` | string | 否 | 数据频率 | 10m, 1h, 24h, 1w, 1month |
| `format` | `f` | string | 否 | 响应格式 | json (默认), csv |
| `timestamp_format` | - | string | 否 | 时间戳格式 | unix (默认), humanized |

### 响应格式

#### JSON 格式（默认）
```json
[
  {
    "t": 1614556800,
    "v": 54321.5
  },
  {
    "t": 1614643200,
    "v": 55678.9
  }
]
```

#### CSV 格式
```csv
t,v
1614556800,54321.5
1614643200,55678.9
```

### HTTP 状态码

| 状态码 | 说明 |
|-------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（API Key 无效） |
| 429 | 请求频率超限 |

## API 端点分类

Glassnode API 包含以下主要分类：

### 1. **Addresses（地址分析）**
分析区块链地址的活动、余额分布和盈亏状况。

### 2. **Blockchain（区块链数据）**
提供区块高度、出块时间、区块大小等基础链上数据。

### 3. **DeFi（去中心化金融）**
跟踪 DeFi 协议的总锁定价值（TVL）和相关指标。

### 4. **Derivatives（衍生品）**
期货和期权市场数据，包括未平仓合约、交易量和清算数据。

### 5. **Market（市场指标）**
市值、MVRV、价格变化等市场分析指标。

### 6. **Supply（供应分析）**
流通供应量、流动性供应、长期持有者供应等。

### 7. **Transactions（交易数据）**
链上交易量、交易所流入流出、实体调整后的交易数据。

### 8. **Fees（手续费）**
网络手续费、Gas 使用情况、矿工收入等。

### 9. **Mining（挖矿数据）**
算力、难度、矿工收入和相关指标。

### 10. **其他分类**
- **Bridges**：跨链桥接数据
- **Breakdowns**：详细分解数据
- **Distribution**：分布数据
- **Entities**：实体分析
- **ETH 2.0**：以太坊 2.0 相关数据
- **Indicators**：技术指标
- **Institutions**：机构数据
- **Lightning**：闪电网络
- **Mempool**：内存池
- **Options**：期权数据
- **Point-In-Time**：时点数据
- **Protocols**：协议数据
- **Signals**：交易信号

## 使用示例

### 示例 1：获取比特币活跃地址数
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/addresses/active_count" \
  -H "X-Api-Key: YOUR_API_KEY" \
  -d "a=BTC" \
  -d "s=1614556800" \
  -d "u=1614643200" \
  -d "i=24h"
```

### 示例 2：获取以太坊 DeFi TVL
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/defi/total_value_locked" \
  -H "X-Api-Key: YOUR_API_KEY" \
  -d "a=ETH" \
  -d "i=1h" \
  -d "f=json"
```

### 示例 3：获取市场 MVRV 比率
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/market/mvrv" \
  -H "X-Api-Key: YOUR_API_KEY" \
  -d "a=BTC" \
  -d "i=24h"
```

## 数据更新频率

不同的端点支持不同的数据更新频率：

- **实时数据（10m）**：部分高频交易和市场数据
- **小时数据（1h）**：大部分链上指标
- **日数据（24h）**：标准分析指标
- **周数据（1w）**：长期趋势分析
- **月数据（1month）**：宏观市场分析

## 最佳实践

1. **缓存数据**：对于历史数据，建议在本地缓存以减少 API 调用
2. **批量请求**：使用合适的时间范围和频率，避免过多的小请求
3. **错误处理**：实现重试机制处理临时网络错误
4. **速率限制**：遵守 API 速率限制，避免请求被拒绝
5. **数据验证**：验证返回的数据完整性和时间戳连续性

## 支持的资产

Glassnode 支持超过 200 种加密货币，主要包括：

- **主流币种**：BTC, ETH, LTC, BCH, XRP
- **稳定币**：USDT, USDC, DAI, BUSD
- **DeFi 代币**：UNI, AAVE, COMP, MKR
- **Layer 2**：MATIC, ARB, OP
- **其他主流资产**：BNB, SOL, ADA, DOT, AVAX

## 联系支持

如需技术支持或定制化服务，请联系 Glassnode Expert Services。

---

*本文档基于 Glassnode API 官方文档编写，具体接口详情请参考各分类的详细文档。*