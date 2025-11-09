#!/usr/bin/env python3
"""
News Intelligence Agent - Web Backend Server
A Flask-based web server to run the news intelligence system locally
"""

import json
import logging
import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.news_pipeline import NewsProcessingPipeline
from services.news_fetcher import NewsFetcher
from utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize pipeline components
pipeline = NewsProcessingPipeline()
news_fetcher = NewsFetcher()

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Intelligence Agent</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        input, textarea, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        textarea {
            height: 120px;
            resize: vertical;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
        }
        button:hover {
            background-color: #0056b3;
        }
        .result {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 20px;
            margin-top: 20px;
        }
        .sentiment-positive { color: #28a745; font-weight: bold; }
        .sentiment-negative { color: #dc3545; font-weight: bold; }
        .sentiment-neutral { color: #6c757d; font-weight: bold; }
        .fake-news-warning { color: #dc3545; font-weight: bold; }
        .fake-news-safe { color: #28a745; font-weight: bold; }
        .summary {
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .api-status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 12px;
            margin: 5px;
        }
        .api-status.ok { background-color: #d4edda; color: #155724; }
        .api-status.error { background-color: #f8d7da; color: #721c24; }
        .loading {
            display: none;
            text-align: center;
            color: #007bff;
            margin: 20px 0;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 News Intelligence Agent</h1>
        <p>AI-powered news analysis with sentiment, fake news detection, and summarization</p>
    </div>

    <div class="container">
        <h2>🔍 Process News Article</h2>
        <form id="processForm">
            <div class="form-group">
                <label for="title">Article Title:</label>
                <input type="text" id="title" name="title" placeholder="Enter article title..." required>
            </div>
            <div class="form-group">
                <label for="content">Article Content:</label>
                <textarea id="content" name="content" placeholder="Paste article content here..." required></textarea>
            </div>
            <div class="form-group">
                <label for="source">Source (optional):</label>
                <input type="text" id="source" name="source" placeholder="e.g., BBC, CNN, TechCrunch">
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" id="includeAnalysis" checked> Include AI Analysis
                </label>
            </div>
            <button type="submit">🚀 Process Article</button>
            <button type="button" onclick="loadSample()">📄 Load Sample</button>
        </form>
        <div id="loading" class="loading">Processing... Please wait...</div>
        <div id="result"></div>
    </div>

    <div class="container">
        <h2>📰 Fetch & Process Latest News</h2>
        <form id="fetchForm">
            <div class="form-group">
                <label for="query">Search Query:</label>
                <input type="text" id="query" name="query" value="technology" placeholder="e.g., technology, politics, sports">
            </div>
            <div class="form-group">
                <label for="pageSize">Number of Articles:</label>
                <select id="pageSize" name="pageSize">
                    <option value="5">5 articles</option>
                    <option value="10" selected>10 articles</option>
                    <option value="20">20 articles</option>
                </select>
            </div>
            <button type="submit">📡 Fetch & Process News</button>
        </form>
        <div id="fetchLoading" class="loading">Fetching and processing news... Please wait...</div>
        <div id="fetchResult"></div>
    </div>

    <div class="container">
        <h2>📊 API Status</h2>
        <div id="apiStatus"></div>
    </div>

    <script>
        // Check API status on page load
        window.onload = function() {
            checkApiStatus();
        };

        // Process single article
        document.getElementById('processForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = {
                operation: 'process_single',
                title: formData.get('title'),
                content: formData.get('content'),
                source: formData.get('source'),
                include_analysis: document.getElementById('includeAnalysis').checked
            };

            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').innerHTML = '';

            try {
                const response = await fetch('/api/process', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                displayResult(result);
            } catch (error) {
                document.getElementById('result').innerHTML = 
                    `<div class="error">Error: ${error.message}</div>`;
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        });

        // Fetch and process news
        document.getElementById('fetchForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = {
                operation: 'fetch_and_process',
                query: formData.get('query'),
                page_size: parseInt(formData.get('pageSize')),
                include_analysis: true
            };

            document.getElementById('fetchLoading').style.display = 'block';
            document.getElementById('fetchResult').innerHTML = '';

            try {
                const response = await fetch('/api/fetch-and-process', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                displayFetchResult(result);
            } catch (error) {
                document.getElementById('fetchResult').innerHTML = 
                    `<div class="error">Error: ${error.message}</div>`;
            } finally {
                document.getElementById('fetchLoading').style.display = 'none';
            }
        });

        // Display processing result
        function displayResult(result) {
            if (result.success) {
                const sentiment = result.sentiment_analysis;
                const fakeNews = result.fake_news_detection;
                const summary = result.summary;
                
                let html = '<div class="success">Article processed successfully!</div>';
                
                // Sentiment Analysis
                if (sentiment) {
                    const sentimentClass = sentiment.sentiment === 'positive' ? 'sentiment-positive' : 
                                         sentiment.sentiment === 'negative' ? 'sentiment-negative' : 'sentiment-neutral';
                    html += `
                        <div class="result">
                            <h3>📊 Sentiment Analysis</h3>
                            <p>Sentiment: <span class="${sentimentClass}">${sentiment.sentiment.toUpperCase()}</span></p>
                            <p>Confidence: ${(sentiment.confidence * 100).toFixed(1)}%</p>
                        </div>
                    `;
                }
                
                // Fake News Detection
                if (fakeNews) {
                    const fakeNewsClass = fakeNews.prediction === 'fake' ? 'fake-news-warning' : 'fake-news-safe';
                    const fakeNewsText = fakeNews.prediction === 'fake' ? '⚠️ POTENTIALLY FAKE' : '✅ LIKELY REAL';
                    html += `
                        <div class="result">
                            <h3>🔍 Fake News Detection</h3>
                            <p>Prediction: <span class="${fakeNewsClass}">${fakeNewsText}</span></p>
                            <p>Confidence: ${(fakeNews.confidence * 100).toFixed(1)}%</p>
                        </div>
                    `;
                }
                
                // Summary
                if (summary && summary.success) {
                    html += `
                        <div class="result">
                            <h3>📝 Summary</h3>
                            <div class="summary">${summary.summary}</div>
                            <p><small>Original: ${summary.original_length} words → Summary: ${summary.summary_length} words</small></p>
                        </div>
                    `;
                }
                
                // AI Analysis
                if (result.ai_analysis && result.ai_analysis.success) {
                    html += `
                        <div class="result">
                            <h3>🤖 AI Analysis</h3>
                            <pre>${JSON.stringify(result.ai_analysis.analysis, null, 2)}</pre>
                        </div>
                    `;
                }
                
                document.getElementById('result').innerHTML = html;
            } else {
                document.getElementById('result').innerHTML = 
                    `<div class="error">Processing failed: ${result.error}</div>`;
            }
        }

        // Display fetch result
        function displayFetchResult(result) {
            if (result.success) {
                let html = `<div class="success">Fetched and processed ${result.total_articles} articles!</div>`;
                
                result.processed_articles.forEach((article, index) => {
                    if (article.success) {
                        const sentiment = article.sentiment_analysis;
                        const fakeNews = article.fake_news_detection;
                        
                        html += `
                            <div class="result">
                                <h3>${index + 1}. ${article.title}</h3>
                                <p><strong>Source:</strong> ${article.source}</p>
                                <p><strong>Sentiment:</strong> 
                                    <span class="sentiment-${sentiment.sentiment}">${sentiment.sentiment.toUpperCase()}</span>
                                    (${(sentiment.confidence * 100).toFixed(1)}%)
                                </p>
                                <p><strong>Fake News Check:</strong> 
                                    <span class="fake-news-${fakeNews.prediction === 'fake' ? 'warning' : 'safe'}">
                                        ${fakeNews.prediction === 'fake' ? '⚠️ POTENTIALLY FAKE' : '✅ LIKELY REAL'}
                                    </span>
                                    (${(fakeNews.confidence * 100).toFixed(1)}%)
                                </p>
                                <div class="summary">${article.summary.summary}</div>
                            </div>
                        `;
                    }
                });
                
                document.getElementById('fetchResult').innerHTML = html;
            } else {
                document.getElementById('fetchResult').innerHTML = 
                    `<div class="error">Fetch failed: ${result.error}</div>`;
            }
        }

        // Load sample data
        function loadSample() {
            document.getElementById('title').value = 'Scientists Discover Breakthrough in Quantum Computing';
            document.getElementById('content').value = 'Scientists at MIT have announced a major breakthrough in quantum computing that could revolutionize the field. The new technique allows for more stable quantum states, potentially solving one of the biggest challenges in quantum computing. The research, published in the journal Nature, demonstrates a 99.9% success rate in maintaining quantum coherence for extended periods. This advancement could lead to more powerful quantum computers that are actually practical for real-world applications. The team used a novel approach combining error correction with advanced materials science to achieve these remarkable results.';
            document.getElementById('source').value = 'MIT News';
        }

        // Check API status
        async function checkApiStatus() {
            try {
                const response = await fetch('/api/health');
                const result = await response.json();
                
                let html = '';
                if (result.status === 'healthy') {
                    html = '<span class="api-status ok">✅ System Healthy</span>';
                } else {
                    html = '<span class="api-status error">❌ System Issue</span>';
                }
                
                // Check API keys
                html += '<br><br><strong>API Configuration:</strong><br>';
                html += result.news_api_configured ? 
                    '<span class="api-status ok">✅ News API Configured</span>' : 
                    '<span class="api-status error">❌ News API Not Configured</span>';
                
                html += result.openrouter_configured ? 
                    '<span class="api-status ok">✅ OpenRouter API Configured</span>' : 
                    '<span class="api-status error">❌ OpenRouter API Not Configured</span>';
                
                document.getElementById('apiStatus').innerHTML = html;
            } catch (error) {
                document.getElementById('apiStatus').innerHTML = 
                    '<span class="api-status error">❌ Unable to connect to API</span>';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        from utils.config import get_config
        config = get_config()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'news_api_configured': bool(config.get('news_api_key') and config.get('news_api_key') != 'your_news_api_key_here'),
            'openrouter_configured': bool(config.get('openrouter_api_key') and config.get('openrouter_api_key') != 'your_openrouter_api_key_here'),
            'models_loaded': True  # Add actual model loading check if needed
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/api/process', methods=['POST'])
def process_article():
    """Process a single article"""
    try:
        data = request.get_json()
        
        # Create article object
        article = {
            'title': data.get('title', ''),
            'description': data.get('content', ''),
            'content': data.get('content', ''),
            'source': {'name': data.get('source', 'User Input')}
        }
        
        include_analysis = data.get('include_analysis', True)
        
        logger.info(f"Processing article: {article['title'][:50]}...")
        
        # Process the article
        result = pipeline.process_single_article(article, include_analysis)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Article processing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'processing_time': 0
        }), 500

@app.route('/api/fetch-and-process', methods=['POST'])
def fetch_and_process():
    """Fetch and process news articles"""
    try:
        data = request.get_json()
        
        query = data.get('query', 'technology')
        page_size = min(data.get('page_size', 10), 20)  # Limit to 20 articles
        include_analysis = data.get('include_analysis', True)
        
        logger.info(f"Fetching news for query: {query}")
        
        # Use the pipeline's news batch processing
        result = pipeline.process_news_batch(query, page_size, include_analysis)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Fetch and process error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'processing_time': 0
        }), 500

@app.route('/api/batch-process', methods=['POST'])
def batch_process():
    """Process multiple articles"""
    try:
        data = request.get_json()
        
        articles = data.get('articles', [])
        include_analysis = data.get('include_analysis', True)
        
        if not articles:
            return jsonify({
                'success': False,
                'error': 'No articles provided',
                'processing_time': 0
            }), 400
        
        logger.info(f"Processing batch of {len(articles)} articles")
        
        # Process multiple articles
        result = pipeline.process_multiple_articles(articles, include_analysis)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Batch processing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'processing_time': 0
        }), 500

@app.route('/api/top-headlines', methods=['GET'])
def top_headlines():
    """Get and process top headlines"""
    try:
        query = request.args.get('query', 'general')
        page_size = min(int(request.args.get('page_size', 10)), 20)
        include_analysis = request.args.get('include_analysis', 'true').lower() == 'true'
        
        logger.info(f"Fetching top headlines for: {query}")
        
        # Fetch top headlines
        articles = news_fetcher.fetch_top_headlines(query, page_size)
        
        if not articles:
            return jsonify({
                'success': False,
                'error': 'No articles found',
                'processing_time': 0
            }), 404
        
        # Process the articles
        result = pipeline.process_multiple_articles(articles, include_analysis)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Top headlines error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'processing_time': 0
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /',
            'GET /api/health',
            'POST /api/process',
            'POST /api/fetch-and-process',
            'POST /api/batch-process',
            'GET /api/top-headlines'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'timestamp': datetime.utcnow().isoformat()
    }), 500

def main():
    """Main function to run the server"""
    logger.info("Starting News Intelligence Agent Web Server...")
    
    # Check if required API keys are configured
    from utils.config import get_config
    config = get_config()
    
    news_api_key = config.get('news_api_key')
    openrouter_api_key = config.get('openrouter_api_key')
    
    if not news_api_key or news_api_key == 'your_news_api_key_here':
        logger.warning("News API key not configured. News fetching will use mock data.")
        logger.info("To enable real news fetching, set NEWS_API_KEY in your .env file")
    
    if not openrouter_api_key or openrouter_api_key == 'your_openrouter_api_key_here':
        logger.warning("OpenRouter API key not configured. AI analysis will use fallback methods.")
        logger.info("To enable AI analysis, set OPENROUTER_API_KEY in your .env file")
    
    logger.info("Starting Flask server on http://localhost:8000")
    logger.info("Available endpoints:")
    logger.info("  - GET  /                    - Web interface")
    logger.info("  - GET  /api/health          - Health check")
    logger.info("  - POST /api/process         - Process single article")
    logger.info("  - POST /api/fetch-and-process - Fetch and process news")
    logger.info("  - POST /api/batch-process   - Process multiple articles")
    logger.info("  - GET  /api/top-headlines   - Get top headlines")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)

if __name__ == '__main__':
    main()