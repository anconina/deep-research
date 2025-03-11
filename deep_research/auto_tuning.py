"""
Automatic parameter tuning for the research process.

This module provides functionality for automatically determining optimal
research parameters such as depth and breadth based on question complexity,
information availability, and resource constraints.
"""

import re
import logging
import asyncio
from typing import Dict, Tuple, List

logger = logging.getLogger(__name__)


class AutoTuner:
    """
    Automatically tune research parameters based on dynamic factors.

    This class analyzes various factors to determine optimal research
    parameters, including:
    - Question complexity and breadth
    - Information availability and quality
    - Time and computational resource constraints
    """

    def __init__(self, max_depth: int = 5, max_breadth: int = 8,
                 time_budget_seconds: int = None):
        """
        Initialize the automatic parameter tuner.

        Args:
            max_depth: Maximum allowed research depth
            max_breadth: Maximum allowed research breadth
            time_budget_seconds: Optional time budget in seconds
        """
        self.max_depth = max_depth
        self.max_breadth = max_breadth
        self.time_budget_seconds = time_budget_seconds
        self.start_time = None

    async def analyze_question_complexity(self, query: str) -> Dict[str, float]:
        """
        Analyze the complexity of a research question.

        Args:
            query: The research question

        Returns:
            Dictionary with complexity metrics
        """
        # Count entities, topics and concepts
        entity_pattern = r'([A-Z][a-z]+ [A-Z][a-z]+|[A-Z][a-z]+\.[A-Z][a-z]+|[A-Z][A-Z]+|[A-Z][a-z]+)'
        entities = re.findall(entity_pattern, query)

        # Count specific question aspects
        aspects = query.count(',') + query.count(';') + query.count('and')

        # Count specific keywords that indicate complexity
        complexity_keywords = ['compare', 'contrast', 'analyze', 'evaluate',
                               'synthesize', 'implications', 'impact', 'effects',
                               'trend', 'development', 'causes', 'relationship']

        keyword_count = sum(1 for word in complexity_keywords if word in query.lower())

        # Calculate weighted complexity score
        complexity_score = (len(entities) * 0.5) + (aspects * 0.3) + (keyword_count * 0.7)

        # Normalize to 0-1 range for easier interpretation
        normalized_score = min(1.0, complexity_score / 10.0)

        return {
            "complexity_score": normalized_score,
            "entity_count": len(entities),
            "aspect_count": aspects,
            "complexity_keyword_count": keyword_count
        }

    def determine_initial_parameters(self, complexity_metrics: Dict[str, float]) -> Tuple[int, int]:
        """
        Determine initial research depth and breadth based on question complexity.

        Args:
            complexity_metrics: Metrics from analyze_question_complexity

        Returns:
            Tuple of (depth, breadth)
        """
        complexity_score = complexity_metrics["complexity_score"]

        # Scale depth and breadth based on complexity score
        depth = max(1, min(self.max_depth, round(1 + complexity_score * (self.max_depth - 1))))
        breadth = max(2, min(self.max_breadth, round(2 + complexity_score * (self.max_breadth - 2))))

        logger.info(f"Auto-tuned initial parameters - Depth: {depth}, Breadth: {breadth} " +
                    f"(complexity score: {complexity_score:.2f})")

        return depth, breadth

    def adjust_parameters(self, current_depth: int, current_breadth: int,
                          info_quality: float, time_usage_fraction: float) -> Tuple[int, int]:
        """
        Adjust research parameters based on ongoing research results.

        Args:
            current_depth: Current research depth
            current_breadth: Current research breadth
            info_quality: Measure of information quality (0-1)
            time_usage_fraction: Fraction of time budget used (0-1)

        Returns:
            Tuple of (new_depth, new_breadth)
        """
        # Base adjustments on information quality
        if info_quality < 0.3:
            # Low quality information - expand search
            depth_adjustment = 1
            breadth_adjustment = 2
        elif info_quality > 0.7:
            # High quality information - can potentially reduce search
            depth_adjustment = -1
            breadth_adjustment = -1
        else:
            # Moderate quality - minor adjustments
            depth_adjustment = 0
            breadth_adjustment = 1

        # Consider time budget constraints
        if time_usage_fraction > 0.7:
            # Running out of time, reduce parameters
            depth_adjustment -= 1
            breadth_adjustment -= 2

        # Apply adjustments with constraints
        new_depth = max(1, min(self.max_depth, current_depth + depth_adjustment))
        new_breadth = max(2, min(self.max_breadth, current_breadth + breadth_adjustment))

        return new_depth, new_breadth

    def estimate_info_quality(self, learnings: List[str], contradictions: List[Dict]) -> float:
        """
        Estimate the quality of information gathered so far.

        Args:
            learnings: List of research learnings
            contradictions: List of detected contradictions

        Returns:
            Quality score between 0 and 1
        """
        # Calculate quality metrics
        if not learnings:
            return 0.0

        # Average learning length (longer often means more detailed)
        avg_length = sum(len(l) for l in learnings) / len(learnings)
        length_score = min(1.0, avg_length / 300)  # Normalize with 300 chars as "good" length

        # Contradiction ratio (fewer contradictions relative to learnings is better)
        contradiction_ratio = len(contradictions) / max(1, len(learnings))
        contradiction_score = max(0, 1 - (contradiction_ratio * 2))  # Lower is better

        # Diversity of content (estimate based on unique words)
        all_text = " ".join(learnings)
        unique_words = len(set(all_text.lower().split()))
        total_words = len(all_text.split())
        diversity_score = min(1.0, unique_words / max(1, total_words) * 3)  # Higher ratio is better

        # Calculate weighted quality score
        quality_score = (length_score * 0.3) + (contradiction_score * 0.3) + (diversity_score * 0.4)

        return quality_score

    def get_time_usage_fraction(self) -> float:
        """
        Calculate the fraction of time budget used.

        Returns:
            Fraction between 0 and 1, or 0.0 if no time budget specified
        """
        if self.time_budget_seconds is None or self.start_time is None:
            return 0.0

        elapsed = (asyncio.get_event_loop().time() - self.start_time)
        return min(1.0, elapsed / self.time_budget_seconds)