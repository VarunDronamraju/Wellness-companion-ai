import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MetadataEnricher:
    """Enrich search results with additional metadata"""
    
    async def enrich_results(self, results: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Add metadata to search results"""
        enriched = results.copy()
        
        # Add query metadata
        enriched['query_metadata'] = {
            'original_query': query,
            'processed_at': datetime.utcnow().isoformat(),
            'result_count': len(results.get('results', []))
        }
        
        # Enrich individual results
        for result in enriched.get('results', []):
            await self._enrich_single_result(result, query)
        
        # Add relevance ranking
        enriched['results'] = self._rank_by_relevance(enriched.get('results', []), query)
        
        return enriched
    
    async def _enrich_single_result(self, result: Dict[str, Any], query: str) -> None:
        """Enrich single result with metadata"""
        # Add content type
        result['content_type'] = self._detect_content_type(result)
        
        # Add relevance indicators
        result['relevance_indicators'] = self._calculate_relevance_indicators(result, query)
        
        # Add trustworthiness score
        result['trust_score'] = self._calculate_trust_score(result)
    
    def _detect_content_type(self, result: Dict[str, Any]) -> str:
        """Detect type of content"""
        url = result.get('url', '').lower()
        title = result.get('title', '').lower()
        
        if 'youtube.com' in url or 'video' in title:
            return 'video'
        elif 'wikipedia.org' in url:
            return 'encyclopedia'
        elif any(term in url for term in ['blog', 'medium.com', 'dev.to']):
            return 'blog'
        elif any(term in url for term in ['github.com', 'stackoverflow.com']):
            return 'technical'
        elif 'news' in url or any(term in url for term in ['cnn.com', 'bbc.com', 'reuters.com']):
            return 'news'
        else:
            return 'general'
    
    def _calculate_relevance_indicators(self, result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Calculate relevance indicators"""
        title = result.get('title', '').lower()
        content = result.get('content', '').lower()
        query_lower = query.lower()
        
        query_words = query_lower.split()
        title_matches = sum(1 for word in query_words if word in title)
        content_matches = sum(1 for word in query_words if word in content)
        
        return {
            'title_word_matches': title_matches,
            'content_word_matches': content_matches,
            'total_matches': title_matches + content_matches,
            'match_ratio': (title_matches + content_matches) / len(query_words) if query_words else 0
        }
    
    def _calculate_trust_score(self, result: Dict[str, Any]) -> float:
        """Calculate trustworthiness score"""
        domain = result.get('domain', '')
        
        trusted_domains = {
            'wikipedia.org': 0.9,
            'github.com': 0.85,
            'stackoverflow.com': 0.8,
            'python.org': 0.9,
            'mozilla.org': 0.85,
            'w3schools.com': 0.75
        }
        
        base_score = trusted_domains.get(domain, 0.5)
        
        # Adjust based on content quality
        content_length = len(result.get('content', ''))
        if content_length > 200:
            base_score += 0.1
        elif content_length < 100:
            base_score -= 0.1
        
        return min(1.0, max(0.0, base_score))
    
    def _rank_by_relevance(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Rank results by combined relevance score"""
        def relevance_score(result):
            tavily_score = result.get('score', 0) * 0.4
            trust_score = result.get('trust_score', 0) * 0.3
            match_ratio = result.get('relevance_indicators', {}).get('match_ratio', 0) * 0.3
            return tavily_score + trust_score + match_ratio
        
        return sorted(results, key=relevance_score, reverse=True)

metadata_enricher = MetadataEnricher()