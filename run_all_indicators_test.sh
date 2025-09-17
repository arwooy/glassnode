#!/bin/bash

# Glassnode全指标测试脚本
echo "========================================"
echo "Glassnode 全指标信息增益分析"
echo "========================================"
echo ""
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 设置API密钥
export GLASSNODE_API_KEY="2lAMxffzOa2lPLbqI6NsBm39Bze"

# 运行测试
python3 glassnode_all_indicators_test.py

# 检查结果文件
echo ""
echo "========================================"
echo "检查生成的文件："
echo "========================================"

if [ -f "glassnode_all_indicators_results.csv" ]; then
    echo "✓ CSV结果文件已生成"
    echo "  文件大小: $(du -h glassnode_all_indicators_results.csv | cut -f1)"
    echo "  行数: $(wc -l glassnode_all_indicators_results.csv | awk '{print $1}')"
fi

if [ -f "glassnode_all_indicators_report.html" ]; then
    echo "✓ HTML报告已生成"
    echo "  文件大小: $(du -h glassnode_all_indicators_report.html | cut -f1)"
fi

if [ -f "glassnode_test_intermediate.json" ]; then
    echo "✓ 中间结果JSON已保存"
    echo "  文件大小: $(du -h glassnode_test_intermediate.json | cut -f1)"
fi

echo ""
echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "提示: 可以打开 glassnode_all_indicators_report.html 查看详细报告"