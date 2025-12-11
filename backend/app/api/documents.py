"""
文档管理 API
"""
import time
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    DocumentListResponse,
    DocumentInfo,
    SyncRequest,
    SyncResponse,
    StatsResponse,
    ErrorResponse
)
from app.services import document_loader, index_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=DocumentListResponse)
async def list_documents():
    """
    获取已索引的文档列表
    """
    try:
        documents = document_loader.load_all_documents()
        
        doc_list = [
            DocumentInfo(
                title=doc.metadata.get("title", "Untitled"),
                file_path=doc.metadata.get("file_path", ""),
                file_name=doc.metadata.get("file_name", ""),
                created_at=doc.metadata.get("created_at", ""),
                updated_at=doc.metadata.get("updated_at", ""),
                word_count=doc.metadata.get("word_count", 0),
                tags=doc.metadata.get("tags", [])
            )
            for doc in documents
        ]
        
        return DocumentListResponse(
            success=True,
            documents=doc_list,
            total=len(doc_list)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync", response_model=SyncResponse)
async def sync_documents(request: SyncRequest):
    """
    同步/重建文档索引
    """
    try:
        start_time = time.time()
        
        if request.force_rebuild:
            # 强制重建整个索引
            count = index_service.build_full_index()
        else:
            # 增量更新
            count = index_service.build_full_index()  # TODO: 实现真正的增量更新
        
        elapsed = time.time() - start_time
        
        return SyncResponse(
            success=True,
            message=f"Successfully indexed {count} documents",
            documents_indexed=count,
            time_taken_seconds=round(elapsed, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    获取索引统计信息
    """
    try:
        stats = index_service.get_stats()
        from app.config import settings
        
        return StatsResponse(
            success=True,
            total_documents=stats.get("total_documents", 0),
            indexed_files=stats.get("indexed_files", 0),
            notes_directories=[str(p) for p in settings.notes_paths]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{file_path:path}")
async def delete_document(file_path: str):
    """
    从索引中删除文档
    """
    try:
        success = index_service.delete_document(file_path)
        if success:
            return {"success": True, "message": "Document deleted from index"}
        else:
            raise HTTPException(status_code=404, detail="Document not found in index")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
