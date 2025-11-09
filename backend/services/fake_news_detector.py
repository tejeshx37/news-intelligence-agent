import pickle
import os
import logging
import re
from typing import Dict, List, Optional
import boto3
from botocore.exceptions import ClientError
from utils.config import get_config
from utils.aws_utils import S3Manager

class FakeNewsDetector:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.s3_handler = S3Manager()
        self.logger = logging.getLogger(__name__)
        self.config = get_config()
        self._load_models()
    
    def _load_models(self):
        """Load fake news detection models from local files or S3"""
        try:
            # Try to load from local files first
            model_path = os.path.join(os.path.dirname(__file__), 'fake_news_model.pkl')
            vectorizer_path = os.path.join(os.path.dirname(__file__), 'fake_vectorizer.pkl')
            
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                self.logger.info("Loading fake news models from local files")
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
            else:
                # Try to download from S3
                self.logger.info("Fake news models not found locally, attempting to download from S3")
                self._download_models_from_s3()
            
            if self.model and self.vectorizer:
                self.logger.info("Fake news detection models loaded successfully")
            else:
                self.logger.warning("Fake news models not available, using heuristic approach")
                
        except Exception as e:
            self.logger.error(f"Error loading fake news models: {str(e)}")
            self.model = None
            self.vectorizer = None
    
    def _download_models_from_s3(self):
        """Download fake news models from S3 bucket"""
        try:
            model_key = 'models/fake_news_model.pkl'
            vectorizer_key = 'models/fake_vectorizer.pkl'
            
            # Download to temp directory
            model_path = '/tmp/fake_news_model.pkl'
            vectorizer_path = '/tmp/fake_vectorizer.pkl'
            
            self.s3_handler.download_file(model_key, model_path)
            self.s3_handler.download_file(vectorizer_key, vectorizer_path)
            
            # Load models
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
                
            self.logger.info("Fake news models downloaded and loaded from S3")
            
        except Exception as e:
            self.logger.error(f"Error downloading fake news models from S3: {str(e)}")
            self.model = None
            self.vectorizer = None
    
    def detect_fake_news(self, text: str, title: Optional[str] = None, source: Optional[str] = None) -> Dict:
        """
        Detect if news is fake or real
        
        Args:
            text: News article content
            title: News article title (optional)
            source: News source (optional)
            
        Returns:
            Dictionary with prediction and confidence
        """
        if not text or not isinstance(text, str):
            return {
                'prediction': 'unknown',
                'confidence': 0.0,
                'reasoning': 'Invalid input text',
                'red_flags': []
            }
        
        try:
            if self.model and self.vectorizer:
                # Use trained model
                features = self._extract_features(text, title, source)
                prediction = self.model.predict([features])[0]
                confidence = max(self.model.predict_proba([features])[0])
                
                # Get reasoning based on features
                reasoning = self._get_model_reasoning(features)
                
                return {
                    'prediction': 'fake' if prediction == 1 else 'real',
                    'confidence': float(confidence),
                    'reasoning': reasoning,
                    'method': 'ml_model',
                    'features': features
                }
            else:
                # Use heuristic approach
                return self._heuristic_detection(text, title, source)
                
        except Exception as e:
            self.logger.error(f"Error in fake news detection: {str(e)}")
            return self._heuristic_detection(text, title, source)
    
    def _extract_features(self, text: str, title: Optional[str] = None, source: Optional[str] = None) -> List[float]:
        """Extract features for fake news detection"""
        # Combine title and text if available
        full_text = f"{title} {text}" if title else text
        
        # Text length
        text_length = len(full_text)
        
        # Exclamation marks count
        exclamation_count = full_text.count('!')
        
        # Question marks count
        question_count = full_text.count('?')
        
        # Capital letters ratio
        caps_ratio = sum(1 for c in full_text if c.isupper()) / len(full_text) if full_text else 0
        
        # Word count
        words = full_text.split()
        word_count = len(words)
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        # Repetition patterns
        word_freq = {}
        for word in words:
            word_lower = word.lower()
            word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        
        # Calculate repetition score
        repetition_score = max(word_freq.values()) if word_freq else 0
        
        # Source credibility (simple heuristic)
        source_score = 0.5  # Default neutral
        if source:
            reputable_sources = ['reuters', 'ap', 'associated press', 'bbc', 'cnn', 'npr', 'wsj', 'nytimes']
            suspicious_sources = ['blog', 'rumor', 'conspiracy', 'fake', 'satire']
            
            source_lower = source.lower()
            if any(rep in source_lower for rep in reputable_sources):
                source_score = 0.1  # Likely real
            elif any(sus in source_lower for sus in suspicious_sources):
                source_score = 0.9  # Likely fake
        
        return [
            text_length,
            exclamation_count,
            question_count,
            caps_ratio,
            word_count,
            avg_word_length,
            repetition_score,
            source_score
        ]
    
    def _get_model_reasoning(self, features: List[float]) -> str:
        """Generate reasoning based on model features"""
        reasoning_parts = []
        
        # Text length
        if features[0] < 100:
            reasoning_parts.append("Very short content")
        elif features[0] > 2000:
            reasoning_parts.append("Unusually long content")
        
        # Exclamation marks
        if features[1] > 3:
            reasoning_parts.append("Excessive use of exclamation marks")
        
        # Question marks
        if features[2] > 3:
            reasoning_parts.append("Excessive use of question marks")
        
        # Capital letters
        if features[3] > 0.3:
            reasoning_parts.append("Excessive use of capital letters")
        
        # Repetition
        if features[6] > 10:
            reasoning_parts.append("High word repetition")
        
        # Source
        if features[7] > 0.7:
            reasoning_parts.append("Suspicious source")
        elif features[7] < 0.3:
            reasoning_parts.append("Reputable source")
        
        return "; ".join(reasoning_parts) if reasoning_parts else "Standard content characteristics"
    
    def _heuristic_detection(self, text: str, title: Optional[str] = None, source: Optional[str] = None) -> Dict:
        """
        Heuristic-based fake news detection
        
        Args:
            text: News article content
            title: News article title (optional)
            source: News source (optional)
            
        Returns:
            Dictionary with heuristic analysis
        """
        red_flags = []
        score = 0
        
        # Combine title and text for analysis
        full_text = f"{title} {text}" if title else text
        
        # Check for sensational language
        sensational_words = [
            'shocking', 'unbelievable', 'incredible', 'mind-blowing', 'devastating',
            'outrageous', 'scandalous', 'breaking', 'urgent', 'must-read',
            'you won\'t believe', 'this will blow your mind', 'what happens next',
            'everyone is talking about', 'viral', 'trending'
        ]
        
        sensational_count = sum(1 for word in sensational_words if word in full_text.lower())
        if sensational_count > 2:
            red_flags.append(f"Excessive sensational language ({sensational_count} instances)")
            score += sensational_count * 0.2
        
        # Check for excessive punctuation
        if full_text.count('!') > 5:
            red_flags.append("Excessive exclamation marks")
            score += 0.3
        
        if full_text.count('?') > 5:
            red_flags.append("Excessive question marks")
            score += 0.2
        
        # Check for ALL CAPS text
        caps_ratio = sum(1 for c in full_text if c.isupper()) / len(full_text) if full_text else 0
        if caps_ratio > 0.2:
            red_flags.append("Excessive use of capital letters")
            score += 0.3
        
        # Check for lack of specific details
        if len(text.split()) < 50:
            red_flags.append("Very short content")
            score += 0.2
        
        # Check for source credibility
        if source:
            suspicious_sources = ['blog', 'rumor', 'conspiracy', 'fake', 'satire', 'hoax']
            if any(sus in source.lower() for sus in suspicious_sources):
                red_flags.append("Suspicious source")
                score += 0.5
        
        # Check for clickbait patterns in title
        if title:
            clickbait_patterns = [
                'you won\'t believe', 'what happened next', 'number ', 'reasons why',
                'how to', 'the truth about', 'exposed', 'revealed'
            ]
            
            if any(pattern in title.lower() for pattern in clickbait_patterns):
                red_flags.append("Clickbait-style title")
                score += 0.3
        
        # Determine prediction based on score
        if score > 0.7:
            prediction = 'fake'
            confidence = min(score, 0.9)
        elif score > 0.4:
            prediction = 'suspicious'
            confidence = score
        else:
            prediction = 'real'
            confidence = 1 - score
        
        return {
            'prediction': prediction,
            'confidence': float(confidence),
            'red_flags': red_flags,
            'score': score,
            'method': 'heuristic',
            'reasoning': f"Found {len(red_flags)} potential red flags"
        }
    
    def detect_batch_fake_news(self, articles: List[Dict]) -> List[Dict]:
        """
        Detect fake news for multiple articles
        
        Args:
            articles: List of articles with 'text', 'title', 'source' keys
            
        Returns:
            List of detection results
        """
        results = []
        for article in articles:
            text = article.get('text', '')
            title = article.get('title', '')
            source = article.get('source', '')
            
            result = self.detect_fake_news(text, title, source)
            results.append(result)
        
        return results
    
    def get_detection_summary(self, results: List[Dict]) -> Dict:
        """
        Generate summary statistics from fake news detection results
        
        Args:
            results: List of detection results
            
        Returns:
            Summary statistics
        """
        if not results:
            return {
                'total': 0,
                'fake_count': 0,
                'real_count': 0,
                'suspicious_count': 0,
                'fake_percentage': 0,
                'real_percentage': 0,
                'suspicious_percentage': 0,
                'average_confidence': 0,
                'total_red_flags': 0
            }
        
        fake_count = sum(1 for r in results if r['prediction'] == 'fake')
        real_count = sum(1 for r in results if r['prediction'] == 'real')
        suspicious_count = sum(1 for r in results if r['prediction'] == 'suspicious')
        
        total = len(results)
        avg_confidence = sum(r['confidence'] for r in results) / total
        total_red_flags = sum(len(r.get('red_flags', [])) for r in results)
        
        return {
            'total': total,
            'fake_count': fake_count,
            'real_count': real_count,
            'suspicious_count': suspicious_count,
            'fake_percentage': (fake_count / total) * 100,
            'real_percentage': (real_count / total) * 100,
            'suspicious_percentage': (suspicious_count / total) * 100,
            'average_confidence': avg_confidence,
            'total_red_flags': total_red_flags,
            'avg_red_flags_per_article': total_red_flags / total
        }

