"""
Content Extractor - Extract and clean relevant content from web search results
Location: services/aiml-orchestration/src/search/content_extractor.py

This module handles content extraction, cleaning, and chunking from web search results.
It processes HTML content, removes noise, and prepares clean text for RAG integration.
"""

import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import html

logger = logging.getLogger(__name__)

class ContentExtractor:
    """
    Content extractor for web search results
    
    Extracts, cleans, and chunks content from web search results
    to prepare it for RAG integration with vector search.
    """
    
    def __init__(self):
        """Initialize content extractor with configuration"""
        self.min_content_length = 100
        self.max_content_length = 5000
        self.chunk_size = 512
        self.chunk_overlap = 50
        
        # Patterns to remove from content
        self.noise_patterns = [
            r'Skip to (?:main )?content',
            r'Jump to (?:main )?content',
            r'Cookie (?:policy|notice|consent)',
            r'Privacy (?:policy|notice)',
            r'Terms (?:of service|and conditions)',
            r'Subscribe to (?:our )?newsletter',
            r'Follow us on (?:social media|Twitter|Facebook)',
            r'Advertisement',
            r'Sponsored content',
            r'Related articles?',
            r'More from (?:this|our) (?:author|site)',
            r'Share this (?:article|story|post)',
            r'Comments? \(\d+\)',
        ]
        
        logger.info("ContentExtractor initialized")
    
    async def extract_relevant_content(
        self, 
        parsed_result: Dict[str, Any],
        query: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract relevant content from a parsed search result
        
        Args:
            parsed_result: Parsed result from ResultParser
            query: Original search query for relevance filtering
            
        Returns:
            Dictionary with extracted and cleaned content
        """
        try:
            logger.debug(f"Extracting content for result: {parsed_result.get('title', 'Unknown')[:50]}...")
            
            # Get raw content
            raw_content = parsed_result.get('content', '')
            if not raw_content:
                logger.warning("No content found in result")
                return None
            
            # Clean the content
            cleaned_content = await self._clean_content(raw_content)
            if not cleaned_content:
                logger.warning("No content remaining after cleaning")
                return None
            
            # Check content length requirements
            if len(cleaned_content) < self.min_content_length:
                logger.debug(f"Content too short: {len(cleaned_content)} chars")
                return None
            
            # Truncate if too long
            if len(cleaned_content) > self.max_content_length:
                cleaned_content = cleaned_content[:self.max_content_length] + "..."
                logger.debug(f"Content truncated to {self.max_content_length} chars")
            
            # Extract relevant sections based on query
            relevant_content = await self._extract_query_relevant_content(
                cleaned_content, query
            )
            
            # Chunk the content
            chunks = await self._chunk_content(relevant_content)
            
            # Create extracted result
            extracted_result = {
                'content': relevant_content,
                'original_content': raw_content,
                'chunks': chunks,
                'content_length': len(relevant_content),
                'chunk_count': len(chunks),
                'extraction_stats': {
                    'original_length': len(raw_content),
                    'cleaned_length': len(cleaned_content),
                    'final_length': len(relevant_content),
                    'reduction_ratio': 1 - (len(relevant_content) / len(raw_content)) if raw_content else 0
                },
                'extracted_at': datetime.utcnow()
            }
            
            # Copy over other fields from parsed result
            for key in ['title', 'url', 'snippet', 'score', 'published_date', 'metadata']:
                if key in parsed_result:
                    extracted_result[key] = parsed_result[key]
            
            logger.debug(f"Successfully extracted {len(relevant_content)} chars, {len(chunks)} chunks")
            return extracted_result
            
        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            return None
    
    async def _clean_content(self, content: str) -> str:
        """
        Clean raw content by removing HTML, noise, and normalizing text
        
        Args:
            content: Raw content string
            
        Returns:
            Cleaned content string
        """
        try:
            # Decode HTML entities
            content = html.unescape(content)
            
            # Remove HTML tags but preserve some structure
            content = self._remove_html_tags(content)
            
            # Remove noise patterns
            content = self._remove_noise_patterns(content)
            
            # Normalize whitespace
            content = self._normalize_whitespace(content)
            
            # Remove empty lines and excessive line breaks
            content = self._clean_line_breaks(content)
            return content
        except Exception as e:
            logger.error(f"Error cleaning content: {e}")
        return ""
    
    def _normalize_whitespace(self, content: str) -> str:
        """Normalize whitespace in content"""
        # Replace multiple spaces with single space
        content = re.sub(r' +', ' ', content)
        
        # Replace multiple tabs with single space
        content = re.sub(r'\t+', ' ', content)
        
        # Normalize line endings
        content = re.sub(r'\r\n', '\n', content)
        content = re.sub(r'\r', '\n', content)
        
        return content
    
    def _clean_line_breaks(self, content: str) -> str:
        """Clean excessive line breaks"""
        # Replace multiple consecutive line breaks with double line break
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in content.split('\n')]
        
        # Remove empty lines at start and end
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        
        # Filter out lines that are too short (likely noise)
        cleaned_lines = []
        for line in lines:
            if len(line.strip()) > 3:  # Keep lines with meaningful content
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    async def _extract_query_relevant_content(self, content: str, query: str) -> str:
        """
        Extract content sections most relevant to the search query
        
        Args:
            content: Cleaned content string
            query: Search query for relevance filtering
            
        Returns:
            Content sections most relevant to query
        """
        try:
            # Split query into keywords
            query_keywords = self._extract_keywords(query)
            if not query_keywords:
                return content
            
            # Split content into paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            if not paragraphs:
                return content
            
            # Score paragraphs based on query relevance
            scored_paragraphs = []
            for para in paragraphs:
                score = self._calculate_relevance_score(para, query_keywords)
                scored_paragraphs.append((score, para))
            
            # Sort by relevance score
            scored_paragraphs.sort(key=lambda x: x[0], reverse=True)
            
            # Select top relevant paragraphs
            selected_content = []
            total_length = 0
            
            for score, para in scored_paragraphs:
                if score > 0:  # Only include paragraphs with some relevance
                    if total_length + len(para) <= self.max_content_length:
                        selected_content.append(para)
                        total_length += len(para)
                    else:
                        # Add partial paragraph if it fits
                        remaining = self.max_content_length - total_length
                        if remaining > 100:  # Only if significant space left
                            selected_content.append(para[:remaining] + "...")
                        break
            
            # If no relevant content found, return first part of original content
            if not selected_content:
                return content[:self.max_content_length]
            
            return '\n\n'.join(selected_content)
            
        except Exception as e:
            logger.error(f"Error extracting query-relevant content: {e}")
            return content
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from search query"""
        # Basic keyword extraction - remove stop words and short words
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 
            'to', 'was', 'will', 'with', 'what', 'how', 'when', 'where', 'why'
        }
        
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords
    
    def _calculate_relevance_score(self, paragraph: str, keywords: List[str]) -> float:
        """Calculate relevance score for a paragraph based on query keywords"""
        if not keywords:
            return 0.0
        
        para_lower = paragraph.lower()
        score = 0.0
        
        for keyword in keywords:
            # Count keyword occurrences
            count = para_lower.count(keyword.lower())
            
            # Base score for presence
            if count > 0:
                score += 1.0
                
                # Bonus for multiple occurrences
                score += min(count - 1, 2) * 0.5
                
                # Bonus for keyword at beginning of paragraph
                if para_lower.startswith(keyword.lower()):
                    score += 0.5
        
        # Normalize by paragraph length (prefer concise relevant content)
        length_factor = min(len(paragraph) / 500, 1.0)  # Normalize to 500 chars
        score = score / max(length_factor, 0.1)
        
        return score
    
    async def _chunk_content(self, content: str) -> List[str]:
        """
        Split content into chunks for vector processing
        
        Args:
            content: Content to chunk
            
        Returns:
            List of content chunks
        """
        try:
            if len(content) <= self.chunk_size:
                return [content]
            
            chunks = []
            paragraphs = content.split('\n\n')
            
            current_chunk = ""
            
            for paragraph in paragraphs:
                # If paragraph alone is too long, split it
                if len(paragraph) > self.chunk_size:
                    # Save current chunk if it has content
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                        current_chunk = ""
                    
                    # Split long paragraph into sentences
                    sentences = self._split_into_sentences(paragraph)
                    temp_chunk = ""
                    
                    for sentence in sentences:
                        if len(temp_chunk + sentence) <= self.chunk_size:
                            temp_chunk += sentence + " "
                        else:
                            if temp_chunk.strip():
                                chunks.append(temp_chunk.strip())
                            temp_chunk = sentence + " "
                    
                    if temp_chunk.strip():
                        current_chunk = temp_chunk
                
                # If adding paragraph exceeds chunk size, save current chunk
                elif len(current_chunk + paragraph) > self.chunk_size:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = paragraph
                
                # Add paragraph to current chunk
                else:
                    if current_chunk:
                        current_chunk += "\n\n" + paragraph
                    else:
                        current_chunk = paragraph
            
            # Add final chunk
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            # Add overlap between chunks if multiple chunks
            if len(chunks) > 1:
                chunks = self._add_chunk_overlap(chunks)
            
            logger.debug(f"Content split into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking content: {e}")
            return [content]  # Return original content as single chunk
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting on common sentence endings
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _add_chunk_overlap(self, chunks: List[str]) -> List[str]:
        """Add overlap between consecutive chunks for better context"""
        if len(chunks) <= 1:
            return chunks
        
        overlapped_chunks = [chunks[0]]  # First chunk unchanged
        
        for i in range(1, len(chunks)):
            prev_chunk = chunks[i-1]
            current_chunk = chunks[i]
            
            # Get last N characters from previous chunk as overlap
            if len(prev_chunk) > self.chunk_overlap:
                overlap = prev_chunk[-self.chunk_overlap:]
                
                # Find a good break point (end of sentence or word)
                break_point = max(
                    overlap.rfind('. '),
                    overlap.rfind('! '),
                    overlap.rfind('? '),
                    overlap.rfind(' ')
                )
                
                if break_point > 0:
                    overlap = overlap[break_point:].strip()
                
                # Add overlap to current chunk
                overlapped_chunk = overlap + " " + current_chunk
                overlapped_chunks.append(overlapped_chunk)
            else:
                overlapped_chunks.append(current_chunk)
        
        return overlapped_chunks
    
    async def clean_text(self, text: str) -> str:
        """
        Public method to clean any text content
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        return await self._clean_content(text)
    
    async def chunk_content(self, content: str, chunk_size: Optional[int] = None) -> List[str]:
        """
        Public method to chunk content with optional custom chunk size
        
        Args:
            content: Content to chunk
            chunk_size: Optional custom chunk size
            
        Returns:
            List of content chunks
        """
        original_chunk_size = self.chunk_size
        if chunk_size:
            self.chunk_size = chunk_size
        
        try:
            chunks = await self._chunk_content(content)
            return chunks
        
            
        except Exception as e:
            logger.error(f"Error cleaning content: {e}")
            return ""
        finally:
            self.chunk_size = original_chunk_size.strip()
    
    def _remove_html_tags(self, content: str) -> str:
        """Remove HTML tags while preserving structure"""
        # Replace common block elements with line breaks
        block_elements = ['</p>', '</div>', '</h1>', '</h2>', '</h3>', '</h4>', '</h5>', '</h6>', 
                         '</li>', '</td>', '</tr>', '</section>', '</article>']
        for element in block_elements:
            content = content.replace(element, element + '\n')
        
        # Remove all HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        return content
    
    def _remove_noise_patterns(self, content: str) -> str:
        """Remove common noise patterns from content"""
        for pattern in self.noise_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # Remove common navigation elements
        content = re.sub(r'Home\s*>\s*[\w\s>]*', '', content)
        content = re.sub(r'Breadcrumb.*?(?=\n|$)', '', content, flags=re.IGNORECASE)
        
        # Remove social media sharing text
        content = re.sub(r'Share on (?:Facebook|Twitter|LinkedIn|Instagram)', '', content, flags=re.IGNORECASE)
        
        # Remove common footers
        content = re.sub(r'Copyright.*?(?=\n|$)', '', content, flags=re.IGNORECASE)
        content = re.sub(r'All rights reserved.*?(?=\n|$)', '', content, flags=re.IGNORECASE)
        
        return content