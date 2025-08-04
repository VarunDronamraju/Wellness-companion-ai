
# ==== FILE 4: services/aiml-orchestration/src/llm/response_handler.py ====

"""
Response processing and validation for LLM outputs.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class ResponseHandler:
    """
    Processes and validates LLM responses.
    """
    
    def __init__(self):
        self.processing_stats = {
            'total_responses_processed': 0,
            'successful_processing': 0,
            'failed_processing': 0,
            'average_processing_time': 0.0,
            'total_processing_time': 0.0,
            'citations_extracted': 0,
            'quality_issues_found': 0
        }

    def process_llm_response(self, raw_response: str) -> str:
        """
        Process and clean LLM response.
        """
        start_time = datetime.now()
        
        try:
            # Basic cleaning
            cleaned_response = self._clean_response(raw_response)
            
            # Validate response quality
            quality_issues = self.validate_response_quality(cleaned_response)
            if quality_issues['critical_issues']:
                logger.warning(f"Critical quality issues found: {quality_issues['critical_issues']}")
            
            # Apply final formatting
            formatted_response = self._apply_formatting(cleaned_response)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(True, processing_time, len(quality_issues['issues']))
            
            return formatted_response
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(False, processing_time, 0)
            logger.error(f"Error processing LLM response: {str(e)}")
            
            # Return cleaned version of original if processing fails
            return self._clean_response(raw_response)

    def extract_citations(self, response: str) -> List[Dict[str, Any]]:
        """
        Extract citations and source references from response.
        """
        citations = []
        
        # Pattern for explicit citations [Source X: ...]
        explicit_citations = re.findall(r'\[Source\s+(\d+):\s*([^\]]+)\]', response)
        for match in explicit_citations:
            citations.append({
                'type': 'explicit',
                'source_id': match[0],
                'source_name': match[1].strip(),
                'confidence': 0.9
            })
        
        # Pattern for implicit source references
        implicit_patterns = [
            r'according to (.+?)(?:,|\.|$)',
            r'based on (.+?)(?:,|\.|$)',
            r'as stated in (.+?)(?:,|\.|$)',
            r'the document mentions (.+?)(?:,|\.|$)'
        ]
        
        for pattern in implicit_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                citations.append({
                    'type': 'implicit',
                    'source_reference': match.strip(),
                    'confidence': 0.6
                })
        
        self.processing_stats['citations_extracted'] += len(citations)
        return citations

    def validate_response_quality(self, response: str) -> Dict[str, Any]:
        """
        Validate response quality and identify issues.
        """
        issues = []
        critical_issues = []
        quality_score = 1.0
        
        # Length checks
        if len(response.strip()) < 10:
            critical_issues.append("Response too short")
            quality_score -= 0.5
        elif len(response) > 2000:
            issues.append("Response very long")
            quality_score -= 0.1
        
        # Content quality checks
        if not response.strip():
            critical_issues.append("Empty response")
            quality_score = 0.0
        
        # Check for repetition
        sentences = response.split('.')
        if self._has_excessive_repetition(sentences):
            issues.append("Excessive repetition detected")
            quality_score -= 0.2
        
        # Check for coherence
        if not self._is_coherent(response):
            issues.append("Response lacks coherence")
            quality_score -= 0.3
        
        # Check for appropriate uncertainty expression
        uncertainty_patterns = [
            r"i don't know",
            r"i'm not sure",
            r"i cannot determine",
            r"insufficient information"
        ]
        
        has_uncertainty = any(
            re.search(pattern, response.lower()) 
            for pattern in uncertainty_patterns
        )
        
        return {
            'quality_score': max(0.0, quality_score),
            'issues': issues,
            'critical_issues': critical_issues,
            'has_uncertainty_expression': has_uncertainty,
            'word_count': len(response.split()),
            'sentence_count': len([s for s in sentences if s.strip()])
        }

    def _clean_response(self, response: str) -> str:
        """Clean and normalize response text."""
        if not response:
            return ""
        
        # Remove extra whitespace
        cleaned = ' '.join(response.split())
        
        # Remove potential artifacts from generation
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)  # Multiple newlines
        cleaned = re.sub(r'^\s*Answer:\s*', '', cleaned)      # Remove "Answer:" prefix
        cleaned = re.sub(r'^\s*Response:\s*', '', cleaned)    # Remove "Response:" prefix
        
        # Ensure proper sentence ending
        cleaned = cleaned.strip()
        if cleaned and not cleaned.endswith(('.', '!', '?')):
            cleaned += '.'
        
        return cleaned

    def _apply_formatting(self, response: str) -> str:
        """Apply final formatting to response."""
        # Ensure proper paragraph breaks
        formatted = re.sub(r'\.\s+([A-Z])', r'.\n\n\1', response)
        
        # Clean up any formatting artifacts
        formatted = re.sub(r'\n\s*\n\s*\n+', '\n\n', formatted)
        
        return formatted.strip()

    def _has_excessive_repetition(self, sentences: List[str]) -> bool:
        """Check for excessive repetition in sentences."""
        if len(sentences) < 3:
            return False
        
        # Check for identical sentences
        sentence_counts = {}
        for sentence in sentences:
            clean_sentence = sentence.strip().lower()
            if clean_sentence:
                sentence_counts[clean_sentence] = sentence_counts.get(clean_sentence, 0) + 1
        
        # If any sentence appears more than twice, flag as repetitive
        return any(count > 2 for count in sentence_counts.values())

    def _is_coherent(self, response: str) -> bool:
        """Basic coherence check for response."""
        # Very basic coherence checks
        sentences = [s.strip() for s in response.split('.') if s.strip()]
        
        if len(sentences) < 2:
            return True  # Single sentence is coherent by default
        
        # Check for logical flow indicators
        flow_indicators = [
            'however', 'therefore', 'furthermore', 'additionally', 
            'moreover', 'consequently', 'meanwhile', 'similarly',
            'in contrast', 'for example', 'specifically', 'finally'
        ]
        
        # If response has flow indicators, it's likely more coherent
        response_lower = response.lower()
        has_flow_indicators = any(indicator in response_lower for indicator in flow_indicators)
        
        return has_flow_indicators or len(sentences) <= 5  # Short responses assumed coherent

    def _update_stats(self, success: bool, processing_time: float, quality_issues: int):
        """Update processing statistics."""
        self.processing_stats['total_responses_processed'] += 1
        
        if success:
            self.processing_stats['successful_processing'] += 1
        else:
            self.processing_stats['failed_processing'] += 1
        
        self.processing_stats['total_processing_time'] += processing_time
        self.processing_stats['average_processing_time'] = (
            self.processing_stats['total_processing_time'] / 
            self.processing_stats['total_responses_processed']
        )
        
        self.processing_stats['quality_issues_found'] += quality_issues

    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get response processing statistics."""
        return {
            **self.processing_stats,
            'success_rate': f"{(self.processing_stats['successful_processing'] / max(1, self.processing_stats['total_responses_processed'])) * 100:.2f}%"
        }

