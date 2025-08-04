
# ==== FILE 5: services/aiml-orchestration/src/search/search_request_builder.py ====

"""
Query formatting and request building for web search.
Optimizes queries for better web search results.
"""

import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

from .web_search_config import WebSearchConfig

logger = logging.getLogger(__name__)

class SearchRequestBuilder:
    """
    Builds and optimizes search requests for web search APIs.
    """
    
    def __init__(self, config: WebSearchConfig):
        self.config = config
        
        # Query enhancement patterns
        self.enhancement_patterns = {
            'question_words': ['what', 'how', 'when', 'where', 'why', 'who', 'which'],
            'technical_terms': ['algorithm', 'method', 'technique', 'approach', 'system'],
            'time_indicators': ['recent', 'latest', 'current', 'new', 'updated', '2024', '2025'],
            'quality_indicators': ['best', 'top', 'expert', 'guide', 'tutorial', 'comprehensive']
        }
        
        # Stop words to potentially remove
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'the', 'this', 'these', 'those'
        }
        
        self.request_stats = {
            'total_requests_built': 0,
            'enhanced_queries': 0,
            'context_enhanced_queries': 0,
            'domain_filtered_queries': 0
        }

    def build_request(
        self,
        query: str,
        max_results: int = 10,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        search_depth: str = "basic",
        enhance_query: bool = True
    ) -> Dict[str, Any]:
        """
        Build optimized search request.
        
        Args:
            query: Original search query
            max_results: Maximum number of results
            include_domains: Domains to include in search
            exclude_domains: Domains to exclude from search
            search_depth: Search depth level
            enhance_query: Whether to enhance the query
            
        Returns:
            Formatted search request
        """
        try:
            # Enhance query if requested
            if enhance_query:
                enhanced_query = self.enhance_query(query)
                if enhanced_query != query:
                    self.request_stats['enhanced_queries'] += 1
            else:
                enhanced_query = query
            
            # Merge domain filters with config defaults
            final_include_domains = self._merge_domain_lists(
                include_domains, 
                self.config.preferred_domains
            )
            
            final_exclude_domains = self._merge_domain_lists(
                exclude_domains,
                self.config.excluded_domains
            )
            
            # Build request
            search_request = {
                'query': enhanced_query,
                'original_query': query,
                'max_results': min(max_results, self.config.max_search_results),
                'search_depth': search_depth,
                'include_domains': final_include_domains[:10] if final_include_domains else [],  # Limit to 10
                'exclude_domains': final_exclude_domains[:10] if final_exclude_domains else [],  # Limit to 10
                'request_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'query_enhanced': enhanced_query != query,
                    'domain_filtering_applied': bool(final_include_domains or final_exclude_domains),
                    'original_query_length': len(query),
                    'enhanced_query_length': len(enhanced_query)
                }
            }
            
            self.request_stats['total_requests_built'] += 1
            
            if final_include_domains or final_exclude_domains:
                self.request_stats['domain_filtered_queries'] += 1
            
            logger.debug(f"Built search request: {enhanced_query} ({search_depth})")
            
            return search_request
            
        except Exception as e:
            logger.error(f"Error building search request: {str(e)}")
            
            # Return basic request on error
            return {
                'query': query,
                'original_query': query,
                'max_results': max_results,
                'search_depth': search_depth,
                'include_domains': [],
                'exclude_domains': [],
                'request_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e),
                    'fallback_request': True
                }
            }

    def enhance_query(self, query: str) -> str:
        """
        Enhance query for better web search results.
        
        Args:
            query: Original query
            
        Returns:
            Enhanced query
        """
        try:
            enhanced = query.strip()
            
            # Skip enhancement for very short queries
            if len(enhanced.split()) <= 2:
                return enhanced
            
            # Remove excessive punctuation
            enhanced = re.sub(r'[^\w\s\-\.]', ' ', enhanced)
            enhanced = ' '.join(enhanced.split())  # Normalize whitespace
            
            # Add context markers for specific query types
            enhanced = self._add_context_markers(enhanced)
            
            # Optimize for search engines
            enhanced = self._optimize_for_search(enhanced)
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"Query enhancement failed: {str(e)}")
            return query

    def enhance_query_with_context(self, query: str, context: str) -> str:
        """
        Enhance query using additional context.
        
        Args:
            query: Original query
            context: Additional context to inform query enhancement
            
        Returns:
            Context-enhanced query
        """
        try:
            enhanced_query = self.enhance_query(query)
            
            # Extract key terms from context
            context_keywords = self._extract_context_keywords(context)
            
            # Add relevant context keywords to query
            if context_keywords:
                # Limit to most relevant keywords
                relevant_keywords = context_keywords[:3]
                
                # Add keywords that aren't already in the query
                query_words = enhanced_query.lower().split()
                new_keywords = [
                    kw for kw in relevant_keywords 
                    if kw.lower() not in query_words
                ]
                
                if new_keywords:
                    enhanced_query += ' ' + ' '.join(new_keywords)
                    self.request_stats['context_enhanced_queries'] += 1
            
            return enhanced_query
            
        except Exception as e:
            logger.warning(f"Context-based query enhancement failed: {str(e)}")
            return self.enhance_query(query)

    def _add_context_markers(self, query: str) -> str:
        """Add context markers based on query type."""
        query_lower = query.lower()
        
        # Question queries
        if any(word in query_lower for word in self.enhancement_patterns['question_words']):
            if 'how' in query_lower and 'tutorial' not in query_lower:
                query += ' tutorial guide'
            elif 'what' in query_lower and 'definition' not in query_lower:
                query += ' definition explanation'
        
        # Technical queries
        if any(word in query_lower for word in self.enhancement_patterns['technical_terms']):
            if 'example' not in query_lower:
                query += ' examples'
        
        # Time-sensitive queries
        if any(word in query_lower for word in self.enhancement_patterns['time_indicators']):
            if '2024' not in query_lower and '2025' not in query_lower:
                query += ' 2024'
        
        return query

    def _optimize_for_search(self, query: str) -> str:
        """Optimize query for search engines."""
        # Remove unnecessary stop words for technical queries
        words = query.split()
        
        if len(words) > 5:  # Only for longer queries
            # Keep important stop words, remove others
            important_stop_words = {'how', 'what', 'when', 'where', 'why', 'who'}
            filtered_words = []
            
            for word in words:
                if (word.lower() not in self.stop_words or 
                    word.lower() in important_stop_words or
                    len(filtered_words) < 3):  # Keep first 3 words regardless
                    filtered_words.append(word)
            
            query = ' '.join(filtered_words)
        
        return query

    def _extract_context_keywords(self, context: str) -> List[str]:
        """Extract relevant keywords from context."""
        if not context or len(context) < 50:
            return []
        
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', context.lower())
        
        # Filter out stop words and get unique words
        keywords = [
            word for word in words 
            if word not in self.stop_words and len(word) >= 4
        ]
        
        # Get most frequent keywords
        word_counts = {}
        for word in keywords:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_keywords = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, count in sorted_keywords[:5]]

    def _merge_domain_lists(
        self, 
        user_domains: Optional[List[str]], 
        config_domains: Optional[List[str]]
    ) -> Optional[List[str]]:
        """Merge user-specified domains with config defaults."""
        if not user_domains and not config_domains:
            return None
        
        if not user_domains:
            return config_domains
        
        if not config_domains:
            return user_domains
        
        # Merge and deduplicate
        combined = list(set(user_domains + config_domains))
        return combined

    def build_contextual_request(
        self,
        query: str,
        local_results: List[Dict[str, Any]],
        confidence_score: float
    ) -> Dict[str, Any]:
        """
        Build search request informed by local search results.
        
        Args:
            query: Original query
            local_results: Results from local search
            confidence_score: Confidence in local results
            
        Returns:
            Contextual search request
        """
        # Extract context from local results
        context_snippets = []
        for result in local_results[:3]:  # Use top 3 results
            content = result.get('content', '')
            if content:
                # Take first 100 characters as context
                context_snippets.append(content[:100])
        
        context = ' '.join(context_snippets)
        
        # Enhance query with context
        enhanced_query = self.enhance_query_with_context(query, context)
        
        # Adjust search depth based on confidence
        search_depth = "basic" if confidence_score > 0.3 else "advanced"
        
        # Build request
        return self.build_request(
            query=enhanced_query,
            search_depth=search_depth,
            enhance_query=False  # Already enhanced
        )

    def get_request_statistics(self) -> Dict[str, Any]:
        """Get search request building statistics."""
        total = self.request_stats['total_requests_built']
        
        return {
            **self.request_stats,
            'enhancement_rate': f"{(self.request_stats['enhanced_queries'] / max(1, total)) * 100:.2f}%",
            'context_enhancement_rate': f"{(self.request_stats['context_enhanced_queries'] / max(1, total)) * 100:.2f}%",
            'domain_filtering_rate': f"{(self.request_stats['domain_filtered_queries'] / max(1, total)) * 100:.2f}%"
        }

    def validate_request(self, request: Dict[str, Any]) -> List[str]:
        """
        Validate search request for common issues.
        
        Returns:
            List of validation issues found
        """
        issues = []
        
        # Check required fields
        if not request.get('query'):
            issues.append("Query is required")
        
        # Check query length
        query = request.get('query', '')
        if len(query) > 500:
            issues.append("Query is too long (max 500 characters)")
        
        if len(query.strip()) < 3:
            issues.append("Query is too short (min 3 characters)")
        
        # Check max results
        max_results = request.get('max_results', 0)
        if max_results <= 0:
            issues.append("Max results must be positive")
        
        if max_results > self.config.max_search_results:
            issues.append(f"Max results exceeds limit ({self.config.max_search_results})")
        
        # Check search depth
        search_depth = request.get('search_depth', '')
        if search_depth not in ['basic', 'advanced']:
            issues.append("Search depth must be 'basic' or 'advanced'")
        
        # Check domain lists
        include_domains = request.get('include_domains', [])
        exclude_domains = request.get('exclude_domains', [])
        
        if len(include_domains) > 10:
            issues.append("Too many include domains (max 10)")
        
        if len(exclude_domains) > 10:
            issues.append("Too many exclude domains (max 10)")
        
        # Check for domain conflicts
        if include_domains and exclude_domains:
            conflicts = set(include_domains) & set(exclude_domains)
            if conflicts:
                issues.append(f"Conflicting domains in include/exclude lists: {list(conflicts)}")
        
        return issues
