"""
Result Validator - Validate and filter web search results for quality and relevance
Location: services/aiml-orchestration/src/search/result_validator.py

This module validates web search results to ensure quality, removes duplicates,
and filters out low-quality or irrelevant content before RAG integration.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from urllib.parse import urlparse
import hashlib

logger = logging.getLogger(__name__)

class ResultValidator:
    """
    Validator for web search results
    
    Validates result quality, removes duplicates, and filters
    out low-quality content to ensure only valuable results
    proceed to RAG integration.
    """
    
    def __init__(self):
        """Initialize result validator with quality thresholds"""
        self.min_content_length = 100
        self.max_content_length = 10000
        self.min_relevance_score = 0.1
        self.similarity_threshold = 0.85  # For duplicate detection
        
        # Quality indicators
        self.quality_indicators = {
            'good_domains': {
                'wikipedia.org', 'britannica.com', 'edu', 'gov', 'org',
                'stackoverflow.com', 'github.com', 'medium.com',
                'nature.com', 'science.org', 'pubmed.ncbi.nlm.nih.gov'
            },
            'spam_patterns': [
                r'click here for more',
                r'buy now',
                r'limited time offer',
                r'act fast',
                r'download now',
                r'free trial',
                r'sign up today',
                r'subscribe for',
                r'get (?:your|our) free',
                r'\$\d+(?:\.\d{2})? off'
            ],
            'low_quality_patterns': [
                r'^(?:home|menu|navigation|sidebar)',
                r'cookie (?:policy|notice)',
                r'privacy policy',
                r'terms of service',
                r'error \d+',
                r'page not found',
                r'access denied'
            ]
        }
        
        logger.info("ResultValidator initialized")
    
    async def validate_results(
        self, 
        extracted_results: List[Dict[str, Any]],
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Validate and filter extracted web search results
        
        Args:
            extracted_results: List of extracted results from ContentExtractor
            query: Original search query for relevance validation
            
        Returns:
            List of validated and filtered results
        """
        try:
            logger.info(f"Validating {len(extracted_results)} extracted results")
            
            if not extracted_results:
                return []
            
            # Step 1: Basic quality validation
            quality_filtered = []
            for result in extracted_results:
                if await self._validate_basic_quality(result):
                    quality_filtered.append(result)
                else:
                    logger.debug(f"Result failed basic quality check: {result.get('title', 'Unknown')[:50]}")
            
            logger.info(f"After quality filtering: {len(quality_filtered)} results")
            
            # Step 2: Remove duplicates
            deduplicated = await self._remove_duplicates(quality_filtered)
            logger.info(f"After deduplication: {len(deduplicated)} results")
            
            # Step 3: Validate content quality
            content_validated = []
            for result in deduplicated:
                if await self._validate_content_quality(result, query):
                    content_validated.append(result)
                else:
                    logger.debug(f"Result failed content validation: {result.get('title', 'Unknown')[:50]}")
            
            logger.info(f"After content validation: {len(content_validated)} results")
            
            # Step 4: Score and rank results
            scored_results = await self._score_results(content_validated, query)
            
            # Step 5: Final filtering based on scores
            final_results = await self._final_score_filter(scored_results)
            
            logger.info(f"Final validated results: {len(final_results)}")
            return final_results
            
        except Exception as e:
            logger.error(f"Error validating results: {e}")
            return extracted_results  # Return original results if validation fails
    
    async def _validate_basic_quality(self, result: Dict[str, Any]) -> bool:
        """Validate basic quality requirements for a result"""
        try:
            # Must have required fields
            if not all(key in result for key in ['title', 'url', 'content']):
                return False
            
            # Title validation
            title = result.get('title', '').strip()
            if not title or len(title) < 10:
                return False
            
            # URL validation
            url = result.get('url', '')
            if not self._is_valid_url(url):
                return False
            
            # Content length validation
            content = result.get('content', '')
            if len(content) < self.min_content_length or len(content) > self.max_content_length:
                return False
            
            # Check for spam patterns
            if self._contains_spam_patterns(title + ' ' + content):
                return False
            
            # Check for low-quality patterns
            if self._contains_low_quality_patterns(content):
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Error in basic quality validation: {e}")
            return False
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format and domain"""
        try:
            parsed = urlparse(url)
            
            # Must have scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Must be HTTP/HTTPS
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Check for suspicious domains
            domain = parsed.netloc.lower()
            
            # Block common spam/ad domains
            spam_domains = {
                'bit.ly', 'tinyurl.com', 'goo.gl', 't.co',
                'clickfunnels.com', 'leadpages.net'
            }
            
            if any(spam_domain in domain for spam_domain in spam_domains):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _contains_spam_patterns(self, text: str) -> bool:
        """Check if text contains spam patterns"""
        text_lower = text.lower()
        
        for pattern in self.quality_indicators['spam_patterns']:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _contains_low_quality_patterns(self, text: str) -> bool:
        """Check if text contains low-quality patterns"""
        text_lower = text.lower()
        
        for pattern in self.quality_indicators['low_quality_patterns']:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    async def _remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on content similarity and URL"""
        if len(results) <= 1:
            return results
        
        try:
            unique_results = []
            seen_urls = set()
            content_hashes = set()
            
            for result in results:
                url = result.get('url', '')
                content = result.get('content', '')
                
                # Skip if same URL already seen
                if url in seen_urls:
                    logger.debug(f"Duplicate URL found: {url}")
                    continue
                
                # Check content similarity using hash
                content_hash = self._get_content_hash(content)
                if content_hash in content_hashes:
                    logger.debug(f"Duplicate content found for: {result.get('title', 'Unknown')[:50]}")
                    continue
                
                # Check for near-duplicate content
                is_duplicate = False
                for existing_result in unique_results:
                    if self._are_similar_contents(content, existing_result.get('content', '')):
                        logger.debug(f"Similar content found for: {result.get('title', 'Unknown')[:50]}")
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    unique_results.append(result)
                    seen_urls.add(url)
                    content_hashes.add(content_hash)
            
            return unique_results
            
        except Exception as e:
            logger.error(f"Error removing duplicates: {e}")
            return results
    
    def _get_content_hash(self, content: str) -> str:
        """Generate hash for content deduplication"""
        # Normalize content for hashing
        normalized = re.sub(r'\s+', ' ', content.lower().strip())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _are_similar_contents(self, content1: str, content2: str) -> bool:
        """Check if two contents are similar using simple similarity measure"""
        if not content1 or not content2:
            return False
        
        # Normalize contents
        norm1 = set(re.findall(r'\b\w+\b', content1.lower()))
        norm2 = set(re.findall(r'\b\w+\b', content2.lower()))
        
        if not norm1 or not norm2:
            return False
        
        # Calculate Jaccard similarity
        intersection = len(norm1.intersection(norm2))
        union = len(norm1.union(norm2))
        
        similarity = intersection / union if union > 0 else 0
        
        return similarity > self.similarity_threshold
    
    async def _validate_content_quality(self, result: Dict[str, Any], query: str) -> bool:
        """Validate content quality and relevance to query"""
        try:
            content = result.get('content', '')
            title = result.get('title', '')
            
            # Check content coherence
            if not self._is_coherent_content(content):
                return False
            
            # Check query relevance
            relevance_score = self._calculate_query_relevance(content + ' ' + title, query)
            if relevance_score < self.min_relevance_score:
                return False
            
            # Check domain quality
            url = result.get('url', '')
            domain_score = self._get_domain_quality_score(url)
            
            # Combine scores for final validation
            combined_score = (relevance_score * 0.7) + (domain_score * 0.3)
            
            result['validation_score'] = combined_score
            return combined_score > 0.3
            
        except Exception as e:
            logger.warning(f"Error in content quality validation: {e}")
            return False
    
    def _is_coherent_content(self, content: str) -> bool:
        """Check if content is coherent and well-formed"""
        if not content:
            return False
        
        # Check for minimum number of sentences
        sentences = re.split(r'[.!?]+', content)
        if len(sentences) < 2:
            return False
        
        # Check for reasonable word count
        words = re.findall(r'\b\w+\b', content)
        if len(words) < 20:
            return False
        
        # Check for excessive repetition
        word_counts = {}
        for word in words:
            word_lower = word.lower()
            word_counts[word_lower] = word_counts.get(word_lower, 0) + 1
        
        # If any word appears more than 20% of the time, it's likely spam
        max_count = max(word_counts.values()) if word_counts else 0
        if max_count > len(words) * 0.2:
            return False
        
        return True
    
    def _calculate_query_relevance(self, text: str, query: str) -> float:
        """Calculate how relevant the text is to the query"""
        if not text or not query:
            return 0.0
        
        text_lower = text.lower()
        query_lower = query.lower()
        
        # Extract query terms
        query_terms = re.findall(r'\b\w+\b', query_lower)
        query_terms = [term for term in query_terms if len(term) > 2]  # Filter short words
        
        if not query_terms:
            return 0.5  # Neutral score if no meaningful query terms
        
        # Calculate term frequency in text
        relevance_score = 0.0
        for term in query_terms:
            count = text_lower.count(term)
            if count > 0:
                # Base score for presence
                relevance_score += 1.0
                
                # Bonus for multiple occurrences (diminishing returns)
                relevance_score += min(count - 1, 3) * 0.2
        
        # Normalize by number of query terms
        relevance_score = relevance_score / len(query_terms)
        
        # Cap at 1.0
        return min(relevance_score, 1.0)
    
    def _get_domain_quality_score(self, url: str) -> float:
        """Calculate quality score based on domain"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # High-quality domains
            if any(good_domain in domain for good_domain in self.quality_indicators['good_domains']):
                return 1.0
            
            # Educational/government domains
            if domain.endswith('.edu') or domain.endswith('.gov'):
                return 0.9
            
            # Organizational domains
            if domain.endswith('.org'):
                return 0.7
            
            # Commercial domains (neutral)
            if domain.endswith('.com') or domain.endswith('.net'):
                return 0.5
            
            # Other domains
            return 0.3
            
        except Exception:
            return 0.3
    
    async def _score_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Score results for final ranking"""
        scored_results = []
        
        for result in results:
            try:
                # Get existing scores
                validation_score = result.get('validation_score', 0.5)
                original_score = result.get('score', 0.5)
                
                # Calculate additional quality metrics
                content_quality = self._calculate_content_quality(result)
                freshness_score = self._calculate_freshness_score(result)
                
                # Combine scores
                final_score = (
                    validation_score * 0.3 +
                    original_score * 0.2 +
                    content_quality * 0.3 +
                    freshness_score * 0.2
                )
                
                result['final_score'] = final_score
                scored_results.append(result)
                
            except Exception as e:
                logger.warning(f"Error scoring result: {e}")
                result['final_score'] = 0.5
                scored_results.append(result)
        
        # Sort by final score
        scored_results.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        return scored_results
    
    def _calculate_content_quality(self, result: Dict[str, Any]) -> float:
        """Calculate content quality score"""
        content = result.get('content', '')
        title = result.get('title', '')
        
        score = 0.5  # Base score
        
        # Length bonus (optimal length gets higher score)
        length = len(content)
        if 500 <= length <= 2000:
            score += 0.2
        elif 200 <= length < 500 or 2000 < length <= 4000:
            score += 0.1
        
        # Title quality
        if title and len(title) > 20:
            score += 0.1
        
        # Paragraph structure
        paragraphs = content.split('\n\n')
        if len(paragraphs) >= 3:
            score += 0.1
        
        # Sentence structure
        sentences = re.split(r'[.!?]+', content)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        if 10 <= avg_sentence_length <= 30:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_freshness_score(self, result: Dict[str, Any]) -> float:
        """Calculate freshness score based on publication date"""
        pub_date = result.get('published_date')
        if not pub_date:
            return 0.5  # Neutral score for unknown date
        
        try:
            now = datetime.utcnow()
            age_days = (now - pub_date).days
            
            # Fresher content gets higher score
            if age_days <= 30:
                return 1.0
            elif age_days <= 90:
                return 0.8
            elif age_days <= 365:
                return 0.6
            elif age_days <= 1095:  # 3 years
                return 0.4
            else:
                return 0.2
                
        except Exception:
            return 0.5
    
    async def _final_score_filter(self, scored_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply final filtering based on scores"""
        # Filter results with very low scores
        min_final_score = 0.3
        filtered_results = [
            result for result in scored_results 
            if result.get('final_score', 0) >= min_final_score
        ]
        
        # Limit to top results
        max_results = 10
        return filtered_results[:max_results]
    
    async def filter_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Public method to filter duplicates from results"""
        return await self._remove_duplicates(results)
    
    async def check_content_quality(self, content: str, title: str = "") -> Dict[str, Any]:
        """Public method to check content quality"""
        result = {
            'content': content,
            'title': title,
            'url': 'http://example.com'  # Dummy URL for testing
        }
        
        is_valid = await self._validate_content_quality(result, "")
        
        return {
            'is_valid': is_valid,
            'validation_score': result.get('validation_score', 0),
            'content_quality': self._calculate_content_quality(result),
            'is_coherent': self._is_coherent_content(content)
        }