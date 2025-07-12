# -*- coding: utf-8 -*-
"""
嵌入处理模块
包含智谱AI嵌入生成和洛伦兹流形处理功能
"""

import numpy as np
import torch
import geoopt
from zhipuai import ZhipuAI
from typing import List, Tuple
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class EmbeddingProcessor:
    """嵌入处理器类"""
    
    def __init__(self):
        """初始化嵌入处理器"""
        # 从环境变量获取API密钥
        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            raise ValueError("请在.env文件中设置ZHIPU_API_KEY")
        
        # 初始化智谱AI客户端
        self.client = ZhipuAI(api_key=api_key)
        
        # 洛伦兹流形参数
        self.embedding_dim = 1024  # 智谱AI embedding-3模型的维度
        self.lorentz_dim = self.embedding_dim + 1  # 洛伦兹流形多一维
        
        # 初始化洛伦兹流形
        self.manifold = geoopt.Lorentz()
    
    def get_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        获取文本的嵌入向量
        
        Args:
            texts: 文本列表
            
        Returns:
            嵌入向量列表
        """
        try:
            # 调用智谱AI嵌入API
            response = self.client.embeddings.create(
                model="embedding-3",
                input=texts
            )
            
            # 提取嵌入向量
            embeddings = []
            for data in response.data:
                embedding = np.array(data.embedding, dtype=np.float32)
                embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            raise Exception(f"嵌入生成失败: {str(e)}")
    
    def euclidean_to_lorentz(self, euclidean_embedding: np.ndarray) -> np.ndarray:
        """
        将欧几里得嵌入转换为洛伦兹流形上的点
        
        Args:
            euclidean_embedding: 欧几里得空间的嵌入向量
            
        Returns:
            洛伦兹流形上的点
        """
        # 将numpy数组转换为torch张量
        x = torch.tensor(euclidean_embedding, dtype=torch.float32)
        
        # 使用指数映射将欧几里得向量投影到洛伦兹流形
        # 首先在原点处创建一个切向量
        tangent_vec = torch.cat([torch.zeros(1), x])  # 在时间维度添加0
        
        # 在洛伦兹流形的原点（单位时间向量）处进行指数映射
        origin = torch.tensor([1.0] + [0.0] * self.embedding_dim, dtype=torch.float32)
        
        # 使用geoopt的指数映射
        lorentz_point = self.manifold.expmap(tangent_vec, origin)
        
        return lorentz_point.detach().numpy()
    
    def lorentz_distance(self, point1: np.ndarray, point2: np.ndarray) -> float:
        """
        计算洛伦兹流形上两点之间的测地距离
        
        Args:
            point1: 洛伦兹流形上的第一个点
            point2: 洛伦兹流形上的第二个点
            
        Returns:
            测地距离
        """
        # 转换为torch张量
        p1 = torch.tensor(point1, dtype=torch.float32)
        p2 = torch.tensor(point2, dtype=torch.float32)
        
        # 计算洛伦兹内积
        # 洛伦兹内积: -x0*y0 + x1*y1 + ... + xn*yn
        lorentz_inner = -p1[0] * p2[0] + torch.sum(p1[1:] * p2[1:])
        
        # 确保内积值在有效范围内（避免数值误差）
        lorentz_inner = torch.clamp(lorentz_inner, min=-1e10, max=-1.0001)
        
        # 计算测地距离
        distance = torch.acosh(-lorentz_inner)
        
        return distance.item()
    
    def process_text_to_lorentz(self, text: str) -> np.ndarray:
        """
        将文本处理为洛伦兹流形上的点
        
        Args:
            text: 输入文本
            
        Returns:
            洛伦兹流形上的点
        """
        # 获取嵌入向量
        embeddings = self.get_embeddings([text])
        euclidean_embedding = embeddings[0]
        
        # 转换为洛伦兹流形上的点
        lorentz_point = self.euclidean_to_lorentz(euclidean_embedding)
        
        return lorentz_point
    
    def process_texts_to_lorentz(self, texts: List[str]) -> List[np.ndarray]:
        """
        批量将文本处理为洛伦兹流形上的点
        
        Args:
            texts: 文本列表
            
        Returns:
            洛伦兹流形上的点列表
        """
        # 批量获取嵌入向量
        embeddings = self.get_embeddings(texts)
        
        # 转换为洛伦兹流形上的点
        lorentz_points = []
        for embedding in embeddings:
            lorentz_point = self.euclidean_to_lorentz(embedding)
            lorentz_points.append(lorentz_point)
        
        return lorentz_points
    
    def find_similar_chunks(self, query_point: np.ndarray, 
                          stored_points: List[Tuple[int, np.ndarray, str, str]], 
                          top_k: int = 10) -> List[Tuple[int, str, str, float]]:
        """
        在洛伦兹流形上找到最相似的文本块
        
        Args:
            query_point: 查询点（洛伦兹流形上的点）
            stored_points: 存储的点列表，格式为(chunk_index, lorentz_point, chunk_text, tag)
            top_k: 返回最相似的前k个结果
            
        Returns:
            相似文本块列表，格式为(chunk_index, chunk_text, tag, distance)
        """
        similarities = []
        
        for chunk_index, lorentz_point, chunk_text, tag in stored_points:
            # 计算测地距离
            distance = self.lorentz_distance(query_point, lorentz_point)
            similarities.append((chunk_index, chunk_text, tag, distance))
        
        # 按距离排序（距离越小越相似）
        similarities.sort(key=lambda x: x[3])
        
        # 返回前k个结果
        return similarities[:top_k]
    
    def normalize_lorentz_point(self, point: np.ndarray) -> np.ndarray:
        """
        标准化洛伦兹流形上的点
        
        Args:
            point: 洛伦兹流形上的点
            
        Returns:
            标准化后的点
        """
        # 转换为torch张量
        p = torch.tensor(point, dtype=torch.float32)
        
        # 使用geoopt的投影操作确保点在流形上
        normalized_point = self.manifold.projx(p)
        
        return normalized_point.detach().numpy()

