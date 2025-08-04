
# File: services/aiml-orchestration/src/orchestrators/source_attribution.py
"""
Source Attribution - Add proper source citations
Location: services/aiml-orchestration/src/orchestrators/source_attribution.py
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class SourceAttribution:
    """Adds proper source attribution and citations"""
    
    def __init__(self):
        self.citation_style = 'simple'
        
    async def add_attribution(
        self, 
        content: str, 
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Add source attribution to combined content"""
        try:
            # Extract unique sources
            sources = await self._extract_sources(results)
            
            # Generate citations
            citations = await self._generate_citations(sources)
            
            # Add inline citations to content
            attributed_content = await self._add_inline_citations(content, results)
            
            return {
                'content': attributed_content,
                'sources': sources,
                'citations': citations,
                'attribution_method': self.citation_style
            }
            
        except Exception as e:
            logger.error(f"Source attribution error: {e}")
            return {'content': content, 'sources': [], 'citations': []}
    
    async def _extract_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract unique sources from results"""
        sources = []
        seen_urls = set()
        
        for result in results:
            url = result.get('url', '')
            title = result.get('title', '')
            source_type = result.get('result_source', 'unknown')
            
            if url and url not in seen_urls:
                seen_urls.add(url)
                sources.append({
                    'url': url,
                    'title': title,
                    'type': source_type,
                    'accessed': datetime.utcnow().isoformat()
                })
        
        return sources
    
    async def _generate_citations(self, sources: List[Dict[str, Any]]) -> List[str]:
        """Generate formatted citations"""
        citations = []
        
        for i, source in enumerate(sources, 1):
            if source['type'] == 'local':
                citation = f"[{i}] Internal Knowledge Base"
            else:
                citation = f"[{i}] {source['title']} - {source['url']}"
            
            citations.append(citation)
        
        return citations
    
    async def _add_inline_citations(
        self, 
        content: str, 
        results: List[Dict[str, Any]]
    ) -> str:
        """Add inline citation markers to content"""
        # Simple implementation - add citations at end
        if not results:
            return content
        
        citation_numbers = []
        for i, result in enumerate(results[:3], 1):
            citation_numbers.append(str(i))
        
        if citation_numbers:
            content += f" [{', '.join(citation_numbers)}]"
        
        return content
