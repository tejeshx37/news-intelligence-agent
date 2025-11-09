import logging
import time
from typing import Dict, List, Optional
from datetime import datetime
from .news_fetcher import NewsFetcher
from .sentiment_analyzer import SentimentAnalyzer
from .fake_news_detector import FakeNewsDetector
from .summarizer import NewsSummarizer
from .openrouter_client import OpenRouterClient

class NewsProcessingPipeline:
    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.fake_news_detector = FakeNewsDetector()
        self.summarizer = NewsSummarizer()
        self.openrouter_client = OpenRouterClient()
        self.logger = logging.getLogger(__name__)
    
    def process_single_article(self, article: Dict, include_analysis: bool = True) -> Dict:
        """
        Process a single news article through the complete pipeline
        
        Args:
            article: Article dictionary with 'title', 'description', 'content', 'source'
            include_analysis: Whether to include AI analysis
            
        Returns:
            Processed article with sentiment, fake news detection, summary, and analysis
        """
        start_time = time.time()
        
        try:
            # Extract article data
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '') or description
            source = article.get('source', {}).get('name', '') if isinstance(article.get('source'), dict) else article.get('source', '')
            
            # Use description if content is empty
            text_to_process = content if content and len(content) > len(description) else description
            
            if not text_to_process:
                return {
                    'original_article': article,
                    'error': 'No content to process',
                    'processing_time': time.time() - start_time,
                    'success': False
                }
            
            # Initialize results
            processed_result = {
                'original_article': article,
                'title': title,
                'source': source,
                'processing_timestamp': datetime.now().isoformat(),
                'success': True
            }
            
            # 1. Sentiment Analysis
            try:
                sentiment_result = self.sentiment_analyzer.analyze_sentiment(text_to_process)
                processed_result['sentiment_analysis'] = sentiment_result
            except Exception as e:
                self.logger.error(f"Sentiment analysis failed: {str(e)}")
                processed_result['sentiment_analysis'] = {
                    'sentiment': 'unknown',
                    'confidence': 0.0,
                    'error': str(e)
                }
            
            # 2. Fake News Detection
            try:
                fake_news_result = self.fake_news_detector.detect_fake_news(
                    text_to_process, title, source
                )
                processed_result['fake_news_detection'] = fake_news_result
            except Exception as e:
                self.logger.error(f"Fake news detection failed: {str(e)}")
                processed_result['fake_news_detection'] = {
                    'prediction': 'unknown',
                    'confidence': 0.0,
                    'error': str(e)
                }
            
            # 3. Summarization
            try:
                summary_result = self.summarizer.summarize_article(
                    text_to_process, title, max_length=100
                )
                processed_result['summary'] = summary_result
            except Exception as e:
                self.logger.error(f"Summarization failed: {str(e)}")
                processed_result['summary'] = {
                    'summary': 'Summary generation failed',
                    'error': str(e),
                    'success': False
                }
            
            # 4. AI Analysis (optional)
            if include_analysis:
                try:
                    analysis_result = self.openrouter_client.analyze_news_content(
                        text_to_process, title
                    )
                    processed_result['ai_analysis'] = analysis_result
                except Exception as e:
                    self.logger.error(f"AI analysis failed: {str(e)}")
                    processed_result['ai_analysis'] = {
                        'analysis': {},
                        'error': str(e),
                        'success': False
                    }
            
            # Calculate overall processing time
            processed_result['processing_time'] = time.time() - start_time
            
            # Add risk assessment
            processed_result['risk_assessment'] = self._assess_article_risk(processed_result)
            
            return processed_result
            
        except Exception as e:
            self.logger.error(f"Pipeline processing failed: {str(e)}")
            return {
                'original_article': article,
                'error': f'Pipeline processing failed: {str(e)}',
                'processing_time': time.time() - start_time,
                'success': False
            }
    
    def process_multiple_articles(self, articles: List[Dict], include_analysis: bool = True) -> Dict:
        """
        Process multiple articles through the pipeline
        
        Args:
            articles: List of article dictionaries
            include_analysis: Whether to include AI analysis
            
        Returns:
            Dictionary with processed articles and aggregate statistics
        """
        start_time = time.time()
        
        if not articles:
            return {
                'processed_articles': [],
                'statistics': {},
                'processing_time': 0,
                'success': False,
                'error': 'No articles provided'
            }
        
        processed_articles = []
        errors = []
        
        # Process each article
        for i, article in enumerate(articles):
            try:
                self.logger.info(f"Processing article {i+1}/{len(articles)}")
                result = self.process_single_article(article, include_analysis)
                processed_articles.append(result)
                
            except Exception as e:
                error_msg = f"Error processing article {i}: {str(e)}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                processed_articles.append({
                    'original_article': article,
                    'error': str(e),
                    'success': False
                })
        
        # Generate statistics
        statistics = self._generate_pipeline_statistics(processed_articles)
        
        return {
            'processed_articles': processed_articles,
            'statistics': statistics,
            'errors': errors,
            'total_articles': len(articles),
            'successful_articles': sum(1 for r in processed_articles if r.get('success', False)),
            'processing_time': time.time() - start_time,
            'success': len(errors) < len(articles)  # Success if at least one article processed
        }
    
    def process_news_batch(self, query: str = "technology", page_size: int = 10, 
                          include_analysis: bool = True) -> Dict:
        """
        Fetch and process a batch of news articles
        
        Args:
            query: Search query for news articles
            page_size: Number of articles to fetch
            include_analysis: Whether to include AI analysis
            
        Returns:
            Dictionary with fetched and processed articles
        """
        try:
            # Fetch news articles
            self.logger.info(f"Fetching news articles for query: {query}")
            news_result = self.news_fetcher.fetch_news(query, page_size=page_size)
            
            if not news_result.get('success', False):
                return {
                    'error': news_result.get('error', 'Failed to fetch news'),
                    'success': False
                }
            
            articles = news_result.get('articles', [])
            
            if not articles:
                return {
                    'error': 'No articles found',
                    'success': False
                }
            
            # Process the articles
            processed_result = self.process_multiple_articles(articles, include_analysis)
            
            # Add fetch information
            processed_result['fetch_info'] = {
                'query': query,
                'page_size': page_size,
                'articles_fetched': len(articles),
                'fetch_timestamp': datetime.now().isoformat()
            }
            
            return processed_result
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {str(e)}")
            return {
                'error': f'Batch processing failed: {str(e)}',
                'success': False
            }
    
    def get_top_headlines_pipeline(self, category: str = "general", country: str = "us", 
                                 page_size: int = 10, include_analysis: bool = True) -> Dict:
        """
        Get and process top headlines
        
        Args:
            category: News category (general, business, technology, etc.)
            country: Country code
            page_size: Number of headlines to fetch
            include_analysis: Whether to include AI analysis
            
        Returns:
            Dictionary with processed headlines
        """
        try:
            # Fetch top headlines
            self.logger.info(f"Fetching top headlines for category: {category}")
            headlines_result = self.news_fetcher.get_top_headlines(
                category=category, country=country, page_size=page_size
            )
            
            if not headlines_result.get('success', False):
                return {
                    'error': headlines_result.get('error', 'Failed to fetch headlines'),
                    'success': False
                }
            
            articles = headlines_result.get('articles', [])
            
            if not articles:
                return {
                    'error': 'No headlines found',
                    'success': False
                }
            
            # Process the headlines
            processed_result = self.process_multiple_articles(articles, include_analysis)
            
            # Add headline information
            processed_result['headline_info'] = {
                'category': category,
                'country': country,
                'page_size': page_size,
                'headlines_fetched': len(articles),
                'fetch_timestamp': datetime.now().isoformat()
            }
            
            return processed_result
            
        except Exception as e:
            self.logger.error(f"Headlines processing failed: {str(e)}")
            return {
                'error': f'Headlines processing failed: {str(e)}',
                'success': False
            }
    
    def _assess_article_risk(self, processed_result: Dict) -> Dict:
        """
        Assess the risk level of an article based on analysis results
        
        Args:
            processed_result: Processed article result
            
        Returns:
            Risk assessment dictionary
        """
        risk_score = 0
        risk_factors = []
        
        # Check fake news detection
        fake_news_result = processed_result.get('fake_news_detection', {})
        if fake_news_result.get('prediction') == 'fake':
            risk_score += 0.4
            risk_factors.append('High fake news probability')
        elif fake_news_result.get('prediction') == 'suspicious':
            risk_score += 0.2
            risk_factors.append('Suspicious content detected')
        
        # Check sentiment
        sentiment_result = processed_result.get('sentiment_analysis', {})
        if sentiment_result.get('sentiment') == 'negative' and sentiment_result.get('confidence', 0) > 0.7:
            risk_score += 0.1
            risk_factors.append('Strong negative sentiment')
        
        # Check AI analysis if available
        ai_analysis = processed_result.get('ai_analysis', {})
        if ai_analysis.get('success', False):
            analysis_data = ai_analysis.get('analysis', {})
            if 'bias_indicators' in analysis_data and len(analysis_data['bias_indicators']) > 2:
                risk_score += 0.15
                risk_factors.append('Multiple bias indicators')
        
        # Determine risk level
        if risk_score >= 0.5:
            risk_level = 'high'
        elif risk_score >= 0.2:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'assessment_timestamp': datetime.now().isoformat()
        }
    
    def _generate_pipeline_statistics(self, processed_articles: List[Dict]) -> Dict:
        """
        Generate statistics from processed articles
        
        Args:
            processed_articles: List of processed article results
            
        Returns:
            Statistics dictionary
        """
        if not processed_articles:
            return {}
        
        successful_articles = [a for a in processed_articles if a.get('success', False)]
        
        # Sentiment statistics
        sentiments = []
        for article in successful_articles:
            sentiment = article.get('sentiment_analysis', {}).get('sentiment')
            if sentiment:
                sentiments.append(sentiment)
        
        sentiment_counts = {
            'positive': sentiments.count('positive'),
            'negative': sentiments.count('negative'),
            'neutral': sentiments.count('neutral'),
            'unknown': len(processed_articles) - len(sentiments)
        }
        
        # Fake news statistics
        fake_news_predictions = []
        for article in successful_articles:
            prediction = article.get('fake_news_detection', {}).get('prediction')
            if prediction:
                fake_news_predictions.append(prediction)
        
        fake_news_counts = {
            'fake': fake_news_predictions.count('fake'),
            'real': fake_news_predictions.count('real'),
            'suspicious': fake_news_predictions.count('suspicious'),
            'unknown': len(processed_articles) - len(fake_news_predictions)
        }
        
        # Risk assessment statistics
        risk_levels = []
        for article in successful_articles:
            risk_level = article.get('risk_assessment', {}).get('risk_level')
            if risk_level:
                risk_levels.append(risk_level)
        
        risk_counts = {
            'high': risk_levels.count('high'),
            'medium': risk_levels.count('medium'),
            'low': risk_levels.count('low'),
            'unknown': len(processed_articles) - len(risk_levels)
        }
        
        # Processing time statistics
        processing_times = [a.get('processing_time', 0) for a in processed_articles]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        return {
            'total_articles': len(processed_articles),
            'successful_articles': len(successful_articles),
            'success_rate': len(successful_articles) / len(processed_articles),
            'sentiment_distribution': sentiment_counts,
            'fake_news_distribution': fake_news_counts,
            'risk_distribution': risk_counts,
            'average_processing_time': avg_processing_time,
            'total_processing_time': sum(processing_times)
        }

