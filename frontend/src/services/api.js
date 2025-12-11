/**
 * API Service - 与后端通信
 */
import axios from 'axios';

const api = axios.create({
    baseURL: '/api',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
});

// 文档相关 API
export const documentsApi = {
    // 获取文档列表
    list: () => api.get('/documents'),

    // 同步文档
    sync: (forceRebuild = false) => api.post('/documents/sync', { force_rebuild: forceRebuild }),

    // 获取统计信息
    stats: () => api.get('/documents/stats'),

    // 删除文档
    delete: (filePath) => api.delete(`/documents/${encodeURIComponent(filePath)}`)
};

// 搜索相关 API
export const searchApi = {
    // 语义搜索
    search: (query, options = {}) => api.post('/search', {
        query,
        top_k: options.topK || 10,
        start_date: options.startDate,
        end_date: options.endDate,
        time_range: options.timeRange,
        tags: options.tags
    }),

    // 获取最近文档
    recent: (limit = 20) => api.get('/search/recent', { params: { limit } }),

    // 相似文档
    similar: (filePath, topK = 5) => api.get(`/search/similar/${encodeURIComponent(filePath)}`, { params: { top_k: topK } })
};

// 对话/生成相关 API
export const chatApi = {
    // 对话
    chat: (messages, topK = 5) => api.post('/chat', {
        messages: messages.map(m => ({ role: m.role, content: m.content })),
        top_k: topK
    }),

    // 生成内容
    generate: (prompt, options = {}) => api.post('/chat/generate', {
        prompt,
        top_k: options.topK || 5,
        style: options.style || 'professional'
    }),

    // 生成摘要
    summary: (topic, topK = 10) => api.post('/chat/summary', null, { params: { topic, top_k: topK } })
};

// 健康检查
export const healthApi = {
    check: () => api.get('/health')
};

// 文件操作
export const filesApi = {
    // 使用系统默认应用打开文件
    open: (filePath) => api.post('/files/open', { file_path: filePath })
};

export default api;
