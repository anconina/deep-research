"""
Deep Research - An automated multi-step research system.

This package provides functionality for executing deep, multi-step research
with iterative refinement, source evaluation, and result synthesis.
"""

__version__ = "1.0.0"

# Import main API functions for easy access
from deep_research.api import deep_research, write_final_report, write_chain_of_thought_report

# Export main classes for advanced usage
from deep_research.engine import ResearchEngine
from deep_research.memory import ResearchMemory
from deep_research.progress import ResearchProgress
from deep_research.content_classifier import ContentClassifier