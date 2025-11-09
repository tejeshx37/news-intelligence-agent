# Galaxy Chatbot - Full Stack Deployment Guide

## Overview
This guide explains how to deploy the Galaxy Chatbot with both frontend and backend services.

## Architecture
- **Frontend**: React application (port 3000)
- **Backend**: Flask API (port 8000)
- **Integration**: Frontend connects to backend via REST API

## Quick Start

### 1. Start Both Services
```bash
# Start backend (from backend directory)
cd backend
python app.py

# Start frontend (from frontend directory, in new terminal)
cd frontend
npm start
```

### 2. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/

## Features

### Frontend Capabilities
- **News Analysis**: Ask about current news topics
- **Article Processing**: Paste article content for analysis
- **Real-time Chat**: Interactive chatbot interface
- **Galaxy Theme**: Beautiful space-themed UI

### Backend Capabilities
- **News Fetching**: Fetch latest news from News API
- **Sentiment Analysis**: Analyze article sentiment
- **Fake News Detection**: Detect potential fake news
- **Content Summarization**: Generate article summaries
- **AI Analysis**: Advanced content analysis using OpenRouter

## API Endpoints

### Process Article
```
POST /api/process
{
  "title": "Article Title",
  "content": "Article content...",
  "source": "News Source",
  "include_analysis": true
}
```

### Fetch and Process News
```
POST /api/fetch-and-process
{
  "query": "technology",
  "page_size": 10,
  "include_analysis": true
}
```

## Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```
OPENROUTER_API_KEY=your_openrouter_api_key
NEWS_API_KEY=your_news_api_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
```

### Frontend Configuration
The frontend automatically connects to `http://localhost:8000`. To change this, update the API URLs in `frontend/src/App.js`.

## Deployment Options

### Option 1: Development Mode
```bash
# Terminal 1 - Backend
cd backend && python app.py

# Terminal 2 - Frontend
cd frontend && npm start
```

### Option 2: Production Mode
```bash
# Build frontend
cd frontend && npm run build

# Serve with production server
cd backend && gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Option 3: Docker Deployment
```bash
# Using existing docker-compose
docker-compose up -d
```

## Testing the Integration

### Test News Query
1. Open http://localhost:3000
2. Type: "What's the latest technology news?"
3. The bot should fetch and analyze recent tech news

### Test Article Processing
1. Copy and paste a news article
2. The bot will analyze sentiment, credibility, and provide summary

### Test API Directly
```bash
# Test article processing
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "content": "Sample content", "include_analysis": true}'

# Test news fetching
curl -X POST http://localhost:8000/api/fetch-and-process \
  -H "Content-Type: application/json" \
  -d '{"query": "politics", "page_size": 5}'
```

## Troubleshooting

### Common Issues
1. **CORS Errors**: Backend has CORS enabled for localhost:3000
2. **API Key Missing**: Set up environment variables
3. **Port Conflicts**: Ensure ports 3000 and 8000 are available
4. **Model Download Errors**: Backend uses fallback methods if models unavailable

### Backend Logs
Check backend logs for detailed error information:
```bash
tail -f backend/logs/app.log
```

### Frontend Console
Open browser developer tools to see frontend errors.

## Production Considerations

### Security
- Use environment variables for sensitive data
- Implement proper authentication
- Use HTTPS in production
- Validate all inputs

### Performance
- Implement caching for news articles
- Use CDN for static assets
- Optimize database queries
- Monitor API rate limits

### Scaling
- Use load balancers for multiple instances
- Implement Redis caching
- Use managed database services
- Monitor resource usage

## Support
For issues and questions:
- Check the logs in both services
- Verify environment variables are set
- Ensure all dependencies are installed
- Test API endpoints directly