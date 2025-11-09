# News Intelligence Agent 🤖📰

An AI-powered news analysis and processing system that combines sentiment analysis, fake news detection, and intelligent summarization to provide comprehensive news intelligence.

## 🌟 Features

- **Galaxy Chatbot UI**: Beautiful React-based chatbot interface with galaxy theme
- **Sentiment Analysis**: Advanced sentiment classification for news articles
- **Fake News Detection**: ML-powered detection of potentially fake or misleading news
- **AI Summarization**: Intelligent article summarization using free AI models
- **News Fetching**: Automated news retrieval from multiple sources
- **Trend Analysis**: Enhanced keyword detection for trend analysis queries
- **AWS Integration**: Scalable cloud deployment with Lambda and S3
- **API Integration**: Support for News API, OpenRouter, and other services
- **Batch Processing**: Efficient processing of multiple articles
- **Real-time Analysis**: Live news processing and analysis
- **Comprehensive Logging**: Detailed logging with CloudWatch integration

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   News API      │    │   OpenRouter     │    │   AWS Services  │
│   (Free Tier)   │    │   (Free Models)   │    │   (S3/Lambda)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │   Frontend (React)   │
                    │   Galaxy Chatbot     │
                    └─────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │   Backend (Flask)    │
                    │   API Endpoints      │
                    └─────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ News Pipeline   │    │ Sentiment        │    │ Fake News       │
│ Orchestrator    │    │ Analyzer         │    │ Detector        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │   Summarizer        │
                    │   (AI-powered)       │
                    └─────────────────────┘
```

## 📁 Project Structure

```
news-intelligence-agent/
│
├── frontend/                          # React Galaxy Chatbot UI
│   ├── src/
│   │   ├── App.js                    # Main chatbot application
│   │   ├── components/               # UI components
│   │   └── index.js                  # React entry point
│   ├── public/                       # Static assets
│   ├── package.json                  # Frontend dependencies
│   └── build/                        # Production build
│
├── backend/                           # Flask API backend
│   ├── app.py                        # Main Flask application
│   ├── api/                          # API routes
│   ├── services/                     # Business logic
│   ├── models/                       # ML models
│   ├── utils/                        # Utility functions
│   └── requirements.txt             # Python dependencies
│
├── model_training/                    # Model training scripts
│   ├── train_sentiment.py            # Sentiment analysis training
│   ├── train_fake_news_detector.py   # Fake news detection training
│   └── trained_models/               # Saved models
│
├── lambda_function/                   # AWS Lambda functions
│   ├── lambda_handler.py             # Main Lambda entry point
│   └── requirements.txt              # Lambda dependencies
│
├── cloudformation/                    # AWS CloudFormation templates
├── data/                             # Data storage
├── s3_upload/                         # S3 upload utilities
├── utils/                            # Shared utilities
├── requirements.txt                  # Main dependencies
├── setup.py                          # Package installation
├── Dockerfile                        # Container configuration
├── docker-compose.yml                # Local development setup
├── DEPLOYMENT.md                     # Deployment guide
└── README.md                         # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- Node.js 16+
- AWS Account (optional, for cloud deployment)
- API Keys (free options available)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/tejeshx37/news-intelligence-agent.git
cd news-intelligence-agent

# Backend setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

# Frontend setup
cd frontend
npm install
npm run build
cd ..

# Install the package
pip install -e .
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
nano .env
```

### 4. API Keys Setup

#### Option A: Free APIs (Recommended for testing)
- **News API**: Get free key at [newsapi.org](https://newsapi.org)
- **OpenRouter**: Get free key at [openrouter.ai](https://openrouter.ai)
  - Free models: `google/gemma-2-9b-it:free`, `meta-llama/llama-3.2-3b-instruct:free`

#### Option B: Premium APIs
- **OpenAI API**: For advanced AI features
- **AWS Services**: For cloud deployment

### 5. Train Models (Optional)

```bash
# Train sentiment analysis model
python model_training/train_sentiment.py

