import logging
from typing import List, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ResultValidator:
    """Validate and filter web search results"""
    
    def __init__(self):
        self.blocked_domains = {
            'pinterest.com', 'instagram.com', 'facebook.com', 'twitter.com',
            'tiktok.com', 'linkedin.com/pulse'
        }
        self.min_content_length = 50
        self.min_score = 0.1
    
    def filter_valid_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out invalid or low-quality results"""
        valid_results = []
        
        for result in results:
            if self._is_valid_result(result):
                valid_results.append(result)
        
        logger.debug(f"Filtered {len(results)} results to {len(valid_results)} valid results")
        return valid_results
    
    def _is_valid_result(self, result: Dict[str, Any]) -> bool:
        """Check if single result is valid"""
        # Check required fields
        if not result.get('url') or not result.get('title'):
            return False
        
        # Check domain blocklist
        domain = result.get('domain', '')
        if domain in self.blocked_domains:
            return False
        
        # Check content quality
        content = result.get('content', '')
        if len(content.strip()) < self.min_content_length:
            return False
        
        # Check relevance score
        score = result.get('score', 0)
        if score < self.min_score:
            return False
        
        # Check URL validity
        if not self._is_valid_url(result['url']):
            return False
        
        return True
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme in ['http', 'https'])
        except:
            return False

result_validator = ResultValidator()