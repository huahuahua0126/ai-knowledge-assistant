import { useState } from 'react'
import { Search, Calendar, Tag, FileText, ExternalLink } from 'lucide-react'
import { searchApi, filesApi } from '../services/api'
import './SearchPage.css'

function SearchPage() {
    const [query, setQuery] = useState('')
    const [results, setResults] = useState([])
    const [loading, setLoading] = useState(false)
    const [timeRange, setTimeRange] = useState('')
    const [searched, setSearched] = useState(false)

    const handleSearch = async (e) => {
        e.preventDefault()
        if (!query.trim()) return

        setLoading(true)
        setSearched(true)

        try {
            const response = await searchApi.search(query, {
                topK: 10,
                timeRange: timeRange || undefined
            })
            setResults(response.data.results || [])
        } catch (error) {
            console.error('Search failed:', error)
            setResults([])
        } finally {
            setLoading(false)
        }
    }

    const formatDate = (dateStr) => {
        if (!dateStr) return ''
        try {
            return new Date(dateStr).toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            })
        } catch {
            return dateStr
        }
    }

    const formatScore = (score) => {
        return Math.round(score * 100) + '%'
    }

    return (
        <div className="search-page">
            {/* Header */}
            <div className="page-header">
                <h1 className="page-title">🔍 智能搜索</h1>
                <p className="page-subtitle">使用自然语言搜索你的知识库</p>
            </div>

            {/* Search Form */}
            <form onSubmit={handleSearch} className="search-form">
                <div className="search-input-wrapper">
                    <Search className="icon" size={20} />
                    <input
                        type="text"
                        className="input search-input"
                        placeholder="例如：去年关于团队激励的想法..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                    />
                </div>

                <div className="search-filters">
                    <select
                        className="filter-select"
                        value={timeRange}
                        onChange={(e) => setTimeRange(e.target.value)}
                    >
                        <option value="">全部时间</option>
                        <option value="today">今天</option>
                        <option value="week">最近一周</option>
                        <option value="month">最近一月</option>
                        <option value="year">最近一年</option>
                    </select>

                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? <span className="spinner"></span> : <Search size={18} />}
                        搜索
                    </button>
                </div>
            </form>

            {/* Results */}
            <div className="search-results">
                {loading && (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>正在搜索...</p>
                    </div>
                )}

                {!loading && searched && results.length === 0 && (
                    <div className="empty-state">
                        <FileText size={48} className="empty-icon" />
                        <h3>未找到相关结果</h3>
                        <p className="text-secondary">尝试使用不同的关键词或调整时间范围</p>
                    </div>
                )}

                {!loading && results.length > 0 && (
                    <>
                        <div className="results-header">
                            <span className="results-count">找到 {results.length} 个结果</span>
                        </div>

                        <div className="results-list">
                            {results.map((result, index) => (
                                <div key={index} className="result-card card animate-fade-in" style={{ animationDelay: `${index * 0.05}s` }}>
                                    <div className="result-header">
                                        <h3 className="result-title">
                                            <FileText size={18} />
                                            {result.title}
                                        </h3>
                                        <span className="score-badge">
                                            {formatScore(result.score)}
                                        </span>
                                    </div>

                                    <p className="result-content">{result.content}</p>

                                    <div className="result-meta">
                                        <span className="meta-item">
                                            <Calendar size={14} />
                                            {formatDate(result.created_at)}
                                        </span>
                                        {result.metadata?.tags && result.metadata.tags.length > 0 && (
                                            <span className="meta-item">
                                                <Tag size={14} />
                                                {result.metadata.tags.join(', ')}
                                            </span>
                                        )}
                                    </div>

                                    <div className="result-actions">
                                        <button
                                            className="btn btn-secondary btn-sm"
                                            onClick={async () => {
                                                if (result.file_path) {
                                                    try {
                                                        await filesApi.open(result.file_path)
                                                    } catch (error) {
                                                        console.error('Failed to open file:', error)
                                                        alert(`无法打开文件: ${result.file_path}`)
                                                    }
                                                }
                                            }}
                                        >
                                            <ExternalLink size={14} />
                                            打开原文
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </>
                )}

                {!loading && !searched && (
                    <div className="welcome-state">
                        <h3>输入关键词开始搜索</h3>
                        <p className="text-secondary">AI 将帮你找到最相关的笔记内容</p>
                    </div>
                )}
            </div>
        </div>
    )
}

export default SearchPage
