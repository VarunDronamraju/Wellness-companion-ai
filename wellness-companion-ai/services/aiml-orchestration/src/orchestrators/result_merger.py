import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ResultMerger:
    """Merge results from different search sources"""
    
    async def merge_results(
        self,
        local_results: List[Dict[str, Any]],
        web_results: Dict[str, Any],
        query: str
    ) -> Dict[str, Any]:
        """Merge local and web results with deduplication"""
        try:
            merged = {
                'query': query,
                'sources': [],
                'primary_answer': web_results.get('answer', ''),
                'total_sources': 0,
                'source_breakdown': {'local': 0, 'web': 0}
            }
            
            # Add web sources
            for result in web_results.get('results', []):
                source = {
                    'type': 'web',
                    'title': result.get('title', ''),
                    'content': result.get('content', ''),
                    'url': result.get('url', ''),
                    'score': result.get('score', 0),
                    'domain': result.get('domain', ''),
                    'trust_score': result.get('trust_score', 0.5)
                }
                merged['sources'].append(source)
            
            # Add local sources (when available)
            for result in local_results:
                source = {
                    'type': 'local',
                    'title': result.get('title', 'Local Document'),
                    'content': result.get('content', ''),
                    'score': result.get('score', 0),
                    'document_id': result.get('document_id', ''),
                    'trust_score': 0.9  # Local documents have high trust
                }
                merged['sources'].append(source)
            
            # Remove duplicates and rank
            merged['sources'] = self._deduplicate_and_rank(merged['sources'])
            merged['total_sources'] = len(merged['sources'])
            merged['source_breakdown'] = {
                'local': len([s for s in merged['sources'] if s['type'] == 'local']),
                'web': len([s for s in merged['sources'] if s['type'] == 'web'])
            }
            
            return merged
            
        except Exception as e:
            logger.error(f"Result merging failed: {str(e)}")
            return {'sources': [], 'error': str(e)}
    
    def _deduplicate_and_rank(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates and rank by relevance"""
        # Simple deduplication by URL/title
        seen_urls = set()
        seen_titles = set()
        unique_sources = []
        
        for source in sources:
            url = source.get('url', '')
            title = source.get('title', '').lower()
            
            if url and url in seen_urls:
                continue
            if title and title in seen_titles:
                continue
                
            unique_sources.append(source)
            if url:
                seen_urls.add(url)
            if title:
                seen_titles.add(title)
        
        # Rank by combined score
        def rank_score(source):
            base_score = source.get('score', 0) * 0.6
            trust_score = source.get('trust_score', 0.5) * 0.4
            return base_score + trust_score
        
        return sorted(unique_sources, key=rank_score, reverse=True)

result_merger = ResultMerger()