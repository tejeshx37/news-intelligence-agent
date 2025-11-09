import React from 'react';
import './MessageBubble.css';

const MessageBubble = ({ message, isLast }) => {
  const isUser = message.sender === 'user';
  
  return (
    <div className={`message-wrapper ${isUser ? 'user-wrapper' : 'bot-wrapper'}`}>
      <div className={`message-bubble ${isUser ? 'user-bubble' : 'bot-bubble'} ${isLast ? 'last-message' : ''}`}>
        <p className="message-text">{message.text}</p>
        <span className="message-time">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  );
};

export default MessageBubble;