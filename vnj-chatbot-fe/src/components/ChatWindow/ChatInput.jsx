import { useState } from 'react';

const ChatInput = ({ onSendMessage }) => {
    const [inputText, setInputText] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault(); // Chặn hành vi tải lại trang mặc định của Form

        if (inputText.trim()) {
            onSendMessage(inputText); // Gửi nội dung tin nhắn lên Component cha
            setInputText(''); // Gửi xong thì xóa trắng ô nhập để khách gõ câu mới
        }
    };

    return (
        <form className="chat-footer" onSubmit={handleSubmit}>
            <input
                type="text"
                placeholder="Nhập tin nhắn..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
            />
            <button type="submit">➤</button>
        </form>
    );
};

export default ChatInput;