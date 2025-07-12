#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试客户端
用于测试文档检索系统的各项功能
"""

import requests
import json
import os
from typing import Dict, Any

class DocumentRetrievalClient:
    """文档检索系统客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化客户端
        
        Args:
            base_url: API服务基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def upload_document(self, file_path: str, tag: str) -> Dict[str, Any]:
        """
        上传文档
        
        Args:
            file_path: 文档文件路径
            tag: 文档标签
            
        Returns:
            上传结果
        """
        try:
            if not os.path.exists(file_path):
                return {"error": f"文件不存在: {file_path}"}
            
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                data = {'tag': tag}
                
                response = self.session.post(
                    f"{self.base_url}/upload",
                    files=files,
                    data=data
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            return {"error": str(e)}
    
    def search_documents(self, query: str, top_k: int = 10, tag_filter: str = None) -> Dict[str, Any]:
        """
        搜索文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            tag_filter: 标签过滤
            
        Returns:
            搜索结果
        """
        try:
            data = {
                "query": query,
                "top_k": top_k
            }
            if tag_filter:
                data["tag_filter"] = tag_filter
            
            response = self.session.post(
                f"{self.base_url}/search",
                json=data
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            response = self.session.get(f"{self.base_url}/stats")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_documents_by_tag(self, tag: str) -> Dict[str, Any]:
        """根据标签获取文档"""
        try:
            response = self.session.get(f"{self.base_url}/documents/{tag}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def delete_documents_by_tag(self, tag: str) -> Dict[str, Any]:
        """根据标签删除文档"""
        try:
            response = self.session.delete(f"{self.base_url}/documents/{tag}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def main():
    """主测试函数"""
    print("=" * 60)
    print("文档检索系统测试客户端")
    print("=" * 60)
    
    # 初始化客户端
    client = DocumentRetrievalClient()
    
    # 健康检查
    print("\n1. 健康检查...")
    health = client.health_check()
    print(f"结果: {json.dumps(health, indent=2, ensure_ascii=False)}")
    
    # 获取统计信息
    print("\n2. 获取数据库统计...")
    stats = client.get_stats()
    print(f"结果: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    # 示例搜索（如果数据库中有数据）
    if stats.get("total_chunks", 0) > 0:
        print("\n3. 示例搜索...")
        search_result = client.search_documents("人工智能", top_k=3)
        print(f"结果: {json.dumps(search_result, indent=2, ensure_ascii=False)}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()

