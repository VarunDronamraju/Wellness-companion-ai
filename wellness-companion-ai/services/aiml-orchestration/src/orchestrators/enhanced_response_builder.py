import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedResponseBuilder:
    """Build final enhanced responses with all metadata"""
    
    async def build_response(
        self,
        attributed_content: Dict[str, Any],
        query: str,
        synthesis_type: str = "enhanced"
    ) -> Dict[str, Any]:
        """Build complete enhanced response"""
        try:
            response = {
                "query": query,
                "synthesis_type": synthesis_type,
                "timestamp": datetime.utcnow().isoformat(),
                "answer": attributed_content.get('primary_answer', ''),
                "combined_content": attributed_content.get('combined_content', ''),
                "key_points": attributed_content.get('key_points', []),
                "sources": attributed_content.get('citations', []),
                "attribution": attributed_content.get('attribution_summary', ''),
                "source_quality": attributed_content.get('source_quality', {}),
                "metadata": {
                    "total_sources": len(attributed_content.get('citations', [])),
                    "processing_time": "< 1s",
                    "confidence": self._calculate_overall_confidence(attributed_content),
                    "synthesis_method": synthesis_type
                }
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Response building failed: {str(e)}")
            return await self.build_fallback_response(query, str(e))
    
    async def build_fallback_response(self, query: str, error: str) -> Dict[str, Any]:
        """Build fallback response when synthesis fails"""
        return {
            "query": query,
            "synthesis_type": "fallback",
            "timestamp": datetime.utcnow().isoformat(),
            "answer": "I encountered an issue processing your request. Please try again.",
            "error": error,
            "sources": [],
            "metadata": {
                "total_sources": 0,
                "confidence": 0.1,
                "synthesis_method": "error_fallback"
            }
        }
    
    def _calculate_overall_confidence(self, content: Dict[str, Any]) -> float:
        """Calculate overall confidence in the response"""
        sources = content.get('citations', [])
        if not sources:
            return 0.3
        
        # Base confidence from source quality
        source_quality = content.get('source_quality', {})
        trust_level = source_quality.get('trust_level', 0.5)
        
        # Adjust based on number of sources
        source_count_factor = min(len(sources) / 3.0, 1.0)
        
        # Combined confidence
        confidence = (trust_level * 0.7) + (source_count_factor * 0.3)
        
        return min(confidence, 0.95)  # Cap at 95%

enhanced_response_builder = EnhancedResponseBuilder()