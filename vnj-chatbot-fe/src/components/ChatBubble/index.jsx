
const ChatBubble = ({ onOpen }) => {
    return (
        <button className="chat-bubble-btn" onClick={onOpen}>
            💬
        </button>
    );
};

export default ChatBubble;