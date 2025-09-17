# Bridges（跨链桥）API 详细文档

## 概述

Bridges API 提供跨链桥接协议的全面数据分析，包括跨链资产转移、桥接流动性、安全性评估、跨链交易统计等。这些数据对于理解多链生态系统的互操作性、评估跨链风险、识别套利机会以及监控DeFi生态系统的资金流动至关重要。

## 基础信息

**基础 URL**: `https://api.glassnode.com/v1/metrics/bridges/`

**支持的资产**: BTC, ETH, USDT, USDC 等主要加密资产

**数据更新频率**: 
- 实时数据：1分钟
- 聚合数据：10分钟、1小时、24小时

## 核心端点

### 1. 桥接总价值锁定（TVL）

#### 1.1 跨链TVL总览

**端点**: `/tvl_sum`

**描述**: 所有桥接协议中锁定的总价值，反映跨链生态系统的规模。

**参数**:
- `a`: 资产符号（如 ETH）
- `i`: 时间间隔（1h, 24h）
- `s`: 开始时间戳
- `bridge`: 特定桥接协议（可选）

**示例请求**:
```bash
curl -X GET "https://api.glassnode.com/v1/metrics/bridges/tvl_sum?a=ETH&i=24h&s=1609459200" \
  -H "X-Api-Key: YOUR_API_KEY"
```