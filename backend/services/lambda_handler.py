import json
import logging
import os
from datetime import datetime
from typing import Dict, Any
from .news_pipeline import NewsProcessingPipeline
from utils.logger import setup_logging
from utils.config import Config

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize pipeline
pipeline = NewsProcessingPipeline()

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for news intelligence processing
    
    Args:
        event: Lambda event containing request parameters
        context: Lambda context
        
    Returns:
        Response dictionary with processing results
    """
    try:
        logger.info("Lambda handler invoked")
        logger.info(f"Event: {json.dumps(event, default=str)}")
        
        # Parse event body
        if 'body' in event:
            try:
                body = json.loads(event['body'])
            except json.JSONDecodeError:
                body = event['body']
        else:
            body = event
        
        # Determine operation type
        operation = body.get('operation', 'process_single')
        
        logger.info(f"Operation: {operation}")
        
        # Route to appropriate handler
        if operation == 'process_single':
            result = handle_process_single(body)
        elif operation == 'process_batch':
            result = handle_process_batch(body)
        elif operation == 'fetch_and_process':
            result = handle_fetch_and_process(body)
        elif operation == 'top_headlines':
            result = handle_top_headlines(body)
        elif operation == 'health_check':
            result = handle_health_check()
        else:
            result = {
                'success': False,
                'error': f'Unknown operation: {operation}'
            }
        
        # Add metadata to response
        result['metadata'] = {
            'operation': operation,
            'timestamp': context.aws_request_id if context else 'local',
            'function_name': context.function_name if context else 'news-intelligence-lambda',
            'memory_limit': context.memory_limit_in_mb if context else 'unknown',
            'remaining_time': context.get_remaining_time_in_millis() if context else 0
        }
        
        logger.info(f"Operation completed successfully: {operation}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(result, default=str)
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        error_response = {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            })
        }
        return error_response

def health_check(event, context):
    """Health check endpoint for the Lambda function"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })
    }

def handle_process_single(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle single article processing
    
    Args:
        body: Request body containing article data
        
    Returns:
        Processing result
    """
    try:
        article = body.get('article')
        include_analysis = body.get('include_analysis', True)
        
        if not article:
            return {
                'success': False,
                'error': 'No article provided'
            }
        
        logger.info("Processing single article")
        result = pipeline.process_single_article(article, include_analysis)
        
        return result
        
    except Exception as e:
        logger.error(f"Single article processing error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def handle_process_batch(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle batch article processing
    
    Args:
        body: Request body containing articles data
        
    Returns:
        Processing result
    """
    try:
        articles = body.get('articles', [])
        include_analysis = body.get('include_analysis', True)
        
        if not articles:
            return {
                'success': False,
                'error': 'No articles provided'
            }
        
        logger.info(f"Processing batch of {len(articles)} articles")
        result = pipeline.process_multiple_articles(articles, include_analysis)
        
        return result
        
    except Exception as e:
        logger.error(f"Batch processing error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def handle_fetch_and_process(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle fetching and processing news articles
    
    Args:
        body: Request body containing search parameters
        
    Returns:
        Processing result
    """
    try:
        query = body.get('query', 'technology')
        page_size = body.get('page_size', 10)
        include_analysis = body.get('include_analysis', True)
        
        logger.info(f"Fetching and processing news for query: {query}")
        result = pipeline.process_news_batch(query, page_size, include_analysis)
        
        return result
        
    except Exception as e:
        logger.error(f"Fetch and process error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def handle_top_headlines(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle fetching and processing top headlines
    
    Args:
        body: Request body containing parameters
        
    Returns:
        Processing result
    """
    try:
        category = body.get('category', 'general')
        country = body.get('country', 'us')
        page_size = body.get('page_size', 10)
        include_analysis = body.get('include_analysis', True)
        
        logger.info(f"Fetching and processing top headlines for category: {category}")
        result = pipeline.get_top_headlines_pipeline(category, country, page_size, include_analysis)
        
        return result
        
    except Exception as e:
        logger.error(f"Top headlines error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def handle_health_check() -> Dict[str, Any]:
    """
    Handle health check request
    
    Returns:
        Health status
    """
    try:
        # Test pipeline components
        components_status = {}
        
        # Test news fetcher
        try:
            test_result = pipeline.news_fetcher.fetch_news("test", page_size=1)
            components_status['news_fetcher'] = 'healthy' if test_result and len(test_result) > 0 else 'unhealthy'
        except Exception as e:
            components_status['news_fetcher'] = f'error: {str(e)}'
        
        # Test sentiment analyzer
        try:
            test_result = pipeline.sentiment_analyzer.analyze_sentiment("This is a test.")
            components_status['sentiment_analyzer'] = 'healthy' if test_result.get('sentiment') else 'unhealthy'
        except Exception as e:
            components_status['sentiment_analyzer'] = f'error: {str(e)}'
        
        # Test fake news detector
        try:
            test_result = pipeline.fake_news_detector.detect_fake_news("This is a test article.")
            components_status['fake_news_detector'] = 'healthy' if test_result.get('prediction') else 'unhealthy'
        except Exception as e:
            components_status['fake_news_detector'] = f'error: {str(e)}'
        
        # Test summarizer
        try:
            test_result = pipeline.summarizer.summarize_article("This is a test article for summarization.")
            components_status['summarizer'] = 'healthy' if test_result.get('success', False) else 'unhealthy'
        except Exception as e:
            components_status['summarizer'] = f'error: {str(e)}'
        
        # Overall health
        healthy_components = sum(1 for status in components_status.values() if status == 'healthy')
        total_components = len(components_status)
        overall_health = 'healthy' if healthy_components == total_components else 'degraded'
        
        return {
            'success': True,
            'health_status': overall_health,
            'components': components_status,
            'healthy_components': healthy_components,
            'total_components': total_components,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'health_status': 'unhealthy'
        }

# Local testing function
def test_lambda_locally():
    """Test the Lambda function locally"""
    print("Testing Lambda function locally...")
    
    # Test health check
    print("\n1. Testing health check:")
    health_event = {'operation': 'health_check'}
    health_result = lambda_handler(health_event, None)
    print(f"Health check result: {json.dumps(health_result, indent=2)}")
    
    # Test single article processing
    print("\n2. Testing single article processing:")
    sample_article = {
        'title': 'Major Climate Summit Reaches Historic Agreement',
        'description': 'World leaders gathered at the UN Climate Summit have reached a historic agreement on carbon emissions.',
        'content': 'In a groundbreaking development at the United Nations Climate Summit, representatives from over 190 countries have unanimously agreed to ambitious new carbon emission targets.',
        'source': {'name': 'Global News Network'}
    }
    
    single_event = {
        'operation': 'process_single',
        'article': sample_article,
        'include_analysis': True
    }
    single_result = lambda_handler(single_event, None)
    print(f"Single article result: {json.dumps(json.loads(single_result['body']), indent=2)}")
    
    # Test top headlines
    print("\n3. Testing top headlines:")
    headlines_event = {
        'operation': 'top_headlines',
        'category': 'technology',
        'page_size': 3,
        'include_analysis': False  # Faster for testing
    }
    headlines_result = lambda_handler(headlines_event, None)
    print(f"Top headlines result: {json.dumps(json.loads(headlines_result['body']), indent=2)}")

if __name__ == "__main__":
    test_lambda_locally()