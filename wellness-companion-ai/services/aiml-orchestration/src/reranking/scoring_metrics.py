
# ==== FILE 3: services/aiml-orchestration/src/reranking/scoring_metrics.py ====

"""
Scoring calculation utilities and metrics for confidence assessment.
Mathematical functions and algorithms for score computation.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime
import math
from enum import Enum

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of scoring metrics."""
    COSINE_SIMILARITY = "cosine_similarity"
    JACCARD_SIMILARITY = "jaccard_similarity"
    EUCLIDEAN_DISTANCE = "euclidean_distance"
    MANHATTAN_DISTANCE = "manhattan_distance"
    PEARSON_CORRELATION = "pearson_correlation"
    NORMALIZED_SCORE = "normalized_score"

@dataclass
class MetricResult:
    """Result of a metric calculation."""
    metric_type: MetricType
    score: float
    metadata: Dict[str, Any]
    calculation_time: float

class ScoringMetrics:
    """
    Utility class for various scoring and similarity calculations.
    """
    
    def __init__(self):
        self.calculation_stats = {
            'total_calculations': 0,
            'successful_calculations': 0,
            'failed_calculations': 0,
            'average_calculation_time': 0.0,
            'total_calculation_time': 0.0,
            'metric_usage_count': {}
        }

    def calculate_cosine_similarity(
        self,
        vector1: List[float],
        vector2: List[float]
    ) -> MetricResult:
        """Calculate cosine similarity between two vectors."""
        start_time = datetime.now()
        
        try:
            if len(vector1) != len(vector2):
                raise ValueError("Vectors must have the same length")
            
            vec1 = np.array(vector1)
            vec2 = np.array(vector2)
            
            # Calculate dot product
            dot_product = np.dot(vec1, vec2)
            
            # Calculate norms
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            # Handle zero vectors
            if norm1 == 0 or norm2 == 0:
                similarity = 0.0
            else:
                similarity = dot_product / (norm1 * norm2)
            
            calculation_time = (datetime.now() - start_time).total_seconds()
            
            result = MetricResult(
                metric_type=MetricType.COSINE_SIMILARITY,
                score=float(similarity),
                metadata={
                    'vector_length': len(vector1),
                    'dot_product': float(dot_product),
                    'norm1': float(norm1),
                    'norm2': float(norm2)
                },
                calculation_time=calculation_time
            )
            
            self._update_stats(True, calculation_time, MetricType.COSINE_SIMILARITY)
            return result
            
        except Exception as e:
            calculation_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(False, calculation_time, MetricType.COSINE_SIMILARITY)
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            
            return MetricResult(
                metric_type=MetricType.COSINE_SIMILARITY,
                score=0.0,
                metadata={'error': str(e)},
                calculation_time=calculation_time
            )

    def calculate_jaccard_similarity(
        self,
        set1: set,
        set2: set
    ) -> MetricResult:
        """Calculate Jaccard similarity between two sets."""
        start_time = datetime.now()
        
        try:
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            
            similarity = intersection / union if union > 0 else 0.0
            
            calculation_time = (datetime.now() - start_time).total_seconds()
            
            result = MetricResult(
                metric_type=MetricType.JACCARD_SIMILARITY,
                score=similarity,
                metadata={
                    'intersection_size': intersection,
                    'union_size': union,
                    'set1_size': len(set1),
                    'set2_size': len(set2)
                },
                calculation_time=calculation_time
            )
            
            self._update_stats(True, calculation_time, MetricType.JACCARD_SIMILARITY)
            return result
            
        except Exception as e:
            calculation_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(False, calculation_time, MetricType.JACCARD_SIMILARITY)
            logger.error(f"Error calculating Jaccard similarity: {str(e)}")
            
            return MetricResult(
                metric_type=MetricType.JACCARD_SIMILARITY,
                score=0.0,
                metadata={'error': str(e)},
                calculation_time=calculation_time
            )

    def calculate_euclidean_distance(
        self,
        vector1: List[float],
        vector2: List[float],
        normalize: bool = True
    ) -> MetricResult:
        """Calculate Euclidean distance between two vectors."""
        start_time = datetime.now()
        
        try:
            if len(vector1) != len(vector2):
                raise ValueError("Vectors must have the same length")
            
            vec1 = np.array(vector1)
            vec2 = np.array(vector2)
            
            distance = np.linalg.norm(vec1 - vec2)
            
            # Normalize to [0, 1] range if requested
            if normalize:
                max_possible_distance = np.sqrt(2 * len(vector1))  # Assuming vectors in [0, 1]
                distance = distance / max_possible_distance
            
            calculation_time = (datetime.now() - start_time).total_seconds()
            
            result = MetricResult(
                metric_type=MetricType.EUCLIDEAN_DISTANCE,
                score=float(distance),
                metadata={
                    'vector_length': len(vector1),
                    'normalized': normalize,
                    'raw_distance': float(np.linalg.norm(vec1 - vec2))
                },
                calculation_time=calculation_time
            )
            
            self._update_stats(True, calculation_time, MetricType.EUCLIDEAN_DISTANCE)
            return result
            
        except Exception as e:
            calculation_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(False, calculation_time, MetricType.EUCLIDEAN_DISTANCE)
            logger.error(f"Error calculating Euclidean distance: {str(e)}")
            
            return MetricResult(
                metric_type=MetricType.EUCLIDEAN_DISTANCE,
                score=1.0,  # Maximum distance on error
                metadata={'error': str(e)},
                calculation_time=calculation_time
            )

    def calculate_normalized_score(
        self,
        scores: List[float],
        method: str = 'min_max'
    ) -> List[float]:
        """Normalize scores using specified method."""
        if not scores:
            return []
        
        try:
            scores_array = np.array(scores)
            
            if method == 'min_max':
                min_score = np.min(scores_array)
                max_score = np.max(scores_array)
                if max_score == min_score:
                    return [0.5] * len(scores)  # All scores equal
                normalized = (scores_array - min_score) / (max_score - min_score)
            
            elif method == 'z_score':
                mean_score = np.mean(scores_array)
                std_score = np.std(scores_array)
                if std_score == 0:
                    return [0.5] * len(scores)  # No variance
                normalized = (scores_array - mean_score) / std_score
                # Convert to [0, 1] range using sigmoid
                normalized = 1 / (1 + np.exp(-normalized))
            
            elif method == 'softmax':
                exp_scores = np.exp(scores_array - np.max(scores_array))
                normalized = exp_scores / np.sum(exp_scores)
            
            else:
                logger.warning(f"Unknown normalization method: {method}, using min_max")
                return self.calculate_normalized_score(scores, 'min_max')
            
            return normalized.tolist()
            
        except Exception as e:
            logger.error(f"Error normalizing scores: {str(e)}")
            return scores  # Return original scores on error

    def calculate_weighted_score(
        self,
        scores: Dict[str, float],
        weights: Dict[str, float]
    ) -> float:
        """Calculate weighted score from multiple components."""
        try:
            total_weight = sum(weights.values())
            if total_weight == 0:
                return 0.0
            
            weighted_sum = sum(
                scores.get(component, 0) * weight
                for component, weight in weights.items()
            )
            
            return weighted_sum / total_weight
            
        except Exception as e:
            logger.error(f"Error calculating weighted score: {str(e)}")
            return 0.0

    def calculate_confidence_interval(
        self,
        scores: List[float],
        confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """Calculate confidence interval for scores."""
        try:
            if not scores:
                return (0.0, 0.0)
            
            scores_array = np.array(scores)
            mean = np.mean(scores_array)
            std_error = np.std(scores_array) / np.sqrt(len(scores))
            
            # Use t-distribution for small samples, normal for large
            if len(scores) < 30:
                from scipy import stats
                t_value = stats.t.ppf((1 + confidence_level) / 2, len(scores) - 1)
                margin_error = t_value * std_error
            else:
                # Normal approximation
                z_value = 1.96 if confidence_level == 0.95 else 2.58  # 95% or 99%
                margin_error = z_value * std_error
            
            lower_bound = mean - margin_error
            upper_bound = mean + margin_error
            
            return (float(lower_bound), float(upper_bound))
            
        except Exception as e:
            logger.error(f"Error calculating confidence interval: {str(e)}")
            mean_score = sum(scores) / len(scores) if scores else 0
            return (mean_score, mean_score)

    def calculate_rank_correlation(
        self,
        ranking1: List[int],
        ranking2: List[int]
    ) -> float:
        """Calculate Spearman rank correlation between two rankings."""
        try:
            if len(ranking1) != len(ranking2):
                raise ValueError("Rankings must have the same length")
            
            n = len(ranking1)
            if n == 0:
                return 0.0
            
            # Calculate rank differences
            d_squared = sum((r1 - r2) ** 2 for r1, r2 in zip(ranking1, ranking2))
            
            # Spearman correlation formula
            correlation = 1 - (6 * d_squared) / (n * (n ** 2 - 1))
            
            return float(correlation)
            
        except Exception as e:
            logger.error(f"Error calculating rank correlation: {str(e)}")
            return 0.0

    def calculate_score_distribution_metrics(
        self,
        scores: List[float]
    ) -> Dict[str, float]:
        """Calculate distribution metrics for a set of scores."""
        try:
            if not scores:
                return {}
            
            scores_array = np.array(scores)
            
            metrics = {
                'mean': float(np.mean(scores_array)),
                'median': float(np.median(scores_array)),
                'std_dev': float(np.std(scores_array)),
                'variance': float(np.var(scores_array)),
                'min': float(np.min(scores_array)),
                'max': float(np.max(scores_array)),
                'range': float(np.max(scores_array) - np.min(scores_array)),
                'q25': float(np.percentile(scores_array, 25)),
                'q75': float(np.percentile(scores_array, 75)),
                'iqr': float(np.percentile(scores_array, 75) - np.percentile(scores_array, 25)),
                'skewness': float(self._calculate_skewness(scores_array)),
                'kurtosis': float(self._calculate_kurtosis(scores_array))
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating score distribution metrics: {str(e)}")
            return {}

    def _calculate_skewness(self, scores: np.ndarray) -> float:
        """Calculate skewness of score distribution."""
        n = len(scores)
        if n < 3:
            return 0.0
        
        mean = np.mean(scores)
        std = np.std(scores)
        
        if std == 0:
            return 0.0
        
        skewness = np.sum(((scores - mean) / std) ** 3) / n
        return skewness

    def _calculate_kurtosis(self, scores: np.ndarray) -> float:
        """Calculate kurtosis of score distribution."""
        n = len(scores)
        if n < 4:
            return 0.0
        
        mean = np.mean(scores)
        std = np.std(scores)
        
        if std == 0:
            return 0.0
        
        kurtosis = np.sum(((scores - mean) / std) ** 4) / n - 3
        return kurtosis

    def _update_stats(self, success: bool, calculation_time: float, metric_type: MetricType):
        """Update calculation statistics."""
        self.calculation_stats['total_calculations'] += 1
        
        if success:
            self.calculation_stats['successful_calculations'] += 1
        else:
            self.calculation_stats['failed_calculations'] += 1
        
        self.calculation_stats['total_calculation_time'] += calculation_time
        self.calculation_stats['average_calculation_time'] = (
            self.calculation_stats['total_calculation_time'] / 
            self.calculation_stats['total_calculations']
        )
        
        # Track metric usage
        metric_name = metric_type.value
        self.calculation_stats['metric_usage_count'][metric_name] = (
            self.calculation_stats['metric_usage_count'].get(metric_name, 0) + 1
        )

    def get_calculation_statistics(self) -> Dict[str, Any]:
        """Get calculation performance statistics."""
        return {
            **self.calculation_stats,
            'success_rate': f"{(self.calculation_stats['successful_calculations'] / max(1, self.calculation_stats['total_calculations'])) * 100:.2f}%"
        }

    def benchmark_metrics(self, test_data: List[Tuple[List[float], List[float]]], iterations: int = 100) -> Dict[str, Dict[str, float]]:
        """Benchmark different similarity metrics."""
        results = {}
        
        for metric_name in ['cosine_similarity', 'euclidean_distance']:
            times = []
            for _ in range(iterations):
                for vec1, vec2 in test_data:
                    start_time = datetime.now()
                    
                    if metric_name == 'cosine_similarity':
                        self.calculate_cosine_similarity(vec1, vec2)
                    elif metric_name == 'euclidean_distance':
                        self.calculate_euclidean_distance(vec1, vec2)
                    
                    times.append((datetime.now() - start_time).total_seconds())
            
            results[metric_name] = {
                'avg_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times),
                'total_operations': len(times)
            }
        
        return results

