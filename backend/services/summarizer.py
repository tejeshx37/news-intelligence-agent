import logging
from typing import Dict, List, Optional
from .openrouter_client import OpenRouterClient

class NewsSummarizer:
    def __init__(self):
        self.openrouter_client = OpenRouterClient()
        self.logger = logging.getLogger(__name__)
    
    def summarize_article(self, article_text: str, title: str = "", max_length: int = 150, 
                         style: str = 'concise') -> Dict:
        """
        Summarize a news article with different style options
        
        Args:
            article_text: Full article text
            title: Article title (optional)
            max_length: Maximum summary length in words
            style: Summary style ('concise', 'detailed', 'bullet-points')
            
        Returns:
            Dictionary with summary and metadata
        """
        if not article_text or not isinstance(article_text, str):
            return {
                'summary': 'Invalid article text provided',
                'error': 'Invalid input',
                'success': False
            }
        
        try:
            # Adjust max_length based on style
            if style == 'detailed':
                max_length = min(max_length * 2, 300)
            elif style == 'bullet-points':
                max_length = min(max_length, 100)
            
            # Get summary from OpenRouter client
            result = self.openrouter_client.summarize_article(article_text, title, max_length)
            
            # Post-process based on style
            if style == 'bullet-points':
                result['summary'] = self._convert_to_bullet_points(result['summary'])
            elif style == 'detailed':
                result['summary'] = self._enhance_detailed_summary(result['summary'])
            
            # Add style information
            result['style'] = style
            result['requested_length'] = max_length
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in article summarization: {str(e)}")
            return {
                'summary': 'Error generating summary',
                'error': str(e),
                'success': False
            }
    
    def summarize_batch_articles(self, articles: List[Dict], max_length: int = 150) -> List[Dict]:
        """
        Summarize multiple articles
        
        Args:
            articles: List of articles with 'text' and optionally 'title'
            max_length: Maximum summary length in words
            
        Returns:
            List of summary results
        """
        results = []
        
        for i, article in enumerate(articles):
            try:
                text = article.get('text', '')
                title = article.get('title', '')
                
                result = self.summarize_article(text, title, max_length)
                result['article_index'] = i
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error summarizing article {i}: {str(e)}")
                results.append({
                    'summary': 'Error generating summary',
                    'error': str(e),
                    'success': False,
                    'article_index': i
                })
        
        return results
    
    def generate_news_digest(self, articles: List[Dict], max_total_length: int = 500) -> Dict:
        """
        Generate a digest/summary of multiple news articles
        
        Args:
            articles: List of articles with 'text', 'title', and optionally 'source'
            max_total_length: Maximum total length of the digest
            
        Returns:
            Dictionary with digest and metadata
        """
        if not articles:
            return {
                'digest': 'No articles provided',
                'article_count': 0,
                'success': False
            }
        
        try:
            # Summarize each article individually
            summaries = []
            total_length = 0
            
            for article in articles:
                # Calculate appropriate length for this article
                article_length = len(article.get('text', '').split())
                target_length = max(30, min(100, article_length // 10))
                
                summary_result = self.summarize_article(
                    article.get('text', ''),
                    article.get('title', ''),
                    target_length,
                    style='concise'
                )
                
                if summary_result['success']:
                    summary_text = summary_result['summary']
                    summaries.append({
                        'title': article.get('title', 'Untitled'),
                        'source': article.get('source', 'Unknown'),
                        'summary': summary_text,
                        'length': len(summary_text.split())
                    })
                    total_length += len(summary_text.split())
            
            # If total length exceeds limit, adjust
            if total_length > max_total_length:
                # Reduce individual summaries proportionally
                target_ratio = max_total_length / total_length
                adjusted_summaries = []
                
                for summary in summaries:
                    target_words = max(20, int(summary['length'] * target_ratio))
                    
                    # Truncate if necessary
                    words = summary['summary'].split()
                    if len(words) > target_words:
                        truncated = ' '.join(words[:target_words]) + '...'
                        summary['summary'] = truncated
                        summary['length'] = target_words
                    
                    adjusted_summaries.append(summary)
                
                summaries = adjusted_summaries
            
            # Format the digest
            digest_parts = []
            for summary in summaries:
                source_info = f" ({summary['source']})" if summary['source'] != 'Unknown' else ""
                digest_parts.append(f"**{summary['title']}{source_info}**: {summary['summary']}")
            
            digest = "\n\n".join(digest_parts)
            
            return {
                'digest': digest,
                'article_count': len(summaries),
                'total_words': sum(s['length'] for s in summaries),
                'summaries': summaries,
                'success': True
            }
            
        except Exception as e:
            self.logger.error(f"Error generating news digest: {str(e)}")
            return {
                'digest': 'Error generating digest',
                'article_count': 0,
                'error': str(e),
                'success': False
            }
    
    def extract_key_points(self, article_text: str, title: str = "", num_points: int = 5) -> Dict:
        """
        Extract key points from an article
        
        Args:
            article_text: Full article text
            title: Article title (optional)
            num_points: Number of key points to extract
            
        Returns:
            Dictionary with key points
        """
        try:
            # Create a prompt for key point extraction
            title_context = f"Title: {title}\n\n" if title else ""
            prompt = f"""Extract the {num_points} most important key points from this news article. 
Each point should be concise (1-2 sentences) and capture essential information.

{title_context}Article:
{article_text}

Key Points:"""

            # Use OpenRouter client for analysis
            analysis_result = self.openrouter_client.analyze_news_content(article_text, title)
            
            if analysis_result['success']:
                # Extract key facts from analysis
                key_facts = analysis_result['analysis'].get('key_facts', [])
                
                # If we have key facts, use them
                if key_facts:
                    key_points = key_facts[:num_points]
                else:
                    # Fallback to summary-based extraction
                    summary_result = self.summarize_article(article_text, title, 100)
                    if summary_result['success']:
                        # Split summary into sentences as key points
                        sentences = summary_result['summary'].split('.')
                        key_points = [s.strip() for s in sentences if s.strip()][:num_points]
                    else:
                        key_points = ['Unable to extract key points']
                
                return {
                    'key_points': key_points,
                    'article_length': len(article_text.split()),
                    'points_extracted': len(key_points),
                    'analysis_method': analysis_result['method'],
                    'success': True
                }
            else:
                # Fallback to summary-based extraction
                summary_result = self.summarize_article(article_text, title, 100)
                if summary_result['success']:
                    sentences = summary_result['summary'].split('.')
                    key_points = [s.strip() for s in sentences if s.strip()][:num_points]
                else:
                    key_points = ['Unable to extract key points']
                
                return {
                    'key_points': key_points,
                    'article_length': len(article_text.split()),
                    'points_extracted': len(key_points),
                    'analysis_method': 'summary_fallback',
                    'success': True
                }
                
        except Exception as e:
            self.logger.error(f"Error extracting key points: {str(e)}")
            return {
                'key_points': ['Error extracting key points'],
                'error': str(e),
                'success': False
            }
    
    def _convert_to_bullet_points(self, text: str) -> str:
        """Convert text to bullet point format"""
        sentences = text.split('.')
        bullet_points = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                bullet_points.append(f"• {sentence}")
        
        return "\n".join(bullet_points)
    
    def _enhance_detailed_summary(self, text: str) -> str:
        """Enhance summary for detailed style"""
        # Add some context or elaboration if possible
        if len(text.split()) < 50:
            return f"Detailed analysis: {text} This development represents a significant development in the ongoing story."
        return text
    
    def get_summary_statistics(self, summaries: List[Dict]) -> Dict:
        """
        Generate statistics from a list of summaries
        
        Args:
            summaries: List of summary results
            
        Returns:
            Statistics dictionary
        """
        if not summaries:
            return {
                'total_summaries': 0,
                'successful_summaries': 0,
                'average_original_length': 0,
                'average_summary_length': 0,
                'average_compression_ratio': 0,
                'methods_used': {}
            }
        
        successful = [s for s in summaries if s.get('success', False)]
        
        if not successful:
            return {
                'total_summaries': len(summaries),
                'successful_summaries': 0,
                'average_original_length': 0,
                'average_summary_length': 0,
                'average_compression_ratio': 0,
                'methods_used': {}
            }
        
        # Calculate statistics
        avg_original = sum(s.get('original_length', 0) for s in successful) / len(successful)
        avg_summary = sum(s.get('summary_length', 0) for s in successful) / len(successful)
        avg_compression = sum(s.get('compression_ratio', 0) for s in successful) / len(successful)
        
        # Count methods used
        methods = {}
        for summary in successful:
            method = summary.get('method', 'unknown')
            methods[method] = methods.get(method, 0) + 1
        
        return {
            'total_summaries': len(summaries),
            'successful_summaries': len(successful),
            'success_rate': len(successful) / len(summaries),
            'average_original_length': avg_original,
            'average_summary_length': avg_summary,
            'average_compression_ratio': avg_compression,
            'methods_used': methods
        }

def main():
    """Test the news summarizer"""
    summarizer = NewsSummarizer()
    
    test_article = """
    Scientists at the Massachusetts Institute of Technology have announced a major breakthrough 
    in quantum computing research. The team, led by Dr. Sarah Chen, has successfully demonstrated 
    a new technique for maintaining quantum coherence that could revolutionize the field.
    
    The research, published in the journal Nature, shows a 99.9% success rate in maintaining 
    stable quantum states for extended periods. This addresses one of the biggest challenges in 
    quantum computing, where quantum bits (qubits) are notoriously fragile and prone to errors.
    
    "This development could accelerate the practical applications of quantum computing by decades," 
    said Dr. Chen. "We're now much closer to building quantum computers that can solve real-world 
    problems that are currently impossible for classical computers."
    
    The breakthrough involves a new error correction method that uses machine learning algorithms 
    to predict and correct quantum state errors before they affect computations. The technique 
    has been tested on a 50-qubit system and shows promising results.
    
    Industry experts are calling this the most significant quantum computing advancement in years, 
    with potential applications in drug discovery, financial modeling, and cryptography.
    """
    
    print("Testing article summarization:")
    result = summarizer.summarize_article(test_article, "Quantum Computing Breakthrough", style='concise')
    print(f"Summary: {result['summary']}")
    print(f"Original length: {result['original_length']} words")
    print(f"Summary length: {result['summary_length']} words")
    print(f"Method: {result['method']}")
    
    print("\n" + "="*50)
    print("Testing key points extraction:")
    key_points = summarizer.extract_key_points(test_article, "Quantum Computing Breakthrough", num_points=3)
    for i, point in enumerate(key_points['key_points'], 1):
        print(f"{i}. {point}")
    
    print("\n" + "="*50)
    print("Testing bullet point summary:")
    bullet_result = summarizer.summarize_article(test_article, style='bullet-points')
    print(bullet_result['summary'])

if __name__ == "__main__":
    main()