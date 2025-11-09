import requests
import json
import logging
import time
from typing import Dict, List, Optional
from utils.config import get_config

class OpenRouterClient:
    def __init__(self):
        self.config = get_config()
        self.api_key = self.config.get('openrouter_api_key')
        self.base_url = "https://openrouter.ai/api/v1"
        self.logger = logging.getLogger(__name__)
        
        # Available models (using free tier models)
        self.available_models = [
            "google/gemma-2-9b-it:free",
            "meta-llama/llama-3.2-3b-instruct:free",
            "microsoft/phi-3-mini-128k-instruct:free",
            "mistralai/mistral-7b-instruct:free"
        ]
        
        # Default model
        self.default_model = "google/gemma-2-9b-it:free"
    
    def summarize_article(self, article_text: str, title: str = "", max_length: int = 150) -> Dict:
        """
        Summarize a news article using OpenRouter API
        
        Args:
            article_text: Full article text
            title: Article title (optional)
            max_length: Maximum summary length in words
            
        Returns:
            Dictionary with summary and metadata
        """
        if not self.api_key:
            self.logger.warning("OpenRouter API key not configured, using fallback summarization")
            return self._fallback_summarization(article_text, title, max_length)
        
        try:
            # Prepare the prompt
            title_context = f"Title: {title}\n\n" if title else ""
            prompt = f"""Please provide a concise summary of the following news article in no more than {max_length} words. 
Focus on the key facts, main points, and important details.

{title_context}Article:
{article_text}

Summary:"""

            # Make API request
            response = self._make_api_request(prompt, max_tokens=max_length * 2)
            
            if response.get('success'):
                summary = response.get('content', '').strip()
                
                # Clean up the summary
                summary = self._clean_summary(summary)
                
                return {
                    'summary': summary,
                    'original_length': len(article_text.split()),
                    'summary_length': len(summary.split()),
                    'compression_ratio': len(summary.split()) / len(article_text.split()),
                    'model_used': response.get('model', self.default_model),
                    'method': 'openrouter_api',
                    'success': True
                }
            else:
                # Fallback if API fails
                return self._fallback_summarization(article_text, title, max_length)
                
        except Exception as e:
            self.logger.error(f"Error in OpenRouter summarization: {str(e)}")
            return self._fallback_summarization(article_text, title, max_length)
    
    def analyze_news_content(self, article_text: str, title: str = "") -> Dict:
        """
        Analyze news content for key insights, entities, and sentiment
        
        Args:
            article_text: Full article text
            title: Article title (optional)
            
        Returns:
            Dictionary with analysis results
        """
        if not self.api_key:
            self.logger.warning("OpenRouter API key not configured, using fallback analysis")
            return self._fallback_analysis(article_text, title)
        
        try:
            title_context = f"Title: {title}\n\n" if title else ""
            prompt = f"""Analyze the following news article and provide:
1. Key entities (people, organizations, locations)
2. Main topics/themes
3. Key facts
4. Potential bias indicators
5. Overall sentiment

{title_context}Article:
{article_text}

Analysis (provide in JSON format):
{{
    "entities": ["entity1", "entity2", ...],
    "topics": ["topic1", "topic2", ...],
    "key_facts": ["fact1", "fact2", ...],
    "bias_indicators": ["indicator1", "indicator2", ...],
    "sentiment": "positive/negative/neutral",
    "confidence": 0.0-1.0
}}"""

            response = self._make_api_request(prompt, max_tokens=500)
            
            if response.get('success'):
                content = response.get('content', '').strip()
                
                # Try to parse JSON response
                try:
                    analysis = json.loads(content)
                    return {
                        'analysis': analysis,
                        'model_used': response.get('model', self.default_model),
                        'method': 'openrouter_api',
                        'success': True
                    }
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    return self._fallback_analysis(article_text, title)
            else:
                return self._fallback_analysis(article_text, title)
                
        except Exception as e:
            self.logger.error(f"Error in OpenRouter analysis: {str(e)}")
            return self._fallback_analysis(article_text, title)
    
    def _make_api_request(self, prompt: str, max_tokens: int = 200, temperature: float = 0.3) -> Dict:
        """Make API request to OpenRouter"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://your-app-domain.com',  # Replace with your domain
            'X-Title': 'News Intelligence Agent'
        }
        
        data = {
            'model': self.default_model,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': max_tokens,
            'temperature': temperature
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                model_used = result.get('model', self.default_model)
                
                return {
                    'success': True,
                    'content': content,
                    'model': model_used,
                    'usage': result.get('usage', {})
                }
            else:
                self.logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return {'success': False, 'error': f'API error: {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {str(e)}")
            return {'success': False, 'error': f'Request error: {str(e)}'}
    
    def _fallback_summarization(self, text: str, title: str = "", max_length: int = 150) -> Dict:
        """Fallback summarization using simple text processing"""
        try:
            # Split into sentences
            sentences = text.split('.')
            
            # Take first few sentences and last sentence
            if len(sentences) > 3:
                summary_sentences = sentences[:2] + [sentences[-1]]
            else:
                summary_sentences = sentences
            
            summary = '. '.join(s.strip() for s in summary_sentences if s.strip())
            
            # Truncate if too long
            words = summary.split()
            if len(words) > max_length:
                summary = ' '.join(words[:max_length]) + '...'
            
            return {
                'summary': summary,
                'original_length': len(text.split()),
                'summary_length': len(summary.split()),
                'compression_ratio': len(summary.split()) / len(text.split()),
                'model_used': 'fallback',
                'method': 'fallback_summarization',
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Fallback summarization error: {str(e)}")
            return {
                'summary': text[:max_length * 5] + '...' if len(text) > max_length * 5 else text,
                'original_length': len(text.split()),
                'summary_length': len(text.split()),
                'compression_ratio': 1.0,
                'model_used': 'error_fallback',
                'method': 'error_fallback',
                'success': False,
                'error': str(e)
            }
    
    def _fallback_analysis(self, text: str, title: str = "") -> Dict:
        """Fallback content analysis using simple heuristics"""
        try:
            # Simple entity extraction (look for capitalized words)
            words = text.split()
            entities = []
            current_entity = []
            
            for word in words:
                if word.istitle() and len(word) > 2:
                    current_entity.append(word)
                else:
                    if len(current_entity) > 1:
                        entities.append(' '.join(current_entity))
                    current_entity = []
            
            if len(current_entity) > 1:
                entities.append(' '.join(current_entity))
            
            # Remove duplicates and limit to top 5
            entities = list(set(entities))[:5]
            
            # Simple sentiment analysis
            positive_words = ['good', 'great', 'excellent', 'positive', 'success', 'improve', 'benefit']
            negative_words = ['bad', 'terrible', 'negative', 'fail', 'problem', 'crisis', 'disaster']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                sentiment = 'positive'
            elif negative_count > positive_count:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # Simple topic extraction (look for common nouns)
            topics = ['news', 'politics', 'economy', 'technology', 'health', 'environment']
            found_topics = [topic for topic in topics if topic in text_lower]
            
            if not found_topics:
                found_topics = ['general news']
            
            return {
                'analysis': {
                    'entities': entities,
                    'topics': found_topics,
                    'key_facts': [f"Article contains {len(words)} words", f"Sentiment appears {sentiment}"],
                    'bias_indicators': ['Manual review recommended'],
                    'sentiment': sentiment,
                    'confidence': 0.5
                },
                'model_used': 'fallback',
                'method': 'fallback_analysis',
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Fallback analysis error: {str(e)}")
            return {
                'analysis': {
                    'entities': [],
                    'topics': ['unknown'],
                    'key_facts': ['Analysis failed'],
                    'bias_indicators': ['Analysis failed'],
                    'sentiment': 'neutral',
                    'confidence': 0.0
                },
                'model_used': 'error_fallback',
                'method': 'error_fallback',
                'success': False,
                'error': str(e)
            }
    
    def _clean_summary(self, summary: str) -> str:
        """Clean up the generated summary"""
        # Remove common prefixes
        prefixes_to_remove = [
            'summary:', 'summary :', 'here is a summary:', 
            'here\'s a summary:', 'the summary is:'
        ]
        
        summary_lower = summary.lower().strip()
        for prefix in prefixes_to_remove:
            if summary_lower.startswith(prefix):
                summary = summary[len(prefix):].strip()
                break
        
        # Remove extra whitespace
        summary = ' '.join(summary.split())
        
        return summary.strip()

def main():
    """Test the OpenRouter client"""
    client = OpenRouterClient()
    
    test_article = """
    Scientists at MIT have announced a breakthrough in quantum computing that could revolutionize 
    the field. The new technique allows for more stable quantum states, potentially solving 
    one of the biggest challenges in quantum computing. The research, published in Nature, 
    demonstrates a 99.9% success rate in maintaining quantum coherence for extended periods.
    """
    
    print("Testing article summarization:")
    summary_result = client.summarize_article(test_article, "Quantum Computing Breakthrough")
    print(f"Summary: {summary_result['summary']}")
    print(f"Original length: {summary_result['original_length']} words")
    print(f"Summary length: {summary_result['summary_length']} words")
    print(f"Method: {summary_result['method']}")
    
    print("\n" + "="*50)
    print("Testing content analysis:")
    analysis_result = client.analyze_news_content(test_article, "Quantum Computing Breakthrough")
    print(f"Analysis: {json.dumps(analysis_result['analysis'], indent=2)}")
    print(f"Method: {analysis_result['method']}")

if __name__ == "__main__":
    main()