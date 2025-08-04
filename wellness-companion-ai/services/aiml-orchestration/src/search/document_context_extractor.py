"""Specialized context extractor for document-based content."""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents a document chunk with enhanced metadata."""
    content: str
    document_id: str
    chunk_id: str
    page_number: Optional[int]
    section_title: Optional[str]
    chunk_index: int
    score: float
    metadata: Dict[str, Any]


class DocumentContextExtractor:
    """Specialized extractor for processing document-based context."""
    
    def __init__(self, 
                 max_chunks_per_document: int = 3,
                 prefer_titled_sections: bool = True,
                 boost_recent_documents: bool = True):
        """
        Initialize document context extractor.
        
        Args:
            max_chunks_per_document: Maximum chunks to include per document
            prefer_titled_sections: Prefer chunks with section titles
            boost_recent_documents: Give higher scores to recently accessed documents
        """
        self.max_chunks_per_document = max_chunks_per_document
        self.prefer_titled_sections = prefer_titled_sections
        self.boost_recent_documents = boost_recent_documents
        
        logger.info("DocumentContextExtractor initialized")
    
    def extract_document_context(self, 
                                vector_results: List[Dict[str, Any]], 
                                query: str) -> List[DocumentChunk]:
        """
        Extract and process document-specific context.
        
        Args:
            vector_results: Results from vector search
            query: User query for relevance scoring
            
        Returns:
            List of processed document chunks
        """
        try:
            # Group results by document
            document_groups = self._group_by_document(vector_results)
            
            processed_chunks = []
            
            for doc_id, chunks in document_groups.items():
                # Process chunks for this document
                doc_chunks = self._process_document_chunks(doc_id, chunks, query)
                
                # Select best chunks from this document
                selected_chunks = self._select_best_chunks(doc_chunks)
                
                processed_chunks.extend(selected_chunks)
            
            # Sort all chunks by score
            processed_chunks.sort(key=lambda x: x.score, reverse=True)
            
            logger.info(f"Extracted {len(processed_chunks)} document chunks from {len(document_groups)} documents")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Error extracting document context: {e}")
            return []
    
    def _group_by_document(self, results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group vector search results by document ID."""
        groups = {}
        
        for result in results:
            doc_id = result.get('document_id', result.get('source', 'unknown'))
            
            if doc_id not in groups:
                groups[doc_id] = []
            
            groups[doc_id].append(result)
        
        return groups
    
    def _process_document_chunks(self, 
                               doc_id: str, 
                               chunks: List[Dict[str, Any]], 
                               query: str) -> List[DocumentChunk]:
        """Process all chunks from a single document."""
        processed = []
        
        for chunk_data in chunks:
            try:
                chunk = self._create_document_chunk(doc_id, chunk_data)
                
                # Enhance chunk with additional scoring
                chunk = self._enhance_chunk_scoring(chunk, query)
                
                processed.append(chunk)
                
            except Exception as e:
                logger.warning(f"Error processing chunk from {doc_id}: {e}")
                continue
        
        return processed
    
    def _create_document_chunk(self, doc_id: str, chunk_data: Dict[str, Any]) -> DocumentChunk:
        """Create a DocumentChunk from raw chunk data."""
        content = chunk_data.get('content', chunk_data.get('text', ''))
        chunk_id = chunk_data.get('chunk_id', chunk_data.get('id', ''))
        score = float(chunk_data.get('score', chunk_data.get('similarity', 0.0)))
        metadata = chunk_data.get('metadata', {})
        
        # Extract additional metadata
        page_number = metadata.get('page_number')
        section_title = metadata.get('section_title', metadata.get('heading'))
        chunk_index = metadata.get('chunk_index', 0)
        
        # Try to extract page number from content if not in metadata
        if page_number is None:
            page_match = re.search(r'Page (\d+)', content, re.IGNORECASE)
            if page_match:
                page_number = int(page_match.group(1))
        
        # Try to extract section title from content
        if section_title is None:
            section_title = self._extract_section_title(content)
        
        return DocumentChunk(
            content=content,
            document_id=doc_id,
            chunk_id=chunk_id,
            page_number=page_number,
            section_title=section_title,
            chunk_index=chunk_index,
            score=score,
            metadata=metadata
        )
    
    def _extract_section_title(self, content: str) -> Optional[str]:
        """Extract section title from content if present."""
        lines = content.split('\n')
        
        for line in lines[:3]:  # Check first few lines
            line = line.strip()
            
            # Look for common heading patterns
            if re.match(r'^#+\s+', line):  # Markdown headers
                return re.sub(r'^#+\s+', '', line)
            
            if re.match(r'^\d+\.?\s+[A-Z]', line):  # Numbered sections
                return line
            
            if line.isupper() and len(line) < 100:  # All caps titles
                return line
            
            if re.match(r'^[A-Z][^.!?]*$', line) and len(line) < 100:  # Title case
                return line
        
        return None
    
    def _enhance_chunk_scoring(self, chunk: DocumentChunk, query: str) -> DocumentChunk:
        """Enhance chunk scoring based on document-specific factors."""
        enhanced_score = chunk.score
        
        # Boost chunks with section titles
        if self.prefer_titled_sections and chunk.section_title:
            title_relevance = self._calculate_title_relevance(chunk.section_title, query)
            enhanced_score += title_relevance * 0.2
            logger.debug(f"Title boost: {title_relevance:.3f} for '{chunk.section_title}'")
        
        # Boost chunks from beginning of document (often contain key info)
        if chunk.chunk_index < 3:
            position_boost = (3 - chunk.chunk_index) * 0.05
            enhanced_score += position_boost
        
        # Boost recent documents (if timestamp available)
        if self.boost_recent_documents:
            recent_boost = self._calculate_recency_boost(chunk.metadata)
            enhanced_score += recent_boost
        
        # Penalize very short chunks
        word_count = len(chunk.content.split())
        if word_count < 20:
            enhanced_score *= 0.8
        elif word_count < 10:
            enhanced_score *= 0.6
        
        chunk.score = enhanced_score
        return chunk
    
    def _calculate_title_relevance(self, title: str, query: str) -> float:
        """Calculate how relevant a section title is to the query."""
        if not title or not query:
            return 0.0
        
        title_words = set(title.lower().split())
        query_words = set(query.lower().split())
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        title_words -= stop_words
        query_words -= stop_words
        
        if not title_words or not query_words:
            return 0.0
        
        intersection = title_words.intersection(query_words)
        union = title_words.union(query_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_recency_boost(self, metadata: Dict[str, Any]) -> float:
        """Calculate boost based on document recency."""
        # This would typically use document access time or creation time
        # For now, return a small default boost
        access_count = metadata.get('access_count', 1)
        
        # Boost frequently accessed documents slightly
        if access_count > 5:
            return 0.1
        elif access_count > 2:
            return 0.05
        
        return 0.0
    
    def _select_best_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Select the best chunks from a document."""
        if not chunks:
            return []
        
        # Sort by score
        sorted_chunks = sorted(chunks, key=lambda x: x.score, reverse=True)
        
        # Take top chunks up to the limit
        selected = sorted_chunks[:self.max_chunks_per_document]
        
        # Ensure we have good coverage across the document
        if len(chunks) > self.max_chunks_per_document:
            selected = self._ensure_document_coverage(chunks, selected)
        
        return selected
    
    def _ensure_document_coverage(self, 
                                all_chunks: List[DocumentChunk], 
                                selected: List[DocumentChunk]) -> List[DocumentChunk]:
        """Ensure selected chunks provide good coverage across the document."""
        if len(selected) < 2:
            return selected
        
        # Check if selected chunks are too clustered
        selected_indices = [chunk.chunk_index for chunk in selected]
        selected_indices.sort()
        
        # If chunks are very close together, try to add some diversity
        max_gap = max(selected_indices) - min(selected_indices)
        if max_gap < 3 and len(all_chunks) > 5:
            # Find a chunk from a different part of the document
            all_sorted = sorted(all_chunks, key=lambda x: x.score, reverse=True)
            
            for chunk in all_sorted:
                if chunk not in selected:
                    # Check if this chunk is far from selected ones
                    min_distance = min(abs(chunk.chunk_index - idx) for idx in selected_indices)
                    if min_distance > 2:
                        # Replace the lowest scoring selected chunk if this one is reasonable
                        if chunk.score > selected[-1].score * 0.8:
                            selected[-1] = chunk
                        break
        
        return selected
    
    def format_document_chunks(self, chunks: List[DocumentChunk]) -> str:
        """Format document chunks for LLM consumption."""
        if not chunks:
            return "No document context available."
        
        formatted_chunks = []
        current_doc = None
        
        for chunk in chunks:
            # Add document header if this is a new document
            if chunk.document_id != current_doc:
                current_doc = chunk.document_id
                doc_name = chunk.metadata.get('document_name', chunk.document_id)
                formatted_chunks.append(f"\n--- Document: {doc_name} ---")
            
            # Format chunk with metadata
            chunk_header = f"[Chunk {chunk.chunk_index}"
            if chunk.page_number:
                chunk_header += f", Page {chunk.page_number}"
            if chunk.section_title:
                chunk_header += f", Section: {chunk.section_title}"
            chunk_header += f", Score: {chunk.score:.3f}]"
            
            formatted_chunk = f"{chunk_header}\n{chunk.content}\n"
            formatted_chunks.append(formatted_chunk)
        
        return "\n".join(formatted_chunks)
    
    def get_document_summary(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """Get summary statistics about the extracted document context."""
        if not chunks:
            return {"total_chunks": 0, "documents": 0, "avg_score": 0.0}
        
        documents = set(chunk.document_id for chunk in chunks)
        avg_score = sum(chunk.score for chunk in chunks) / len(chunks)
        
        # Group by document for detailed stats
        doc_stats = {}
        for chunk in chunks:
            doc_id = chunk.document_id
            if doc_id not in doc_stats:
                doc_stats[doc_id] = {
                    "chunk_count": 0,
                    "avg_score": 0.0,
                    "page_range": set(),
                    "sections": set()
                }
            
            stats = doc_stats[doc_id]
            stats["chunk_count"] += 1
            
            if chunk.page_number:
                stats["page_range"].add(chunk.page_number)
            
            if chunk.section_title:
                stats["sections"].add(chunk.section_title)
        
        # Calculate average scores per document
        for doc_id, stats in doc_stats.items():
            doc_chunks = [c for c in chunks if c.document_id == doc_id]
            stats["avg_score"] = sum(c.score for c in doc_chunks) / len(doc_chunks)
            stats["page_range"] = sorted(list(stats["page_range"]))
            stats["sections"] = list(stats["sections"])
        
        return {
            "total_chunks": len(chunks),
            "documents": len(documents),
            "avg_score": avg_score,
            "document_details": doc_stats
        }