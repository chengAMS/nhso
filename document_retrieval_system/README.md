# 文档检索系统

基于洛伦兹流形的智能文档检索系统，支持PDF文件上传、文本分块、嵌入生成和高精度检索。

## 功能特性

- 📄 **多格式支持**: 支持PDF、TXT、MD文件上传
- 🔍 **智能检索**: 基于洛伦兹流形的测地距离检索
- 🧠 **AI嵌入**: 使用智谱AI embedding-3模型生成高质量嵌入
- 📊 **文本分块**: 使用LangChain进行智能文本分割
- 🗄️ **数据存储**: SQLite数据库存储文档块和嵌入向量
- 🚀 **高性能**: FastAPI框架提供高性能API服务
- 🏷️ **标签管理**: 支持文档标签分类和过滤

## 技术架构

### 核心组件

1. **文档处理器** (`document_processor.py`)
   - PDF文本提取
   - 文本分块（chunk_size=1000）
   - 多格式文件支持

2. **嵌入处理器** (`embedding_processor.py`)
   - 智谱AI嵌入生成
   - 洛伦兹流形转换
   - 测地距离计算

3. **数据库管理** (`database.py`)
   - SQLite数据库操作
   - 嵌入向量存储
   - 标签管理

4. **API服务** (`main.py`)
   - FastAPI REST API
   - 文件上传接口
   - 检索查询接口

### 洛伦兹流形处理

系统使用洛伦兹流形进行向量检索，具有以下优势：
- **高维几何**: 洛伦兹流形比欧几里得空间多一维
- **指数投影**: 通过指数映射将欧几里得向量投影到流形
- **测地距离**: 使用测地距离计算相似度，更准确反映语义关系

## 安装部署

### 环境要求

- Python 3.8+
- 智谱AI API密钥

### 安装步骤

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，设置您的智谱AI API密钥
```

3. **启动服务**
```bash
python run.py
```

服务启动后访问：
- API服务: http://localhost:8000
- API文档: http://localhost:8000/docs

## API接口

### 1. 文档上传
```http
POST /upload
Content-Type: multipart/form-data

参数:
- file: 文档文件（PDF/TXT/MD）
- tag: 文档标签
```

### 2. 文档检索
```http
POST /search
Content-Type: application/json

{
  "query": "查询文本",
  "top_k": 10,
  "tag_filter": "可选标签过滤"
}
```

### 3. 数据库统计
```http
GET /stats
```

### 4. 删除文档
```http
DELETE /documents/{tag}
```

### 5. 获取文档
```http
GET /documents/{tag}
```

## 使用示例

### Python客户端示例

```python
import requests

# 上传文档
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/upload",
        files={"file": f},
        data={"tag": "技术文档"}
    )
print(response.json())

# 搜索文档
search_data = {
    "query": "人工智能的应用",
    "top_k": 5
}
response = requests.post(
    "http://localhost:8000/search",
    json=search_data
)
print(response.json())
```

### cURL示例

```bash
# 上传文档
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "tag=技术文档"

# 搜索文档
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "人工智能的应用", "top_k": 5}'
```

## 数据库结构

```sql
CREATE TABLE document_chunks (
    chunk_index INTEGER PRIMARY KEY AUTOINCREMENT,
    embedding TEXT NOT NULL,           -- JSON格式的洛伦兹流形向量
    chunk_text TEXT NOT NULL,          -- 文本块内容
    tag TEXT NOT NULL,                 -- 文档标签
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 配置说明

### 环境变量

- `ZHIPU_API_KEY`: 智谱AI API密钥（必需）
- `DATABASE_PATH`: 数据库文件路径（可选，默认documents.db）
- `HOST`: 服务监听地址（可选，默认0.0.0.0）
- `PORT`: 服务端口（可选，默认8000）

### 文本分块参数

- `chunk_size`: 文本块大小（默认1000字符）
- `chunk_overlap`: 文本块重叠（默认200字符）

## 性能优化

1. **批量处理**: 支持批量嵌入生成，提高处理效率
2. **向量缓存**: 嵌入向量存储在数据库中，避免重复计算
3. **异步处理**: FastAPI异步框架，支持高并发请求
4. **内存优化**: 流式文件处理，支持大文件上传

## 错误处理

系统包含完善的错误处理机制：
- 文件格式验证
- 文件大小限制（50MB）
- API密钥验证
- 数据库连接检查
- 详细错误日志

## 扩展功能

### 支持的文件格式
- PDF文档
- TXT文本文件
- Markdown文件

### 未来扩展
- Word文档支持
- 图片OCR识别
- 多语言支持
- 分布式部署

## 故障排除

### 常见问题

1. **API密钥错误**
   - 检查.env文件中的ZHIPU_API_KEY设置
   - 确认API密钥有效且有足够额度

2. **文件上传失败**
   - 检查文件格式是否支持
   - 确认文件大小不超过50MB

3. **检索结果为空**
   - 确认数据库中有相关文档
   - 检查标签过滤条件

4. **服务启动失败**
   - 检查端口是否被占用
   - 确认所有依赖包已正确安装

## 开发说明

### 项目结构
```
document_retrieval_system/
├── main.py                 # FastAPI主应用
├── database.py            # 数据库操作
├── document_processor.py  # 文档处理
├── embedding_processor.py # 嵌入处理
├── requirements.txt       # 依赖包
├── .env.example          # 环境变量模板
├── run.py                # 启动脚本
└── README.md             # 说明文档
```

### 代码规范
- 使用中文注释
- 遵循PEP 8代码规范
- 完整的错误处理
- 详细的API文档

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 技术交流群

---

**注意**: 使用前请确保已获得智谱AI API密钥，并遵守相关服务条款。

