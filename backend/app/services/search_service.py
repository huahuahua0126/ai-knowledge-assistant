"""
检索服务
提供语义搜索和时间感知检索功能
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from llama_index.core.vector_stores import (
    MetadataFilters,
    MetadataFilter,
    FilterOperator,
    FilterCondition
)

from app.services.index_service import index_service


class SearchResult:
    """搜索结果"""
    
    def __init__(
        self,
        title: str,
        content: str,
        file_path: str,
        score: float,
        created_at: str,
        updated_at: str,
        metadata: Dict[str, Any]
    ):
        self.title = title
        self.content = content
        self.file_path = file_path
        self.score = score
        self.created_at = created_at
        self.updated_at = updated_at
        self.metadata = metadata
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "content": self.content,
            "file_path": self.file_path,
            "score": self.score,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }


class SearchService:
    """搜索服务"""
    
    def __init__(self):
        self.default_top_k = 10
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        time_range: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """
        执行语义搜索
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            start_date: 开始日期 (ISO格式)
            end_date: 结束日期 (ISO格式)
            time_range: 时间范围快捷方式 (today, week, month, year)
            tags: 标签过滤
            
        Returns:
            SearchResult 列表
        """
        index = index_service.get_or_create_index()
        
        # 构建元数据过滤器
        filters = self._build_filters(start_date, end_date, time_range, tags)
        
        # 创建查询引擎
        query_engine = index.as_query_engine(
            similarity_top_k=top_k,
            filters=filters if filters else None
        )
        
        # 获取检索器直接使用以获取原始节点
        retriever = index.as_retriever(
            similarity_top_k=top_k,
            filters=filters if filters else None
        )
        
        # 执行检索
        nodes = retriever.retrieve(query)
        
        # 转换为 SearchResult
        results = []
        for node in nodes:
            metadata = node.node.metadata
            results.append(SearchResult(
                title=metadata.get("title", "Untitled"),
                content=node.node.get_content()[:500],  # 截断内容预览
                file_path=metadata.get("file_path", ""),
                score=node.score if node.score else 0.0,
                created_at=metadata.get("created_at", ""),
                updated_at=metadata.get("updated_at", ""),
                metadata=metadata
            ))
        
        return results
    
    def _build_filters(
        self,
        start_date: Optional[str],
        end_date: Optional[str],
        time_range: Optional[str],
        tags: Optional[List[str]]
    ) -> Optional[MetadataFilters]:
        """
        构建元数据过滤器
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            time_range: 时间范围快捷方式
            tags: 标签列表
            
        Returns:
            MetadataFilters 或 None
        """
        filters = []
        
        # 处理时间范围快捷方式
        if time_range:
            now = datetime.now()
            if time_range == "today":
                start_date = now.replace(hour=0, minute=0, second=0).isoformat()
            elif time_range == "week":
                start_date = (now - timedelta(days=7)).isoformat()
            elif time_range == "month":
                start_date = (now - timedelta(days=30)).isoformat()
            elif time_range == "year":
                start_date = (now - timedelta(days=365)).isoformat()
        
        # 添加日期过滤
        if start_date:
            filters.append(MetadataFilter(
                key="created_at",
                value=start_date,
                operator=FilterOperator.GTE
            ))
        
        if end_date:
            filters.append(MetadataFilter(
                key="created_at",
                value=end_date,
                operator=FilterOperator.LTE
            ))
        
        # 添加标签过滤
        if tags:
            for tag in tags:
                filters.append(MetadataFilter(
                    key="tags",
                    value=tag,
                    operator=FilterOperator.CONTAINS
                ))
        
        if not filters:
            return None
        
        return MetadataFilters(
            filters=filters,
            condition=FilterCondition.AND
        )
    
    def get_recent_documents(self, limit: int = 20) -> List[SearchResult]:
        """
        获取最近更新的文档
        
        Args:
            limit: 返回数量限制
            
        Returns:
            SearchResult 列表
        """
        # 使用通用查询获取所有内容，按时间排序
        return self.search(
            query="",
            top_k=limit,
            time_range="month"
        )
    
    def search_by_similarity(
        self,
        reference_file_path: str,
        top_k: int = 5
    ) -> List[SearchResult]:
        """
        查找与指定文档相似的其他文档
        
        Args:
            reference_file_path: 参考文档路径
            top_k: 返回数量
            
        Returns:
            相似文档列表
        """
        # 首先获取参考文档的内容
        from app.services.document_loader import document_loader
        ref_doc = document_loader.load_single_document(reference_file_path)
        
        if ref_doc is None:
            return []
        
        # 使用文档内容作为查询
        results = self.search(
            query=ref_doc.text[:1000],  # 使用前 1000 字符
            top_k=top_k + 1  # 多取一个，因为会包含自己
        )
        
        # 过滤掉参考文档本身
        return [r for r in results if r.file_path != reference_file_path][:top_k]


# 全局实例
search_service = SearchService()
