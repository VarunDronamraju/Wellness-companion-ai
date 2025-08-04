
# File: services/aiml-orchestration/src/orchestrators/content_combiner.py
"""
Content Combiner - Combine content from multiple sources
Location: services/aiml-orchestration/src/orchestrators/content_combiner.py
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class ContentCombiner:
    """Combines content from multiple sources into coherent response"""
    
    def __init__(self):
        self.max_combined_length = 3000
        self.local_weight = 0.6
        self.web_weight = 0.4
        
    async def combine_content(
        self, 
        merged_results: List[Dict[str, Any]], 
        query: str
    ) -> str:
        """Combine content from merged results into coherent text"""
        try:
            if not merged_results:
                return ""
            
            # Separate local and web content
            local_content = []
            web_content = []
            
            for result in merged_results:
                content = result.get('content', '')
                if result.get('result_source') == 'local':
                    local_content.append(content)
                else:
                    web_content.append(content)
            
            # Build combined response
            combined_parts = []
            
            # Start with most relevant local content
            if local_content:
                local_summary = await self._summarize_content(local_content[:3])
                combined_parts.append(local_summary)
            
            # Add web content for additional context
            if web_content:
                web_summary = await self._summarize_content(web_content[:2])
                combined_parts.append(web_summary)
            
            # Join with transitions
            combined_content = await self._join_with_transitions(combined_parts)
            
            # Ensure length limit
            if len(combined_content) > self.max_combined_length:
                combined_content = combined_content[:self.max_combined_length] + "..."
            
            return combined_content
            
        except Exception as e:
            logger.error(f"Content combination error: {e}")
            return ""
    
    async def _summarize_content(self, content_list: List[str]) -> str:
        """Summarize list of content into coherent text"""
        if not content_list:
            return ""
        
        # Simple concatenation with deduplication
        unique_sentences = []
        seen_sentences = set()
        
        for content in content_list:
            sentences = content.split('. ')
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and sentence not in seen_sentences and len(sentence) > 20:
                    seen_sentences.add(sentence)
                    unique_sentences.append(sentence)
        
        return '. '.join(unique_sentences[:5]) + '.'
    
    async def _join_with_transitions(self, parts: List[str]) -> str:
        """Join content parts with smooth transitions"""
        if not parts:
            return ""
        
        if len(parts) == 1:
            return parts[0]
        
        transitions = [
            "Additionally, ",
            "Furthermore, ",
            "Recent information also indicates that ",
            "Moreover, "
        ]
        
        combined = parts[0]
        for i, part in enumerate(parts[1:]):
            if part:
                transition = transitions[i % len(transitions)]
                combined += " " + transition + part
        
        return combined
