
const ChatHeader = ({ onClose, onMinimize }) => {
    return (
        <div className="chat-header">
            <span>Hỗ trợ trực tuyến VNJ</span>
            <div className="header-controls">
                {/* Gọi hàm onMinimize khi bấm nút gập */}
                <button onClick={onMinimize}>▼</button>
                <button onClick={onClose}>✖</button>
            </div>
        </div>
    );
};

export default ChatHeader;