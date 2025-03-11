"""
Tests for the auto_tuning module.
"""

import pytest
from unittest.mock import patch, MagicMock
import asyncio

from deep_research.auto_tuning import AutoTuner


class TestAutoTuner:
    """Tests for the AutoTuner class."""

    @pytest.fixture
    def auto_tuner(self):
        """Return an AutoTuner instance for testing."""
        return AutoTuner(max_depth=5, max_breadth=8, time_budget_seconds=300)

    @pytest.mark.asyncio
    async def test_analyze_question_complexity_simple(self, auto_tuner):
        """Test analyzing a simple question."""
        query = "What is quantum computing?"

        result = await auto_tuner.analyze_question_complexity(query)

        assert isinstance(result, dict)
        assert "complexity_score" in result
        assert 0 <= result["complexity_score"] <= 1
        assert result["complexity_score"] < 0.5  # Simple question should have low score

    @pytest.mark.asyncio
    async def test_analyze_question_complexity_complex(self, auto_tuner):
        """Test analyzing a complex question."""
        query = "Compare and contrast the quantum computing approaches of IBM, Google, and Microsoft, and analyze the implications for the development of quantum error correction techniques and their impact on the future of computational chemistry."

        result = await auto_tuner.analyze_question_complexity(query)

        assert isinstance(result, dict)
        assert "complexity_score" in result
        assert 0 <= result["complexity_score"] <= 1
        assert result["complexity_score"] > 0.5  # Complex question should have high score
        assert result["entity_count"] >= 3  # Should detect IBM, Google, Microsoft

    def test_determine_initial_parameters(self, auto_tuner):
        """Test determining initial parameters."""
        # Test with low complexity
        complexity_metrics = {"complexity_score": 0.2, "entity_count": 1, "aspect_count": 1,
                              "complexity_keyword_count": 0}
        depth, breadth = auto_tuner.determine_initial_parameters(complexity_metrics)

        assert 1 <= depth <= 5
        assert 2 <= breadth <= 8
        assert depth < auto_tuner.max_depth  # Should be less than max for low complexity

        # Test with high complexity
        complexity_metrics = {"complexity_score": 0.9, "entity_count": 5, "aspect_count": 4,
                              "complexity_keyword_count": 6}
        depth, breadth = auto_tuner.determine_initial_parameters(complexity_metrics)

        assert 1 <= depth <= 5
        assert 2 <= breadth <= 8
        assert depth == auto_tuner.max_depth or depth == auto_tuner.max_depth - 1  # Should be near max for high complexity

    def test_adjust_parameters_low_quality(self, auto_tuner):
        """Test parameter adjustment with low info quality."""
        current_depth = 3
        current_breadth = 4
        info_quality = 0.2  # Low quality
        time_usage_fraction = 0.4  # Not running out of time

        new_depth, new_breadth = auto_tuner.adjust_parameters(
            current_depth, current_breadth, info_quality, time_usage_fraction
        )

        # With low quality, should increase search (unless already at max)
        assert new_depth >= current_depth or new_depth == auto_tuner.max_depth
        assert new_breadth > current_breadth or new_breadth == auto_tuner.max_breadth

    def test_adjust_parameters_high_quality(self, auto_tuner):
        """Test parameter adjustment with high info quality."""
        current_depth = 3
        current_breadth = 4
        info_quality = 0.8  # High quality
        time_usage_fraction = 0.4  # Not running out of time

        new_depth, new_breadth = auto_tuner.adjust_parameters(
            current_depth, current_breadth, info_quality, time_usage_fraction
        )

        # With high quality, could potentially reduce search
        assert new_depth <= current_depth or new_depth == 1  # Don't go below 1
        assert new_breadth <= current_breadth or new_breadth == 2  # Don't go below 2

    def test_adjust_parameters_time_constraint(self, auto_tuner):
        """Test parameter adjustment with time constraint."""
        current_depth = 3
        current_breadth = 4
        info_quality = 0.5  # Medium quality
        time_usage_fraction = 0.8  # Running out of time

        new_depth, new_breadth = auto_tuner.adjust_parameters(
            current_depth, current_breadth, info_quality, time_usage_fraction
        )

        # Running out of time should reduce parameters
        assert new_depth < current_depth or new_depth == 1
        assert new_breadth < current_breadth or new_breadth == 2

    def test_estimate_info_quality(self, auto_tuner, sample_learnings):
        """Test estimating information quality."""
        # Test with good learnings and no contradictions
        quality = auto_tuner.estimate_info_quality(sample_learnings, [])
        assert 0 <= quality <= 1
        assert quality > 0.5  # Good learnings should have high quality

        # Test with contradictions
        contradictions = [
            {"topic": "Test", "claim1": "A", "claim2": "B"},
            {"topic": "Test2", "claim1": "X", "claim2": "Y"}
        ]
        quality_with_contradictions = auto_tuner.estimate_info_quality(sample_learnings, contradictions)
        assert quality_with_contradictions < quality  # Contradictions should lower quality

    def test_get_time_usage_fraction(self, auto_tuner):
        """Test getting time usage fraction."""
        # Test with no time budget
        auto_tuner.time_budget_seconds = None
        assert auto_tuner.get_time_usage_fraction() == 0.0

        # Test with time budget but no start time
        auto_tuner.time_budget_seconds = 300
        auto_tuner.start_time = None
        assert auto_tuner.get_time_usage_fraction() == 0.0

        # Test with time budget and start time
        auto_tuner.time_budget_seconds = 300
        # Mock the event loop time
        with patch('asyncio.get_event_loop') as mock_loop:
            mock_time = MagicMock()
            mock_loop.return_value.time.return_value = 150  # 150 seconds elapsed
            auto_tuner.start_time = 0  # Started at 0

            fraction = auto_tuner.get_time_usage_fraction()
            assert fraction == 0.5  # 150/300 = 0.5