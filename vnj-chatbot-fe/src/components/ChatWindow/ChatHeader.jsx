const ChatHeader = ({ onClose, onMinimize, isMinimized }) => {
    return (
        <div className="chat-header">
            <h4>Hỗ trợ trực tuyến VNJ</h4>
            <div className="header-actions">
                <button onClick={onMinimize} className="action-btn">
                    {/* Thẻ span này sẽ nhận class 'rotated' nếu isMinimized = true */}
                    <span className={`icon-arrow ${isMinimized ? 'rotated' : ''}`}>▼</span>
                </button>
                <button onClick={onClose} className="action-btn">✖</button>
            </div>
        </div>
    );
};

export default ChatHeader;