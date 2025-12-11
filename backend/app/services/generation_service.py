"""
生成服务
基于 RAG 的内容生成和来源引用
"""
from typing import List, Dict, Any, Optional
from llama_index.core import PromptTemplate
from llama_index.core.response_synthesizers import ResponseMode

from app.services.index_service import index_service


# RAG Prompt 模板
RAG_PROMPT_TEMPLATE = """你是用户的个人知识助手。请基于以下笔记内容回答问题或完成任务。

要求：
1. 仅使用提供的笔记内容，不要编造信息
2. 生成内容时，用【来源X】标注引用了哪篇笔记
3. 保持用户一贯的行文风格
4. 如果笔记中没有相关信息，请明确说明

### 参考笔记内容
{context_str}

### 用户请求
{query_str}

### 回答
"""

SUMMARY_PROMPT_TEMPLATE = """请基于以下笔记内容生成一份简洁的总结：

### 笔记内容
{context_str}

### 总结要求
{query_str}

请生成总结，并在末尾注明参考了哪些笔记【来源X】：
"""


class SourceReference:
    """来源引用"""
    
    def __init__(
        self,
        index: int,
        title: str,
        file_path: str,
        created_at: str,
        content_preview: str,
        relevance_score: float
    ):
        self.index = index
        self.title = title
        self.file_path = file_path
        self.created_at = created_at
        self.content_preview = content_preview
        self.relevance_score = relevance_score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "title": self.title,
            "file_path": self.file_path,
            "created_at": self.created_at,
            "content_preview": self.content_preview,
            "relevance_score": self.relevance_score
        }


class GenerationResult:
    """生成结果"""
    
    def __init__(
        self,
        content: str,
        sources: List[SourceReference],
        query: str
    ):
        self.content = content
        self.sources = sources
        self.query = query
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "sources": [s.to_dict() for s in self.sources],
            "query": self.query
        }


class GenerationService:
    """生成服务"""
    
    def __init__(self):
        self.default_top_k = 5
    
    def generate_response(
        self,
        query: str,
        top_k: int = 5,
        prompt_template: Optional[str] = None
    ) -> GenerationResult:
        """
        基于知识库生成回答
        
        Args:
            query: 用户查询
            top_k: 参考文档数量
            prompt_template: 自定义 prompt 模板
            
        Returns:
            GenerationResult
        """
        index = index_service.get_or_create_index()
        
        # 使用自定义或默认模板
        template = prompt_template or RAG_PROMPT_TEMPLATE
        qa_prompt = PromptTemplate(template)
        
        # 创建查询引擎
        query_engine = index.as_query_engine(
            similarity_top_k=top_k,
            text_qa_template=qa_prompt,
            response_mode=ResponseMode.COMPACT
        )
        
        # 执行查询
        response = query_engine.query(query)
        
        # 提取来源
        sources = self._extract_sources(response.source_nodes)
        
        return GenerationResult(
            content=str(response),
            sources=sources,
            query=query
        )
    
    def generate_summary(
        self,
        topic: str,
        top_k: int = 10
    ) -> GenerationResult:
        """
        生成主题摘要
        
        Args:
            topic: 主题描述
            top_k: 参考文档数量
            
        Returns:
            GenerationResult
        """
        return self.generate_response(
            query=f"请总结关于「{topic}」的内容",
            top_k=top_k,
            prompt_template=SUMMARY_PROMPT_TEMPLATE
        )
    
    def generate_report(
        self,
        requirements: str,
        style: str = "professional",
        top_k: int = 10
    ) -> GenerationResult:
        """
        生成报告
        
        Args:
            requirements: 报告要求
            style: 写作风格 (professional, casual, academic)
            top_k: 参考文档数量
            
        Returns:
            GenerationResult
        """
        style_hints = {
            "professional": "使用专业、正式的语言风格",
            "casual": "使用轻松、口语化的风格",
            "academic": "使用学术、严谨的风格，注意逻辑结构"
        }
        
        enhanced_query = f"""
{requirements}

写作风格要求：{style_hints.get(style, style_hints['professional'])}
"""
        
        return self.generate_response(
            query=enhanced_query,
            top_k=top_k
        )
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        top_k: int = 5
    ) -> GenerationResult:
        """
        对话式交互
        
        Args:
            messages: 对话历史 [{"role": "user/assistant", "content": "..."}]
            top_k: 参考文档数量
            
        Returns:
            GenerationResult
        """
        # 构建对话上下文
        conversation = "\n".join([
            f"{'用户' if m['role'] == 'user' else 'AI'}: {m['content']}"
            for m in messages[-5:]  # 保留最近5轮对话
        ])
        
        # 获取最新的用户消息
        latest_query = messages[-1]["content"] if messages else ""
        
        chat_prompt = f"""基于以下对话上下文和知识库内容，继续对话：

### 对话历史
{conversation}

### 请基于知识库回答用户最新的问题
"""
        
        return self.generate_response(
            query=chat_prompt,
            top_k=top_k
        )
    
    def _extract_sources(self, source_nodes) -> List[SourceReference]:
        """
        从响应中提取来源引用
        
        Args:
            source_nodes: LlamaIndex source nodes
            
        Returns:
            SourceReference 列表
        """
        sources = []
        
        for i, node in enumerate(source_nodes, 1):
            metadata = node.node.metadata
            sources.append(SourceReference(
                index=i,
                title=metadata.get("title", "Untitled"),
                file_path=metadata.get("file_path", ""),
                created_at=metadata.get("created_at", ""),
                content_preview=node.node.get_content()[:200],
                relevance_score=node.score if node.score else 0.0
            ))
        
        return sources


# 全局实例
generation_service = GenerationService()
