
# File: services/aiml-orchestration/src/orchestrators/enhanced_response_builder.py
"""
Enhanced Response Builder - Build final enhanced response
Location: services/aiml-orchestration/src/orchestrators/enhanced_response_builder.py
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedResponseBuilder:
    """Builds final enhanced response with metadata"""
    
    def __init__(self):
        self.response_format = 'structured'
        
    async def build_response(
        self, 
        attributed_content: Dict[str, Any], 
        results: List[Dict[str, Any]], 
        query: str
    ) -> Dict[str, Any]:
        """Build final enhanced response"""
        try:
            # Calculate response metrics
            metrics = await self._calculate_metrics(results)
            
            # Build response structure
            response = {
                'query': query,
                'content': attributed_content.get('content', ''),
                'sources': attributed_content.get('sources', []),
                'citations': attributed_content.get('citations', []),
                'metadata': {
                    'total_sources': len(results),
                    'local_sources': len([r for r in results if r.get('result_source') == 'local']),
                    'web_sources': len([r for r in results if r.get('result_source') == 'web']),
                    'confidence_score': metrics.get('avg_confidence', 0.0),
                    'response_type': 'hybrid',
                    'generated_at': datetime.utcnow().isoformat()
                },
                'metrics': metrics
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Response building error: {e}")
            return {
                'query': query,
                'content': '',
                'sources': [],
                'error': str(e)
            }
    
    async def _calculate_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate response quality metrics"""
        if not results:
            return {'avg_confidence': 0.0, 'source_diversity': 0.0}
        
        # Average confidence
        scores = [r.get('score', 0.0) for r in results]
        avg_confidence = sum(scores) / len(scores) if scores else 0.0
        
        # Source diversity
        source_types = set(r.get('result_source', 'unknown') for r in results)
        source_diversity = len(source_types) / 2.0  # Normalized to 0-1
        
        # Content quality
        total_content_length = sum(len(r.get('content', '')) for r in results)
        avg_content_length = total_content_length / len(results)
        
        return {
            'avg_confidence': avg_confidence,
            'source_diversity': source_diversity,
            'avg_content_length': avg_content_length,
            'total_results': len(results)
        }
