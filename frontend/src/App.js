import React, { useState, useRef, useEffect } from 'react';
import './App.css';
import GalaxyBackground from './components/GalaxyBackground';
import ChatContainer from './components/ChatContainer';

function App() {
  const [messages, setMessages] = useState([
    {
      text: "Welcome to the Galaxy News Intelligence Chatbot! 🌌 I can help you analyze news articles, detect fake news, and provide sentiment analysis. What would you like to explore?",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      text: inputValue.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    let botMessage;

    try {
      // Check if user is asking for news analysis or just chatting
      const isNewsQuery = userMessage.text.toLowerCase().includes('news') || 
                          userMessage.text.toLowerCase().includes('article') ||
                          userMessage.text.toLowerCase().includes('analyze') ||
                          userMessage.text.toLowerCase().includes('trend') ||
                          userMessage.text.toLowerCase().includes('trends') ||
                          userMessage.text.toLowerCase().includes('recent') ||
                          userMessage.text.toLowerCase().includes('latest') ||
                          userMessage.text.toLowerCase().includes('development') ||
                          userMessage.text.toLowerCase().includes('developments') ||
                          userMessage.text.toLowerCase().includes('progress') ||
                          userMessage.text.toLowerCase().includes('evolution');

      // Check if user pasted article content (long text)
      const isArticleContent = userMessage.text.length > 200;

      if (isArticleContent) {
        // Process pasted article content
        const lines = userMessage.text.split('\n');
        const title = lines[0] || 'User Provided Article';
        const content = lines.slice(1).join('\n').trim() || userMessage.text;
        
        const response = await fetch('http://localhost:8000/api/process', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            title: title,
            content: content,
            source: 'User Input',
            include_analysis: true
          })
        });

        if (response.ok) {
          const article = await response.json();
          const sentiment = article.sentiment_analysis || {};
          const fakeNews = article.fake_news_detection || {};
          
          const analysisText = `📄 **Article Analysis:**

**${article.title}**

${article.summary || article.original_article?.description || article.original_article?.content?.substring(0, 300) + '...'}

🔍 **Analysis Results:**
- Sentiment: ${sentiment.sentiment || 'Neutral'} ${sentiment.confidence ? `(${sentiment.confidence.toFixed(2)})` : ''}
- Credibility: ${fakeNews.confidence ? `${(fakeNews.confidence * 100).toFixed(0)}%` : 'High'} ${fakeNews.prediction === 'fake' ? '⚠️ Potential fake news detected' : '✅ Likely authentic'}
- Source: ${article.source || 'User provided'}

*Analysis completed using AI-powered news intelligence.*`;

          botMessage = {
            text: analysisText,
            sender: 'bot',
            timestamp: new Date()
          };
        } else {
          throw new Error('Failed to process article');
        }
      } else if (isNewsQuery) {
        // Fetch and analyze news
        const response = await fetch('http://localhost:8000/api/fetch-and-process', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            query: userMessage.text,
            page_size: 5,
            include_analysis: true
          })
        });

        if (response.ok) {
          const data = await response.json();
          const processed_articles = data.processed_articles || [];
          
          if (processed_articles.length > 0) {
            const article = processed_articles[0];
            const sentiment = article.sentiment_analysis || {};
            const fakeNews = article.fake_news_detection || {};
            
            // Check if this is a trend analysis query
            const isTrendQuery = userMessage.text.toLowerCase().includes('trend') ||
                                userMessage.text.toLowerCase().includes('trends') ||
                                userMessage.text.toLowerCase().includes('progress') ||
                                userMessage.text.toLowerCase().includes('evolution');
            
            const analysisText = isTrendQuery ? 
              `📈 **Trend Analysis for: ${userMessage.text}**

**${article.title}**

${article.summary || article.original_article?.description || article.original_article?.content?.substring(0, 200) + '...'}

🔍 **Trend Insights:**
- Current Sentiment: ${sentiment.sentiment || 'Neutral'} ${sentiment.confidence ? `(${sentiment.confidence.toFixed(2)})` : ''}
- Credibility Score: ${fakeNews.confidence ? `${(fakeNews.confidence * 100).toFixed(0)}%` : 'High'} ${fakeNews.prediction === 'fake' ? '⚠️ Potential fake news detected' : '✅ Likely authentic'}
- Source: ${article.source || article.original_article?.source?.name || 'Unknown'}
- Published: ${article.original_article?.published_at ? new Date(article.original_article.published_at).toLocaleDateString() : 'Recent'}

*This analysis represents the latest developments in this trend. For comprehensive trend analysis, consider checking multiple sources over time.*`
              :
              `📰 **Latest News:**

**${article.title}**

${article.summary || article.original_article?.description || article.original_article?.content?.substring(0, 200) + '...'}

🔍 **Analysis:**
- Sentiment: ${sentiment.sentiment || 'Neutral'} ${sentiment.confidence ? `(${sentiment.confidence.toFixed(2)})` : ''}
- Credibility: ${fakeNews.confidence ? `${(fakeNews.confidence * 100).toFixed(0)}%` : 'High'} ${fakeNews.prediction === 'fake' ? '⚠️ Potential fake news detected' : '✅ Likely authentic'}
- Source: ${article.source || article.original_article?.source?.name || 'Unknown'}

${article.original_article?.published_at ? `Published: ${new Date(article.original_article.published_at).toLocaleDateString()}` : ''}`;

            botMessage = {
              text: analysisText,
              sender: 'bot',
              timestamp: new Date()
            };
          } else {
            botMessage = {
              text: "I couldn't find any relevant news articles. Try asking about a different topic! 🔄",
              sender: 'bot',
              timestamp: new Date()
            };
          }
        } else {
          throw new Error('Failed to fetch news');
        }
      } else {
        // General chat response
        await new Promise(resolve => setTimeout(resolve, 800));
        
        const generalResponses = [
          "Hello! I'm your Galaxy News Intelligence Chatbot. 🌌 I can help you analyze news trends, detect fake news, and provide sentiment analysis. Try asking me about AI trends, recent developments, or current news topics!",
          "I'm here to help you understand news trends! 📈 Ask me about trends in AI, technology, or any topic, and I'll provide trend analysis, sentiment analysis, and fake news detection.",
          "Welcome to the future of news analysis! 🔍 I can analyze news trends, track developments over time, and provide comprehensive analysis. What trend interests you?",
          "I'm your AI-powered news analyst! ⚡ I can help you identify trends, analyze sentiment, and track the evolution of any topic. Ask me about AI trends or any recent developments!"
        ];

        const randomResponse = generalResponses[Math.floor(Math.random() * generalResponses.length)];
        
        botMessage = {
          text: randomResponse,
          sender: 'bot',
          timestamp: new Date()
        };
      }

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMsg = {
        text: "I'm having trouble connecting to the analysis service. Please try again in a moment. ⚠️",
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="App">
      <GalaxyBackground />
      <ChatContainer
        messages={messages}
        inputValue={inputValue}
        setInputValue={setInputValue}
        handleSendMessage={handleSendMessage}
        handleKeyPress={handleKeyPress}
        isLoading={isLoading}
        messagesEndRef={messagesEndRef}
      />
    </div>
  );
}

export default App;