# Galaxy Chatbot Backend

This is the backend API for the Galaxy Chatbot application, providing AI-powered news analysis with sentiment analysis, fake news detection, and summarization capabilities.

## Features

- **News Processing Pipeline**: Comprehensive news article analysis
- **Sentiment Analysis**: AI-powered sentiment classification
- **Fake News Detection**: Machine learning-based fake news identification
- **Text Summarization**: Automatic article summarization
- **News Fetching**: Integration with news APIs for latest articles
- **RESTful API**: Clean API endpoints for frontend integration
- **CORS Support**: Cross-origin resource sharing enabled
- **Logging**: Comprehensive logging system

## Architecture

```
backend/
├── api/                    # API routes and endpoints
├── config/                 # Configuration files
├── models/                 # Machine learning models and training scripts
├── services/               # Business logic and external service integrations
├── utils/                  # Utility functions and helpers
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the backend directory with:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
NEWS_API_KEY=your_news_api_key_here
```

5. Download required NLTK data:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
```

## Usage

### Start the Development Server

```bash
python app.py
```

The server will start on `http://localhost:8000`

### API Endpoints

#### Process News Article
- **POST** `/process_article`
- **Body**: JSON with `title`, `content`, `source` (optional), `includeAnalysis` (optional)
- **Response**: Processed article with sentiment, fake news detection, and summary

#### Fetch Latest News
- **POST** `/fetch_news`
- **Body**: JSON with `query` and `pageSize` (optional)
- **Response**: Array of processed news articles

#### Health Check
- **GET** `/health`
- **Response**: Service status and API connectivity information

### Example Requests

**Process Article:**
```bash
curl -X POST http://localhost:8000/process_article \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sample News Article",
    "content": "This is the content of the news article...",
    "source": "Example News",
    "includeAnalysis": true
  }'
```

**Fetch News:**
```bash
curl -X POST http://localhost:8000/fetch_news \
  -H "Content-Type: application/json" \
  -d '{
    "query": "technology",
    "pageSize": 10
  }'
```

## Configuration

Configuration files are located in the `config/` directory:

- `config.json`: Main application configuration
- Environment variables: API keys and sensitive settings

## Services

The backend includes several specialized services:

### News Processing Pipeline (`services/news_pipeline.py`)
Orchestrates the complete news analysis workflow including sentiment analysis, fake news detection, and summarization.

### News Fetcher (`services/news_fetcher.py`)
Integrates with external news APIs to fetch latest articles based on search queries.

### Sentiment Analyzer
Uses VADER sentiment analysis and machine learning models to determine article sentiment.

### Fake News Detector
Employs trained machine learning models to identify potentially fake news articles.

### Text Summarizer
Generates concise summaries of news articles using extractive summarization techniques.

## Models

Machine learning models and training scripts are located in the `models/` directory:

- `train_fake_news_detector.py`: Script to train fake news detection models
- `train_sentiment.py`: Script to train sentiment analysis models
- Pre-trained models are stored in the `models/` directory

## Utilities

Common utilities and helpers are in the `utils/` directory:

- `logger.py`: Logging configuration and setup
- `aws_utils.py`: AWS integration utilities
- `config.py`: Configuration management

## Development

### Adding New Endpoints

1. Create the route handler in `app.py`
2. Add any new business logic to appropriate service files
3. Update this README with the new endpoint documentation

### Adding New Services

1. Create new service files in the `services/` directory
2. Import and use the service in `app.py`
3. Add service documentation to this README

## Production Deployment

For production deployment:

1. Use a production WSGI server like Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

2. Set up proper environment variables
3. Configure logging for production
4. Set up monitoring and health checks
5. Use a reverse proxy like Nginx

## Docker Support

The backend can be containerized using the provided Dockerfile in the parent directory.

## Contributing

1. Follow PEP 8 style guidelines
2. Add appropriate logging
3. Update documentation for new features
4. Test your changes thoroughly
5. Submit pull requests for review

## License

This project is part of the Galaxy Chatbot application.