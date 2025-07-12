# -*- coding: utf-8 -*-
"""
数据库模型和操作
包含文档块的存储和检索功能
"""

import sqlite3
import json
import numpy as np
from typing import List, Tuple, Optional
import os

class DocumentDatabase:
    """文档数据库管理类"""
    
    def __init__(self, db_path: str = "documents.db"):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建文档块表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_chunks (
                chunk_index INTEGER PRIMARY KEY AUTOINCREMENT,
                embedding TEXT NOT NULL,
                chunk_text TEXT NOT NULL,
                tag TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_chunk(self, embedding: np.ndarray, chunk_text: str, tag: str) -> int:
        """
        插入文档块到数据库
        
        Args:
            embedding: 嵌入向量
            chunk_text: 文本块内容
            tag: 标签
            
        Returns:
            插入的记录ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 将numpy数组转换为JSON字符串存储
        embedding_json = json.dumps(embedding.tolist())
        
        cursor.execute('''
            INSERT INTO document_chunks (embedding, chunk_text, tag)
            VALUES (?, ?, ?)
        ''', (embedding_json, chunk_text, tag))
        
        chunk_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return chunk_id
    
    def get_all_chunks(self) -> List[Tuple[int, np.ndarray, str, str]]:
        """
        获取所有文档块
        
        Returns:
            包含(chunk_index, embedding, chunk_text, tag)的列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT chunk_index, embedding, chunk_text, tag
            FROM document_chunks
        ''')
        
        results = []
        for row in cursor.fetchall():
            chunk_index, embedding_json, chunk_text, tag = row
            # 将JSON字符串转换回numpy数组
            embedding = np.array(json.loads(embedding_json))
            results.append((chunk_index, embedding, chunk_text, tag))
        
        conn.close()
        return results
    
    def get_chunks_by_tag(self, tag: str) -> List[Tuple[int, np.ndarray, str, str]]:
        """
        根据标签获取文档块
        
        Args:
            tag: 标签
            
        Returns:
            包含(chunk_index, embedding, chunk_text, tag)的列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT chunk_index, embedding, chunk_text, tag
            FROM document_chunks
            WHERE tag = ?
        ''', (tag,))
        
        results = []
        for row in cursor.fetchall():
            chunk_index, embedding_json, chunk_text, tag = row
            embedding = np.array(json.loads(embedding_json))
            results.append((chunk_index, embedding, chunk_text, tag))
        
        conn.close()
        return results
    
    def delete_chunks_by_tag(self, tag: str) -> int:
        """
        根据标签删除文档块
        
        Args:
            tag: 标签
            
        Returns:
            删除的记录数
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM document_chunks WHERE tag = ?', (tag,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def get_chunk_count(self) -> int:
        """
        获取文档块总数
        
        Returns:
            文档块总数
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM document_chunks')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

