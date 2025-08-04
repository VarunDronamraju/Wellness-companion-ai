"""
Metadata Enricher - Add comprehensive metadata and source attribution to web search results
Location: services/aiml-orchestration/src/search/metadata_enricher.py

This module enriches validated web search results with comprehensive metadata,
source attribution, confidence scores, and citation formatting for RAG integration.
"""

import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urlparse, unquote
import hashlib

logger = logging.getLogger(__name__)

class MetadataEnricher:
    """
    Metadata enricher for web search results
    
    Adds comprehensive metadata, source attribution, confidence scores,
    and properly formatted citations to web search results for RAG integration.
    """
    
    def __init__(self):
        """Initialize metadata enricher with configuration"""
        self.domain_authority_scores = {
            # High authority domains
            'wikipedia.org': 0.95,
            'britannica.com': 0.90,
            'nature.com': 0.95,
            'science.org': 0.95,
            'pubmed.ncbi.nlm.nih.gov': 0.90,
            'arxiv.org': 0.85,
            'stackoverflow.com': 0.85,
            'github.com': 0.80,
            'medium.com': 0.70,
            
            # Educational domains
            '.edu': 0.85,
            '.gov': 0.90,
            '.org': 0.75,
            
            # Commercial domains
            '.com': 0.60,
            '.net': 0.55,
            '.io': 0.65,
            
            # Default
            'default': 0.50
        }
        
        self.source_types = {
            'academic': ['edu', 'arxiv.org', 'pubmed', 'nature.com', 'science.org'],
            'reference': ['wikipedia.org', 'britannica.com'],
            'technical': ['stackoverflow.com', 'github.com', 'docs.'],
            'news': ['reuters.com', 'bbc.com', 'cnn.com', 'npr.org'],
            'blog': ['medium.com', 'substack.com', 'wordpress.com'],
            'commercial': ['com', 'net', 'biz'],
            'government': ['gov'],
            'organization': ['org']
        }
        
        logger.info("MetadataEnricher initialized")
    
    async def enrich_with_metadata(
        self, 
        validated_result: Dict[str, Any],
        query: str
    ) -> Dict[str, Any]:
        """
        Enrich validated result with comprehensive metadata and source attribution
        
        Args:
            validated_result: Validated result from ResultValidator
            query: Original search query for context
            
        Returns:
            Enriched result with comprehensive metadata
        """
        try:
            logger.debug(f"Enriching metadata for: {validated_result.get('title', 'Unknown')[:50]}...")
            
            # Create enriched result copy
            enriched = validated_result.copy()
            
            # Add domain analysis
            domain_info = self._analyze_domain(validated_result.get('url', ''))
            enriched['domain_info'] = domain_info
            
            # Calculate confidence scores
            confidence_scores = await self._calculate_confidence_scores(validated_result, query)
            enriched.update(confidence_scores)
            
            # Generate citation information
            citation_info = await self._generate_citation_info(validated_result)
            enriched['citations'] = citation_info
            
            # Add source attribution
            source_attribution = self._create_source_attribution(validated_result, domain_info)
            enriched['source_attribution'] = source_attribution
            
            # Extract and enrich existing metadata
            enhanced_metadata = await self._enhance_metadata(validated_result, query)
            enriched['metadata'] = enhanced_metadata
            
            # Add processing timestamps
            enriched['enrichment_timestamp'] = datetime.utcnow()
            enriched['processing_pipeline'] = 'tavily_web_search'
            
            # Calculate final quality score
            quality_score = self._calculate_final_quality_score(enriched)
            enriched['quality_score'] = quality_score
            
            # Add search context
            enriched['search_context'] = {
                'query': query,
                'query_keywords': self._extract_query_keywords(query),
                'relevance_indicators': self._find_relevance_indicators(validated_result, query)
            }
            
            logger.debug(f"Successfully enriched metadata with confidence: {confidence_scores.get('confidence_score', 0):.2f}")
            return enriched
            
        except Exception as e:
            logger.error(f"Error enriching metadata: {e}")
            # Return original result with minimal enrichment
            validated_result['enrichment_error'] = str(e)
            validated_result['enrichment_timestamp'] = datetime.utcnow()
            return validated_result
    
    def _analyze_domain(self, url: str) -> Dict[str, Any]:
        """Analyze domain for authority, type, and trustworthiness"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Get domain authority score
            authority_score = self._get_domain_authority(domain)
            
            # Determine source type
            source_type = self._determine_source_type(domain)
            
            # Extract domain parts
            domain_parts = domain.split('.')
            
            return {
                'full_domain': domain,
                'root_domain': '.'.join(domain_parts[-2:]) if len(domain_parts) >= 2 else domain,
                'subdomain': '.'.join(domain_parts[:-2]) if len(domain_parts) > 2 else '',
                'tld': domain_parts[-1] if domain_parts else '',
                'authority_score': authority_score,
                'source_type': source_type,
                'is_secure': parsed.scheme == 'https',
                'path_depth': len([p for p in parsed.path.split('/') if p]),
                'has_parameters': bool(parsed.query)
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing domain: {e}")
            return {
                'full_domain': 'unknown',
                'authority_score': 0.3,
                'source_type': 'unknown',
                'error': str(e)
            }
    
    def _get_domain_authority(self, domain: str) -> float:
        """Get domain authority score"""
        # Check exact matches first
        if domain in self.domain_authority_scores:
            return self.domain_authority_scores[domain]
        
        # Check TLD matches
        for tld, score in self.domain_authority_scores.items():
            if domain.endswith(tld):
                return score
        
        # Special case for edu domains
        if domain.endswith('.edu'):
            return self.domain_authority_scores['.edu']
        
        return self.domain_authority_scores['default']
    
    def _determine_source_type(self, domain: str) -> str:
        """Determine the type of source based on domain"""
        for source_type, indicators in self.source_types.items():
            for indicator in indicators:
                if indicator in domain:
                    return source_type
        
        return 'general'
    
    async def _calculate_confidence_scores(
        self, 
        result: Dict[str, Any], 
        query: str
    ) -> Dict[str, float]:
        """Calculate various confidence scores for the result"""
        try:
            # Get existing scores
            validation_score = result.get('validation_score', 0.5)
            final_score = result.get('final_score', 0.5)
            original_score = result.get('score', 0.5)
            
            # Calculate domain confidence
            domain_confidence = self._get_domain_authority(
                urlparse(result.get('url', '')).netloc.lower()
            )
            
            # Calculate content confidence
            content_confidence = self._calculate_content_confidence(result)
            
            # Calculate query relevance confidence
            relevance_confidence = self._calculate_relevance_confidence(result, query)
            
            # Calculate temporal confidence (freshness)
            temporal_confidence = self._calculate_temporal_confidence(result)
            
            # Combine into overall confidence score
            confidence_weights = {
                'domain': 0.25,
                'content': 0.30,
                'relevance': 0.25,
                'temporal': 0.10,
                'validation': 0.10
            }
            
            overall_confidence = (
                domain_confidence * confidence_weights['domain'] +
                content_confidence * confidence_weights['content'] +
                relevance_confidence * confidence_weights['relevance'] +
                temporal_confidence * confidence_weights['temporal'] +
                validation_score * confidence_weights['validation']
            )
            
            return {
                'confidence_score': min(overall_confidence, 1.0),
                'domain_confidence': domain_confidence,
                'content_confidence': content_confidence,
                'relevance_confidence': relevance_confidence,
                'temporal_confidence': temporal_confidence,
                'validation_confidence': validation_score,
                'confidence_breakdown': confidence_weights
            }
            
        except Exception as e:
            logger.warning(f"Error calculating confidence scores: {e}")
            return {'confidence_score': 0.5}
    
    def _calculate_content_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence based on content quality"""
        content = result.get('content', '')
        title = result.get('title', '')
        
        score = 0.5  # Base score
        
        # Content length factor
        length = len(content)
        if 300 <= length <= 3000:
            score += 0.2
        elif 100 <= length < 300 or 3000 < length <= 5000:
            score += 0.1
        
        # Title quality
        if title and 20 <= len(title) <= 100:
            score += 0.1
        
        # Structure indicators
        if '\n\n' in content:  # Has paragraphs
            score += 0.1
        
        # Language quality (basic check)
        words = re.findall(r'\b\w+\b', content)
        if len(words) >= 50:
            # Check for reasonable word diversity
            unique_words = len(set(w.lower() for w in words))
            diversity_ratio = unique_words / len(words)
            if diversity_ratio > 0.3:
                score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_relevance_confidence(self, result: Dict[str, Any], query: str) -> float:
        """Calculate confidence based on query relevance"""
        if not query:
            return 0.5
        
        content = result.get('content', '')
        title = result.get('title', '')
        combined_text = (title + ' ' + content).lower()
        
        query_keywords = self._extract_query_keywords(query)
        if not query_keywords:
            return 0.5
        
        relevance_score = 0.0
        
        for keyword in query_keywords:
            keyword_lower = keyword.lower()
            
            # Count occurrences
            title_count = title.lower().count(keyword_lower)
            content_count = content.lower().count(keyword_lower)
            
            # Score based on presence and frequency
            if title_count > 0:
                relevance_score += 0.3  # Title matches are important
                relevance_score += min(title_count - 1, 2) * 0.1
            
            if content_count > 0:
                relevance_score += 0.2  # Content matches
                relevance_score += min(content_count - 1, 3) * 0.05
        
        # Normalize by number of keywords
        relevance_score = relevance_score / len(query_keywords)
        
        return min(relevance_score, 1.0)
    
    def _calculate_temporal_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence based on content freshness"""
        pub_date = result.get('published_date')
        if not pub_date:
            return 0.5  # Neutral for unknown dates
        
        try:
            now = datetime.utcnow()
            age_days = (now - pub_date).days
            
            # Fresher content generally more reliable for dynamic topics
            if age_days <= 7:
                return 0.9
            elif age_days <= 30:
                return 0.8
            elif age_days <= 180:
                return 0.7
            elif age_days <= 365:
                return 0.6
            elif age_days <= 1095:  # 3 years
                return 0.5
            else:
                return 0.4
                
        except Exception:
            return 0.5
    
    async def _generate_citation_info(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate proper citation information for the result"""
        try:
            url = result.get('url', '')
            title = result.get('title', '')
            pub_date = result.get('published_date')
            
            # Parse domain for author/source
            domain = urlparse(url).netloc.lower() if url else 'Unknown'
            
            # Generate different citation formats
            citations = {
                'apa': self._format_apa_citation(title, domain, url, pub_date),
                'mla': self._format_mla_citation(title, domain, url, pub_date),
                'chicago': self._format_chicago_citation(title, domain, url, pub_date),
                'simple': self._format_simple_citation(title, domain, url),
                'inline': f'[{domain}]({url})'
            }
            
            # Add citation metadata
            citation_metadata = {
                'source_url': url,
                'source_domain': domain,
                'title': title,
                'access_date': datetime.utcnow().strftime('%Y-%m-%d'),
                'publication_date': pub_date.strftime('%Y-%m-%d') if pub_date else None,
                'citation_id': self._generate_citation_id(url, title)
            }
            
            return {
                'formats': citations,
                'metadata': citation_metadata,
                'short_cite': f"{domain} - {title[:50]}..." if title else domain
            }
            
        except Exception as e:
            logger.warning(f"Error generating citation info: {e}")
            return {
                'formats': {'simple': result.get('url', 'Unknown source')},
                'metadata': {'error': str(e)}
            }
    
    def _format_apa_citation(self, title: str, domain: str, url: str, pub_date: Optional[datetime]) -> str:
        """Format APA style citation"""
        date_str = pub_date.strftime('%Y, %B %d') if pub_date else 'n.d.'
        access_date = datetime.utcnow().strftime('%B %d, %Y')
        
        return f"{domain}. ({date_str}). {title}. Retrieved {access_date}, from {url}"
    
    def _format_mla_citation(self, title: str, domain: str, url: str, pub_date: Optional[datetime]) -> str:
        """Format MLA style citation"""
        date_str = pub_date.strftime('%d %b %Y') if pub_date else 'n.d.'
        access_date = datetime.utcnow().strftime('%d %b %Y')
        
        return f'"{title}." {domain}, {date_str}, {url}. Accessed {access_date}.'
    
    def _format_chicago_citation(self, title: str, domain: str, url: str, pub_date: Optional[datetime]) -> str:
        """Format Chicago style citation"""
        date_str = pub_date.strftime('%B %d, %Y') if pub_date else 'n.d.'
        access_date = datetime.utcnow().strftime('%B %d, %Y')
        
        return f'{domain}. "{title}." Last modified {date_str}. Accessed {access_date}. {url}.'
    
    def _format_simple_citation(self, title: str, domain: str, url: str) -> str:
        """Format simple citation"""
        return f"{title} - {domain} ({url})"
    
    def _generate_citation_id(self, url: str, title: str) -> str:
        """Generate unique citation ID"""
        content = f"{url}_{title}"
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def _create_source_attribution(self, result: Dict[str, Any], domain_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create source attribution information"""
        return {
            'source_name': domain_info.get('root_domain', 'Unknown'),
            'source_type': domain_info.get('source_type', 'general'),
            'authority_level': self._get_authority_level(domain_info.get('authority_score', 0.5)),
            'trustworthiness': domain_info.get('authority_score', 0.5),
            'content_type': self._infer_content_type(result),
            'language': self._detect_language(result.get('content', '')),
            'geographic_focus': self._detect_geographic_focus(result),
            'topic_category': self._categorize_topic(result)
        }
    
    def _get_authority_level(self, score: float) -> str:
        """Convert authority score to categorical level"""
        if score >= 0.8:
            return 'high'
        elif score >= 0.6:
            return 'medium'
        elif score >= 0.4:
            return 'low'
        else:
            return 'very_low'
    
    def _infer_content_type(self, result: Dict[str, Any]) -> str:
        """Infer the type of content"""
        content = result.get('content', '').lower()
        title = result.get('title', '').lower()
        combined = content + ' ' + title
        
        # Look for indicators
        if any(word in combined for word in ['study', 'research', 'analysis', 'findings']):
            return 'research'
        elif any(word in combined for word in ['tutorial', 'how to', 'guide', 'instructions']):
            return 'tutorial'
        elif any(word in combined for word in ['news', 'reported', 'breaking', 'update']):
            return 'news'
        elif any(word in combined for word in ['opinion', 'think', 'believe', 'editorial']):
            return 'opinion'
        elif any(word in combined for word in ['review', 'rating', 'stars', 'recommend']):
            return 'review'
        else:
            return 'informational'
    
    def _detect_language(self, content: str) -> str:
        """Basic language detection"""
        # Very basic detection - in practice, use proper language detection library
        if not content:
            return 'unknown'
        
        # Simple heuristic based on common English words
        english_indicators = ['the', 'and', 'to', 'of', 'a', 'in', 'is', 'it', 'you', 'that']
        words = re.findall(r'\b\w+\b', content.lower())
        
        if not words:
            return 'unknown'
        
        english_count = sum(1 for word in words[:100] if word in english_indicators)
        english_ratio = english_count / min(len(words), 100)
        
        return 'english' if english_ratio > 0.1 else 'other'
    
    def _detect_geographic_focus(self, result: Dict[str, Any]) -> Optional[str]:
        """Detect geographic focus of content"""
        content = result.get('content', '').lower()
        title = result.get('title', '').lower()
        combined = content + ' ' + title
        
        # Look for country/region indicators
        regions = {
            'usa': ['united states', 'america', 'us', 'usa'],
            'uk': ['united kingdom', 'britain', 'uk', 'england'],
            'canada': ['canada', 'canadian'],
            'australia': ['australia', 'australian'],
            'europe': ['europe', 'european', 'eu'],
            'asia': ['asia', 'asian'],
            'global': ['global', 'worldwide', 'international']
        }
        
        for region, indicators in regions.items():
            if any(indicator in combined for indicator in indicators):
                return region
        
        return None
    
    def _categorize_topic(self, result: Dict[str, Any]) -> str:
        """Categorize the topic of the content"""
        content = result.get('content', '').lower()
        title = result.get('title', '').lower()
        combined = content + ' ' + title
        
        categories = {
            'technology': ['software', 'computer', 'digital', 'tech', 'programming', 'ai', 'machine learning'],
            'science': ['research', 'study', 'scientific', 'biology', 'chemistry', 'physics'],
            'health': ['medical', 'health', 'disease', 'treatment', 'doctor', 'patient'],
            'business': ['business', 'economy', 'financial', 'market', 'company', 'corporate'],
            'education': ['education', 'school', 'university', 'learning', 'academic'],
            'news': ['news', 'current', 'today', 'recent', 'breaking', 'update']
        }
        
        max_score = 0
        best_category = 'general'
        
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in combined)
            if score > max_score:
                max_score = score
                best_category = category
        
        return best_category
    
    async def _enhance_metadata(self, result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Enhance existing metadata with additional information"""
        existing_metadata = result.get('metadata', {})
        
        enhanced = existing_metadata.copy()
        
        # Add processing metadata
        enhanced.update({
            'word_count': len(re.findall(r'\b\w+\b', result.get('content', ''))),
            'character_count': len(result.get('content', '')),
            'paragraph_count': len(result.get('content', '').split('\n\n')),
            'estimated_reading_time': self._estimate_reading_time(result.get('content', '')),
            'content_hash': hashlib.md5(result.get('content', '').encode()).hexdigest()[:16],
            'extraction_method': 'tavily_api',
            'processing_version': '1.0.0'
        })
        
        # Add query relationship metadata
        enhanced['query_relationship'] = {
            'original_query': query,
            'keyword_matches': self._find_keyword_matches(result, query),
            'semantic_similarity': self._calculate_semantic_similarity(result, query)
        }
        
        return enhanced
    
    def _estimate_reading_time(self, content: str) -> int:
        """Estimate reading time in minutes (assuming 200 words per minute)"""
        word_count = len(re.findall(r'\b\w+\b', content))
        return max(1, round(word_count / 200))
    
    def _find_keyword_matches(self, result: Dict[str, Any], query: str) -> List[str]:
        """Find which query keywords match in the content"""
        content = result.get('content', '').lower()
        title = result.get('title', '').lower()
        
        query_keywords = self._extract_query_keywords(query)
        matches = []
        
        for keyword in query_keywords:
            if keyword.lower() in content or keyword.lower() in title:
                matches.append(keyword)
        
        return matches
    
    def _calculate_semantic_similarity(self, result: Dict[str, Any], query: str) -> float:
        """Calculate basic semantic similarity (placeholder for more advanced implementation)"""
        # This is a simplified version - in practice, you'd use embeddings
        content_words = set(re.findall(r'\b\w+\b', result.get('content', '').lower()))
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        
        if not content_words or not query_words:
            return 0.0
        
        intersection = len(content_words.intersection(query_words))
        union = len(content_words.union(query_words))
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_query_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from query"""
        # Remove common stop words
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'what', 'how', 'when', 'where', 'why'
        }
        
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords
    
    def _find_relevance_indicators(self, result: Dict[str, Any], query: str) -> List[str]:
        """Find specific indicators of relevance to the query"""
        content = result.get('content', '')
        title = result.get('title', '')
        
        indicators = []
        
        # Check for exact query match
        if query.lower() in content.lower():
            indicators.append('exact_query_match')
        
        # Check for title relevance
        query_keywords = self._extract_query_keywords(query)
        title_keywords = set(re.findall(r'\b\w+\b', title.lower()))
        
        if any(keyword.lower() in title_keywords for keyword in query_keywords):
            indicators.append('title_keyword_match')
        
        # Check for semantic indicators
        if any(word in content.lower() for word in ['definition', 'explanation', 'overview']):
            indicators.append('definitional_content')
        
        if any(word in content.lower() for word in ['example', 'instance', 'case study']):
            indicators.append('example_content')
        
        return indicators
    
    def _calculate_final_quality_score(self, enriched_result: Dict[str, Any]) -> float:
        """Calculate final quality score combining all factors"""
        try:
            confidence_score = enriched_result.get('confidence_score', 0.5)
            domain_authority = enriched_result.get('domain_info', {}).get('authority_score', 0.5)
            validation_score = enriched_result.get('validation_score', 0.5)
            
            # Weight different factors
            final_score = (
                confidence_score * 0.4 +
                domain_authority * 0.3 +
                validation_score * 0.3
            )
            
            return min(final_score, 1.0)
            
        except Exception:
            return 0.5
    
    async def add_confidence_scores(
        self, 
        results: List[Dict[str, Any]], 
        query: str
    ) -> List[Dict[str, Any]]:
        """Public method to add confidence scores to a list of results"""
        scored_results = []
        
        for result in results:
            try:
                confidence_scores = await self._calculate_confidence_scores(result, query)
                result.update(confidence_scores)
                scored_results.append(result)
            except Exception as e:
                logger.warning(f"Failed to add confidence scores: {e}")
                result['confidence_score'] = 0.5
                scored_results.append(result)
        
        return scored_results
    
    async def format_citations(self, results: List[Dict[str, Any]], style: str = 'simple') -> List[str]:
        """Public method to format citations for a list of results"""
        citations = []
        
        for result in results:
            citation_info = result.get('citations', {})
            formats = citation_info.get('formats', {})
            
            citation = formats.get(style, result.get('url', 'Unknown source'))
            citations.append(citation)
        
        return citations