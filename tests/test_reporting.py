"""
Tests for the reporting module.
"""

import pytest
from unittest.mock import patch, AsyncMock
import json

from deep_research.reporting import write_chain_of_thought_report, write_final_report


class TestReporting:
    """Tests for the reporting functions."""

    @pytest.mark.asyncio
    async def test_write_chain_of_thought_report(self, mock_llm_client, sample_learnings):
        """Test writing a chain of thought report."""
        # Create a simple chain of thought
        chain_of_thought = [
            "[2024-03-10 12:00:00] Starting research on quantum computing hardware.",
            "[2024-03-10 12:01:30] Generating SERP queries for: quantum computing hardware developments.",
            "[2024-03-10 12:02:45] Found 5 results for query: quantum computing hardware IBM Google.",
            "[2024-03-10 12:05:10] Successfully scraped 4 out of 5 URLs.",
            "[2024-03-10 12:10:25] Extracted 3 learnings about IBM's quantum processors.",
            "[2024-03-10 12:15:40] Identified 2 follow-up questions for deeper research.",
            "[2024-03-10 12:20:15] Contradiction detected in topic 'Quantum Supremacy': Google claimed quantum supremacy vs IBM disputed the claim."
        ]

        result = await write_chain_of_thought_report(chain_of_thought)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "research process" in result.lower()

        # The mock response should contain "chain of thought" content
        assert "research process began by analyzing" in result.lower()

    @pytest.mark.asyncio
    async def test_write_final_report(self, mock_llm_client, sample_learnings, sample_contradictions):
        """Test writing a final report."""
        prompt = "Analyze the recent developments in quantum computing hardware."

        # Create a simple information map
        information_map = {
            "Hardware Approaches": {
                "consensus": [
                    "Superconducting qubits are currently the most widely used quantum computing technology.",
                    "Most quantum processors require near absolute zero temperatures to operate."
                ],
                "contradictions": [
                    "There is disagreement about whether trapped-ion or superconducting qubits will prove superior in the long run."
                ],
                "gaps": [
                    "Limited information on the long-term stability of different qubit implementations."
                ]
            },
            "Error Correction": {
                "consensus": [
                    "Quantum error correction is essential for building fault-tolerant quantum computers.",
                    "Surface codes are a promising approach to quantum error correction."
                ],
                "contradictions": [],
                "gaps": [
                    "Unclear how many physical qubits will be required per logical qubit in practical implementations."
                ]
            }
        }

        # Create some source evaluations
        source_evaluations = [
            {
                "url": "https://research.ibm.com/blog/1000-qubit-processor",
                "title": "IBM Unveils 1,000+ Qubit Quantum Processor",
                "credibility_rating": "high",
                "relevance_rating": "high",
                "justification": "Official IBM research blog with technical details",
                "key_points": ["1,121-qubit Condor processor", "December 2023 release"]
            },
            {
                "url": "https://quantumai.google/hardware",
                "title": "Google Quantum AI Hardware",
                "credibility_rating": "high",
                "relevance_rating": "medium",
                "justification": "Official Google research site",
                "key_points": ["Sycamore processor", "Quantum supremacy experiment"]
            }
        ]

        result = await write_final_report(prompt, sample_learnings, information_map, sample_contradictions,
                                          source_evaluations)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "quantum computing" in result.lower()

        # Check for main report sections
        assert "# quantum computing hardware report" in result.lower() or "## introduction" in result.lower()

        # The mock LLM response should contain some markdown formatting
        assert "#" in result  # Headers
        assert "-" in result or "*" in result  # List items

    @pytest.mark.asyncio
    async def test_write_final_report_error_handling(self, mock_llm_client):
        """Test error handling in write_final_report."""
        prompt = "Analyze the recent developments in quantum computing hardware."
        learnings = ["IBM has developed a 1,121-qubit processor."]

        # Force an error in the LLM call
        with patch('deep_research.ai.providers.acompletion', side_effect=Exception("API error")):
            result = await write_final_report(prompt, learnings)

            assert isinstance(result, str)
            assert "Error generating report" in result

    @pytest.mark.asyncio
    async def test_write_chain_of_thought_report_error_handling(self, mock_llm_client):
        """Test error handling in write_chain_of_thought_report."""
        chain_of_thought = ["[2024-03-10 12:00:00] Starting research on quantum computing hardware."]

        # Force an error in the LLM call
        with patch('deep_research.ai.providers.acompletion', side_effect=Exception("API error")):
            result = await write_chain_of_thought_report(chain_of_thought)

            assert isinstance(result, str)
            assert "Error generating" in result