
# File 3: services/aiml-orchestration/src/search/search_filter.py
"""
Search filtering logic and utilities.
"""

import logging
from typing import Dict, List, Any, Optional, Callable
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SearchFilter:
    """Implements search filtering and result post-processing"""
    
    def __init__(self):
        self.filter_stats = {
            'filters_applied': 0,
            'results_filtered': 0,
            'total_results_processed': 0
        }
    
    def apply_metadata_filters(self,
                             search_results: List[Dict[str, Any]],
                             filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply metadata-based filters to search results
        
        Args:
            search_results: List of search results
            filters: Dictionary of filter criteria
            
        Returns:
            Filtered search results
        """
        try:
            if not filters or not search_results:
                return search_results
            
            self.filter_stats['filters_applied'] += 1
            initial_count = len(search_results)
            self.filter_stats['total_results_processed'] += initial_count
            
            filtered_results = []
            
            for result in search_results:
                if self._matches_filters(result, filters):
                    filtered_results.append(result)
            
            filtered_count = len(filtered_results)
            self.filter_stats['results_filtered'] += (initial_count - filtered_count)
            
            logger.info(f"Applied filters: {initial_count} → {filtered_count} results")
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Filter application failed: {str(e)}")
            return search_results  # Return unfiltered results on error
    
    def _matches_filters(self, result: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if a result matches the filter criteria"""
        try:
            payload = result.get('payload', {})
            
            for filter_key, filter_value in filters.items():
                if not self._matches_single_filter(payload, filter_key, filter_value):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Filter matching failed: {str(e)}")
            return True  # Include result if filter evaluation fails
    
    def _matches_single_filter(self, payload: Dict[str, Any], key: str, value: Any) -> bool:
        """Check if payload matches a single filter criterion"""
        # Handle nested keys (e.g., "metadata.author")
        if '.' in key:
            keys = key.split('.')
            current_data = payload
            for k in keys:
                if isinstance(current_data, dict) and k in current_data:
                    current_data = current_data[k]
                else:
                    return False
            payload_value = current_data
        else:
            payload_value = payload.get(key)
        
        # Handle different filter types
        if isinstance(value, dict):
            return self._handle_complex_filter(payload_value, value)
        elif isinstance(value, list):
            # Check if payload value is in the list
            return payload_value in value
        elif isinstance(value, str) and value.startswith('regex:'):
            # Regex matching
            pattern = value[6:]  # Remove 'regex:' prefix
            return bool(re.search(pattern, str(payload_value), re.IGNORECASE))
        else:
            # Direct equality
            return payload_value == value
    
    def _handle_complex_filter(self, payload_value: Any, filter_config: Dict[str, Any]) -> bool:
        """Handle complex filter configurations"""
        try:
            # Range filters
            if 'min' in filter_config or 'max' in filter_config:
                if not isinstance(payload_value, (int, float)):
                    return False
                
                if 'min' in filter_config and payload_value < filter_config['min']:
                    return False
                if 'max' in filter_config and payload_value > filter_config['max']:
                    return False
                return True
            
            # Date filters
            if 'after' in filter_config or 'before' in filter_config:
                try:
                    if isinstance(payload_value, (int, float)):
                        # Assume timestamp
                        payload_date = datetime.fromtimestamp(payload_value)
                    else:
                        # Try to parse as ISO date
                        payload_date = datetime.fromisoformat(str(payload_value))
                    
                    if 'after' in filter_config:
                        after_date = datetime.fromisoformat(filter_config['after'])
                        if payload_date <= after_date:
                            return False
                    if 'before' in filter_config:
                        before_date = datetime.fromisoformat(filter_config['before'])
                        if payload_date >= before_date:
                            return False
                    return True
                except (ValueError, TypeError):
                    return False
            
            # String filters
            if 'contains' in filter_config:
                return filter_config['contains'].lower() in str(payload_value).lower()
            
            if 'starts_with' in filter_config:
                return str(payload_value).lower().startswith(filter_config['starts_with'].lower())
            
            if 'ends_with' in filter_config:
                return str(payload_value).lower().endswith(filter_config['ends_with'].lower())
            
            return True
            
        except Exception as e:
            logger.error(f"Complex filter evaluation failed: {str(e)}")
            return True
    
    def filter_by_score_range(self,
                            search_results: List[Dict[str, Any]],
                            min_score: float = 0.0,
                            max_score: float = 1.0) -> List[Dict[str, Any]]:
        """Filter results by similarity score range"""
        try:
            return [
                result for result in search_results
                if min_score <= result.get('score', 0.0) <= max_score
            ]
        except Exception as e:
            logger.error(f"Score filtering failed: {str(e)}")
            return search_results
    
    def filter_by_document_type(self,
                               search_results: List[Dict[str, Any]],
                               allowed_types: List[str]) -> List[Dict[str, Any]]:
        """Filter results by document type"""
        try:
            return [
                result for result in search_results
                if result.get('payload', {}).get('file_type', '').lower() in 
                [t.lower() for t in allowed_types]
            ]
        except Exception as e:
            logger.error(f"Document type filtering failed: {str(e)}")
            return search_results
    
    def filter_by_recency(self,
                         search_results: List[Dict[str, Any]],
                         max_age_days: int = 30) -> List[Dict[str, Any]]:
        """Filter results by recency (age in days)"""
        try:
            cutoff_timestamp = datetime.now().timestamp() - (max_age_days * 24 * 3600)
            
            return [
                result for result in search_results
                if result.get('payload', {}).get('stored_at', 0) >= cutoff_timestamp
            ]
        except Exception as e:
            logger.error(f"Recency filtering failed: {str(e)}")
            return search_results
    
    def deduplicate_results(self,
                          search_results: List[Dict[str, Any]],
                          dedup_key: str = 'document_id') -> List[Dict[str, Any]]:
        """Remove duplicate results based on a key"""
        try:
            seen_values = set()
            unique_results = []
            
            for result in search_results:
                key_value = result.get('payload', {}).get(dedup_key) or result.get(dedup_key)
                
                if key_value not in seen_values:
                    seen_values.add(key_value)
                    unique_results.append(result)
            
            logger.info(f"Deduplication: {len(search_results)} → {len(unique_results)} results")
            return unique_results
            
        except Exception as e:
            logger.error(f"Deduplication failed: {str(e)}")
            return search_results
    
    def get_filter_stats(self) -> Dict[str, Any]:
        """Get filtering statistics"""
        filter_rate = 0.0
        if self.filter_stats['total_results_processed'] > 0:
            filter_rate = (
                self.filter_stats['results_filtered'] / 
                self.filter_stats['total_results_processed']
            ) * 100
        
        return {
            **self.filter_stats,
            'filter_rate': f"{filter_rate:.2f}%"
        }