# 🤖 AI知识库助手

> 基于 LlamaIndex + 通义千问 的智能知识库系统，支持语义搜索与 AI 对话

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)
![LlamaIndex](https://img.shields.io/badge/LlamaIndex-0.10+-purple)

---

## ✨ 功能特性

| 功能 | 描述 |
|------|------|
| **🔍 语义搜索** | 使用向量化技术，通过自然语言搜索笔记内容 |
| **💬 AI 对话** | 基于 RAG 技术，AI 根据知识库内容回答问题 |
| **📚 来源引用** | 每次回答自动标注参考来源，支持一键打开原文 |
| **📋 一键复制** | 快速复制 AI 回复内容 |
| **🕐 历史保持** | 切换页面不丢失对话记录 |
| **⚡ 增量索引** | 支持增量同步，无需每次全量重建 |

---

## 🛠️ 技术栈

### 后端

| 技术 | 用途 |
|------|------|
| **FastAPI** | 高性能 API 框架 |
| **LlamaIndex** | RAG 框架，向量索引与检索 |
| **通义千问 (DashScope)** | LLM 与 Embedding 模型 |
| **Pydantic** | 数据校验与序列化 |

### 前端

| 技术 | 用途 |
|------|------|
| **React 18** | 现代化 UI 框架 |
| **React Router** | 单页面路由 |
| **Axios** | HTTP 请求 |
| **React Markdown** | Markdown 渲染 |
| **Lucide React** | 图标库 |
| **Vite** | 开发构建工具 |

---

## 🚀 快速开始

### 1. 克隆项目

```bash
cd ~/.gemini/antigravity/scratch/second-brain
```

### 2. 配置后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入通义千问 API Key
```

### 3. 启动后端

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. 启动前端

```bash
cd ../frontend
npm install
npm run dev
```

### 5. 访问应用

打开浏览器访问：**http://localhost:3000**

---

## 📁 项目结构

```
second-brain/
├── backend/                    # Python 后端
│   ├── app/
│   │   ├── api/                # API 路由
│   │   │   ├── chat.py         # AI 对话接口
│   │   │   ├── documents.py    # 文档管理接口
│   │   │   ├── files.py        # 文件操作接口
│   │   │   └── search.py       # 搜索接口
│   │   ├── services/           # 业务逻辑
│   │   │   ├── generation_service.py  # RAG 生成
│   │   │   ├── index_service.py       # 向量索引
│   │   │   └── search_service.py      # 语义搜索
│   │   ├── config.py           # 配置管理
│   │   └── main.py             # 应用入口
│   └── requirements.txt
│
├── frontend/                   # React 前端
│   ├── src/
│   │   ├── components/         # 共用组件
│   │   ├── contexts/           # React Context
│   │   ├── pages/              # 页面组件
│   │   ├── services/           # API 服务
│   │   └── styles/             # 全局样式
│   └── package.json
│
└── data/
    ├── chroma_db/              # 向量数据库
    └── notes/                  # 笔记目录
```

---

## 🔌 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/documents` | GET | 获取文档列表 |
| `/api/documents/sync` | POST | 同步/重建索引 |
| `/api/search` | POST | 语义搜索 |
| `/api/chat` | POST | AI 对话 |
| `/api/files/open` | POST | 打开本地文件 |

---

## ⚙️ 环境变量

在 `backend/.env` 中配置：

```env
# 通义千问 API Key (必填)
DASHSCOPE_API_KEY=sk-xxxxxxxx

# 笔记目录 (可配置多个，用逗号分隔)
NOTES_DIRECTORIES=../data/notes

# LLM 配置
LLM_MODEL=qwen3-max
EMBEDDING_MODEL=text-embedding-v2
```

---

## 📝 使用说明

1. **添加笔记**：将 Markdown、TXT、Word 等文件放入 `data/notes` 目录
2. **构建索引**：在设置页面点击「重建索引」
3. **开始使用**：
   - 使用「搜索」页面查找笔记
   - 使用「对话」页面与 AI 交流

---

## 📄 License

MIT License
