"""
Content classification and validation.

This module provides functionality for classifying and validating content,
including factual/speculative classification, temporal consistency checks,
and numerical reasonableness validation.
"""

import re
from typing import Tuple
from datetime import datetime


class ContentClassifier:
    """
    Helper class to classify and validate content.

    This class provides methods to:
    - Classify content as factual, speculative, or opinion
    - Validate temporal consistency of content
    - Assess numerical reasonableness of projections
    """

    def __init__(self, current_date: datetime = None):
        """
        Initialize the content classifier.

        Args:
            current_date: Current date for temporal validation (optional)
        """
        self.current_date = current_date or datetime.now()

    def classify_content_type(self, text: str) -> str:
        """
        Classify content as factual, speculative, or opinion.

        Args:
            text: Content text to classify

        Returns:
            Classification as "factual", "speculative", or "opinion"
        """
        speculative_phrases = [
            r"(?i)could be", r"(?i)might be", r"(?i)potentially",
            r"(?i)possibly", r"(?i)projected", r"(?i)forecasted",
            r"(?i)expected to", r"(?i)anticipated", r"(?i)estimated",
            r"(?i)by 20\d\d", r"(?i)in the future"
        ]

        opinion_phrases = [
            r"(?i)believe", r"(?i)feel", r"(?i)think",
            r"(?i)suggest", r"(?i)indicate", r"(?i)likely",
            r"(?i)recommend", r"(?i)advocate", r"(?i)argue"
        ]

        for phrase in speculative_phrases:
            if re.search(phrase, text):
                return "speculative"

        for phrase in opinion_phrases:
            if re.search(phrase, text):
                return "opinion"

        return "factual"

    def validate_temporal_consistency(self, text: str) -> Tuple[bool, str]:
        """
        Check if dates/events in the text are temporally consistent with the current date.

        Args:
            text: Content text to validate

        Returns:
            Tuple of (is_valid, message) where is_valid is a boolean and message is an explanation
        """
        # Extract dates and events with their time frames
        upcoming_pattern = r"(?i)upcoming.{0,50}(january|february|march|april|may|june|july|august|september|october|november|december).{0,10}(20\d\d)"
        scheduled_pattern = r"(?i)scheduled.*?for.*?(january|february|march|april|may|june|july|august|september|october|november|december).*?(20\d\d)"
        date_pattern = r"(?i)(january|february|march|april|may|june|july|august|september|october|november|december).{0,10}(20\d\d)"

        # Check upcoming events
        upcoming_matches = re.finditer(upcoming_pattern, text)
        for match in upcoming_matches:
            month = match.group(1).lower()
            year = int(match.group(2))

            # Create a datetime object for the event
            month_num = ["january", "february", "march", "april", "may", "june",
                         "july", "august", "september", "october", "november", "december"].index(month) + 1
            event_date = datetime(year, month_num, 1)  # Using day 1 as default

            # Check if the event is actually in the future
            if event_date < self.current_date:
                return False, f"Temporal inconsistency: '{match.group(0)}' refers to a past event as upcoming"

        # Check scheduled events
        scheduled_matches = re.finditer(scheduled_pattern, text)
        for match in scheduled_matches:
            month = match.group(1).lower()
            year = int(match.group(2))

            month_num = ["january", "february", "march", "april", "may", "june",
                         "july", "august", "september", "october", "november", "december"].index(month) + 1
            event_date = datetime(year, month_num, 1)  # Using day 1 as default

            # Check if the event is in the past
            if event_date < self.current_date:
                return False, f"Temporal inconsistency: '{match.group(0)}' refers to a scheduled event that should have already occurred"

        return True, "No temporal inconsistencies detected"

    def validate_numerical_reasonableness(self, text: str) -> Tuple[bool, str]:
        """
        Check if numerical projections or estimates are reasonable.

        Args:
            text: Content text to validate

        Returns:
            Tuple of (is_valid, message) where is_valid is a boolean and message is an explanation
        """
        # Look for very precise long-term projections
        #long_term_projection_pattern = r"(?i)(by|in|reach|hitting).{0,10}(20[3-9]\d).{0,30}\$?([0-9,]+\.[0-9]+)"
        long_term_projection_pattern = r"(?i)(by|in|reach|hitting).{0,20}(20[3-9]\d).{0,50}\$?([0-9,]+\.[0-9]+)"

        matches = re.finditer(long_term_projection_pattern, text)
        for match in matches:
            year = int(match.group(2))
            value = match.group(3).replace(',', '')

            # Check if the projection is too precise for the time frame
            years_ahead = year - self.current_date.year
            if years_ahead > 10 and '.' in value:
                return False, f"Unreasonable precision: '{match.group(0)}' has decimal precision for a {years_ahead}-year forecast"

        return True, "No unreasonable numerical projections detected"