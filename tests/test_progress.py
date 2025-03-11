"""
Tests for the progress module.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from deep_research.progress import ResearchProgress


class TestResearchProgress:
    """Tests for the ResearchProgress class."""

    @pytest.fixture
    def progress(self):
        """Return a ResearchProgress instance for testing."""
        return ResearchProgress(initial_depth=3, initial_breadth=4)

    def test_initialization(self, progress):
        """Test initialization of the ResearchProgress class."""
        assert progress.total_depth == 3
        assert progress.total_breadth == 4
        assert progress.current_depth == 3
        assert progress.current_breadth == 4
        assert progress.total_queries == 0
        assert progress.completed_queries == 0
        assert progress.current_query == ""
        assert isinstance(progress.start_time, datetime)

    def test_update(self, progress):
        """Test updating progress tracking."""
        # Update with new values
        progress.update({
            "current_depth": 2,
            "current_breadth": 3,
            "total_queries": 6,
            "completed_queries": 2,
            "current_query": "quantum computing hardware"
        })

        assert progress.current_depth == 2
        assert progress.current_breadth == 3
        assert progress.total_queries == 6
        assert progress.completed_queries == 2
        assert progress.current_query == "quantum computing hardware"

        # Partial update should only change the specified attributes
        progress.update({
            "completed_queries": 4
        })

        assert progress.current_depth == 2  # Unchanged
        assert progress.current_breadth == 3  # Unchanged
        assert progress.total_queries == 6  # Unchanged
        assert progress.completed_queries == 4  # Updated
        assert progress.current_query == "quantum computing hardware"  # Unchanged

    def test_report_progress(self, progress):
        """Test reporting progress."""
        # Mock the logger to verify it was called with the right information
        with patch('deep_research.progress.logger') as mock_logger:
            # Set up test parameters
            progress.total_queries = 10
            progress.completed_queries = 5
            progress.current_query = "quantum computing hardware"

            # Call the report progress method indirectly through update
            progress.update({})

            # Verify logger was called
            mock_logger.info.assert_called_once()

            # Verify the log message contains the expected information
            log_message = mock_logger.info.call_args[0][0]
            assert "Research Progress" in log_message
            assert "completedQueries" in log_message
            assert "totalQueries" in log_message

            # The completion percentage should be 50% (5/10)
            assert "completionPercentage" in log_message
            assert "50" in log_message

    def test_completion_percentage_calculation(self, progress):
        """Test calculation of completion percentage."""
        # Test with zero total queries (should avoid division by zero)
        progress.total_queries = 0
        progress.completed_queries = 0

        with patch('deep_research.progress.logger') as mock_logger:
            progress.update({})

            # Verify logger was called
            mock_logger.info.assert_called_once()

            # Extract and verify the logged progress info
            log_message = mock_logger.info.call_args[0][0]
            assert "completionPercentage" in log_message
            assert "0" in log_message  # Should be 0% complete

            # Test with non-zero queries
            mock_logger.reset_mock()
            progress.total_queries = 8
            progress.completed_queries = 6

            progress.update({})

            # Verify logger was called again
            mock_logger.info.assert_called_once()

            # The completion percentage should be 75% (6/8)
            log_message = mock_logger.info.call_args[0][0]
            assert "completionPercentage" in log_message
            assert "75" in log_message

    def test_elapsed_time_tracking(self, progress):
        """Test tracking of elapsed time."""
        # Mock datetime.now to return a fixed time
        start_time = datetime(2024, 3, 10, 12, 0, 0)
        current_time = start_time + timedelta(minutes=5)  # 5 minutes later

        with patch('deep_research.progress.datetime') as mock_datetime:
            # Configure the mock to return our fixed times
            mock_datetime.now.return_value = current_time
            # Set the start time manually
            progress.start_time = start_time

            with patch('deep_research.progress.logger') as mock_logger:
                progress.update({})

                # Verify logger was called again
                mock_logger.info.assert_called_once()

                log_message = mock_logger.info.call_args[0][0]
                assert "elapsedSeconds" in log_message
                assert "300.0" in log_message