def main():
    """Test the news processing pipeline"""
    pipeline = NewsProcessingPipeline()
    
    # Test with a sample article
    sample_article = {
        'title': 'Major Climate Summit Reaches Historic Agreement',
        'description': 'World leaders gathered at the UN Climate Summit have reached a historic agreement on carbon emissions, marking a significant step forward in the fight against climate change.',
        'content': 'In a groundbreaking development at the United Nations Climate Summit, representatives from over 190 countries have unanimously agreed to ambitious new carbon emission targets. The agreement, which was reached after intense negotiations lasting throughout the night, commits nations to reducing emissions by 50% over the next decade. Environmental activists and scientists have praised the agreement as a crucial step toward preventing catastrophic climate change. However, some critics argue that the targets are not ambitious enough and that implementation remains uncertain.',
        'source': {'name': 'Global News Network'}
    }
    
    print("Testing single article processing:")
    result = pipeline.process_single_article(sample_article)
    
    if result['success']:
        print(f"Article: {result['title']}")
        print(f"Sentiment: {result['sentiment_analysis']['sentiment']} (confidence: {result['sentiment_analysis']['confidence']:.2f})")
        print(f"Fake News Prediction: {result['fake_news_detection']['prediction']} (confidence: {result['fake_news_detection']['confidence']:.2f})")
        print(f"Summary: {result['summary']['summary']}")
        print(f"Risk Level: {result['risk_assessment']['risk_level']}")
        print(f"Processing Time: {result['processing_time']:.2f}s")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()