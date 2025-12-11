"""
Pydantic 数据模型
用于 API 请求和响应的数据验证
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ============ 通用响应 ============

class BaseResponse(BaseModel):
    """基础响应"""
    success: bool = True
    message: str = ""


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error: str
    detail: Optional[str] = None


# ============ 文档相关 ============

class DocumentInfo(BaseModel):
    """文档信息"""
    title: str
    file_path: str
    file_name: str
    created_at: str
    updated_at: str
    word_count: int = 0
    tags: List[str] = []


class DocumentListResponse(BaseResponse):
    """文档列表响应"""
    documents: List[DocumentInfo] = []
    total: int = 0


class SyncRequest(BaseModel):
    """同步请求"""
    directories: Optional[List[str]] = None
    force_rebuild: bool = False


class SyncResponse(BaseResponse):
    """同步响应"""
    documents_indexed: int = 0
    time_taken_seconds: float = 0


# ============ 搜索相关 ============

class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., min_length=1, description="搜索查询")
    top_k: int = Field(default=10, ge=1, le=50, description="返回结果数量")
    start_date: Optional[str] = Field(default=None, description="开始日期 (ISO格式)")
    end_date: Optional[str] = Field(default=None, description="结束日期 (ISO格式)")
    time_range: Optional[str] = Field(default=None, description="时间范围: today, week, month, year")
    tags: Optional[List[str]] = Field(default=None, description="标签过滤")


class SearchResultItem(BaseModel):
    """搜索结果项"""
    title: str
    content: str
    file_path: str
    score: float
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = {}


class SearchResponse(BaseResponse):
    """搜索响应"""
    results: List[SearchResultItem] = []
    query: str = ""
    total: int = 0


# ============ 对话/生成相关 ============

class ChatMessage(BaseModel):
    """对话消息"""
    role: str = Field(..., description="角色: user 或 assistant")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """对话请求"""
    messages: List[ChatMessage] = Field(..., min_length=1, description="对话历史")
    top_k: int = Field(default=5, ge=1, le=20, description="参考文档数量")


class GenerateRequest(BaseModel):
    """生成请求"""
    prompt: str = Field(..., min_length=1, description="生成提示")
    top_k: int = Field(default=5, ge=1, le=20, description="参考文档数量")
    style: str = Field(default="professional", description="写作风格: professional, casual, academic")


class SourceInfo(BaseModel):
    """来源信息"""
    index: int
    title: str
    file_path: str
    created_at: str
    content_preview: str
    relevance_score: float


class GenerateResponse(BaseResponse):
    """生成响应"""
    content: str = ""
    sources: List[SourceInfo] = []
    query: str = ""


class ChatResponse(GenerateResponse):
    """对话响应"""
    pass


# ============ 配置相关 ============

class ConfigInfo(BaseModel):
    """配置信息"""
    notes_directories: List[str] = []
    llm_model: str = ""
    embedding_model: str = ""
    has_api_key: bool = False


class ConfigUpdateRequest(BaseModel):
    """配置更新请求"""
    notes_directories: Optional[List[str]] = None
    api_key: Optional[str] = None


class StatsResponse(BaseResponse):
    """统计信息响应"""
    total_documents: int = 0
    indexed_files: int = 0
    notes_directories: List[str] = []
