"""
搜索 API
"""
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    SearchRequest,
    SearchResponse,
    SearchResultItem
)
from app.services import search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    语义搜索
    
    支持:
    - 自然语言查询
    - 时间范围过滤 (start_date, end_date 或 time_range)
    - 标签过滤
    """
    try:
        results = search_service.search(
            query=request.query,
            top_k=request.top_k,
            start_date=request.start_date,
            end_date=request.end_date,
            time_range=request.time_range,
            tags=request.tags
        )
        
        result_items = [
            SearchResultItem(
                title=r.title,
                content=r.content,
                file_path=r.file_path,
                score=r.score,
                created_at=r.created_at,
                updated_at=r.updated_at,
                metadata=r.metadata
            )
            for r in results
        ]
        
        return SearchResponse(
            success=True,
            results=result_items,
            query=request.query,
            total=len(result_items)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent", response_model=SearchResponse)
async def get_recent(limit: int = 20):
    """
    获取最近更新的文档
    """
    try:
        results = search_service.get_recent_documents(limit=limit)
        
        result_items = [
            SearchResultItem(
                title=r.title,
                content=r.content,
                file_path=r.file_path,
                score=r.score,
                created_at=r.created_at,
                updated_at=r.updated_at,
                metadata=r.metadata
            )
            for r in results
        ]
        
        return SearchResponse(
            success=True,
            results=result_items,
            query="recent",
            total=len(result_items)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similar/{file_path:path}", response_model=SearchResponse)
async def find_similar(file_path: str, top_k: int = 5):
    """
    查找与指定文档相似的其他文档
    """
    try:
        results = search_service.search_by_similarity(
            reference_file_path=file_path,
            top_k=top_k
        )
        
        result_items = [
            SearchResultItem(
                title=r.title,
                content=r.content,
                file_path=r.file_path,
                score=r.score,
                created_at=r.created_at,
                updated_at=r.updated_at,
                metadata=r.metadata
            )
            for r in results
        ]
        
        return SearchResponse(
            success=True,
            results=result_items,
            query=f"similar to {file_path}",
            total=len(result_items)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
