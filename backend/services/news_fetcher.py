import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from utils.config import Config

class NewsFetcher:
    def __init__(self):
        from utils.config import get_config
        config = get_config()
        self.api_key = config.get('news_api_key', '')
        self.base_url = "https://newsapi.org/v2"
        self.logger = logging.getLogger(__name__)
        
    def fetch_news(self, 
                   query: str = "latest",
                   sources: List[str] = None,
                   from_date: str = None,
                   to_date: str = None,
                   language: str = "en",
                   sort_by: str = "publishedAt",
                   page_size: int = 20) -> List[Dict]:
        """
        Fetch news articles from News API
        
        Args:
            query: Search query
            sources: List of news sources
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            language: Language code
            sort_by: Sort criteria
            page_size: Number of articles to fetch
            
        Returns:
            List of news articles
        """
        
        if not self.api_key:
            self.logger.warning("News API key not configured. Using mock data.")
            return self._get_mock_news(query, sources, page_size)
        
        try:
            params = {
                'q': query,
                'language': language,
                'sortBy': sort_by,
                'pageSize': page_size,
                'apiKey': self.api_key
            }
            
            if sources:
                params['sources'] = ','.join(sources)
            
            if from_date:
                params['from'] = from_date
            
            if to_date:
                params['to'] = to_date
            
            response = requests.get(f"{self.base_url}/everything", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'ok':
                articles = data.get('articles', [])
                self.logger.info(f"Successfully fetched {len(articles)} articles")
                
                # Process and standardize article format
                processed_articles = []
                for article in articles:
                    processed_article = {
                        'id': article.get('url', ''),
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'content': article.get('content', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'author': article.get('author', 'Unknown'),
                        'published_at': article.get('publishedAt', ''),
                        'image_url': article.get('urlToImage', ''),
                        'language': language
                    }
                    processed_articles.append(processed_article)
                
                return processed_articles
            else:
                self.logger.error(f"News API error: {data.get('message', 'Unknown error')}")
                return self._get_mock_news(query, sources, page_size)
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching news: {str(e)}")
            return self._get_mock_news(query, sources, page_size)
        except Exception as e:
            self.logger.error(f"Unexpected error fetching news: {str(e)}")
            return self._get_mock_news(query, sources, page_size)
    
    def get_top_headlines(self,
                         country: str = "us",
                         category: str = None,
                         sources: List[str] = None,
                         page_size: int = 20) -> List[Dict]:
        """Get top headlines"""
        
        if not self.api_key:
            self.logger.warning("News API key not configured. Using mock headlines.")
            return self._get_mock_headlines(page_size)
        
        try:
            params = {
                'country': country,
                'pageSize': page_size,
                'apiKey': self.api_key
            }
            
            if category:
                params['category'] = category
            
            if sources:
                params['sources'] = ','.join(sources)
            
            response = requests.get(f"{self.base_url}/top-headlines", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] == 'ok':
                articles = data.get('articles', [])
                self.logger.info(f"Successfully fetched {len(articles)} headlines")
                return self._process_articles(articles)
            else:
                self.logger.error(f"News API error: {data.get('message', 'Unknown error')}")
                return self._get_mock_headlines(page_size)
                
        except Exception as e:
            self.logger.error(f"Error fetching headlines: {str(e)}")
            return self._get_mock_headlines(page_size)
    
    def _process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process and standardize article format"""
        processed_articles = []
        for article in articles:
            processed_article = {
                'id': article.get('url', ''),
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'content': article.get('content', ''),
                'url': article.get('url', ''),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'author': article.get('author', 'Unknown'),
                'published_at': article.get('publishedAt', ''),
                'image_url': article.get('urlToImage', ''),
                'language': 'en'
            }
            processed_articles.append(processed_article)
        
        return processed_articles
    
    def _get_mock_news(self, query: str, sources: List[str], count: int) -> List[Dict]:
        """Return mock news data when API is not available"""
        mock_articles = [
            {
                'id': '1',
                'title': f'Breaking: Major developments in {query} sector',
                'description': f'Recent developments in {query} show significant progress and innovation.',
                'content': f'Full article content about {query} developments and their impact on the industry...',
                'url': 'https://example.com/article1',
                'source': 'Tech News Daily',
                'author': 'John Reporter',
                'published_at': datetime.utcnow().isoformat(),
                'image_url': 'https://example.com/image1.jpg',
                'language': 'en'
            },
            {
                'id': '2',
                'title': f'Analysis: {query} trends for 2024',
                'description': f'Comprehensive analysis of current {query} trends and future predictions.',
                'content': f'Detailed analysis covering various aspects of {query} including market trends...',
                'url': 'https://example.com/article2',
                'source': 'Business Weekly',
                'author': 'Jane Analyst',
                'published_at': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                'image_url': 'https://example.com/image2.jpg',
                'language': 'en'
            },
            {
                'id': '3',
                'title': f'Research: New findings in {query} field',
                'description': f'Researchers discover breakthrough findings related to {query}.',
                'content': f'Scientific research paper discussing new discoveries in {query} field...',
                'url': 'https://example.com/article3',
                'source': 'Research Journal',
                'author': 'Dr. Smith',
                'published_at': (datetime.utcnow() - timedelta(hours=4)).isoformat(),
                'image_url': 'https://example.com/image3.jpg',
                'language': 'en'
            }
        ]
        
        return mock_articles[:count]
    
    def _get_mock_headlines(self, count: int) -> List[Dict]:
        """Return mock headline data"""
        return self._get_mock_news("latest", None, count)

def main():
    """Test the news fetcher"""
    fetcher = NewsFetcher()
    
    # Test fetching news
    articles = fetcher.fetch_news(
        query="technology",
        sources=["techcrunch", "reuters"],
        page_size=5
    )
    
    print(f"Fetched {len(articles)} articles")
    for i, article in enumerate(articles[:3]):
        print(f"\nArticle {i+1}:")
        print(f"Title: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"Description: {article['description'][:100]}...")

if __name__ == "__main__":
    main()