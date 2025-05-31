#!/bin/bash

echo "========================================"
echo "医疗产品短名称生成器"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误：未检测到Python3，请先安装Python 3.7或更高版本"
    exit 1
fi

# 运行启动脚本
python3 start.py
