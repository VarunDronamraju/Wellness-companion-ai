
# File 3: services/aiml-orchestration/src/embeddings/embedding_validator.py
"""
Embedding validation and quality checks.
"""

import logging
from typing import List, Dict, Any, Tuple
import numpy as np
import math

logger = logging.getLogger(__name__)

class EmbeddingValidator:
    """Validates embedding quality and consistency"""
    
    def __init__(self, expected_dimension: int = 384):
        self.expected_dimension = expected_dimension
        self.validation_stats = {
            'total_validations': 0,
            'passed_validations': 0,
            'failed_validations': 0,
            'common_issues': {}
        }
    
    def validate_single_embedding(self, embedding: List[float]) -> Dict[str, Any]:
        """
        Validate a single embedding vector
        
        Args:
            embedding: Single embedding vector
            
        Returns:
            Validation result dictionary
        """
        issues = []
        
        # Dimension check
        if len(embedding) != self.expected_dimension:
            issues.append(f"Wrong dimension: {len(embedding)} != {self.expected_dimension}")
        
        # NaN/Infinity check
        if not all(math.isfinite(val) for val in embedding):
            issues.append("Contains NaN or infinite values")
        
        # Zero vector check
        if all(val == 0.0 for val in embedding):
            issues.append("Zero vector detected")
        
        # Range check (typical embeddings are between -1 and 1 for normalized models)
        if any(abs(val) > 10.0 for val in embedding):
            issues.append("Values outside expected range")
        
        # Magnitude check
        magnitude = np.linalg.norm(embedding)
        if magnitude < 0.1 or magnitude > 10.0:
            issues.append(f"Unusual magnitude: {magnitude:.3f}")
        
        is_valid = len(issues) == 0
        
        return {
            'valid': is_valid,
            'issues': issues,
            'dimension': len(embedding),
            'magnitude': magnitude,
            'has_nan': any(not math.isfinite(val) for val in embedding),
            'is_zero_vector': all(val == 0.0 for val in embedding)
        }
    
    def validate_batch_embeddings(self, embeddings: List[List[float]]) -> Dict[str, Any]:
        """
        Validate a batch of embeddings
        
        Args:
            embeddings: List of embedding vectors
            
        Returns:
            Batch validation result
        """
        self.validation_stats['total_validations'] += 1
        
        if not embeddings:
            self.validation_stats['failed_validations'] += 1
            return {
                'valid': False,
                'error': 'No embeddings provided',
                'batch_size': 0
            }
        
        individual_results = []
        valid_count = 0
        dimension_issues = 0
        quality_issues = 0
        
        for i, embedding in enumerate(embeddings):
            result = self.validate_single_embedding(embedding)
            individual_results.append(result)
            
            if result['valid']:
                valid_count += 1
            else:
                for issue in result['issues']:
                    if 'dimension' in issue.lower():
                        dimension_issues += 1
                    else:
                        quality_issues += 1
                    
                    # Track common issues
                    if issue not in self.validation_stats['common_issues']:
                        self.validation_stats['common_issues'][issue] = 0
                    self.validation_stats['common_issues'][issue] += 1
        
        batch_valid = valid_count == len(embeddings)
        
        if batch_valid:
            self.validation_stats['passed_validations'] += 1
        else:
            self.validation_stats['failed_validations'] += 1
        
        # Calculate consistency metrics
        dimensions = [len(emb) for emb in embeddings]
        dimension_consistency = len(set(dimensions)) == 1
        
        magnitudes = [np.linalg.norm(emb) for emb in embeddings]
        avg_magnitude = np.mean(magnitudes)
        std_magnitude = np.std(magnitudes)
        
        return {
            'valid': batch_valid,
            'batch_size': len(embeddings),
            'valid_count': valid_count,
            'invalid_count': len(embeddings) - valid_count,
            'success_rate': (valid_count / len(embeddings)) * 100,
            'dimension_consistency': dimension_consistency,
            'dimension_issues': dimension_issues,
            'quality_issues': quality_issues,
            'magnitude_stats': {
                'average': avg_magnitude,
                'std_deviation': std_magnitude,
                'range': [min(magnitudes), max(magnitudes)]
            },
            'individual_results': individual_results[:5]  # First 5 for debugging
        }
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of all validations performed"""
        total = self.validation_stats['total_validations']
        if total == 0:
            return {'message': 'No validations performed yet'}
        
        success_rate = (self.validation_stats['passed_validations'] / total) * 100
        
        return {
            'total_validations': total,
            'passed_validations': self.validation_stats['passed_validations'],
            'failed_validations': self.validation_stats['failed_validations'],
            'success_rate': f"{success_rate:.2f}%",
            'common_issues': self.validation_stats['common_issues']
        }
    
    def suggest_fixes(self, validation_result: Dict[str, Any]) -> List[str]:
        """Suggest fixes for common validation issues"""
        suggestions = []
        
        if not validation_result.get('valid', False):
            if validation_result.get('dimension_issues', 0) > 0:
                suggestions.append("Check model configuration - dimension mismatch detected")
            
            if validation_result.get('quality_issues', 0) > 0:
                suggestions.append("Check input text preprocessing - quality issues detected")
            
            if validation_result.get('success_rate', 100) < 50:
                suggestions.append("Consider reprocessing the entire batch")
            
            # Check magnitude statistics
            mag_stats = validation_result.get('magnitude_stats', {})
            if mag_stats.get('std_deviation', 0) > 2.0:
                suggestions.append("High variance in embedding magnitudes - check text diversity")
        
        return suggestions