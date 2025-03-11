"""
Tests for the content_classifier module.
"""

import pytest
from datetime import datetime, timedelta

from deep_research.content_classifier import ContentClassifier


class TestContentClassifier:
    """Tests for the ContentClassifier class."""

    @pytest.fixture
    def classifier(self):
        """Return a ContentClassifier instance for testing."""
        current_date = datetime(2024, 3, 15)
        return ContentClassifier(current_date)

    def test_classify_content_type_factual(self, classifier):
        """Test classifying factual content."""
        text = "The IBM quantum computer has 1,121 qubits. It was released in December 2023."
        result = classifier.classify_content_type(text)
        assert result == "factual"

    def test_classify_content_type_speculative(self, classifier):
        """Test classifying speculative content."""
        text = "Quantum computers could potentially break current encryption standards by 2030."
        result = classifier.classify_content_type(text)
        assert result == "speculative"

        text = "It is projected that quantum computing will reach commercial viability in the future."
        result = classifier.classify_content_type(text)
        assert result == "speculative"

    def test_classify_content_type_opinion(self, classifier):
        """Test classifying opinion content."""
        text = "I believe IBM's approach to quantum computing is superior to Google's strategy."
        result = classifier.classify_content_type(text)
        assert result == "opinion"

        text = "Experts suggest that trapped-ion qubits may offer advantages over superconducting qubits."
        result = classifier.classify_content_type(text)
        assert result == "opinion"

    def test_validate_temporal_consistency_valid(self, classifier):
        """Test validating temporally consistent content."""
        # Content with past events described as past
        text = "IBM released its 1,121-qubit processor in December 2023."
        is_valid, message = classifier.validate_temporal_consistency(text)
        assert is_valid is True

        # Content with future events described as upcoming (after current date)
        text = "The upcoming quantum computing conference in December 2024 will showcase new technologies."
        is_valid, message = classifier.validate_temporal_consistency(text)
        assert is_valid is True

        # Content with events scheduled for the future
        text = "Google has scheduled a major quantum computing announcement for January 2025."
        is_valid, message = classifier.validate_temporal_consistency(text)
        assert is_valid is True

    def test_validate_temporal_consistency_invalid(self, classifier):
        """Test validating temporally inconsistent content."""
        # Content with past events described as upcoming
        text = "The upcoming quantum computing conference in December 2023 will showcase new technologies."
        is_valid, message = classifier.validate_temporal_consistency(text)
        assert is_valid is False
        assert "refers to a past event as upcoming" in message

        # Content with past events described as scheduled
        text = "IBM has scheduled a major quantum computing announcement for January 2023."
        is_valid, message = classifier.validate_temporal_consistency(text)
        assert is_valid is False
        assert "refers to a scheduled event that should have already occurred" in message

    def test_validate_numerical_reasonableness_valid(self, classifier):
        """Test validating numerically reasonable content."""
        # Near-term projection with reasonable precision
        text = "Quantum computing market is expected to reach $2 billion by 2026."
        is_valid, message = classifier.validate_numerical_reasonableness(text)
        assert is_valid is True

        # Long-term projection without decimal precision
        text = "By 2040, the quantum computing industry could reach $50 billion in value."
        is_valid, message = classifier.validate_numerical_reasonableness(text)
        assert is_valid is True

    def test_validate_numerical_reasonableness_invalid(self, classifier):
        """Test validating numerically unreasonable content."""
        # Long-term projection with unreasonable precision
        text = "By 2035, the quantum computing market will reach exactly $42.75 billion."
        is_valid, message = classifier.validate_numerical_reasonableness(text)
        assert is_valid is False
        assert "Unreasonable precision" in message

    def test_classifier_with_current_date(self):
        """Test ContentClassifier using current date."""
        classifier = ContentClassifier()  # No date specified, should use current

        # This should be valid as it refers to a past event
        text = "IBM released its quantum processor in December 2023."
        is_valid, _ = classifier.validate_temporal_consistency(text)
        assert is_valid is True

        # Create a date in the future for testing
        future_date = datetime.now() + timedelta(days=365)
        future_month = future_date.strftime("%B").lower()
        future_year = future_date.year

        # This should be valid as it refers to a future event
        text = f"The upcoming quantum computing conference in {future_month} {future_year} will showcase new technologies."
        is_valid, _ = classifier.validate_temporal_consistency(text)
        assert is_valid is True