#!/bin/bash
# -*- coding: utf-8 -*-
# 文档检索系统部署脚本

echo "=================================="
echo "文档检索系统部署脚本"
echo "=================================="

# 检查Python版本
echo "检查Python版本..."
python3 --version
if [ $? -ne 0 ]; then
    echo "错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查pip
echo "检查pip..."
pip3 --version
if [ $? -ne 0 ]; then
    echo "错误: 未找到pip3，请先安装pip"
    exit 1
fi

# 安装依赖
echo "安装Python依赖包..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "错误: 依赖包安装失败"
    exit 1
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "创建环境变量文件..."
    cp .env.example .env
    echo "请编辑.env文件，设置您的智谱AI API密钥"
    echo "ZHIPU_API_KEY=your_api_key_here"
fi

# 设置执行权限
chmod +x run.py
chmod +x test_client.py

echo "=================================="
echo "部署完成！"
echo "=================================="
echo "下一步操作："
echo "1. 编辑.env文件，设置API密钥"
echo "2. 运行: python3 run.py"
echo "3. 访问: http://localhost:8000/docs"
echo "=================================="

