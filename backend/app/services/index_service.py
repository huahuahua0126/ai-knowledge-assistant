"""
索引服务
管理向量索引的创建、更新和持久化
使用 LlamaIndex 内置的简单向量存储 (无需 chromadb)
"""
import hashlib
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Settings,
    load_index_from_storage
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.dashscope import DashScope
from llama_index.embeddings.dashscope import DashScopeEmbedding

from app.config import settings
from app.services.document_loader import document_loader, Document


class IndexService:
    """索引管理服务"""
    
    PERSIST_DIR = None
    
    def __init__(self):
        """初始化索引服务"""
        self._index: Optional[VectorStoreIndex] = None
        self._file_hashes: Dict[str, str] = {}
        
        # 设置持久化目录
        self.PERSIST_DIR = str(settings.chroma_path / "index")
        
        # 配置 LlamaIndex 全局设置
        self._configure_llm_settings()
    
    def _configure_llm_settings(self):
        """配置 LLM 和 Embedding 模型"""
        if settings.dashscope_api_key:
            # 设置环境变量 (dashscope 需要)
            os.environ["DASHSCOPE_API_KEY"] = settings.dashscope_api_key
            
            Settings.llm = DashScope(
                model_name=settings.llm_model,
                api_key=settings.dashscope_api_key,
                max_tokens=2048  # 适当的输出 token 限制
            )
            Settings.embed_model = DashScopeEmbedding(
                model_name=settings.embedding_model,
                api_key=settings.dashscope_api_key
            )
        
        # 配置文本分块
        Settings.node_parser = SentenceSplitter(
            chunk_size=512,
            chunk_overlap=50
        )
    
    def get_or_create_index(self) -> VectorStoreIndex:
        """
        获取或创建向量索引
        
        Returns:
            VectorStoreIndex 实例
        """
        if self._index is not None:
            return self._index
        
        persist_path = Path(self.PERSIST_DIR)
        
        # 尝试从存储加载
        if persist_path.exists() and (persist_path / "docstore.json").exists():
            try:
                storage_context = StorageContext.from_defaults(persist_dir=self.PERSIST_DIR)
                self._index = load_index_from_storage(storage_context)
                print(f"✅ Loaded existing index from {self.PERSIST_DIR}")
                return self._index
            except Exception as e:
                print(f"⚠️ Failed to load index: {e}, will create new one")
        
        # 创建新的空索引
        self._index = VectorStoreIndex([])
        return self._index
    
    def build_full_index(self) -> int:
        """
        构建完整索引（首次或重建）
        
        Returns:
            索引的文档数量
        """
        # 加载所有文档
        documents = document_loader.load_all_documents()
        
        if not documents:
            print("⚠️ No documents found to index")
            return 0
        
        print(f"📚 Found {len(documents)} documents to index")
        
        # 创建新索引
        self._index = VectorStoreIndex.from_documents(
            documents=documents,
            show_progress=True
        )
        
        # 持久化
        persist_path = Path(self.PERSIST_DIR)
        persist_path.mkdir(parents=True, exist_ok=True)
        self._index.storage_context.persist(persist_dir=self.PERSIST_DIR)
        
        print(f"✅ Index built and saved to {self.PERSIST_DIR}")
        
        # 记录文件哈希
        for doc in documents:
            file_path = doc.metadata.get("file_path")
            if file_path:
                self._file_hashes[file_path] = self._compute_file_hash(file_path)
        
        return len(documents)
    
    def update_document(self, file_path: str) -> bool:
        """
        更新单个文档（增量更新）
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否更新成功
        """
        index = self.get_or_create_index()
        
        # 检查文件是否真的变更了
        current_hash = self._compute_file_hash(file_path)
        if file_path in self._file_hashes and self._file_hashes[file_path] == current_hash:
            return False  # 文件未变更
        
        # 加载新文档
        document = document_loader.load_single_document(file_path)
        if document is None:
            return False
        
        # 删除旧的索引条目（如果存在）
        try:
            index.delete_ref_doc(file_path, delete_from_docstore=True)
        except Exception:
            pass  # 可能不存在
        
        # 插入新文档
        index.insert(document)
        
        # 持久化
        index.storage_context.persist(persist_dir=self.PERSIST_DIR)
        
        # 更新哈希
        self._file_hashes[file_path] = current_hash
        
        return True
    
    def delete_document(self, file_path: str) -> bool:
        """
        删除文档索引
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否删除成功
        """
        index = self.get_or_create_index()
        
        try:
            index.delete_ref_doc(file_path, delete_from_docstore=True)
            index.storage_context.persist(persist_dir=self.PERSIST_DIR)
            self._file_hashes.pop(file_path, None)
            return True
        except Exception as e:
            print(f"Failed to delete document {file_path}: {e}")
            return False
    
    def _compute_file_hash(self, file_path: str) -> str:
        """计算文件内容哈希"""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def get_stats(self) -> Dict:
        """获取索引统计信息"""
        try:
            index = self.get_or_create_index()
            # 获取文档数量
            doc_count = len(index.docstore.docs) if hasattr(index, 'docstore') else 0
            return {
                "total_documents": doc_count,
                "indexed_files": len(self._file_hashes)
            }
        except Exception:
            return {
                "total_documents": 0,
                "indexed_files": 0
            }


# 全局实例
index_service = IndexService()
