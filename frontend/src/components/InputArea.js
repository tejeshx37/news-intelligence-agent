import React from 'react';
import { Send } from 'lucide-react';
import './InputArea.css';

const InputArea = ({ 
  inputValue, 
  setInputValue, 
  handleSendMessage, 
  handleKeyPress, 
  isLoading 
}) => {
  const isDisabled = !inputValue.trim() || isLoading;

  return (
    <div className="input-area">
      <div className="input-container">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          className="message-input"
          disabled={isLoading}
          maxLength={500}
        />
        <button
          onClick={handleSendMessage}
          disabled={isDisabled}
          className={`send-button ${isDisabled ? 'disabled' : ''}`}
          aria-label="Send message"
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
};

export default InputArea;