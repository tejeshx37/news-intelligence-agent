import React from 'react';
import './ChatContainer.css';
import MessagesWindow from './MessagesWindow';
import InputArea from './InputArea';

const ChatContainer = ({ 
  messages, 
  inputValue, 
  setInputValue, 
  handleSendMessage, 
  handleKeyPress, 
  isLoading,
  messagesEndRef 
}) => {
  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Galaxy News Intelligence</h2>
        <div className="status-indicator">
          <span className={`status-dot ${isLoading ? 'loading' : 'online'}`}></span>
          <span className="status-text">{isLoading ? 'Analyzing...' : 'Online'}</span>
        </div>
      </div>
      
      <MessagesWindow 
        messages={messages} 
        messagesEndRef={messagesEndRef}
        isLoading={isLoading}
      />
      
      <InputArea
        inputValue={inputValue}
        setInputValue={setInputValue}
        handleSendMessage={handleSendMessage}
        handleKeyPress={handleKeyPress}
        isLoading={isLoading}
      />
    </div>
  );
};

export default ChatContainer;