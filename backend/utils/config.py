import os
import json
from typing import Dict, Any, Optional

class Config:
    """Configuration management for the news intelligence system"""
    
    def __init__(self):
        self._config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from environment variables and config files"""
        # API Keys
        self._config['news_api_key'] = os.getenv('NEWS_API_KEY', '')
        self._config['openrouter_api_key'] = os.getenv('OPENROUTER_API_KEY', '')
        self._config['openai_api_key'] = os.getenv('OPENAI_API_KEY', '')
        
        # AWS Configuration
        self._config['aws_region'] = os.getenv('AWS_REGION', 'us-east-1')
        self._config['s3_bucket'] = os.getenv('S3_BUCKET', 'news-intelligence-models')
        self._config['lambda_function_name'] = os.getenv('LAMBDA_FUNCTION_NAME', 'news-intelligence-lambda')
        
        # Model Configuration
        self._config['sentiment_model_path'] = os.getenv('SENTIMENT_MODEL_PATH', 'sentiment_model.pkl')
        self._config['sentiment_vectorizer_path'] = os.getenv('SENTIMENT_VECTORIZER_PATH', 'vectorizer.pkl')
        self._config['fake_news_model_path'] = os.getenv('FAKE_NEWS_MODEL_PATH', 'fake_news_model.pkl')
        self._config['fake_news_vectorizer_path'] = os.getenv('FAKE_NEWS_VECTORIZER_PATH', 'fake_vectorizer.pkl')
        
        # S3 Paths
        self._config['s3_sentiment_model_key'] = os.getenv('S3_SENTIMENT_MODEL_KEY', 'models/sentiment_model.pkl')
        self._config['s3_sentiment_vectorizer_key'] = os.getenv('S3_SENTIMENT_VECTORIZER_KEY', 'models/vectorizer.pkl')
        self._config['s3_fake_news_model_key'] = os.getenv('S3_FAKE_NEWS_MODEL_KEY', 'models/fake_news_model.pkl')
        self._config['s3_fake_news_vectorizer_key'] = os.getenv('S3_FAKE_NEWS_VECTORIZER_KEY', 'models/fake_vectorizer.pkl')
        
        # API Configuration
        self._config['news_api_base_url'] = os.getenv('NEWS_API_BASE_URL', 'https://newsapi.org/v2')
        self._config['news_api_timeout'] = int(os.getenv('NEWS_API_TIMEOUT', '30'))
        self._config['openrouter_base_url'] = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        self._config['openrouter_timeout'] = int(os.getenv('OPENROUTER_TIMEOUT', '60'))
        
        # Processing Configuration
        self._config['max_articles_per_request'] = int(os.getenv('MAX_ARTICLES_PER_REQUEST', '20'))
        self._config['default_page_size'] = int(os.getenv('DEFAULT_PAGE_SIZE', '10'))
        self._config['batch_processing_size'] = int(os.getenv('BATCH_PROCESSING_SIZE', '5'))
        
        # Logging Configuration
        self._config['log_level'] = os.getenv('LOG_LEVEL', 'INFO')
        self._config['enable_cloudwatch'] = os.getenv('ENABLE_CLOUDWATCH', 'true').lower() == 'true'
        
        # Feature Flags
        self._config['enable_sentiment_analysis'] = os.getenv('ENABLE_SENTIMENT_ANALYSIS', 'true').lower() == 'true'
        self._config['enable_fake_news_detection'] = os.getenv('ENABLE_FAKE_NEWS_DETECTION', 'true').lower() == 'true'
        self._config['enable_summarization'] = os.getenv('ENABLE_SUMMARIZATION', 'true').lower() == 'true'
        self._config['enable_ai_analysis'] = os.getenv('ENABLE_AI_ANALYSIS', 'true').lower() == 'true'
        
        # Free API Models (when premium APIs are not available)
        self._config['free_sentiment_models'] = [
            'google/gemma-2-9b-it:free',
            'meta-llama/llama-3.2-3b-instruct:free',
            'microsoft/phi-3-mini-128k-instruct:free'
        ]
        self._config['free_summarization_models'] = [
            'google/gemma-2-9b-it:free',
            'meta-llama/llama-3.2-3b-instruct:free'
        ]
        
        # Cache Configuration
        self._config['cache_ttl_seconds'] = int(os.getenv('CACHE_TTL_SECONDS', '3600'))
        self._config['enable_caching'] = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
        
        # Retry Configuration
        self._config['max_retries'] = int(os.getenv('MAX_RETRIES', '3'))
        self._config['retry_delay_seconds'] = int(os.getenv('RETRY_DELAY_SECONDS', '1'))
        
        # Rate Limiting
        self._config['news_api_rate_limit'] = int(os.getenv('NEWS_API_RATE_LIMIT', '100'))
        self._config['openrouter_rate_limit'] = int(os.getenv('OPENROUTER_RATE_LIMIT', '60'))
        
        # Load from config file if it exists
        config_file = os.getenv('CONFIG_FILE', 'config.json')
        if os.path.exists(config_file):
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file: str):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                self._config.update(file_config)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = value
    
    def has_api_key(self, api_type: str) -> bool:
        """Check if API key is available"""
        if api_type == 'news':
            return bool(self._config.get('news_api_key'))
        elif api_type == 'openrouter':
            return bool(self._config.get('openrouter_api_key'))
        elif api_type == 'openai':
            return bool(self._config.get('openai_api_key'))
        return False
    
    def get_api_key(self, api_type: str) -> str:
        """Get API key for specified type"""
        if api_type == 'news':
            return self._config.get('news_api_key', '')
        elif api_type == 'openrouter':
            return self._config.get('openrouter_api_key', '')
        elif api_type == 'openai':
            return self._config.get('openai_api_key', '')
        return ''
    
    def get_free_model(self, model_type: str) -> str:
        """Get a free model for the specified type"""
        if model_type == 'sentiment':
            models = self._config.get('free_sentiment_models', [])
        elif model_type == 'summarization':
            models = self._config.get('free_summarization_models', [])
        else:
            return ''
        
        return models[0] if models else ''
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        feature_key = f'enable_{feature.lower().replace(" ", "_")}'
        return self._config.get(feature_key, True)
    
    def get_aws_credentials(self) -> Dict[str, str]:
        """Get AWS credentials"""
        return {
            'region': self._config.get('aws_region', 'us-east-1'),
            'bucket': self._config.get('s3_bucket', 'news-intelligence-models')
        }
    
    def get_model_paths(self) -> Dict[str, str]:
        """Get model file paths"""
        return {
            'sentiment_model': self._config.get('sentiment_model_path', 'sentiment_model.pkl'),
            'sentiment_vectorizer': self._config.get('sentiment_vectorizer_path', 'vectorizer.pkl'),
            'fake_news_model': self._config.get('fake_news_model_path', 'fake_news_model.pkl'),
            'fake_news_vectorizer': self._config.get('fake_news_vectorizer_path', 'fake_vectorizer.pkl')
        }
    
    def get_s3_model_keys(self) -> Dict[str, str]:
        """Get S3 keys for model storage"""
        return {
            'sentiment_model': self._config.get('s3_sentiment_model_key', 'models/sentiment_model.pkl'),
            'sentiment_vectorizer': self._config.get('s3_sentiment_vectorizer_key', 'models/vectorizer.pkl'),
            'fake_news_model': self._config.get('s3_fake_news_model_key', 'models/fake_news_model.pkl'),
            'fake_news_vectorizer': self._config.get('s3_fake_news_vectorizer_key', 'models/fake_vectorizer.pkl')
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return self._config.copy()
    
    def save_to_file(self, filename: str):
        """Save configuration to file"""
        with open(filename, 'w') as f:
            json.dump(self._config, f, indent=2)

# Global configuration instance
config = Config()

def get_config() -> Config:
    """Get the global configuration instance"""
    return config

def setup_environment():
    """Setup environment variables for development"""
    # Development API keys (these are example keys - replace with your actual keys)
    os.environ.setdefault('NEWS_API_KEY', 'your_news_api_key_here')
    os.environ.setdefault('OPENROUTER_API_KEY', 'your_openrouter_api_key_here')
    os.environ.setdefault('OPENAI_API_KEY', 'your_openai_api_key_here')
    
    # AWS Configuration
    os.environ.setdefault('AWS_REGION', 'us-east-1')
    os.environ.setdefault('S3_BUCKET', 'news-intelligence-models')
    
    # Feature flags
    os.environ.setdefault('ENABLE_SENTIMENT_ANALYSIS', 'true')
    os.environ.setdefault('ENABLE_FAKE_NEWS_DETECTION', 'true')
    os.environ.setdefault('ENABLE_SUMMARIZATION', 'true')
    os.environ.setdefault('ENABLE_AI_ANALYSIS', 'true')
    
    # Logging
    os.environ.setdefault('LOG_LEVEL', 'INFO')
    os.environ.setdefault('ENABLE_CLOUDWATCH', 'true')

if __name__ == "__main__":
    # Setup development environment
    setup_environment()
    
    # Test configuration
    config = get_config()
    print("Configuration loaded:")
    print(f"News API Key configured: {config.has_api_key('news')}")
    print(f"OpenRouter API Key configured: {config.has_api_key('openrouter')}")
    print(f"AWS Region: {config.get('aws_region')}")
    print(f"S3 Bucket: {config.get('s3_bucket')}")
    print(f"Sentiment Analysis enabled: {config.is_feature_enabled('sentiment_analysis')}")
    print(f"Fake News Detection enabled: {config.is_feature_enabled('fake_news_detection')}")
    print(f"Summarization enabled: {config.is_feature_enabled('summarization')}")
    print(f"AI Analysis enabled: {config.is_feature_enabled('ai_analysis')}")
    
    # Save example config file
    config.save_to_file('config_example.json')
    print("\nExample configuration saved to config_example.json")