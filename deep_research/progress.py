"""
Research progress tracking and reporting.

This module provides functionality for tracking and reporting the progress of
research processes, including depth, breadth, and query execution metrics.
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ResearchProgress:
    """
    Track and report progress of the research process.

    This class provides real-time tracking of the research progress, including:
    - Depth and breadth of the research
    - Query counts and completion status
    - Elapsed time statistics
    """

    def __init__(self, initial_depth: int, initial_breadth: int):
        """
        Initialize research progress tracking.

        Args:
            initial_depth: Initial depth of the research (levels of follow-up queries)
            initial_breadth: Initial breadth of the research (parallel queries per level)
        """
        self.total_depth = initial_depth
        self.total_breadth = initial_breadth
        self.current_depth = initial_depth
        self.current_breadth = initial_breadth
        self.total_queries = 0
        self.completed_queries = 0
        self.current_query = ""
        self.start_time = datetime.now()

    def update(self, update_dict: Dict[str, Any]) -> None:
        """
        Update progress tracking with new values.

        Args:
            update_dict: Dictionary of attributes to update
        """
        for key, value in update_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self._report_progress()

    def _report_progress(self) -> None:
        """Log current progress information."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        progress_info = {
            "elapsedSeconds": elapsed,
            "currentDepth": self.current_depth,
            "totalDepth": self.total_depth,
            "currentBreadth": self.current_breadth,
            "totalBreadth": self.total_breadth,
            "completedQueries": self.completed_queries,
            "totalQueries": self.total_queries,
            "currentQuery": self.current_query,
            "completionPercentage": (self.completed_queries / max(1, self.total_queries)) * 100 if self.total_queries else 0
        }
        logger.info(f"Research Progress: {progress_info}")