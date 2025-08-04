"""
Query preprocessing and analysis for RAG pipeline.
Handles query enhancement, intent analysis, and optimization.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class QueryAnalysis:
    """Analysis results for a processed query."""
    original_query: str
    processed_query: str
    intent: str
    entities: List[str]
    keywords: List[str]
    query_type: str
    confidence: float
    metadata: Dict[str, Any]

class QueryProcessor:
    """
    Processes and analyzes user queries for optimal RAG retrieval.
    """
    
    def __init__(self):
        self.query_stats = {
            'total_processed': 0,
            'successful_processing': 0,
            'failed_processing': 0,
            'average_processing_time': 0.0,
            'total_processing_time': 0.0
        }
        
        # Query type patterns
        self.query_patterns = {
            'question': [r'\?$', r'^(what|how|when|where|why|who|which)', r'(can you|could you|would you)'],
            'command': [r'^(find|search|show|tell|explain|describe)', r'(help me|assist me)'],
            'factual': [r'(define|definition|meaning)', r'(is|are|was|were).*\?'],
            'complex': [r'(compare|contrast|analyze|evaluate)', r'(pros and cons|advantages)']
        }
        
        # Common stop words for filtering
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }

    async def process_query(self, query: str, context: Optional[Dict] = None) -> QueryAnalysis:
        """
        Process and analyze a user query.
        
        Args:
            query: Raw user query
            context: Optional context information
            
        Returns:
            QueryAnalysis with processed query and metadata
        """
        start_time = datetime.now()
        
        try:
            # Clean and normalize query
            cleaned_query = self._clean_query(query)
            
            # Extract entities and keywords
            entities = self._extract_entities(cleaned_query)
            keywords = self._extract_keywords(cleaned_query)
            
            # Determine query intent and type
            intent = self._analyze_intent(cleaned_query)
            query_type = self._classify_query_type(cleaned_query)
            
            # Generate enhanced query
            processed_query = self._enhance_query(cleaned_query, keywords, entities)
            
            # Calculate confidence
            confidence = self._calculate_query_confidence(cleaned_query, entities, keywords)
            
            # Prepare metadata
            metadata = {
                'original_length': len(query),
                'processed_length': len(processed_query),
                'entity_count': len(entities),
                'keyword_count': len(keywords),
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'context_provided': context is not None,
                'timestamp': datetime.now().isoformat()
            }
            
            analysis = QueryAnalysis(
                original_query=query,
                processed_query=processed_query,
                intent=intent,
                entities=entities,
                keywords=keywords,
                query_type=query_type,
                confidence=confidence,
                metadata=metadata
            )
            
            self._update_stats(True, metadata['processing_time'])
            logger.info(f"Successfully processed query: {query[:50]}...")
            
            return analysis
            
        except Exception as e:
            self._update_stats(False, (datetime.now() - start_time).total_seconds())
            logger.error(f"Error processing query '{query}': {str(e)}")
            
            # Return basic analysis for failed processing
            return QueryAnalysis(
                original_query=query,
                processed_query=query,
                intent='unknown',
                entities=[],
                keywords=query.split(),
                query_type='unknown',
                confidence=0.5,
                metadata={'error': str(e), 'timestamp': datetime.now().isoformat()}
            )

    def _clean_query(self, query: str) -> str:
        """Clean and normalize the query."""
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        # Remove special characters but keep important punctuation
        query = re.sub(r'[^\w\s\?\!\.\,\-]', '', query)
        
        # Convert to lowercase for processing
        query = query.lower().strip()
        
        return query

    def _extract_entities(self, query: str) -> List[str]:
        """Extract named entities from the query."""
        entities = []
        
        # Simple entity extraction patterns
        patterns = {
            'dates': r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b',
            'numbers': r'\b\d+(?:\.\d+)?\b',
            'capitalized': r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
            'technical_terms': r'\b[A-Z]{2,}\b'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, query)
            entities.extend(matches)
        
        return list(set(entities))

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from the query."""
        words = query.split()
        
        # Filter out stop words and short words
        keywords = [
            word for word in words 
            if word not in self.stop_words and len(word) > 2
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords

    def _analyze_intent(self, query: str) -> str:
        """Analyze the intent of the query."""
        query_lower = query.lower()
        
        # Intent detection patterns
        intents = {
            'search': ['find', 'search', 'look for', 'locate'],
            'explain': ['explain', 'describe', 'tell me about', 'what is'],
            'compare': ['compare', 'difference', 'vs', 'versus'],
            'help': ['help', 'assist', 'guide', 'how to'],
            'question': ['?', 'what', 'when', 'where', 'why', 'how', 'who'],
            'analysis': ['analyze', 'evaluate', 'assess', 'review']
        }
        
        for intent, keywords in intents.items():
            if any(keyword in query_lower for keyword in keywords):
                return intent
        
        return 'general'

    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query."""
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return query_type
        
        return 'general'

    def _enhance_query(self, query: str, keywords: List[str], entities: List[str]) -> str:
        """Enhance the query for better retrieval."""
        # Start with the original query
        enhanced = query
        
        # Add important keywords if not already present
        important_keywords = [kw for kw in keywords if len(kw) > 4]
        for keyword in important_keywords[:3]:  # Limit to top 3
            if keyword not in enhanced:
                enhanced += f" {keyword}"
        
        # Add entities for context
        for entity in entities[:2]:  # Limit to top 2
            if entity not in enhanced:
                enhanced += f" {entity}"
        
        return enhanced.strip()

    def _calculate_query_confidence(self, query: str, entities: List[str], keywords: List[str]) -> float:
        """Calculate confidence score for the query."""
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on query characteristics
        if len(query.split()) >= 3:
            confidence += 0.1
        
        if entities:
            confidence += min(0.2, len(entities) * 0.05)
        
        if keywords:
            confidence += min(0.2, len(keywords) * 0.03)
        
        # Query type bonus
        if any(char in query for char in '?!'):
            confidence += 0.05
        
        return min(1.0, confidence)

    def _update_stats(self, success: bool, processing_time: float):
        """Update processing statistics."""
        self.query_stats['total_processed'] += 1
        
        if success:
            self.query_stats['successful_processing'] += 1
        else:
            self.query_stats['failed_processing'] += 1
        
        self.query_stats['total_processing_time'] += processing_time
        self.query_stats['average_processing_time'] = (
            self.query_stats['total_processing_time'] / 
            self.query_stats['total_processed']
        )

    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get query processing statistics."""
        return {
            **self.query_stats,
            'success_rate': f"{(self.query_stats['successful_processing'] / max(1, self.query_stats['total_processed'])) * 100:.2f}%"
        }

    async def batch_process_queries(self, queries: List[str]) -> List[QueryAnalysis]:
        """Process multiple queries concurrently."""
        tasks = [self.process_query(query) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful results
        successful_results = [
            result for result in results 
            if isinstance(result, QueryAnalysis)
        ]
        
        logger.info(f"Batch processed {len(successful_results)}/{len(queries)} queries successfully")
        return successful_results