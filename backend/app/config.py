"""
配置管理模块
从环境变量加载配置
"""
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Settings(BaseSettings):
    """应用配置"""
    
    # API Key
    dashscope_api_key: str = os.getenv("DASHSCOPE_API_KEY", "")
    
    # 笔记目录
    notes_directories: str = os.getenv("NOTES_DIRECTORIES", "../data/notes")
    
    # 向量数据库路径
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "../data/chroma_db")
    
    # LLM 配置
    llm_model: str = os.getenv("LLM_MODEL", "qwen3-max")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-v2")
    
    # 服务配置
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    @property
    def notes_paths(self) -> List[Path]:
        """获取笔记目录路径列表"""
        paths = []
        for dir_path in self.notes_directories.split(","):
            path = Path(dir_path.strip())
            if path.exists():
                paths.append(path)
        return paths
    
    @property
    def chroma_path(self) -> Path:
        """获取向量数据库路径"""
        return Path(self.chroma_db_path)
    
    class Config:
        env_file = ".env"


# 全局配置实例
settings = Settings()
