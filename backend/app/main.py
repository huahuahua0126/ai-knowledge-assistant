"""
AI知识库助手
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import documents_router, search_router, chat_router, files_router

# 创建 FastAPI 应用
app = FastAPI(
    title="AI知识库助手 API",
    description="智能知识库 API - 语义搜索与 RAG 对话",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(documents_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(files_router, prefix="/api")


@app.get("/")
async def root():
    """健康检查"""
    return {
        "name": "AI知识库助手 API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """详细健康检查"""
    from app.services import index_service
    
    stats = index_service.get_stats()
    
    return {
        "status": "healthy",
        "api_key_configured": bool(settings.dashscope_api_key),
        "notes_directories": [str(p) for p in settings.notes_paths],
        "indexed_documents": stats.get("total_documents", 0)
    }


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print("=" * 50)
    print("� AI知识库助手 Starting...")
    print(f"📁 Notes directories: {settings.notes_directories}")
    print(f"🔑 API Key configured: {bool(settings.dashscope_api_key)}")
    print(f"📊 LLM Model: {settings.llm_model}")
    print("=" * 50)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
