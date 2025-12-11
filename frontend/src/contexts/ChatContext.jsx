import { createContext, useContext, useState } from 'react'

const ChatContext = createContext()

export function ChatProvider({ children }) {
    const [messages, setMessages] = useState([])

    const addMessage = (message) => {
        setMessages(prev => [...prev, message])
    }

    const clearMessages = () => {
        setMessages([])
    }

    return (
        <ChatContext.Provider value={{ messages, setMessages, addMessage, clearMessages }}>
            {children}
        </ChatContext.Provider>
    )
}

export function useChat() {
    const context = useContext(ChatContext)
    if (!context) {
        throw new Error('useChat must be used within a ChatProvider')
    }
    return context
}
