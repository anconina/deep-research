"""
Public API for the deep research system.

This module provides the main entry points for using the deep research system,
including functions for executing research and generating reports.
"""

import logging
from typing import Dict, Optional

from .engine import ResearchEngine
from .reporting import write_chain_of_thought_report, write_final_report

logger = logging.getLogger(__name__)

async def deep_research(query: str, breadth: Optional[int] = None, depth: Optional[int] = None,
                      auto_tune: bool = False, max_depth: int = 5,
                      max_breadth: int = 8, time_budget_seconds: Optional[int] = None) -> Dict:
    """
    Execute the deep research process and return the results.

    This function serves as the main entry point for the deep research system.
    It initializes the research engine, executes the research process, and
    returns the results in a structured format.

    Args:
        query: The research question or topic
        breadth: How many parallel queries to explore (breadth of research)
                If None and auto_tune is True, breadth will be determined automatically.
        depth: How many levels of follow-up queries to explore (depth of research)
               If None and auto_tune is True, depth will be determined automatically.
        auto_tune: Whether to automatically determine research parameters
        max_depth: Maximum allowed research depth when auto-tuning
        max_breadth: Maximum allowed research breadth when auto-tuning
        time_budget_seconds: Optional time budget in seconds for auto-tuning

    Returns:
        Dictionary containing research results, including:
        - learnings: List of research learnings
        - visited_urls: List of visited URLs
        - chain_of_thought: List of reasoning steps
        - information_map: Dictionary mapping topics to consensus, contradictions, and gaps
        - contradictions: List of detected contradictions
        - source_evaluations: List of source evaluations
    """
    try:
        # Initialize the research engine with auto-tuning if enabled
        engine = ResearchEngine(
            auto_tune=auto_tune,
            max_depth=max_depth,
            max_breadth=max_breadth,
            time_budget_seconds=time_budget_seconds
        )

        # Execute the research process
        result = await engine.deep_research(query=query, breadth=breadth, depth=depth)

        return result

    except Exception as e:
        logger.error(f"Critical error in deep research: {str(e)}")
        return {
            "learnings": [f"Research error: {str(e)}"],
            "visited_urls": [],
            "chain_of_thought": [f"Critical error in research process: {str(e)}"]
        }

__all__ = ['deep_research', 'write_chain_of_thought_report', 'write_final_report']