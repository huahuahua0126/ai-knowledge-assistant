import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Sparkles, Copy, Check, ExternalLink } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { chatApi, filesApi } from '../services/api'
import { useChat } from '../contexts/ChatContext'
import './ChatPage.css'

function ChatPage() {
    const { messages, setMessages } = useChat()
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [copiedIndex, setCopiedIndex] = useState(null)
    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const handleCopy = async (content, index) => {
        try {
            await navigator.clipboard.writeText(content)
            setCopiedIndex(index)
            setTimeout(() => setCopiedIndex(null), 2000)
        } catch (error) {
            console.error('Failed to copy:', error)
        }
    }

    const handleSend = async (e) => {
        e.preventDefault()
        if (!input.trim() || loading) return

        const userMessage = { role: 'user', content: input, sources: [] }
        setMessages(prev => [...prev, userMessage])
        setInput('')
        setLoading(true)

        try {
            const response = await chatApi.chat([...messages, userMessage], 5)
            const data = response.data

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: data.content,
                sources: data.sources || []
            }])
        } catch (error) {
            console.error('Chat failed:', error)
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: '抱歉，发生了错误，请稍后重试。',
                sources: []
            }])
        } finally {
            setLoading(false)
        }
    }

    const handleQuickAction = (prompt) => {
        setInput(prompt)
    }

    // 使用后端 API 打开本地文件
    const openSourceFile = async (source) => {
        if (source.file_path) {
            try {
                await filesApi.open(source.file_path)
            } catch (error) {
                console.error('Failed to open file:', error)
                alert(`无法打开文件: ${source.file_path}`)
            }
        }
    }

    return (
        <div className="chat-page">
            {/* Header */}
            <div className="page-header">
                <h1 className="page-title">💬 AI 对话</h1>
                <p className="page-subtitle">基于你的知识库进行智能对话</p>
            </div>

            <div className="chat-container">
                {/* Chat Messages */}
                <div className="chat-messages">
                    {messages.length === 0 && (
                        <div className="chat-welcome">
                            <Sparkles size={48} className="welcome-icon" />
                            <h3>开始与 AI 助手对话</h3>
                            <p className="text-secondary">AI 会基于你的笔记回答问题，并标注参考来源</p>

                            <div className="quick-actions">
                                <p className="quick-label">快捷操作：</p>
                                <div className="quick-buttons">
                                    {[
                                        '总结一下最近的工作内容',
                                        '帮我复习关于产品设计的笔记',
                                        '基于我的笔记写一段周报'
                                    ].map((action, i) => (
                                        <button
                                            key={i}
                                            className="quick-btn"
                                            onClick={() => handleQuickAction(action)}
                                        >
                                            {action}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {messages.map((msg, index) => (
                        <div key={index} className={`message ${msg.role}`}>
                            <div className="message-avatar">
                                {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                            </div>
                            <div className="message-content">
                                <ReactMarkdown>{msg.content}</ReactMarkdown>

                                {/* AI 回复的参考来源（在同一个对话框内） */}
                                {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
                                    <div className="inline-sources">
                                        <span className="sources-label">参考来源：</span>
                                        {msg.sources.map((source, sIndex) => (
                                            <a
                                                key={sIndex}
                                                className="source-link"
                                                href={source.file_path ? `file://${source.file_path}` : '#'}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                title={`${source.title} (相关度: ${Math.round(source.relevance_score * 100)}%)`}
                                                onClick={(e) => {
                                                    e.preventDefault()
                                                    openSourceFile(source)
                                                }}
                                            >
                                                <span className="source-index">【{source.index}】</span>
                                                <span className="source-name">{source.title}</span>
                                                <ExternalLink size={12} />
                                            </a>
                                        ))}
                                    </div>
                                )}

                                {/* 一键复制按钮 */}
                                {msg.role === 'assistant' && (
                                    <button
                                        className="copy-btn"
                                        onClick={() => handleCopy(msg.content, index)}
                                        title="复制内容"
                                    >
                                        {copiedIndex === index ? (
                                            <><Check size={14} /> 已复制</>
                                        ) : (
                                            <><Copy size={14} /> 复制</>
                                        )}
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}

                    {loading && (
                        <div className="message assistant">
                            <div className="message-avatar">
                                <Bot size={20} />
                            </div>
                            <div className="message-bubble">
                                <div className="message-content">
                                    <div className="typing-indicator">
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <form onSubmit={handleSend} className="chat-input-form">
                    <input
                        type="text"
                        className="input chat-input"
                        placeholder="输入你的问题..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        className="btn btn-primary send-btn"
                        disabled={loading || !input.trim()}
                    >
                        <Send size={18} />
                    </button>
                </form>
            </div>
        </div>
    )
}

export default ChatPage
