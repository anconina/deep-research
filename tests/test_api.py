"""
Tests for the public API functions.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from deep_research.api import deep_research
from deep_research.engine import ResearchEngine


class TestAPI:
    """Tests for the API functions."""

    @pytest.mark.asyncio
    async def test_deep_research(self, mock_llm_client, mock_search_engine, mock_firecrawl):
        """Test the deep_research function."""
        query = "Analyze the recent developments in quantum computing hardware."

        # Mock the ResearchEngine to avoid actual API calls
        with patch('deep_research.api.ResearchEngine') as MockEngine:
            # Configure the mock engine
            mock_engine_instance = MockEngine.return_value
            mock_engine_instance.deep_research = AsyncMock()
            mock_engine_instance.deep_research.return_value = {
                "learnings": [
                    "IBM unveiled a 1,121-qubit 'Condor' processor in December 2023.",
                    "Google's Quantum AI team continues to develop their quantum supremacy experiments."
                ],
                "visited_urls": [
                    "https://research.ibm.com/blog/1000-qubit-processor",
                    "https://quantumai.google/hardware"
                ],
                "chain_of_thought": [
                    "[2024-03-10 12:00:00] Starting research on quantum computing hardware.",
                    "[2024-03-10 12:10:25] Extracted 2 learnings about IBM's quantum processors."
                ],
                "information_map": {
                    "Quantum Hardware": {
                        "consensus": ["Superconducting qubits are widely used."],
                        "contradictions": [],
                        "gaps": ["Limited information on long-term stability."]
                    }
                },
                "contradictions": [],
                "source_evaluations": []
            }

            result = await deep_research(
                query=query,
                depth=3,
                breadth=4,
                auto_tune=True,
                max_depth=5,
                max_breadth=8,
                time_budget_seconds=300
            )

            # Check that the function returns the expected result
            assert isinstance(result, dict)
            assert "learnings" in result
            assert "visited_urls" in result
            assert "chain_of_thought" in result
            assert "information_map" in result
            assert "contradictions" in result
            assert "source_evaluations" in result

            # Check that the engine was initialized with the correct parameters
            MockEngine.assert_called_once_with(
                auto_tune=True,
                max_depth=5,
                max_breadth=8,
                time_budget_seconds=300
            )

            # Check that deep_research was called with the correct parameters
            mock_engine_instance.deep_research.assert_called_once_with(
                query=query,
                breadth=4,
                depth=3
            )

    @pytest.mark.asyncio
    async def test_deep_research_error_handling(self, mock_llm_client, mock_search_engine, mock_firecrawl):
        """Test error handling in deep_research function."""
        query = "Analyze the recent developments in quantum computing hardware."

        # Mock the ResearchEngine to raise an exception
        with patch('deep_research.api.ResearchEngine') as MockEngine:
            # Configure the mock engine to raise an exception
            mock_engine_instance = MockEngine.return_value
            mock_engine_instance.deep_research = AsyncMock(side_effect=Exception("Research engine error"))

            result = await deep_research(query=query)

            # Check that the function handles the error gracefully
            assert isinstance(result, dict)
            assert "learnings" in result
            assert "Research error" in result["learnings"][0]
            assert "visited_urls" in result
            assert "chain_of_thought" in result
            assert "Critical error" in result["chain_of_thought"][0]