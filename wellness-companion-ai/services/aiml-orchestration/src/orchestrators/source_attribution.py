import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class SourceAttribution:
    """Add proper source attribution to combined content"""
    
    async def add_attribution(
        self,
        content: Dict[str, Any],
        merged_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add source attribution to content"""
        try:
            sources = merged_results.get('sources', [])
            
            # Create citation map
            citations = []
            for i, source in enumerate(sources[:5], 1):
                citation = {
                    'id': i,
                    'type': source.get('type', 'unknown'),
                    'title': source.get('title', 'Untitled'),
                    'url': source.get('url', ''),
                    'domain': source.get('domain', ''),
                    'trust_score': source.get('trust_score', 0.5)
                }
                citations.append(citation)
            
            # Add attribution info
            content['citations'] = citations
            content['attribution_summary'] = self._create_attribution_summary(citations)
            content['source_quality'] = self._assess_source_quality(citations)
            
            return content
            
        except Exception as e:
            logger.error(f"Source attribution failed: {str(e)}")
            return content
    
    def _create_attribution_summary(self, citations: List[Dict[str, Any]]) -> str:
        """Create human-readable attribution summary"""
        if not citations:
            return "No sources available"
        
        web_sources = [c for c in citations if c['type'] == 'web']
        local_sources = [c for c in citations if c['type'] == 'local']
        
        summary_parts = []
        
        if web_sources:
            domains = list(set([c['domain'] for c in web_sources if c['domain']]))
            if len(domains) == 1:
                summary_parts.append(f"Source: {domains[0]}")
            elif len(domains) <= 3:
                summary_parts.append(f"Sources: {', '.join(domains)}")
            else:
                summary_parts.append(f"Sources: {len(web_sources)} web sources")
        
        if local_sources:
            summary_parts.append(f"{len(local_sources)} local document(s)")
        
        return " | ".join(summary_parts) if summary_parts else "Multiple sources"
    
    def _assess_source_quality(self, citations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess overall quality of sources"""
        if not citations:
            return {"quality": "unknown", "trust_level": 0.5}
        
        avg_trust = sum(c.get('trust_score', 0.5) for c in citations) / len(citations)
        
        if avg_trust >= 0.8:
            quality = "high"
        elif avg_trust >= 0.6:
            quality = "medium"
        else:
            quality = "low"
        
        return {
            "quality": quality,
            "trust_level": avg_trust,
            "total_sources": len(citations),
            "web_sources": len([c for c in citations if c['type'] == 'web']),
            "local_sources": len([c for c in citations if c['type'] == 'local'])
        }

source_attribution = SourceAttribution()