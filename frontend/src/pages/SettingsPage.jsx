import { useState, useEffect } from 'react'
import { FolderOpen, RefreshCw, Database, CheckCircle, AlertCircle } from 'lucide-react'
import { documentsApi, healthApi } from '../services/api'
import './SettingsPage.css'

function SettingsPage() {
    const [health, setHealth] = useState(null)
    const [stats, setStats] = useState(null)
    const [syncing, setSyncing] = useState(false)
    const [syncResult, setSyncResult] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadData()
    }, [])

    const loadData = async () => {
        setLoading(true)
        try {
            const [healthRes, statsRes] = await Promise.all([
                healthApi.check().catch(() => ({ data: null })),
                documentsApi.stats().catch(() => ({ data: null }))
            ])
            setHealth(healthRes.data)
            setStats(statsRes.data)
        } catch (error) {
            console.error('Failed to load settings data:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSync = async (forceRebuild = false) => {
        setSyncing(true)
        setSyncResult(null)

        try {
            const response = await documentsApi.sync(forceRebuild)
            setSyncResult({
                success: true,
                message: `成功索引 ${response.data.documents_indexed} 个文档，耗时 ${response.data.time_taken_seconds} 秒`
            })
            // 刷新统计
            const statsRes = await documentsApi.stats()
            setStats(statsRes.data)
        } catch (error) {
            setSyncResult({
                success: false,
                message: error.response?.data?.detail || '同步失败，请检查后端服务'
            })
        } finally {
            setSyncing(false)
        }
    }

    return (
        <div className="settings-page">
            {/* Header */}
            <div className="page-header">
                <h1 className="page-title">⚙️ 设置</h1>
                <p className="page-subtitle">管理知识库配置和同步</p>
            </div>

            {loading ? (
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>加载中...</p>
                </div>
            ) : (
                <div className="settings-content">
                    {/* Status Card */}
                    <div className="settings-card card">
                        <h3 className="card-title">
                            <Database size={20} />
                            系统状态
                        </h3>

                        <div className="status-grid">
                            <div className="status-item">
                                <span className="status-label">后端服务</span>
                                <span className={`status-value ${health ? 'success' : 'error'}`}>
                                    {health ? (
                                        <><CheckCircle size={16} /> 运行中</>
                                    ) : (
                                        <><AlertCircle size={16} /> 未连接</>
                                    )}
                                </span>
                            </div>

                            <div className="status-item">
                                <span className="status-label">API Key</span>
                                <span className={`status-value ${health?.api_key_configured ? 'success' : 'warning'}`}>
                                    {health?.api_key_configured ? '已配置' : '未配置'}
                                </span>
                            </div>

                            <div className="status-item">
                                <span className="status-label">已索引文档</span>
                                <span className="status-value">
                                    {stats?.total_documents || 0} 个
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Directories Card */}
                    <div className="settings-card card">
                        <h3 className="card-title">
                            <FolderOpen size={20} />
                            笔记目录
                        </h3>

                        {health?.notes_directories && health.notes_directories.length > 0 ? (
                            <ul className="directories-list">
                                {health.notes_directories.map((dir, index) => (
                                    <li key={index} className="directory-item">
                                        <FolderOpen size={16} />
                                        <span>{dir}</span>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p className="text-secondary">未配置笔记目录，请在 backend/.env 中设置 NOTES_DIRECTORIES</p>
                        )}
                    </div>

                    {/* Sync Card */}
                    <div className="settings-card card">
                        <h3 className="card-title">
                            <RefreshCw size={20} />
                            索引同步
                        </h3>

                        <p className="text-secondary mb-md">
                            同步将扫描笔记目录，更新向量索引。首次使用或笔记有大量变更时，建议使用"重建索引"。
                        </p>

                        <div className="sync-actions">
                            <button
                                className="btn btn-primary"
                                onClick={() => handleSync(false)}
                                disabled={syncing}
                            >
                                {syncing ? <span className="spinner"></span> : <RefreshCw size={18} />}
                                增量同步
                            </button>

                            <button
                                className="btn btn-secondary"
                                onClick={() => handleSync(true)}
                                disabled={syncing}
                            >
                                <Database size={18} />
                                重建索引
                            </button>
                        </div>

                        {syncResult && (
                            <div className={`sync-result ${syncResult.success ? 'success' : 'error'}`}>
                                {syncResult.success ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
                                {syncResult.message}
                            </div>
                        )}
                    </div>

                    {/* Help Card */}
                    <div className="settings-card card">
                        <h3 className="card-title">📖 快速指南</h3>

                        <div className="help-content">
                            <div className="help-step">
                                <span className="step-number">1</span>
                                <div>
                                    <strong>配置 API Key</strong>
                                    <p className="text-secondary">在 backend/.env 中填入通义千问 API Key</p>
                                </div>
                            </div>

                            <div className="help-step">
                                <span className="step-number">2</span>
                                <div>
                                    <strong>设置笔记目录</strong>
                                    <p className="text-secondary">配置 NOTES_DIRECTORIES 指向你的笔记文件夹</p>
                                </div>
                            </div>

                            <div className="help-step">
                                <span className="step-number">3</span>
                                <div>
                                    <strong>构建索引</strong>
                                    <p className="text-secondary">点击上方"重建索引"按钮初始化知识库</p>
                                </div>
                            </div>

                            <div className="help-step">
                                <span className="step-number">4</span>
                                <div>
                                    <strong>开始使用</strong>
                                    <p className="text-secondary">前往"搜索"或"对话"页面体验智能检索</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default SettingsPage