# Train fake news detection model
python model_training/train_fake_news_detector.py
```

### 6. Run Locally

```bash
# Run with Docker Compose (recommended)
docker-compose up

# Or run backend directly
cd backend && python app.py

# Or run frontend development server
cd frontend && npm start
```

## 🎯 Usage Examples

### Trend Analysis
Ask the chatbot about:
- "AI trends of last ten years"
- "Recent developments in technology"
- "Show me news about artificial intelligence"
- "Analyze trends in renewable energy"

### Article Processing
- Paste article text for analysis
- Get sentiment analysis and fake news detection
- Receive AI-powered summaries
- View confidence scores and detailed insights

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEWS_API_KEY` | News API key | Required |
| `OPENROUTER_API_KEY` | OpenRouter API key | Optional |
| `AWS_REGION` | AWS region | `us-east-1` |
| `S3_BUCKET` | S3 bucket name | `news-intelligence-models` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `MAX_ARTICLES_PER_REQUEST` | Max articles per API call | `100` |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/process` | POST | Process single article |
| `/api/fetch-and-process` | POST | Fetch and process news |
| `/api/health` | GET | Health check |

## 🧪 Testing

```bash
# Test backend
cd backend && python -m pytest tests/ -v

# Test frontend
cd frontend && npm test

# Test API endpoints
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Article", "content": "Test content", "include_analysis": true}'
```

## 🏭 Production Deployment

### AWS Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Docker Deployment

```bash
# Build and run with Docker
docker build -t news-intelligence .
docker run -p 8000:8000 --env-file .env news-intelligence

# Or use Docker Compose
docker-compose up -d
```

## 📊 Performance Metrics

| Component | Latency | Throughput | Accuracy |
|-----------|---------|------------|----------|
| News Fetching | ~200ms | 100 req/min | N/A |
| Sentiment Analysis | ~50ms | 500 req/sec | 85% |
| Fake News Detection | ~75ms | 300 req/sec | 92% |
| Summarization | ~500ms | 50 req/sec | N/A |
| Total Pipeline | ~1s | 20 req/sec | N/A |

## 🛡️ Security

- **API Key Management**: Environment variables and AWS Secrets Manager
- **Input Validation**: Comprehensive sanitization and validation
- **Rate Limiting**: Built-in rate limiting for API endpoints
- **Data Encryption**: S3 encryption for model storage
- **Logging**: Sanitized logging to prevent data leakage

## 🔍 Model Information

### Sentiment Analysis
- **Algorithm**: Logistic Regression with TF-IDF
- **Accuracy**: ~85% on test data
- **Classes**: Positive, Negative, Neutral
- **Features**: Text preprocessing, stopword removal, n-grams

### Fake News Detection
- **Algorithm**: Random Forest Classifier
- **Accuracy**: ~92% on test data
- **Features**: Text length, punctuation, caps ratio, word count, source credibility
- **Training Data**: Combination of reliable and unreliable news sources

## 🔧 Troubleshooting

### Common Issues

1. **Frontend Build Issues**:
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

2. **Backend Dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r backend/requirements.txt --upgrade
   ```

3. **Port Conflicts**:
   ```bash
   # Check what's using port 3000 or 8000
   lsof -i :3000
   lsof -i :8000
   ```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📈 Roadmap

- [ ] Multi-language support
- [ ] Real-time news streaming
- [ ] Advanced NLP models (BERT, RoBERTa)
- [ ] GraphQL API
- [ ] Mobile app integration
- [ ] Advanced analytics dashboard
- [ ] Machine learning model retraining
- [ ] A/B testing framework

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [News API](https://newsapi.org) for news data
- [OpenRouter](https://openrouter.ai) for free AI models
- [scikit-learn](https://scikit-learn.org) for ML algorithms
- [AWS](https://aws.amazon.com) for cloud infrastructure
- [React](https://reactjs.org) for frontend framework

## 📞 Support

- 📧 Email: tejeshx37@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/tejeshx37/news-intelligence-agent/issues)
- ⭐ Star this repository if you find it helpful!

---

**🚀 Ready to analyze news with AI intelligence!**
