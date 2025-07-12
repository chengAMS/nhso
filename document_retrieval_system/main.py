# -*- coding: utf-8 -*-
"""
FastAPI主应用程序
提供文档上传、处理和检索的API接口
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
import traceback

# 导入自定义模块
from database import DocumentDatabase
from document_processor import DocumentProcessor
from embedding_processor import EmbeddingProcessor

# 创建FastAPI应用实例
app = FastAPI(
    title="文档检索系统",
    description="基于洛伦兹流形的智能文档检索系统",
    version="1.0.0"
)

# 添加CORS中间件，允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 初始化组件
db = DocumentDatabase()
doc_processor = DocumentProcessor()
embedding_processor = EmbeddingProcessor()

# Pydantic模型定义
class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str
    top_k: Optional[int] = 10
    tag_filter: Optional[str] = None

class SearchResult(BaseModel):
    """搜索结果模型"""
    chunk_index: int
    chunk_text: str
    tag: str
    distance: float

class UploadResponse(BaseModel):
    """上传响应模型"""
    success: bool
    message: str
    file_info: dict
    chunks_count: int
    tag: str

class DatabaseStats(BaseModel):
    """数据库统计模型"""
    total_chunks: int
    tags: List[str]

@app.get("/", summary="根路径", description="API根路径，返回欢迎信息")
async def root():
    """根路径端点"""
    return {
        "message": "欢迎使用文档检索系统API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "upload": "/upload",
            "search": "/search",
            "stats": "/stats",
            "health": "/health"
        }
    }

@app.get("/health", summary="健康检查", description="检查系统健康状态")
async def health_check():
    """健康检查端点"""
    try:
        # 检查数据库连接
        chunk_count = db.get_chunk_count()
        
        return {
            "status": "healthy",
            "database": "connected",
            "total_chunks": chunk_count,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"系统健康检查失败: {str(e)}")

@app.post("/upload", response_model=UploadResponse, summary="上传文档", 
          description="上传PDF或TXT文档，自动进行文本分块和嵌入处理")
async def upload_document(
    file: UploadFile = File(..., description="要上传的文档文件"),
    tag: str = Form(..., description="文档标签，用于分类和过滤")
):
    """
    上传文档端点
    
    Args:
        file: 上传的文件（支持PDF、TXT、MD格式）
        tag: 文档标签
        
    Returns:
        上传结果信息
    """
    try:
        # 检查文件大小（限制为50MB）
        if file.size > 50 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="文件大小超过50MB限制")
        
        # 读取文件内容
        file_content = await file.read()
        
        # 获取文件信息
        file_info = doc_processor.get_file_info(file.filename, len(file_content))
        
        # 检查文件格式是否支持
        if not file_info["supported"]:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件格式: {file_info['file_extension']}"
            )
        
        # 处理文档并分块
        chunks = doc_processor.process_and_chunk_file(file_content, file.filename)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="文档内容为空或无法提取文本")
        
        # 生成嵌入向量并转换为洛伦兹流形上的点
        lorentz_points = embedding_processor.process_texts_to_lorentz(chunks)
        
        # 存储到数据库
        stored_count = 0
        for chunk_text, lorentz_point in zip(chunks, lorentz_points):
            try:
                db.insert_chunk(lorentz_point, chunk_text, tag)
                stored_count += 1
            except Exception as e:
                print(f"存储文本块失败: {str(e)}")
                continue
        
        return UploadResponse(
            success=True,
            message=f"文档上传成功，共处理{len(chunks)}个文本块，成功存储{stored_count}个",
            file_info=file_info,
            chunks_count=stored_count,
            tag=tag
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"上传处理错误: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")

@app.post("/search", response_model=List[SearchResult], summary="搜索文档", 
          description="基于洛伦兹流形测地距离搜索相关文档块")
async def search_documents(request: SearchRequest):
    """
    搜索文档端点
    
    Args:
        request: 搜索请求，包含查询文本、返回数量和标签过滤
        
    Returns:
        搜索结果列表
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="查询文本不能为空")
        
        # 将查询文本转换为洛伦兹流形上的点
        query_lorentz_point = embedding_processor.process_text_to_lorentz(request.query)
        
        # 获取存储的文档块
        if request.tag_filter:
            stored_chunks = db.get_chunks_by_tag(request.tag_filter)
        else:
            stored_chunks = db.get_all_chunks()
        
        if not stored_chunks:
            return []
        
        # 在洛伦兹流形上进行相似度搜索
        similar_chunks = embedding_processor.find_similar_chunks(
            query_lorentz_point, 
            stored_chunks, 
            request.top_k
        )
        
        # 构建搜索结果
        results = []
        for chunk_index, chunk_text, tag, distance in similar_chunks:
            results.append(SearchResult(
                chunk_index=chunk_index,
                chunk_text=chunk_text,
                tag=tag,
                distance=float(distance)
            ))
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"搜索处理错误: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"搜索处理失败: {str(e)}")

@app.get("/stats", response_model=DatabaseStats, summary="数据库统计", 
         description="获取数据库中文档块的统计信息")
async def get_database_stats():
    """
    获取数据库统计信息端点
    
    Returns:
        数据库统计信息
    """
    try:
        # 获取总文档块数
        total_chunks = db.get_chunk_count()
        
        # 获取所有标签
        all_chunks = db.get_all_chunks()
        tags = list(set(chunk[3] for chunk in all_chunks))  # chunk[3]是tag字段
        
        return DatabaseStats(
            total_chunks=total_chunks,
            tags=sorted(tags)
        )
        
    except Exception as e:
        print(f"统计信息获取错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@app.delete("/documents/{tag}", summary="删除文档", 
            description="根据标签删除文档块")
async def delete_documents_by_tag(tag: str):
    """
    根据标签删除文档块端点
    
    Args:
        tag: 要删除的文档标签
        
    Returns:
        删除结果信息
    """
    try:
        deleted_count = db.delete_chunks_by_tag(tag)
        
        return {
            "success": True,
            "message": f"成功删除标签为'{tag}'的{deleted_count}个文档块",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        print(f"删除文档错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}")

@app.get("/documents/{tag}", summary="获取文档", 
         description="根据标签获取文档块列表")
async def get_documents_by_tag(tag: str):
    """
    根据标签获取文档块端点
    
    Args:
        tag: 文档标签
        
    Returns:
        文档块列表
    """
    try:
        chunks = db.get_chunks_by_tag(tag)
        
        results = []
        for chunk_index, embedding, chunk_text, chunk_tag in chunks:
            results.append({
                "chunk_index": chunk_index,
                "chunk_text": chunk_text,
                "tag": chunk_tag,
                "text_length": len(chunk_text)
            })
        
        return {
            "tag": tag,
            "chunks_count": len(results),
            "chunks": results
        }
        
    except Exception as e:
        print(f"获取文档错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取文档失败: {str(e)}")

if __name__ == "__main__":
    # 运行FastAPI应用
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # 监听所有网络接口
        port=8000,
        reload=True,  # 开发模式下自动重载
        log_level="info"
    )

