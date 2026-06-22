import { useEffect, useState } from 'react';
import { chatAPI } from '../../services/api';
import ChatHeader from '../ChatWindow/ChatHeader';
import ChatInput from '../ChatWindow/ChatInput';
import MessageList from '../ChatWindow/MessageList';
import './ChatWidget.css';

const ChatWidget = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const [messages, setMessages] = useState([
        { id: 1, sender: 'bot', text: 'Xin chào! Trợ lý ảo VNJ rất sẵn lòng hỗ trợ bạn!' }
    ]);

    // Khởi tạo phiên chat
    useEffect(() => {
        if (isOpen && !sessionId) {
            chatAPI.startChat().then(data => setSessionId(data.session_id)).catch(console.error);
        }
    }, [isOpen, sessionId]);

    const handleSendMessage = async (text) => {
        if (!text.trim() || !sessionId) return;

        // Thêm tin user
        setMessages(prev => [...prev, { id: Date.now(), sender: 'user', text }]);

        try {
            const botResponse = await chatAPI.sendMessage(sessionId, text);
            // Thêm tin bot (Backend trả về message_text hoặc text)
            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                sender: 'bot',
                text: botResponse.message_text || botResponse.text
            }]);
        } catch (error) {
            setMessages(prev => [...prev, { id: Date.now() + 1, sender: 'bot', text: 'Hệ thống đang bận, vui lòng thử lại sau.' }]);
        }
    };

    return (
        <div className="chat-widget-container">
            {!isOpen ? (
                <div className="chat-bubble-btn" onClick={() => setIsOpen(true)}>💬</div>
            ) : (
                /* 2. THÊM LOGIC ĐỔI CLASS MINIMIZED VÀO ĐÂY */
                <div className={`chat-window ${isMinimized ? 'minimized' : ''}`}>

                    {/* 3. TRUYỀN HÀM ONMINIMIZE CHO CHATHEADER */}
                    <ChatHeader
                        onClose={() => setIsOpen(false)}
                        onMinimize={() => setIsMinimized(!isMinimized)}
                    />

                    {/* Ẩn nội dung chat nếu đang thu nhỏ để code gọn gàng */}
                    {!isMinimized && (
                        <>
                            <MessageList messages={messages} />
                            <ChatInput onSendMessage={handleSendMessage} />
                        </>
                    )}
                </div>
            )}
        </div>
    );
};

export default ChatWidget;