# ==== FILE 1: services/aiml-orchestration/src/reranking/confidence_scorer.py ====

"""
Confidence calculation algorithms for RAG results.
Determines confidence scores and fallback triggers.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import math

logger = logging.getLogger(__name__)

@dataclass
class ConfidenceMetrics:
    """Confidence calculation metrics."""
    overall_confidence: float
    component_scores: Dict[str, float]
    confidence_level: str
    fallback_recommended: bool
    calculation_details: Dict[str, Any]

class ConfidenceScorer:
    """
    Calculates confidence scores for RAG pipeline results.
    """
    
    def __init__(self):
        # Confidence thresholds
        self.thresholds = {
            'very_high': 0.9,
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4,
            'very_low': 0.2,
            'fallback': 0.7  # Below this triggers web search
        }
        
        # Component weights for final confidence
        self.weights = {
            'retrieval_quality': 0.3,
            'context_relevance': 0.25,
            'response_quality': 0.2,
            'source_diversity': 0.1,
            'query_clarity': 0.1,
            'system_performance': 0.05
        }
        
        self.scoring_stats = {
            'total_scores_calculated': 0,
            'high_confidence_scores': 0,
            'medium_confidence_scores': 0,
            'low_confidence_scores': 0,
            'fallback_triggers': 0,
            'average_confidence': 0.0,
            'total_confidence': 0.0
        }

    def calculate_confidence(
        self,
        retrieval_result: Any = None,
        response_result: Any = None,
        query_analysis: Any = None,
        system_metrics: Dict[str, Any] = None
    ) -> ConfidenceMetrics:
        """
        Calculate comprehensive confidence score.
        
        Args:
            retrieval_result: Results from retrieval phase
            response_result: Results from response synthesis
            query_analysis: Query analysis results
            system_metrics: System performance metrics
            
        Returns:
            ConfidenceMetrics with detailed confidence analysis
        """
        try:
            # Component confidence scores
            component_scores = {}
            
            # 1. Retrieval Quality Score
            component_scores['retrieval_quality'] = self._score_retrieval_quality(retrieval_result)
            
            # 2. Context Relevance Score
            component_scores['context_relevance'] = self._score_context_relevance(retrieval_result)
            
            # 3. Response Quality Score
            component_scores['response_quality'] = self._score_response_quality(response_result)
            
            # 4. Source Diversity Score
            component_scores['source_diversity'] = self._score_source_diversity(retrieval_result)
            
            # 5. Query Clarity Score
            component_scores['query_clarity'] = self._score_query_clarity(query_analysis)
            
            # 6. System Performance Score
            component_scores['system_performance'] = self._score_system_performance(system_metrics)
            
            # Calculate weighted overall confidence
            overall_confidence = sum(
                score * self.weights[component]
                for component, score in component_scores.items()
                if component in self.weights
            )
            
            # Apply confidence boosting/penalties
            overall_confidence = self._apply_confidence_adjustments(
                overall_confidence, component_scores
            )
            
            # Determine confidence level and fallback recommendation
            confidence_level = self._get_confidence_level(overall_confidence)
            fallback_recommended = overall_confidence < self.thresholds['fallback']
            
            # Prepare calculation details
            calculation_details = {
                'timestamp': datetime.now().isoformat(),
                'component_weights': self.weights,
                'thresholds_used': self.thresholds,
                'adjustments_applied': self._get_adjustment_details(component_scores),
                'raw_weighted_score': sum(
                    score * self.weights[component]
                    for component, score in component_scores.items()
                    if component in self.weights
                )
            }
            
            # Update statistics
            self._update_stats(overall_confidence, fallback_recommended)
            
            confidence_metrics = ConfidenceMetrics(
                overall_confidence=max(0.0, min(1.0, overall_confidence)),
                component_scores=component_scores,
                confidence_level=confidence_level,
                fallback_recommended=fallback_recommended,
                calculation_details=calculation_details
            )
            
            logger.debug(f"Confidence calculated: {overall_confidence:.2f} ({confidence_level})")
            
            return confidence_metrics
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return self._create_error_confidence(str(e))

    def _score_retrieval_quality(self, retrieval_result: Any) -> float:
        """Score the quality of retrieval results."""
        if not retrieval_result:
            return 0.0
        
        score = 0.5  # Base score
        
        try:
            # Number of results found
            if hasattr(retrieval_result, 'search_results'):
                result_count = len(retrieval_result.search_results)
                if result_count >= 3:
                    score += 0.2
                elif result_count >= 1:
                    score += 0.1
            
            # Retrieval confidence from the retrieval system
            if hasattr(retrieval_result, 'retrieval_confidence'):
                retrieval_conf = retrieval_result.retrieval_confidence
                score += retrieval_conf * 0.3
            
            # Average relevance score of results
            if hasattr(retrieval_result, 'search_results'):
                relevance_scores = []
                for result in retrieval_result.search_results:
                    if isinstance(result, dict) and 'score' in result:
                        relevance_scores.append(result['score'])
                
                if relevance_scores:
                    avg_relevance = sum(relevance_scores) / len(relevance_scores)
                    score += avg_relevance * 0.2
            
        except Exception as e:
            logger.warning(f"Error scoring retrieval quality: {str(e)}")
        
        return min(1.0, score)

    def _score_context_relevance(self, retrieval_result: Any) -> float:
        """Score the relevance of assembled context."""
        if not retrieval_result:
            return 0.0
        
        score = 0.3  # Base score
        
        try:
            if hasattr(retrieval_result, 'assembled_context'):
                context = retrieval_result.assembled_context
                
                # Context availability
                if hasattr(context, 'context_text') and context.context_text.strip():
                    score += 0.2
                
                # Context relevance score
                if hasattr(context, 'relevance_score'):
                    score += context.relevance_score * 0.3
                
                # Context completeness (chunk count)
                if hasattr(context, 'total_chunks'):
                    chunk_count = context.total_chunks
                    if chunk_count >= 3:
                        score += 0.15
                    elif chunk_count >= 1:
                        score += 0.1
                
                # Token efficiency
                if hasattr(context, 'total_tokens'):
                    tokens = context.total_tokens
                    if 100 <= tokens <= 2000:  # Optimal range
                        score += 0.05
                    elif 50 <= tokens < 100 or 2000 < tokens <= 3000:
                        score += 0.02
            
        except Exception as e:
            logger.warning(f"Error scoring context relevance: {str(e)}")
        
        return min(1.0, score)

    def _score_response_quality(self, response_result: Any) -> float:
        """Score the quality of generated response."""
        if not response_result:
            return 0.0
        
        score = 0.4  # Base score
        
        try:
            # Response length appropriateness
            if hasattr(response_result, 'response_text'):
                response_length = len(response_result.response_text)
                if 50 <= response_length <= 500:  # Optimal range
                    score += 0.2
                elif 20 <= response_length < 50 or 500 < response_length <= 1000:
                    score += 0.1
            
            # Response confidence from synthesis
            if hasattr(response_result, 'confidence'):
                synthesis_conf = response_result.confidence
                score += synthesis_conf * 0.3
            
            # Processing time efficiency
            if hasattr(response_result, 'processing_time'):
                proc_time = response_result.processing_time
                if proc_time <= 2.0:  # Fast response
                    score += 0.1
                elif proc_time <= 5.0:  # Acceptable response
                    score += 0.05
            
        except Exception as e:
            logger.warning(f"Error scoring response quality: {str(e)}")
        
        return min(1.0, score)

    def _score_source_diversity(self, retrieval_result: Any) -> float:
        """Score the diversity of information sources."""
        if not retrieval_result:
            return 0.5  # Neutral score when no retrieval data
        
        score = 0.3  # Base score
        
        try:
            if hasattr(retrieval_result, 'assembled_context'):
                context = retrieval_result.assembled_context
                
                if hasattr(context, 'sources'):
                    unique_sources = len(set(context.sources))
                    if unique_sources >= 3:
                        score += 0.4
                    elif unique_sources >= 2:
                        score += 0.3
                    elif unique_sources >= 1:
                        score += 0.2
            
        except Exception as e:
            logger.warning(f"Error scoring source diversity: {str(e)}")
        
        return min(1.0, score)

    def _score_query_clarity(self, query_analysis: Any) -> float:
        """Score the clarity and quality of the query."""
        if not query_analysis:
            return 0.5  # Neutral score when no query analysis
        
        score = 0.4  # Base score
        
        try:
            # Query confidence from analysis
            if hasattr(query_analysis, 'confidence'):
                query_conf = query_analysis.confidence
                score += query_conf * 0.3
            
            # Intent clarity
            if hasattr(query_analysis, 'intent'):
                intent = query_analysis.intent
                if intent not in ['unknown', 'unclear']:
                    score += 0.2
            
            # Keyword extraction success
            if hasattr(query_analysis, 'keywords'):
                keyword_count = len(query_analysis.keywords)
                if keyword_count >= 2:
                    score += 0.1
            
        except Exception as e:
            logger.warning(f"Error scoring query clarity: {str(e)}")
        
        return min(1.0, score)

    def _score_system_performance(self, system_metrics: Dict[str, Any]) -> float:
        """Score overall system performance."""
        if not system_metrics:
            return 0.8  # Assume good performance when no metrics
        
        score = 0.5  # Base score
        
        try:
            # Response time performance
            if 'response_time' in system_metrics:
                resp_time = system_metrics['response_time']
                if resp_time <= 1.0:
                    score += 0.3
                elif resp_time <= 3.0:
                    score += 0.2
                elif resp_time <= 5.0:
                    score += 0.1
            
            # Error rates
            if 'error_rate' in system_metrics:
                error_rate = system_metrics['error_rate']
                if error_rate <= 0.01:  # Less than 1% errors
                    score += 0.2
                elif error_rate <= 0.05:  # Less than 5% errors
                    score += 0.1
            
        except Exception as e:
            logger.warning(f"Error scoring system performance: {str(e)}")
        
        return min(1.0, score)

    def _apply_confidence_adjustments(
        self, 
        base_confidence: float, 
        component_scores: Dict[str, float]
    ) -> float:
        """Apply confidence boosting or penalties."""
        adjusted_confidence = base_confidence
        
        # Boost for high-quality components
        if component_scores.get('retrieval_quality', 0) >= 0.8:
            adjusted_confidence += 0.05
        
        if component_scores.get('context_relevance', 0) >= 0.8:
            adjusted_confidence += 0.05
        
        # Penalty for poor retrieval
        if component_scores.get('retrieval_quality', 0) <= 0.3:
            adjusted_confidence -= 0.1
        
        # Penalty for poor context
        if component_scores.get('context_relevance', 0) <= 0.3:
            adjusted_confidence -= 0.1
        
        return adjusted_confidence

    def _get_adjustment_details(self, component_scores: Dict[str, float]) -> List[str]:
        """Get details about confidence adjustments applied."""
        adjustments = []
        
        if component_scores.get('retrieval_quality', 0) >= 0.8:
            adjustments.append("High quality retrieval boost (+0.05)")
        
        if component_scores.get('context_relevance', 0) >= 0.8:
            adjustments.append("High context relevance boost (+0.05)")
        
        if component_scores.get('retrieval_quality', 0) <= 0.3:
            adjustments.append("Poor retrieval penalty (-0.1)")
        
        if component_scores.get('context_relevance', 0) <= 0.3:
            adjustments.append("Poor context penalty (-0.1)")
        
        return adjustments

    def _get_confidence_level(self, confidence: float) -> str:
        """Get human-readable confidence level."""
        if confidence >= self.thresholds['very_high']:
            return 'very_high'
        elif confidence >= self.thresholds['high']:
            return 'high'
        elif confidence >= self.thresholds['medium']:
            return 'medium'
        elif confidence >= self.thresholds['low']:
            return 'low'
        else:
            return 'very_low'

    def _create_error_confidence(self, error: str) -> ConfidenceMetrics:
        """Create error confidence metrics."""
        return ConfidenceMetrics(
            overall_confidence=0.0,
            component_scores={},
            confidence_level='very_low',
            fallback_recommended=True,
            calculation_details={
                'error': error,
                'timestamp': datetime.now().isoformat()
            }
        )

    def _update_stats(self, confidence: float, fallback_recommended: bool):
        """Update confidence scoring statistics."""
        self.scoring_stats['total_scores_calculated'] += 1
        self.scoring_stats['total_confidence'] += confidence
        self.scoring_stats['average_confidence'] = (
            self.scoring_stats['total_confidence'] / 
            self.scoring_stats['total_scores_calculated']
        )
        
        if confidence >= self.thresholds['high']:
            self.scoring_stats['high_confidence_scores'] += 1
        elif confidence >= self.thresholds['medium']:
            self.scoring_stats['medium_confidence_scores'] += 1
        else:
            self.scoring_stats['low_confidence_scores'] += 1
        
        if fallback_recommended:
            self.scoring_stats['fallback_triggers'] += 1

    def get_scoring_statistics(self) -> Dict[str, Any]:
        """Get confidence scoring statistics."""
        total = self.scoring_stats['total_scores_calculated']
        return {
            **self.scoring_stats,
            'high_confidence_rate': f"{(self.scoring_stats['high_confidence_scores'] / max(1, total)) * 100:.2f}%",
            'medium_confidence_rate': f"{(self.scoring_stats['medium_confidence_scores'] / max(1, total)) * 100:.2f}%",
            'low_confidence_rate': f"{(self.scoring_stats['low_confidence_scores'] / max(1, total)) * 100:.2f}%",
            'fallback_trigger_rate': f"{(self.scoring_stats['fallback_triggers'] / max(1, total)) * 100:.2f}%"
        }

    def calibrate_thresholds(self, performance_data: List[Dict[str, Any]]):
        """Calibrate confidence thresholds based on performance data."""
        if not performance_data:
            return
        
        # Analyze performance data to optimize thresholds
        confidence_scores = [data.get('confidence', 0) for data in performance_data]
        actual_quality = [data.get('quality_score', 0) for data in performance_data]
        
        if len(confidence_scores) >= 10:  # Minimum data for calibration
            # Calculate optimal thresholds using statistical analysis
            sorted_pairs = sorted(zip(confidence_scores, actual_quality))
            
            # Update fallback threshold based on accuracy analysis
            optimal_fallback = self._find_optimal_threshold(sorted_pairs, target_accuracy=0.85)
            if optimal_fallback:
                self.thresholds['fallback'] = optimal_fallback
                logger.info(f"Calibrated fallback threshold to {optimal_fallback:.2f}")

    def _find_optimal_threshold(self, sorted_pairs: List[Tuple[float, float]], target_accuracy: float) -> Optional[float]:
        """Find optimal threshold for target accuracy."""
        best_threshold = None
        best_accuracy = 0
        
        for i in range(len(sorted_pairs)):
            threshold = sorted_pairs[i][0]
            
            # Calculate accuracy at this threshold
            true_positives = sum(1 for conf, qual in sorted_pairs[i:] if qual >= target_accuracy)
            false_positives = sum(1 for conf, qual in sorted_pairs[i:] if qual < target_accuracy)
            
            if true_positives + false_positives > 0:
                accuracy = true_positives / (true_positives + false_positives)
                
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_threshold = threshold
        
        return best_threshold