def main():
    """Test the fake news detector"""
    detector = FakeNewsDetector()
    
    # Test articles
    test_articles = [
        {
            'title': 'Breaking: Scientists Discover Cure for Cancer!',
            'text': 'Scientists have made an incredible breakthrough that will change medicine forever! This shocking discovery will save millions of lives and you won\'t believe how simple it is!',
            'source': 'medical-breakthrough-blog.com'
        },
        {
            'title': 'Quarterly Economic Report Shows Modest Growth',
            'text': 'The quarterly economic report released today indicates a 2.3% growth in GDP, slightly above analyst expectations. The Federal Reserve noted that inflation remains within target ranges.',
            'source': 'Reuters'
        },
        {
            'title': 'Local Community Garden Opens New Section',
            'text': 'The Riverside Community Garden announced the opening of a new section dedicated to native plants. The expansion was funded by a local grant and will provide educational opportunities.',
            'source': 'City News'
        }
    ]
    
    print("Testing fake news detection:")
    for i, article in enumerate(test_articles, 1):
        result = detector.detect_fake_news(
            article['text'], 
            article['title'], 
            article['source']
        )
        print(f"\nArticle {i}: {article['title']}")
        print(f"Prediction: {result['prediction']} (confidence: {result['confidence']:.2f})")
        print(f"Reasoning: {result['reasoning']}")
        if 'red_flags' in result:
            print(f"Red flags: {result['red_flags']}")
    
    # Test batch detection
    print("\n" + "="*50)
    print("Testing batch fake news detection:")
    batch_results = detector.detect_batch_fake_news(test_articles)
    summary = detector.get_detection_summary(batch_results)
    print(f"Detection Summary: {summary}")

if __name__ == "__main__":
    main()