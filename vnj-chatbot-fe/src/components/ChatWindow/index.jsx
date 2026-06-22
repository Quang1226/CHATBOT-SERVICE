import ChatHeader from './ChatHeader';
import ChatInput from './ChatInput';
import MessageList from './MessageList';

const ChatWindow = ({
    isMinimized,
    messages,
    inputText,
    setInputText,
    onClose,
    onMinimize,
    onSendMessage
}) => {
    return (
        <div className={`chat-window ${isMinimized ? 'minimized' : ''}`}>
            <ChatHeader
                isMinimized={isMinimized}
                onMinimize={onMinimize}
                onClose={onClose}
            />

            {!isMinimized && (
                <>
                    <MessageList messages={messages} />
                    <ChatInput
                        inputText={inputText}
                        setInputText={setInputText}
                        onSendMessage={onSendMessage}
                    />
                </>
            )}
        </div>
    );
};

export default ChatWindow;