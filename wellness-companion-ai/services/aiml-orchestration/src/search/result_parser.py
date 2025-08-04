import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ResultParser:
    """Parse and structure Tavily API responses"""
    
    def parse_tavily_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse complete Tavily response into structured format"""
        try:
            return {
                'answer': response.get('answer', ''),
                'results': [self._parse_single_result(r) for r in response.get('results', [])],
                'follow_up_questions': response.get('follow_up_questions', []),
                'images': response.get('images', []),
                'response_time': response.get('response_time'),
                'total_results': len(response.get('results', []))
            }
        except Exception as e:
            logger.error(f"Error parsing Tavily response: {str(e)}")
            return {'results': [], 'error': str(e)}
    
    def _parse_single_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse individual search result"""
        return {
            'title': result.get('title', '').strip(),
            'url': result.get('url', ''),
            'content': result.get('content', '').strip(),
            'score': float(result.get('score', 0.0)),
            'published_date': result.get('published_date'),
            'raw_content': result.get('raw_content'),
            'domain': self._extract_domain(result.get('url', ''))
        }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.lower()
        except:
            return ''

result_parser = ResultParser()