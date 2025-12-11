"""
文档加载服务
负责从本地文件系统加载 Markdown 笔记并提取元数据
"""
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import frontmatter
from llama_index.core import Document
from llama_index.core.readers import SimpleDirectoryReader

from app.config import settings


class DocumentLoader:
    """文档加载器"""
    
    SUPPORTED_EXTENSIONS = [".md", ".txt", ".markdown"]
    
    def __init__(self, directories: Optional[List[Path]] = None):
        """
        初始化文档加载器
        
        Args:
            directories: 笔记目录列表，默认从配置读取
        """
        self.directories = directories or settings.notes_paths
    
    def load_all_documents(self) -> List[Document]:
        """
        加载所有目录下的文档
        
        Returns:
            LlamaIndex Document 列表
        """
        all_documents = []
        
        for directory in self.directories:
            if directory.exists():
                documents = self._load_from_directory(directory)
                all_documents.extend(documents)
        
        return all_documents
    
    def _load_from_directory(self, directory: Path) -> List[Document]:
        """
        从单个目录加载文档
        
        Args:
            directory: 目录路径
            
        Returns:
            Document 列表
        """
        documents = []
        
        for file_path in directory.rglob("*"):
            if file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                try:
                    doc = self._load_single_file(file_path)
                    if doc:
                        documents.append(doc)
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        
        return documents
    
    def _load_single_file(self, file_path: Path) -> Optional[Document]:
        """
        加载单个文件并提取元数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            LlamaIndex Document 或 None
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 提取元数据
            metadata = self._extract_metadata(file_path, content)
            
            # 如果是 markdown，解析 frontmatter
            if file_path.suffix.lower() in [".md", ".markdown"]:
                post = frontmatter.loads(content)
                # 合并 frontmatter 中的元数据
                metadata.update(post.metadata)
                content = post.content
            
            return Document(
                text=content,
                metadata=metadata,
                doc_id=str(file_path)
            )
            
        except Exception as e:
            print(f"Failed to load {file_path}: {e}")
            return None
    
    def _extract_metadata(self, file_path: Path, content: str) -> Dict[str, Any]:
        """
        提取文件元数据
        
        Args:
            file_path: 文件路径
            content: 文件内容
            
        Returns:
            元数据字典
        """
        stat = file_path.stat()
        
        # 从文件名提取标题
        title = file_path.stem
        
        # 尝试从内容提取第一个标题
        lines = content.split("\n")
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break
        
        return {
            "file_name": file_path.name,
            "file_path": str(file_path.absolute()),
            "title": title,
            "extension": file_path.suffix,
            "created_at": datetime.fromtimestamp(stat.st_birthtime).isoformat() if hasattr(stat, 'st_birthtime') else datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "updated_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "file_size": stat.st_size,
            "word_count": len(content.split()),
        }
    
    def load_single_document(self, file_path: str) -> Optional[Document]:
        """
        加载单个文档（用于增量更新）
        
        Args:
            file_path: 文件路径字符串
            
        Returns:
            Document 或 None
        """
        path = Path(file_path)
        if path.exists() and path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
            return self._load_single_file(path)
        return None


# 全局实例
document_loader = DocumentLoader()
