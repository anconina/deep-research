"""
Report generation functionality.

This module provides functions for generating reports based on research results,
including chain of thought reports and final comprehensive reports.
"""

import logging
from typing import Dict, List
from datetime import datetime

from deep_research.llm import trim_prompt, generate_object
from deep_research.prompts import system_prompt, get_prompt
from deep_research.models import (
    Report,
    ChainOfThoughtSummary
)

logger = logging.getLogger(__name__)


async def write_chain_of_thought_report(chain_of_thought: List[str]) -> str:
    """
    Generate a detailed chain-of-thought report from the research process.

    Args:
        chain_of_thought: List of reasoning steps from the research process

    Returns:
        Formatted chain of thought report as a string
    """
    chain_of_thought_string = "\n".join(chain_of_thought)

    # Generate prompt using the centralized prompt management
    prompt_text = get_prompt(
        prompt_type="enhanced_chain_of_thought",
        chain_of_thought_string=chain_of_thought_string
    )

    try:
        res = await generate_object(
            model="gpt-4o",
            system="You are an expert Chain of Thought analyst",
            prompt=prompt_text,
            schema=ChainOfThoughtSummary,
        )

        report = ChainOfThoughtSummary.model_validate_json(res)
        return report.summary

    except Exception as e:
        logger.error(f"Error generating chain of thought report: {str(e)}")
        return f"Error generating report: {str(e)}"


async def write_final_report(prompt: str, learnings: List[str], information_map: Dict = None,
                             contradictions: List[Dict] = None, source_evaluations: List[Dict] = None) -> str:
    """
    Generate the final comprehensive research report with attention to data quality issues.

    Args:
        prompt: The original research question or topic
        learnings: List of research learnings
        information_map: Dictionary mapping topics to consensus, contradictions, and gaps
        contradictions: List of contradiction dictionaries
        source_evaluations: List of source evaluation dictionaries

    Returns:
        Formatted final report as a string
    """
    # Format learnings for the prompt
    learnings_string = trim_prompt(
        "\n".join([f"<learning>\n{learning}\n</learning>" for learning in learnings]), 180000
    )

    # Include information map if available
    information_map_string = ""
    if information_map:
        map_sections = []
        for topic, data in information_map.items():
            section = f"<topic>{topic}</topic>\n"

            if data.get("consensus"):
                section += "<consensus>\n"
                section += "\n".join([f"- {item}" for item in data["consensus"]])
                section += "\n</consensus>\n"

            if data.get("contradictions"):
                section += "<contradictions>\n"
                section += "\n".join([f"- {item}" for item in data["contradictions"]])
                section += "\n</contradictions>\n"

            if data.get("gaps"):
                section += "<gaps>\n"
                section += "\n".join([f"- {item}" for item in data["gaps"]])
                section += "\n</gaps>\n"

            map_sections.append(section)

        information_map_string = "\n**Information Map:**\n" + "\n".join(map_sections)

    # Include contradictions if available
    contradictions_string = ""
    if contradictions:
        contradictions_string = "\n**Detected Contradictions:**\n<contradictions>\n"
        for i, contradiction in enumerate(contradictions):
            contradictions_string += f"{i + 1}. Topic: {contradiction.get('topic')}\n"
            contradictions_string += f"   Claim 1: {contradiction.get('claim1')}\n"
            contradictions_string += f"   Claim 2: {contradiction.get('claim2')}\n"
            if contradiction.get('source1') or contradiction.get('source2'):
                contradictions_string += f"   Sources: {contradiction.get('source1')} vs {contradiction.get('source2')}\n"
            contradictions_string += "\n"
        contradictions_string += "</contradictions>\n"

    # Include source evaluations if available
    evaluations_string = ""
    if source_evaluations:
        evaluations_string = "\n**Source Evaluations:**\n<evaluations>\n"
        high_credibility_sources = [e for e in source_evaluations if e.get('credibility_rating') == 'high']
        medium_credibility_sources = [e for e in source_evaluations if e.get('credibility_rating') == 'medium']
        low_credibility_sources = [e for e in source_evaluations if e.get('credibility_rating') == 'low']

        if high_credibility_sources:
            evaluations_string += "High Credibility Sources:\n"
            for e in high_credibility_sources[:3]:  # Limit to top 3 for brevity
                evaluations_string += f"- {e.get('title') or e.get('url')}: {e.get('justification')[:100]}...\n"

        if low_credibility_sources:
            evaluations_string += "\nLow Credibility Sources (used with caution):\n"
            for e in low_credibility_sources[:3]:  # Limit to top 3 for brevity
                evaluations_string += f"- {e.get('title') or e.get('url')}: {e.get('justification')[:100]}...\n"

        evaluations_string += "</evaluations>\n"

    current_date = datetime.now().strftime("%Y-%m-%d")

    # Generate prompt using the centralized prompt management
    prompt_text = get_prompt(
        prompt_type="enhanced_report",
        prompt=prompt,
        learnings_string=learnings_string,
        current_date=current_date,
        information_map_string=information_map_string,
        contradictions_string=contradictions_string,
        evaluations_string=evaluations_string
    )

    try:
        res = await generate_object(
            model="o3-mini",
            system=system_prompt(),
            prompt=prompt_text,
            schema=Report,
        )

        report = Report.model_validate_json(res)
        return report.markdown

    except Exception as e:
        logger.error(f"Error generating final report: {str(e)}")
        return f"Error generating report: {str(e)}"