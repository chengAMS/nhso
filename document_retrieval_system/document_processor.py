# -*- coding: utf-8 -*-
"""
文档处理模块
支持PDF文件读取和文本分块功能
"""

import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, BinaryIO
import io
import os

class DocumentProcessor:
    """文档处理器类"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        初始化文档处理器
        
        Args:
            chunk_size: 文本块大小，默认1000字符
            chunk_overlap: 文本块重叠大小，默认200字符
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_file: BinaryIO) -> str:
        """
        从PDF文件中提取文本
        
        Args:
            pdf_file: PDF文件的二进制流
            
        Returns:
            提取的文本内容
        """
        try:
            # 创建PDF阅读器
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # 提取所有页面的文本
            text_content = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text() + "\n"
            
            return text_content.strip()
            
        except Exception as e:
            raise Exception(f"PDF文件读取失败: {str(e)}")
    
    def extract_text_from_txt(self, txt_file: BinaryIO) -> str:
        """
        从TXT文件中提取文本
        
        Args:
            txt_file: TXT文件的二进制流
            
        Returns:
            提取的文本内容
        """
        try:
            # 尝试不同的编码格式
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            
            for encoding in encodings:
                try:
                    txt_file.seek(0)  # 重置文件指针
                    content = txt_file.read().decode(encoding)
                    return content.strip()
                except UnicodeDecodeError:
                    continue
            
            raise Exception("无法识别文件编码格式")
            
        except Exception as e:
            raise Exception(f"TXT文件读取失败: {str(e)}")
    
    def process_file(self, file_content: bytes, filename: str) -> str:
        """
        处理上传的文件，提取文本内容
        
        Args:
            file_content: 文件内容的字节数据
            filename: 文件名
            
        Returns:
            提取的文本内容
        """
        file_stream = io.BytesIO(file_content)
        
        # 根据文件扩展名选择处理方法
        file_extension = os.path.splitext(filename.lower())[1]
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_stream)
        elif file_extension in ['.txt', '.md']:
            return self.extract_text_from_txt(file_stream)
        else:
            raise Exception(f"不支持的文件格式: {file_extension}")
    
    def split_text_into_chunks(self, text: str) -> List[str]:
        """
        将文本分割成块
        
        Args:
            text: 要分割的文本
            
        Returns:
            文本块列表
        """
        if not text.strip():
            return []
        
        # 使用langchain的文本分割器
        chunks = self.text_splitter.split_text(text)
        
        # 过滤掉空的或过短的文本块
        filtered_chunks = []
        for chunk in chunks:
            chunk = chunk.strip()
            if len(chunk) > 10:  # 只保留长度大于10的文本块
                filtered_chunks.append(chunk)
        
        return filtered_chunks
    
    def process_and_chunk_file(self, file_content: bytes, filename: str) -> List[str]:
        """
        处理文件并分割成文本块
        
        Args:
            file_content: 文件内容的字节数据
            filename: 文件名
            
        Returns:
            文本块列表
        """
        # 提取文本
        text = self.process_file(file_content, filename)
        
        # 分割成块
        chunks = self.split_text_into_chunks(text)
        
        return chunks
    
    def get_file_info(self, filename: str, file_size: int) -> dict:
        """
        获取文件信息
        
        Args:
            filename: 文件名
            file_size: 文件大小（字节）
            
        Returns:
            文件信息字典
        """
        file_extension = os.path.splitext(filename.lower())[1]
        
        return {
            "filename": filename,
            "file_extension": file_extension,
            "file_size": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "supported": file_extension in ['.pdf', '.txt', '.md']
        }

