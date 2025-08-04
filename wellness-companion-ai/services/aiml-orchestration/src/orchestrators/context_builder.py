"""
Context assembly for RAG pipeline.
Combines search results into coherent context for LLM.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)

@dataclass
class ContextChunk:
    """Individual context chunk with metadata."""
    content: str
    source: str
    relevance_score: float
    chunk_id: str
    document_id: str
    metadata: Dict[str, Any]

@dataclass
class AssembledContext:
    """Assembled context ready for LLM."""
    context_text: str
    total_chunks: int
    total_tokens: int
    relevance_score: float
    sources: List[str]
    chunks: List[ContextChunk]
    metadata: Dict[str, Any]

class ContextBuilder:
    """
    Builds coherent context from search results for LLM consumption.
    """
    
    def __init__(self, max_context_length: int = 4000, max_chunks: int = 10):
        self.max_context_length = max_context_length
        self.max_chunks = max_chunks
        
        self.context_stats = {
            'total_contexts_built': 0,
            'successful_builds': 0,
            'failed_builds': 0,
            'average_build_time': 0.0,
            'total_build_time': 0.0,
            'average_chunks_per_context': 0.0,
            'total_chunks_processed': 0
        }

    async def build_context(
        self, 
        search_results: List[Dict[str, Any]], 
        query: str,
        context_type: str = "comprehensive"
    ) -> AssembledContext:
        """
        Build context from search results.
        
        Args:
            search_results: List of search results with content and scores
            query: Original query for relevance
            context_type: Type of context to build (comprehensive, focused, summary)
            
        Returns:
            AssembledContext ready for LLM
        """
        start_time = datetime.now()
        
        try:
            if not search_results:
                return self._create_empty_context(query)
            
            # Convert search results to context chunks
            context_chunks = self._convert_to_chunks(search_results)
            
            # Filter and rank chunks
            filtered_chunks = self._filter_chunks(context_chunks, query)
            ranked_chunks = self._rank_chunks(filtered_chunks, query)
            
            # Select optimal chunks for context
            selected_chunks = self._select_chunks(ranked_chunks, context_type)
            
            # Assemble final context
            assembled_context = self._assemble_context(selected_chunks, query)
            
            build_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(True, build_time, len(selected_chunks))
            
            logger.info(f"Built context with {len(selected_chunks)} chunks, {assembled_context.total_tokens} tokens")
            
            return assembled_context
            
        except Exception as e:
            build_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(False, build_time, 0)
            logger.error(f"Error building context: {str(e)}")
            
            return self._create_error_context(query, str(e))

    def _convert_to_chunks(self, search_results: List[Dict[str, Any]]) -> List[ContextChunk]:
        """Convert search results to context chunks."""
        chunks = []
        
        for idx, result in enumerate(search_results):
            try:
                chunk = ContextChunk(
                    content=result.get('content', result.get('text', '')),
                    source=result.get('source', f"Document_{idx}"),
                    relevance_score=result.get('score', result.get('relevance_score', 0.0)),
                    chunk_id=result.get('id', f"chunk_{idx}"),
                    document_id=result.get('document_id', f"doc_{idx}"),
                    metadata=result.get('metadata', {})
                )
                
                if chunk.content.strip():  # Only add non-empty chunks
                    chunks.append(chunk)
                    
            except Exception as e:
                logger.warning(f"Failed to convert search result {idx} to chunk: {str(e)}")
                continue
        
        return chunks

    def _filter_chunks(self, chunks: List[ContextChunk], query: str) -> List[ContextChunk]:
        """Filter chunks based on quality and relevance."""
        filtered = []
        
        for chunk in chunks:
            # Filter criteria
            if (len(chunk.content.strip()) < 10 or  # Too short
                chunk.relevance_score < 0.1 or      # Too low relevance
                len(chunk.content) > 2000):         # Too long
                continue
            
            # Check for query relevance
            if self._has_query_relevance(chunk.content, query):
                filtered.append(chunk)
        
        return filtered

    def _has_query_relevance(self, content: str, query: str) -> bool:
        """Check if content has relevance to the query."""
        content_lower = content.lower()
        query_words = query.lower().split()
        
        # Check if at least 30% of query words appear in content
        matches = sum(1 for word in query_words if word in content_lower)
        relevance_ratio = matches / len(query_words) if query_words else 0
        
        return relevance_ratio >= 0.3

    def _rank_chunks(self, chunks: List[ContextChunk], query: str) -> List[ContextChunk]:
        """Rank chunks by combined relevance and quality scores."""
        
        for chunk in chunks:
            # Calculate combined score
            relevance_weight = 0.6
            quality_weight = 0.4
            
            quality_score = self._calculate_quality_score(chunk.content)
            combined_score = (
                chunk.relevance_score * relevance_weight + 
                quality_score * quality_weight
            )
            
            # Update chunk metadata with combined score
            chunk.metadata['combined_score'] = combined_score
            chunk.metadata['quality_score'] = quality_score
        
        # Sort by combined score (descending)
        return sorted(chunks, key=lambda x: x.metadata.get('combined_score', 0), reverse=True)

    def _calculate_quality_score(self, content: str) -> float:
        """Calculate quality score for content."""
        score = 0.5  # Base score
        
        # Length bonus (optimal around 200-800 characters)
        length = len(content)
        if 200 <= length <= 800:
            score += 0.2
        elif 100 <= length < 200 or 800 < length <= 1200:
            score += 0.1
        
        # Sentence structure bonus
        sentences = content.count('.') + content.count('!') + content.count('?')
        if sentences >= 2:
            score += 0.1
        
        # Capitalization bonus (proper formatting)
        if content[0].isupper() if content else False:
            score += 0.05
        
        # Completeness bonus (ends with punctuation)
        if content.strip().endswith(('.', '!', '?')):
            score += 0.05
        
        return min(1.0, score)

    def _select_chunks(self, ranked_chunks: List[ContextChunk], context_type: str) -> List[ContextChunk]:
        """Select optimal chunks based on context type and constraints."""
        if not ranked_chunks:
            return []
        
        selected = []
        current_length = 0
        
        # Context type specific limits
        type_limits = {
            'focused': {'max_chunks': 3, 'max_length': 1500},
            'comprehensive': {'max_chunks': self.max_chunks, 'max_length': self.max_context_length},
            'summary': {'max_chunks': 5, 'max_length': 2000}
        }
        
        limits = type_limits.get(context_type, type_limits['comprehensive'])
        
        for chunk in ranked_chunks:
            chunk_length = len(chunk.content)
            
            # Check if adding this chunk would exceed limits
            if (len(selected) >= limits['max_chunks'] or 
                current_length + chunk_length > limits['max_length']):
                break
            
            selected.append(chunk)
            current_length += chunk_length
        
        return selected

    def _assemble_context(self, chunks: List[ContextChunk], query: str) -> AssembledContext:
        """Assemble final context from selected chunks."""
        if not chunks:
            return self._create_empty_context(query)
        
        # Build context text
        context_parts = []
        sources = set()
        
        for i, chunk in enumerate(chunks):
            # Add chunk with source attribution
            chunk_text = f"[Source {i+1}: {chunk.source}]\n{chunk.content.strip()}\n"
            context_parts.append(chunk_text)
            sources.add(chunk.source)
        
        context_text = "\n".join(context_parts)
        
        # Calculate relevance score (weighted average)
        total_weight = sum(len(chunk.content) for chunk in chunks)
        relevance_score = sum(
            chunk.relevance_score * len(chunk.content) 
            for chunk in chunks
        ) / total_weight if total_weight > 0 else 0.0
        
        # Estimate token count (rough approximation)
        total_tokens = self._estimate_tokens(context_text)
        
        metadata = {
            'build_timestamp': datetime.now().isoformat(),
            'query': query,
            'context_type': 'comprehensive',
            'average_relevance': relevance_score,
            'unique_sources': len(sources),
            'context_length': len(context_text)
        }
        
        return AssembledContext(
            context_text=context_text,
            total_chunks=len(chunks),
            total_tokens=total_tokens,
            relevance_score=relevance_score,
            sources=list(sources),
            chunks=chunks,
            metadata=metadata
        )

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Rough estimate: 1 token ≈ 4 characters for English text
        return max(1, len(text) // 4)

    def _create_empty_context(self, query: str) -> AssembledContext:
        """Create empty context when no results available."""
        return AssembledContext(
            context_text="No relevant context found for the query.",
            total_chunks=0,
            total_tokens=10,
            relevance_score=0.0,
            sources=[],
            chunks=[],
            metadata={
                'build_timestamp': datetime.now().isoformat(),
                'query': query,
                'context_type': 'empty',
                'reason': 'No search results available'
            }
        )

    def _create_error_context(self, query: str, error: str) -> AssembledContext:
        """Create error context when build fails."""
        return AssembledContext(
            context_text=f"Error building context: {error}",
            total_chunks=0,
            total_tokens=15,
            relevance_score=0.0,
            sources=[],
            chunks=[],
            metadata={
                'build_timestamp': datetime.now().isoformat(),
                'query': query,
                'context_type': 'error',
                'error': error
            }
        )

    def _update_stats(self, success: bool, build_time: float, chunks_processed: int):
        """Update build statistics."""
        self.context_stats['total_contexts_built'] += 1
        self.context_stats['total_chunks_processed'] += chunks_processed
        
        if success:
            self.context_stats['successful_builds'] += 1
        else:
            self.context_stats['failed_builds'] += 1
        
        self.context_stats['total_build_time'] += build_time
        self.context_stats['average_build_time'] = (
            self.context_stats['total_build_time'] / 
            self.context_stats['total_contexts_built']
        )
        
        self.context_stats['average_chunks_per_context'] = (
            self.context_stats['total_chunks_processed'] / 
            self.context_stats['total_contexts_built']
        )

    def get_build_statistics(self) -> Dict[str, Any]:
        """Get context building statistics."""
        return {
            **self.context_stats,
            'success_rate': f"{(self.context_stats['successful_builds'] / max(1, self.context_stats['total_contexts_built'])) * 100:.2f}%"
        }

    async def rebuild_context_with_constraints(
        self, 
        context: AssembledContext, 
        max_tokens: int
    ) -> AssembledContext:
        """Rebuild context with different token constraints."""
        if context.total_tokens <= max_tokens:
            return context
        
        # Calculate how many chunks we can fit
        available_chunks = []
        current_tokens = 0
        
        for chunk in context.chunks:
            chunk_tokens = self._estimate_tokens(chunk.content)
            if current_tokens + chunk_tokens <= max_tokens:
                available_chunks.append(chunk)
                current_tokens += chunk_tokens
            else:
                break
        
        # Rebuild with available chunks
        return self._assemble_context(available_chunks, context.metadata.get('query', ''))

    def validate_context_quality(self, context: AssembledContext) -> Dict[str, Any]:
        """Validate the quality of assembled context."""
        validation = {
            'is_valid': True,
            'issues': [],
            'quality_score': 0.0,
            'recommendations': []
        }
        
        # Check basic requirements
        if context.total_chunks == 0:
            validation['is_valid'] = False
            validation['issues'].append('No chunks in context')
        
        if context.total_tokens > self.max_context_length:
            validation['issues'].append(f'Context too long: {context.total_tokens} tokens')
            validation['recommendations'].append('Consider using focused context type')
        
        if context.relevance_score < 0.3:
            validation['issues'].append(f'Low relevance score: {context.relevance_score:.2f}')
            validation['recommendations'].append('Review search parameters or query processing')
        
        # Calculate quality score
        quality_factors = {
            'relevance': min(1.0, context.relevance_score / 0.8),
            'chunk_count': min(1.0, context.total_chunks / 5),
            'source_diversity': min(1.0, len(context.sources) / 3),
            'token_efficiency': min(1.0, context.total_tokens / self.max_context_length)
        }
        
        validation['quality_score'] = sum(quality_factors.values()) / len(quality_factors)
        
        return validation