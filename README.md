# Glassnode API 分析系统

一个全面的 Glassnode API 数据分析系统，用于分析加密货币市场指标和链上数据。

## 🚀 功能特性

- **全面的指标覆盖**：支持 643+ 个 Glassnode API 端点，覆盖 15 个类别
- **信息增益分析**：计算各指标对价格预测的信息增益(IG)和互信息(MI)
- **市场状态识别**：自动识别牛市、熊市、崩盘和震荡期
- **多维数据支持**：处理单值和多维数据格式
- **完整的报告生成**：生成 HTML、CSV 和 JSON 格式的分析报告

## 📁 项目结构

```
glassnode/
│
├── glassnode_endpoints_config.json      # 完整的API端点配置（643个端点）
├── glassnode_all_indicators_test.py     # 主要分析程序
├── glassnode_comprehensive_analysis.py  # 综合分析系统
├── glassnode_information_gain_analysis.py # 信息增益分析
├── glassnode_prediction_analysis.py     # 预测分析
│
├── glassnode_complete_config.py         # 完整配置生成器
├── glassnode_complete_endpoints_final.py # 最终端点配置
├── validate_config.py                   # 配置验证工具
│
├── test_multidim_endpoints.py           # 多维数据测试
├── fetch_all_categories_endpoints.py    # 端点获取工具
│
└── docs/
    ├── glassnode_multidim_indicators.md # 多维指标文档
    └── glassnode_top5_indicators_detail.md # TOP5指标详解
```

## 📊 支持的类别

1. **地址分析** (35 endpoints) - 地址活动和分布
2. **区块链基础** (28 endpoints) - 区块和UTXO数据
3. **衍生品** (91 endpoints) - 期货和期权数据
4. **分布分析** (42 endpoints) - 余额和持有分布
5. **实体分析** (28 endpoints) - 实体级别指标
6. **ETH2.0** (7 endpoints) - 以太坊2.0相关
7. **手续费** (42 endpoints) - 交易费用分析
8. **核心指标** (68 endpoints) - SOPR、NUPL、MVRV等
9. **机构指标** (47 endpoints) - ETF和机构数据
10. **闪电网络** (24 endpoints) - 闪电网络统计
11. **市场数据** (51 endpoints) - 价格和市值
12. **内存池** (26 endpoints) - 内存池分析
13. **挖矿数据** (30 endpoints) - 挖矿相关指标
14. **供应分析** (68 endpoints) - 供应动态
15. **交易分析** (56 endpoints) - 交易量和转账

## 🔧 安装和使用

### 环境要求

```bash
pip install pandas numpy scipy requests
```

### 配置 API 密钥

在代码中设置你的 Glassnode API 密钥：

```python
API_KEY = "your_api_key_here"
```

### 运行分析

```bash
# 运行完整的指标测试
python glassnode_all_indicators_test.py

# 运行综合分析
python glassnode_comprehensive_analysis.py

# 验证配置
python validate_config.py
```

## 📈 主要指标说明

### TOP 5 预测指标

1. **NUPL (Net Unrealized Profit/Loss)** - 净未实现盈亏
   - 信息增益: 0.105
   - 衡量整体市场情绪

2. **Reserve Risk** - 储备风险
   - 信息增益: 0.098
   - 评估长期持有者信心

3. **SOPR (Spent Output Profit Ratio)** - 花费产出利润率
   - 信息增益: 0.095
   - 实时盈亏指标

4. **MVRV (Market Value to Realized Value)** - 市场价值与实现价值比
   - 信息增益: 0.092
   - 估值指标

5. **Hash Rate** - 哈希率
   - 信息增益: 0.089
   - 网络安全性指标

## 📊 输出格式

- **HTML报告**: `glassnode_all_indicators_report.html`
- **CSV数据**: `glassnode_all_indicators_results.csv`
- **JSON配置**: `glassnode_endpoints_config.json`
- **中间结果**: `glassnode_test_intermediate.json`

## 🔍 数据处理特性

- 支持单值数据（'v'字段）和多维数据（'o'字段）
- 自动计算赫芬达尔指数(HHI)用于分布数据
- 智能处理API限流和错误
- 增量保存中间结果

## 📝 License

MIT License

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请在 GitHub 上提交 Issue。

---

**注意**: 使用此系统需要有效的 Glassnode API 密钥。某些端点可能需要专业版订阅。