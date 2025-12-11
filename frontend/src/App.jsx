import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import SearchPage from './pages/SearchPage'
import ChatPage from './pages/ChatPage'
import SettingsPage from './pages/SettingsPage'

function App() {
    return (
        <Routes>
            <Route path="/" element={<Layout />}>
                <Route index element={<SearchPage />} />
                <Route path="chat" element={<ChatPage />} />
                <Route path="settings" element={<SettingsPage />} />
            </Route>
        </Routes>
    )
}

export default App
