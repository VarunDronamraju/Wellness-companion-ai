import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ContentCombiner:
    """Intelligently combine content from multiple sources"""
    
    async def combine_content(
        self,
        merged_results: Dict[str, Any],
        query: str
    ) -> Dict[str, Any]:
        """Combine content from all sources"""
        try:
            sources = merged_results.get('sources', [])
            
            if not sources:
                return merged_results
            
            # Extract key information from each source
            key_points = []
            for source in sources[:5]:  # Limit to top 5 sources
                points = self._extract_key_points(source, query)
                key_points.extend(points)
            
            # Combine into coherent content
            combined_content = self._synthesize_key_points(key_points, query)
            
            merged_results['combined_content'] = combined_content
            merged_results['key_points'] = key_points[:10]  # Top 10 points
            
            return merged_results
            
        except Exception as e:
            logger.error(f"Content combination failed: {str(e)}")
            return merged_results
    
    def _extract_key_points(self, source: Dict[str, Any], query: str) -> List[str]:
        """Extract key points from a source"""
        content = source.get('content', '')
        if not content:
            return []
        
        # Simple sentence extraction based on query relevance
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        query_words = query.lower().split()
        
        relevant_sentences = []
        for sentence in sentences:
            if len(sentence) > 20:  # Minimum sentence length
                relevance = sum(1 for word in query_words if word in sentence.lower())
                if relevance > 0:
                    relevant_sentences.append((sentence, relevance))
        
        # Return top 3 most relevant sentences
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        return [sentence for sentence, _ in relevant_sentences[:3]]
    
    def _synthesize_key_points(self, key_points: List[str], query: str) -> str:
        """Synthesize key points into coherent content"""
        if not key_points:
            return "No specific information found for your query."
        
        # Group similar points and create summary
        unique_points = list(dict.fromkeys(key_points))  # Remove duplicates
        
        if len(unique_points) == 1:
            return unique_points[0]
        elif len(unique_points) <= 3:
            return " ".join(unique_points)
        else:
            # Create structured summary
            summary = f"Based on multiple sources: {unique_points[0]}"
            if len(unique_points) > 1:
                summary += f" Additionally, {unique_points[1]}"
            if len(unique_points) > 2:
                summary += f" Furthermore, {unique_points[2]}"
            
            return summary

content_combiner = ContentCombiner()