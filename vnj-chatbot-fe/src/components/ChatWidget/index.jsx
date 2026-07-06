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

    // Khởi tạo phiên chat khi mở widget lần đầu (chỉ tạo 1 lần cho tới khi đã có sessionId).
    useEffect(() => {
        if (isOpen && !sessionId) {
            chatAPI.startChat()
                .then(data => setSessionId(data.session_id))
                .catch(console.error);
        }
    }, [isOpen, sessionId]);


    const handleSendMessage = async (text) => {
        if (!text.trim() || !sessionId) return;

        // Thêm tin nhắn từ khách vào danh sách hiển thị.
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
                /* 1. GIAO DIỆN LÚC ĐÓNG: Nhân vật Avatar và Bóng thoại thu hút */
                <div className="chat-trigger-container" onClick={() => setIsOpen(true)}>
                    <div className="chat-greeting-bubble">
                        👋 Xin chào! Mình là trợ lý ảo VNJ.<br />
                        Bạn cần hỗ trợ gì không, hãy cho mình biết nhé!
                    </div>
                    <div className="chat-avatar-wrapper">
                        <img
                            src="https://cdn-icons-png.flaticon.com/512/8943/8943377.png"
                            alt="VNJ Chatbot"
                            className="chat-avatar-img"
                        />
                    </div>
                </div>
            ) : (
                /* 2. GIAO DIỆN LÚC MỞ: Giữ nguyên cấu trúc Component cực xịn của bạn */
                <div className={`chat-window ${isMinimized ? 'minimized' : ''}`}>

                    {/* TRUYỀN HÀM ONMINIMIZE CHO CHATHEADER */}
                    <ChatHeader
                        isMinimized={isMinimized}
                        onClose={() => {
                            setIsOpen(false);
                            setIsMinimized(false); // Reset luôn trạng thái thu nhỏ khi tắt
                        }}
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