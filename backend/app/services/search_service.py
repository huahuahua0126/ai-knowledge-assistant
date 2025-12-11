"""
检索服务
提供语义搜索、混合检索和时间感知检索功能
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import math
from llama_index.core.vector_stores import (
    MetadataFilters,
    MetadataFilter,
    FilterOperator,
    FilterCondition
)
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.retrievers.bm25 import BM25Retriever

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
    """搜索服务 - 支持混合检索和时间衰减"""
    
    def __init__(self):
        self.default_top_k = 10
        # 时间衰减参数
        self.time_decay_enabled = True
        self.time_decay_half_life_days = 30  # 半衰期：30天后分数减半
        # 混合检索参数
        self.hybrid_search_enabled = True
        self.vector_weight = 0.7  # 向量检索权重
        self.bm25_weight = 0.3    # BM25 检索权重
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        time_range: Optional[str] = None,
        tags: Optional[List[str]] = None,
        use_hybrid: bool = True,
        use_time_decay: bool = True
    ) -> List[SearchResult]:
        """
        执行混合检索 + 时间衰减重排序
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            start_date: 开始日期 (ISO格式)
            end_date: 结束日期 (ISO格式)
            time_range: 时间范围快捷方式 (today, week, month, year)
            tags: 标签过滤
            use_hybrid: 是否使用混合检索
            use_time_decay: 是否使用时间衰减
            
        Returns:
            SearchResult 列表
        """
        index = index_service.get_or_create_index()
        
        # 构建元数据过滤器
        filters = self._build_filters(start_date, end_date, time_range, tags)
        
        # 选择检索策略
        if use_hybrid and self.hybrid_search_enabled:
            nodes = self._hybrid_search(index, query, top_k * 2, filters)  # 多取一些用于重排序
        else:
            nodes = self._vector_search(index, query, top_k * 2, filters)
        
        # 转换为 SearchResult
        results = []
        for node in nodes:
            metadata = node.node.metadata
            score = node.score if node.score else 0.0
            
            # 应用时间衰减
            if use_time_decay and self.time_decay_enabled:
                created_at = metadata.get("created_at", "")
                score = self._apply_time_decay(score, created_at)
            
            results.append(SearchResult(
                title=metadata.get("title", "Untitled"),
                content=node.node.get_content()[:500],
                file_path=metadata.get("file_path", ""),
                score=score,
                created_at=metadata.get("created_at", ""),
                updated_at=metadata.get("updated_at", ""),
                metadata=metadata
            ))
        
        # 按调整后的分数重新排序
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results[:top_k]
    
    def _hybrid_search(self, index, query: str, top_k: int, filters) -> list:
        """
        混合检索：结合 BM25 关键词检索 + 向量语义检索
        
        使用 Reciprocal Rank Fusion (RRF) 融合两种检索结果
        """
        try:
            # 获取所有节点用于 BM25
            all_nodes = list(index.docstore.docs.values())
            
            if not all_nodes:
                return []
            
            # 创建 BM25 检索器
            bm25_retriever = BM25Retriever.from_defaults(
                nodes=all_nodes,
                similarity_top_k=top_k
            )
            
            # 创建向量检索器
            vector_retriever = index.as_retriever(
                similarity_top_k=top_k,
                filters=filters if filters else None
            )
            
            # 创建混合检索器 (QueryFusionRetriever)
            hybrid_retriever = QueryFusionRetriever(
                retrievers=[vector_retriever, bm25_retriever],
                similarity_top_k=top_k,
                num_queries=1,  # 不生成额外查询
                mode="reciprocal_rerank",  # 使用 RRF 融合
                use_async=False
            )
            
            # 执行检索
            nodes = hybrid_retriever.retrieve(query)
            return nodes
            
        except Exception as e:
            print(f"⚠️ Hybrid search failed, falling back to vector search: {e}")
            return self._vector_search(index, query, top_k, filters)
    
    def _vector_search(self, index, query: str, top_k: int, filters) -> list:
        """纯向量语义检索"""
        retriever = index.as_retriever(
            similarity_top_k=top_k,
            filters=filters if filters else None
        )
        return retriever.retrieve(query)
    
    def _apply_time_decay(self, score: float, created_at: str) -> float:
        """
        应用时间衰减
        
        使用指数衰减公式：
        adjusted_score = score * exp(-decay_rate * days_old)
        
        其中 decay_rate = ln(2) / half_life_days
        """
        if not created_at:
            return score
        
        try:
            # 解析创建时间
            if 'T' in created_at:
                doc_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                doc_time = datetime.strptime(created_at, "%Y-%m-%d")
            
            # 计算文档年龄（天数）
            now = datetime.now(doc_time.tzinfo) if doc_time.tzinfo else datetime.now()
            days_old = (now - doc_time).days
            
            if days_old < 0:
                days_old = 0
            
            # 计算衰减系数
            # 使用半衰期公式：decay = 0.5^(days/half_life) = exp(-ln(2) * days / half_life)
            decay_rate = math.log(2) / self.time_decay_half_life_days
            decay_factor = math.exp(-decay_rate * days_old)
            
            # 限制最小衰减系数，避免老文档完全被忽略
            decay_factor = max(decay_factor, 0.1)
            
            return score * decay_factor
            
        except Exception as e:
            print(f"⚠️ Time decay calculation failed: {e}")
            return score
    
    def _build_filters(
        self,
        start_date: Optional[str],
        end_date: Optional[str],
        time_range: Optional[str],
        tags: Optional[List[str]]
    ) -> Optional[MetadataFilters]:
        """
        构建元数据过滤器
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
        """获取最近更新的文档"""
        return self.search(
            query="",
            top_k=limit,
            time_range="month",
            use_hybrid=False,
            use_time_decay=False
        )
    
    def search_by_similarity(
        self,
        reference_file_path: str,
        top_k: int = 5
    ) -> List[SearchResult]:
        """查找与指定文档相似的其他文档"""
        from app.services.document_loader import document_loader
        ref_doc = document_loader.load_single_document(reference_file_path)
        
        if ref_doc is None:
            return []
        
        results = self.search(
            query=ref_doc.text[:1000],
            top_k=top_k + 1,
            use_hybrid=True,
            use_time_decay=False
        )
        
        return [r for r in results if r.file_path != reference_file_path][:top_k]


# 全局实例
search_service = SearchService()
