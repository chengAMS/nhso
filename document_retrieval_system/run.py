#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本
用于启动文档检索系统服务
"""

import uvicorn
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def main():
    """主函数"""
    # 获取配置参数
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print("=" * 50)
    print("文档检索系统启动中...")
    print(f"服务地址: http://{host}:{port}")
    print(f"API文档: http://{host}:{port}/docs")
    print("=" * 50)
    
    # 启动服务
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()

