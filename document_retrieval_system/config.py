# -*- coding: utf-8 -*-
"""
配置文件
系统配置参数定义
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """系统配置类"""
    
    # API配置
    ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
    
    # 数据库配置
    DATABASE_PATH = os.getenv("DATABASE_PATH", "documents.db")
    
    # 服务器配置
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # 文档处理配置
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB
    
    # 支持的文件格式
    SUPPORTED_EXTENSIONS = ['.pdf', '.txt', '.md']
    
    # 嵌入模型配置
    EMBEDDING_MODEL = "embedding-3"
    EMBEDDING_DIM = 1024
    
    # 检索配置
    DEFAULT_TOP_K = 10
    MAX_TOP_K = 100
    
    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.ZHIPU_API_KEY:
            raise ValueError("请设置ZHIPU_API_KEY环境变量")
        
        if cls.CHUNK_SIZE <= 0:
            raise ValueError("CHUNK_SIZE必须大于0")
        
        if cls.CHUNK_OVERLAP < 0:
            raise ValueError("CHUNK_OVERLAP不能小于0")
        
        if cls.MAX_FILE_SIZE <= 0:
            raise ValueError("MAX_FILE_SIZE必须大于0")
    
    @classmethod
    def get_info(cls):
        """获取配置信息"""
        return {
            "database_path": cls.DATABASE_PATH,
            "host": cls.HOST,
            "port": cls.PORT,
            "chunk_size": cls.CHUNK_SIZE,
            "chunk_overlap": cls.CHUNK_OVERLAP,
            "max_file_size_mb": cls.MAX_FILE_SIZE // (1024 * 1024),
            "supported_extensions": cls.SUPPORTED_EXTENSIONS,
            "embedding_model": cls.EMBEDDING_MODEL,
            "embedding_dim": cls.EMBEDDING_DIM,
            "default_top_k": cls.DEFAULT_TOP_K,
            "max_top_k": cls.MAX_TOP_K
        }

