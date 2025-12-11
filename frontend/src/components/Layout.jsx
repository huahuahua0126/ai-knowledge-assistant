import { NavLink, Outlet } from 'react-router-dom'
import { Search, MessageSquare, Settings } from 'lucide-react'
import './Layout.css'

function Layout() {
    return (
        <div className="layout">
            {/* Top Navigation */}
            <header className="top-nav">
                <div className="nav-container">
                    <div className="logo">
                        <span className="logo-text">AI知识库助手</span>
                    </div>

                    <nav className="nav-links">
                        <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} end>
                            <Search size={18} />
                            <span>搜索</span>
                        </NavLink>
                        <NavLink to="/chat" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                            <MessageSquare size={18} />
                            <span>对话</span>
                        </NavLink>
                        <NavLink to="/settings" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                            <Settings size={18} />
                            <span>设置</span>
                        </NavLink>
                    </nav>
                </div>
            </header>

            {/* Main Content */}
            <main className="main-content">
                <Outlet />
            </main>
        </div>
    )
}

export default Layout
