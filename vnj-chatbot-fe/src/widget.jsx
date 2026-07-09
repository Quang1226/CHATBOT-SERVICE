import React from 'react';
import ReactDOM from 'react-dom/client';
import './App.css';
import ChatWidget from './components/ChatWidget/index.jsx';

// 1. Tự động tạo vùng chứa nếu web khách hàng chưa có
let rootElement = document.getElementById('vnj-chatbot-root');
if (!rootElement) {
    rootElement = document.createElement('div');
    rootElement.id = 'vnj-chatbot-root';
    document.body.appendChild(rootElement);
}

// 2. Chỉ bơm mỗi ChatWidget vào đây (Tuyệt đối không kèm Router hay Admin)
ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
        <ChatWidget />
    </React.StrictMode>
);