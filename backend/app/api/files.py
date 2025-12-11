"""
文件操作 API
用于在本地系统打开文件
"""
import subprocess
import platform
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/files", tags=["files"])


class OpenFileRequest(BaseModel):
    file_path: str


@router.post("/open")
async def open_file(request: OpenFileRequest):
    """
    使用系统默认应用打开本地文件
    
    - Windows: start
    - macOS: open
    - Linux: xdg-open
    """
    file_path = request.file_path
    
    # 验证文件存在
    if not Path(file_path).exists():
        raise HTTPException(status_code=404, detail=f"文件不存在: {file_path}")
    
    try:
        system = platform.system()
        
        if system == "Darwin":  # macOS
            subprocess.Popen(["open", file_path])
        elif system == "Windows":
            subprocess.Popen(["start", "", file_path], shell=True)
        else:  # Linux
            subprocess.Popen(["xdg-open", file_path])
        
        return {
            "success": True,
            "message": f"已打开文件: {file_path}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"无法打开文件: {str(e)}")
