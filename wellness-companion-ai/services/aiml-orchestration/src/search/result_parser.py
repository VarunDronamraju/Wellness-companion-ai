"""
Result Parser - Parse raw Tavily API responses into structured format
Location: services/aiml-orchestration/src/search/result_parser.py

This module handles parsing of raw Tavily API JSON responses and extracts
structured search result data including titles, URLs, snippets, and metadata.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)

class ResultParser:
    """
    Parser for Tavily API responses
    
    Converts raw JSON responses from Tavily API into structured
    dictionaries ready for further processing in the pipeline.
    """
    
    def __init__(self):
        """Initialize result parser with configuration"""
        self.required_fields = ['title', 'url', 'content']
        self.optional_fields = ['snippet', 'published_date', 'score']
        
        logger.info("ResultParser initialized")
    
    async def parse_tavily_response(self, tavily_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse raw Tavily API response into structured result list
        
        Args:
            tavily_response: Raw JSON response from Tavily API
            
        Returns:
            List of parsed result dictionaries
        """
        try:
            logger.info("Parsing Tavily API response")
            
            # Validate response structure
            if not self._validate_response_structure(tavily_response):
                logger.error("Invalid Tavily response structure")
                return []
            
            # Extract results array
            raw_results = tavily_response.get('results', [])
            if not raw_results:
                logger.warning("No results found in Tavily response")
                return []
            
            logger.info(f"Found {len(raw_results)} raw results to parse")
            
            # Parse each result
            parsed_results = []
            for idx, raw_result in enumerate(raw_results):
                try:
                    parsed_result = await self._parse_single_result(raw_result, idx)
                    if parsed_result:
                        parsed_results.append(parsed_result)
                except Exception as e:
                    logger.warning(f"Failed to parse result {idx}: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(parsed_results)} results")
            return parsed_results
            
        except Exception as e:
            logger.error(f"Error parsing Tavily response: {e}")
            return []
    
    def _validate_response_structure(self, response: Dict[str, Any]) -> bool:
        """Validate that Tavily response has expected structure"""
        if not isinstance(response, dict):
            logger.error("Response is not a dictionary")
            return False
        
        if 'results' not in response:
            logger.error("Response missing 'results' field")
            return False
        
        if not isinstance(response['results'], list):
            logger.error("Response 'results' field is not a list")
            return False
        
        return True
    
    async def _parse_single_result(self, raw_result: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """
        Parse a single result from Tavily response
        
        Args:
            raw_result: Single result dictionary from Tavily
            index: Result index for logging
            
        Returns:
            Parsed result dictionary or None if parsing fails
        """
        try:
            # Check for required fields
            if not self._has_required_fields(raw_result):
                logger.warning(f"Result {index} missing required fields")
                return None
            
            # Extract basic fields
            parsed = {
                'title': self._clean_title(raw_result.get('title', '')),
                'url': self._clean_url(raw_result.get('url', '')),
                'content': self._clean_content(raw_result.get('content', '')),
                'snippet': self._extract_snippet(raw_result),
                'published_date': self._parse_published_date(raw_result),
                'score': self._extract_score(raw_result),
                'raw_data': raw_result,  # Keep original for debugging
                'parsed_at': datetime.utcnow(),
                'result_index': index
            }
            
            # Extract additional metadata
            parsed['metadata'] = self._extract_metadata(raw_result)
            
            # Validate final result
            if not self._validate_parsed_result(parsed):
                logger.warning(f"Parsed result {index} failed validation")
                return None
            
            logger.debug(f"Successfully parsed result {index}: {parsed['title'][:50]}...")
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing single result {index}: {e}")
            return None
    
    def _has_required_fields(self, result: Dict[str, Any]) -> bool:
        """Check if result has all required fields"""
        for field in self.required_fields:
            if field not in result or not result[field]:
                return False
        return True
    
    def _clean_title(self, title: str) -> str:
        """Clean and normalize title text"""
        if not title:
            return "Untitled"
        
        # Remove extra whitespace and normalize
        title = re.sub(r'\s+', ' ', title.strip())
        
        # Remove common prefixes/suffixes
        title = re.sub(r'^(.*?)\s*[-|]\s*(.*?)$', r'\1', title)
        
        # Limit length
        if len(title) > 200:
            title = title[:197] + "..."
        
        return title
    
    def _clean_url(self, url: str) -> str:
        """Clean and validate URL"""
        if not url:
            return ""
        
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Remove tracking parameters (basic cleanup)
        url = re.sub(r'[?&]utm_[^&]*', '', url)
        url = re.sub(r'[?&]fbclid=[^&]*', '', url)
        
        return url.strip()
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize content text"""
        if not content:
            return ""
        
        # Remove HTML tags (basic cleanup)
        content = re.sub(r'<[^>]+>', '', content)
        
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Remove common noise patterns
        content = re.sub(r'\b(Skip to|Jump to|Go to)\s+\w+\b', '', content, flags=re.IGNORECASE)
        
        return content
    
    def _extract_snippet(self, result: Dict[str, Any]) -> str:
        """Extract or generate snippet from result"""
        # Try to get snippet from result
        snippet = result.get('snippet', '')
        
        # If no snippet, create one from content
        if not snippet:
            content = result.get('content', '')
            if content:
                # Take first 300 characters as snippet
                snippet = content[:300].strip()
                if len(content) > 300:
                    snippet += "..."
        
        # Clean snippet
        snippet = re.sub(r'\s+', ' ', snippet.strip())
        
        return snippet
    
    def _parse_published_date(self, result: Dict[str, Any]) -> Optional[datetime]:
        """Parse published date from various possible fields"""
        date_fields = ['published_date', 'publishedDate', 'date', 'timestamp']
        
        for field in date_fields:
            if field in result and result[field]:
                try:
                    date_value = result[field]
                    
                    # Handle different date formats
                    if isinstance(date_value, str):
                        # Try common formats
                        for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                            try:
                                return datetime.strptime(date_value[:19], fmt)
                            except ValueError:
                                continue
                    
                    elif isinstance(date_value, (int, float)):
                        # Assume timestamp
                        return datetime.fromtimestamp(date_value)
                        
                except Exception as e:
                    logger.debug(f"Failed to parse date from {field}: {e}")
                    continue
        
        return None
    
    def _extract_score(self, result: Dict[str, Any]) -> float:
        """Extract relevance score from result"""
        score_fields = ['score', 'relevance_score', 'relevance', 'rank']
        
        for field in score_fields:
            if field in result:
                try:
                    score = float(result[field])
                    # Normalize score to 0-1 range if needed
                    if score > 1.0:
                        score = score / 100.0  # Assume percentage
                    return max(0.0, min(1.0, score))
                except (ValueError, TypeError):
                    continue
        
        # Default score if not found
        return 0.5
    
    def _extract_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract additional metadata from result"""
        metadata = {}
        
        # Extract domain from URL
        url = result.get('url', '')
        if url:
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                metadata['domain'] = parsed_url.netloc
                metadata['path'] = parsed_url.path
            except:
                pass
        
        # Extract other useful fields
        useful_fields = [
            'author', 'source', 'category', 'language', 
            'word_count', 'reading_time', 'tags'
        ]
        
        for field in useful_fields:
            if field in result and result[field]:
                metadata[field] = result[field]
        
        return metadata
    
    def _validate_parsed_result(self, parsed: Dict[str, Any]) -> bool:
        """Validate that parsed result meets quality requirements"""
        # Must have title and content
        if not parsed.get('title') or not parsed.get('content'):
            return False
        
        # Content must be meaningful length
        if len(parsed['content']) < 50:
            return False
        
        # URL must be valid
        url = parsed.get('url', '')
        if not url or not url.startswith(('http://', 'https://')):
            return False
        
        return True
    
    async def extract_snippets(self, results: List[Dict[str, Any]]) -> List[str]:
        """Extract just the snippets from parsed results"""
        snippets = []
        for result in results:
            snippet = result.get('snippet', '')
            if snippet:
                snippets.append(snippet)
        return snippets
    
    async def parse_metadata(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse and aggregate metadata from all results"""
        aggregated_metadata = {
            'total_results': len(results),
            'domains': set(),
            'average_score': 0.0,
            'date_range': {'earliest': None, 'latest': None},
            'content_stats': {
                'total_length': 0,
                'average_length': 0,
                'min_length': float('inf'),
                'max_length': 0
            }
        }
        
        if not results:
            return aggregated_metadata
        
        total_score = 0
        total_length = 0
        
        for result in results:
            # Collect domains
            if 'metadata' in result and 'domain' in result['metadata']:
                aggregated_metadata['domains'].add(result['metadata']['domain'])
            
            # Aggregate scores
            score = result.get('score', 0)
            total_score += score
            
            # Content length stats
            content_length = len(result.get('content', ''))
            total_length += content_length
            aggregated_metadata['content_stats']['min_length'] = min(
                aggregated_metadata['content_stats']['min_length'], content_length
            )
            aggregated_metadata['content_stats']['max_length'] = max(
                aggregated_metadata['content_stats']['max_length'], content_length
            )
            
            # Date range
            pub_date = result.get('published_date')
            if pub_date:
                if not aggregated_metadata['date_range']['earliest'] or pub_date < aggregated_metadata['date_range']['earliest']:
                    aggregated_metadata['date_range']['earliest'] = pub_date
                if not aggregated_metadata['date_range']['latest'] or pub_date > aggregated_metadata['date_range']['latest']:
                    aggregated_metadata['date_range']['latest'] = pub_date
        
        # Calculate averages
        aggregated_metadata['average_score'] = total_score / len(results)
        aggregated_metadata['content_stats']['total_length'] = total_length
        aggregated_metadata['content_stats']['average_length'] = total_length / len(results)
        aggregated_metadata['domains'] = list(aggregated_metadata['domains'])
        
        if aggregated_metadata['content_stats']['min_length'] == float('inf'):
            aggregated_metadata['content_stats']['min_length'] = 0
        
        return aggregated_metadata