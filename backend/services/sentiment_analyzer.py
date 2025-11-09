import pickle
import os
import logging
import sys
from typing import Dict, List
import boto3
from botocore.exceptions import ClientError
from utils.config import get_config
from utils.aws_utils import S3Manager

class SentimentAnalyzer:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.s3_handler = S3Manager()
        self.logger = logging.getLogger(__name__)
        self.config = get_config()
        self._load_models()
    
    def _load_models(self):
        """Load sentiment analysis models from local files or S3"""
        try:
            # Try to load from local files first
            model_path = os.path.join(os.path.dirname(__file__), 'sentiment_model.pkl')
            vectorizer_path = os.path.join(os.path.dirname(__file__), 'vectorizer.pkl')
            
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                self.logger.info("Loading models from local files")
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
            else:
                # Try to download from S3
                self.logger.info("Models not found locally, attempting to download from S3")
                self._download_models_from_s3()
            
            if self.model and self.vectorizer:
                self.logger.info("Sentiment analysis models loaded successfully")
            else:
                self.logger.warning("Models not available, using fallback logic")
                
        except Exception as e:
            self.logger.error(f"Error loading models: {str(e)}")
            self.model = None
            self.vectorizer = None
    
    def _download_models_from_s3(self):
        """Download models from S3 bucket"""
        try:
            model_key = 'models/sentiment_model.pkl'
            vectorizer_key = 'models/vectorizer.pkl'
            
            # Download to temp directory
            model_path = '/tmp/sentiment_model.pkl'
            vectorizer_path = '/tmp/vectorizer.pkl'
            
            self.s3_handler.download_file(model_key, model_path)
            self.s3_handler.download_file(vectorizer_key, vectorizer_path)
            
            # Load models
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
                
            self.logger.info("Models downloaded and loaded from S3")
            
        except Exception as e:
            self.logger.error(f"Error downloading models from S3: {str(e)}")
            self.model = None
            self.vectorizer = None
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of the given text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment and confidence
        """
        if not text or not isinstance(text, str):
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'error': 'Invalid input text'
            }
        
        try:
            if self.model and self.vectorizer:
                # Use trained model
                text_vector = self.vectorizer.transform([text])
                sentiment = self.model.predict(text_vector)[0]
                confidence = max(self.model.predict_proba(text_vector)[0])
                
                return {
                    'sentiment': sentiment,
                    'confidence': float(confidence),
                    'method': 'ml_model'
                }
            else:
                # Fallback to rule-based approach
                return self._rule_based_sentiment(text)
                
        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {str(e)}")
            return self._rule_based_sentiment(text)
    
    def analyze_batch_sentiment(self, texts: List[str]) -> List[Dict]:
        """
        Analyze sentiment for multiple texts
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of sentiment results
        """
        results = []
        for text in texts:
            result = self.analyze_sentiment(text)
            results.append(result)
        
        return results
    
    def _rule_based_sentiment(self, text: str) -> Dict:
        """
        Fallback rule-based sentiment analysis
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment and confidence
        """
        text_lower = text.lower()
        
        # Positive keywords
        positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'positive', 'success', 'successful', 'improve', 'improved',
            'benefit', 'beneficial', 'outstanding', 'brilliant', 'superb',
            'outstanding', 'remarkable', 'impressive', 'promising', 'thrilled',
            'excited', 'happy', 'pleased', 'satisfied', 'optimistic'
        ]
        
        # Negative keywords
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'disappointing',
            'negative', 'fail', 'failed', 'problem', 'issue', 'concern',
            'worry', 'worried', 'dangerous', 'risk', 'threat', 'crisis',
            'disaster', 'catastrophe', 'devastating', 'alarming', 'shocking',
            'outrageous', 'scandal', 'corruption', 'scandalous', 'tragic'
        ]
        
        # Count positive and negative words
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Determine sentiment
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(0.5 + (positive_count - negative_count) * 0.1, 0.8)
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = min(0.5 + (negative_count - positive_count) * 0.1, 0.8)
        else:
            sentiment = 'neutral'
            confidence = 0.6
        
        return {
            'sentiment': sentiment,
            'confidence': float(confidence),
            'method': 'rule_based',
            'positive_keywords': positive_count,
            'negative_keywords': negative_count
        }
    
    def get_sentiment_summary(self, sentiments: List[Dict]) -> Dict:
        """
        Generate summary statistics from sentiment analysis results
        
        Args:
            sentiments: List of sentiment results
            
        Returns:
            Summary statistics
        """
        if not sentiments:
            return {
                'total': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'positive_percentage': 0,
                'negative_percentage': 0,
                'neutral_percentage': 0,
                'average_confidence': 0
            }
        
        positive_count = sum(1 for s in sentiments if s['sentiment'] == 'positive')
        negative_count = sum(1 for s in sentiments if s['sentiment'] == 'negative')
        neutral_count = sum(1 for s in sentiments if s['sentiment'] == 'neutral')
        
        total = len(sentiments)
        avg_confidence = sum(s['confidence'] for s in sentiments) / total
        
        return {
            'total': total,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_percentage': (positive_count / total) * 100,
            'negative_percentage': (negative_count / total) * 100,
            'neutral_percentage': (neutral_count / total) * 100,
            'average_confidence': avg_confidence,
            'dominant_sentiment': max(['positive', 'negative', 'neutral'], 
                                    key=lambda x: [positive_count, negative_count, neutral_count][['positive', 'negative', 'neutral'].index(x)])
        }

def main():
    """Test the sentiment analyzer"""
    analyzer = SentimentAnalyzer()
    
    # Test texts
    test_texts = [
        "This is amazing news! I'm so happy about the positive developments.",
        "This is terrible and disappointing. I can't believe this happened.",
        "The weather today is cloudy with a chance of rain.",
        "Great breakthrough in medical research could save millions of lives!",
        "Economic crisis continues to worsen with no end in sight."
    ]
    
    print("Testing sentiment analysis:")
    for text in test_texts:
        result = analyzer.analyze_sentiment(text)
        print(f"\nText: {text}")
        print(f"Sentiment: {result['sentiment']} (confidence: {result['confidence']:.2f})")
        if 'method' in result:
            print(f"Method: {result['method']}")
    
    # Test batch analysis
    print("\n" + "="*50)
    print("Testing batch sentiment analysis:")
    batch_results = analyzer.analyze_batch_sentiment(test_texts)
    summary = analyzer.get_sentiment_summary(batch_results)
    print(f"Sentiment Summary: {summary}")

if __name__ == "__main__":
    main()