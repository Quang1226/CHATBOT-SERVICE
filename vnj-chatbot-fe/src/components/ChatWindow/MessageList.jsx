import { useEffect, useRef } from 'react';

const MessageList = ({ messages }) => {
    const messagesEndRef = useRef(null);

    // Bắt sự kiện: Cứ mỗi khi có tin nhắn mới (mảng messages thay đổi) là cuộn xuống
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    return (
        <div className="chat-body">
            {messages.map((msg) => (
                <div key={msg.id} className={`message ${msg.sender}`}>
                    {msg.text}
                </div>
            ))}

            {/* Đây là điểm mấu chốt: Mỏ neo phải nằm BÊN TRONG thẻ .chat-body */}
            <div ref={messagesEndRef} />
        </div>
    );
};

export default MessageList;