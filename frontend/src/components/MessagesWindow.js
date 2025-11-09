import React from 'react';
import './MessagesWindow.css';
import MessageBubble from './MessageBubble';

const MessagesWindow = ({ messages, messagesEndRef, isLoading }) => {
  return (
    <div className="messages-window">
      <div className="messages-container">
        {messages.map((message, index) => (
          <MessageBubble
            key={index}
            message={message}
            isLast={index === messages.length - 1}
          />
        ))}
        {isLoading && (
          <div className="typing-indicator">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default MessagesWindow;