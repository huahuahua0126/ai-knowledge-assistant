"""
对话/生成 API
"""
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    GenerateRequest,
    GenerateResponse,
    SourceInfo
)
from app.services import generation_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    对话式交互
    
    基于知识库内容进行对话，自动引用相关笔记
    """
    try:
        # 转换消息格式
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        result = generation_service.chat(
            messages=messages,
            top_k=request.top_k
        )
        
        sources = [
            SourceInfo(
                index=s.index,
                title=s.title,
                file_path=s.file_path,
                created_at=s.created_at,
                content_preview=s.content_preview,
                relevance_score=s.relevance_score
            )
            for s in result.sources
        ]
        
        return ChatResponse(
            success=True,
            content=result.content,
            sources=sources,
            query=result.query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    内容生成
    
    基于知识库生成报告、总结等内容
    """
    try:
        result = generation_service.generate_report(
            requirements=request.prompt,
            style=request.style,
            top_k=request.top_k
        )
        
        sources = [
            SourceInfo(
                index=s.index,
                title=s.title,
                file_path=s.file_path,
                created_at=s.created_at,
                content_preview=s.content_preview,
                relevance_score=s.relevance_score
            )
            for s in result.sources
        ]
        
        return GenerateResponse(
            success=True,
            content=result.content,
            sources=sources,
            query=result.query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summary", response_model=GenerateResponse)
async def summarize(topic: str, top_k: int = 10):
    """
    生成主题摘要
    """
    try:
        result = generation_service.generate_summary(
            topic=topic,
            top_k=top_k
        )
        
        sources = [
            SourceInfo(
                index=s.index,
                title=s.title,
                file_path=s.file_path,
                created_at=s.created_at,
                content_preview=s.content_preview,
                relevance_score=s.relevance_score
            )
            for s in result.sources
        ]
        
        return GenerateResponse(
            success=True,
            content=result.content,
            sources=sources,
            query=result.query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
