"""
Research memory management.

This module provides functionality for storing and managing research findings,
including learnings, sources, contradictions, and information maps.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ResearchMemory:
    """
    Store and manage research findings and context throughout the research process.

    This class provides a structured memory system for:
    - Tracking research learnings
    - Managing visited sources
    - Maintaining a reasoning chain of thought
    - Tracking information consensus, contradictions, and gaps
    - Evaluating source credibility and relevance
    """

    def __init__(self):
        """Initialize an empty research memory."""
        self.learnings: List[str] = []
        self.visited_urls: List[str] = []
        self.chain_of_thought: List[str] = []
        self.information_map: Dict[str, Dict] = {}  # Track consensus, contradictions, and gaps
        self.contradictions: List[Dict] = []  # Explicitly track contradictions
        self.source_evaluations: List[Dict] = []  # Track source evaluations
        self.current_date = datetime.now()  # Store current date for temporal validation

    def add_learning(self, learning: str) -> None:
        """
        Add a new learning to the research memory.

        Args:
            learning: New research learning to add
        """
        if learning not in self.learnings:
            self.learnings.append(learning)
            logger.info(f"New learning added: {learning[:100]}...")

    def add_learnings(self, new_learnings: List[str]) -> None:
        """
        Add multiple new learnings to the research memory.

        Args:
            new_learnings: List of new learnings to add
        """
        for learning in new_learnings:
            self.add_learning(learning)

    def add_url(self, url: str) -> None:
        """
        Add a visited URL to the research memory.

        Args:
            url: URL to add to visited sources
        """
        if url not in self.visited_urls:
            self.visited_urls.append(url)

    def add_urls(self, new_urls: List[str]) -> None:
        """
        Add multiple visited URLs to the research memory.

        Args:
            new_urls: List of URLs to add to visited sources
        """
        for url in new_urls:
            self.add_url(url)

    def add_thought(self, thought: str) -> None:
        """
        Add a reasoning step to the chain of thought.

        Args:
            thought: Reasoning step to add to the chain of thought
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.chain_of_thought.append(f"[{timestamp}] {thought}")
        logger.info(f"Chain of thought: {thought}")

    def add_contradiction(self, topic: str, claim1: str, claim2: str, source1: str = "", source2: str = "") -> None:
        """
        Add a detected contradiction to the research memory.

        Args:
            topic: Topic of the contradiction
            claim1: First conflicting claim
            claim2: Second conflicting claim
            source1: Source of the first claim (optional)
            source2: Source of the second claim (optional)
        """
        contradiction = {
            "topic": topic,
            "claim1": claim1,
            "claim2": claim2,
            "source1": source1,
            "source2": source2,
            "timestamp": datetime.now().isoformat()
        }
        self.contradictions.append(contradiction)
        self.add_thought(f"Contradiction detected in topic '{topic}': {claim1} vs {claim2}")

    def add_source_evaluation(self, evaluation: Dict) -> None:
        """
        Add a source evaluation to the research memory.

        Args:
            evaluation: Dictionary containing source evaluation data
        """
        self.source_evaluations.append(evaluation)

    def update_information_map(self, topic: str, info_type: str, content: Any) -> None:
        """
        Update the information map with new content.

        Args:
            topic: Topic to update in the information map
            info_type: Type of information (consensus, contradictions, gaps)
            content: Content to add to the information map
        """
        if topic not in self.information_map:
            self.information_map[topic] = {"consensus": [], "contradictions": [], "gaps": []}

        if info_type in self.information_map[topic]:
            if isinstance(content, list):
                self.information_map[topic][info_type].extend(content)
            else:
                self.information_map[topic][info_type].append(content)