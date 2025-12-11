import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ChatProvider } from './contexts/ChatContext'
import App from './App'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <BrowserRouter>
            <ChatProvider>
                <App />
            </ChatProvider>
        </BrowserRouter>
    </React.StrictMode>,
)

