
# File: services/aiml-orchestration/src/orchestrators/result_merger.py
"""
Result Merger - Merge different result types
Location: services/aiml-orchestration/src/orchestrators/result_merger.py
"""

import logging
from typing import Dict, List, Optional, Any
import hashlib

logger = logging.getLogger(__name__)

class ResultMerger:
    """Merges results from different sources with deduplication"""
    
    def __init__(self):
        self.similarity_threshold = 0.8
        
    async def merge_results(
        self, 
        local_results: List[Dict[str, Any]], 
        web_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge local and web results with deduplication"""
        try:
            all_results = []
            
            # Add local results with source tagging
            for result in local_results:
                result_copy = result.copy()
                result_copy['result_source'] = 'local'
                result_copy['source_priority'] = 1
                all_results.append(result_copy)
            
            # Add web results with source tagging
            for result in web_results:
                result_copy = result.copy()
                result_copy['result_source'] = 'web'
                result_copy['source_priority'] = 2
                all_results.append(result_copy)
            
            # Remove duplicates
            deduplicated = await self._deduplicate_results(all_results)
            
            # Sort by relevance and source priority
            sorted_results = sorted(
                deduplicated, 
                key=lambda x: (x.get('score', 0), -x.get('source_priority', 0)), 
                reverse=True
            )
            
            return sorted_results
            
        except Exception as e:
            logger.error(f"Result merging error: {e}")
            return local_results + web_results
    
    async def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on content similarity"""
        if not results:
            return results
        
        unique_results = []
        content_hashes = set()
        
        for result in results:
            content = result.get('content', '')
            title = result.get('title', '')
            
            # Create content hash
            content_hash = hashlib.md5((content + title).encode()).hexdigest()
            
            if content_hash not in content_hashes:
                content_hashes.add(content_hash)
                unique_results.append(result)
        
        return unique_results