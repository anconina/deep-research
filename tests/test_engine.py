"""
Tests for the engine module.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import json

from tradingagents.deep_research.engine import ResearchEngine
from tradingagents.deep_research.models import SerpQuery, Learnings


class TestResearchEngine:
    """Tests for the ResearchEngine class."""

    @pytest.fixture
    def engine(self):
        """Return a ResearchEngine instance for testing."""
        return ResearchEngine(auto_tune=True, max_depth=4, max_breadth=6)

    @pytest.mark.asyncio
    async def test_determine_auto_parameters(self, engine, mock_llm_client):
        """Test determining automatic parameters."""
        # Test with auto-tuning disabled
        engine.auto_tune = False
        depth, breadth = await engine.determine_auto_parameters("test query")
        assert depth == 2  # Default values when auto-tuning is disabled
        assert breadth == 4

        # Test with auto-tuning enabled
        engine.auto_tune = True

        # Create a patched auto_tuner that returns predictable values
        mock_auto_tuner = MagicMock()
        mock_auto_tuner.analyze_question_complexity.return_value = asyncio.Future()
        mock_auto_tuner.analyze_question_complexity.return_value.set_result({
            "complexity_score": 0.7,
            "entity_count": 3,
            "aspect_count": 2,
            "complexity_keyword_count": 4
        })
        mock_auto_tuner.determine_initial_parameters.return_value = (3, 5)
        engine.auto_tuner = mock_auto_tuner

        depth, breadth = await engine.determine_auto_parameters("complex query with multiple aspects")
        assert depth == 3
        assert breadth == 5
        mock_auto_tuner.analyze_question_complexity.assert_called_once()
        mock_auto_tuner.determine_initial_parameters.assert_called_once()

    @pytest.mark.asyncio
    async def test_adjust_parameters(self, engine):
        """Test adjusting parameters based on results."""
        # Test with auto-tuning disabled
        engine.auto_tune = False
        current_depth = 3
        current_breadth = 4
        new_depth, new_breadth = await engine.adjust_parameters(current_depth, current_breadth)
        assert new_depth == current_depth
        assert new_breadth == current_breadth

        # Test with auto-tuning enabled
        engine.auto_tune = True

        # Create a patched auto_tuner
        mock_auto_tuner = MagicMock()
        mock_auto_tuner.estimate_info_quality.return_value = 0.8
        mock_auto_tuner.get_time_usage_fraction.return_value = 0.4
        mock_auto_tuner.adjust_parameters.return_value = (2, 3)
        engine.auto_tuner = mock_auto_tuner

        new_depth, new_breadth = await engine.adjust_parameters(current_depth, current_breadth)
        assert new_depth == 2
        assert new_breadth == 3
        mock_auto_tuner.estimate_info_quality.assert_called_once()
        mock_auto_tuner.get_time_usage_fraction.assert_called_once()
        mock_auto_tuner.adjust_parameters.assert_called_once_with(
            current_depth, current_breadth, 0.8, 0.4
        )

    @pytest.mark.asyncio
    async def test_generate_serp_queries(self, engine, mock_llm_client):
        """Test generating SERP queries."""
        # Add learnings to memory to test inclusion in prompt
        engine.memory.add_learning("Quantum computers use qubits instead of classical bits.")

        queries = await engine.generate_serp_queries("What are the latest developments in quantum computing?", 2)

        assert len(queries) == 2
        assert isinstance(queries[0], SerpQuery)
        assert hasattr(queries[0], 'query')
        assert hasattr(queries[0], 'research_goal')
        assert isinstance(queries[0].query, str)
        assert isinstance(queries[0].research_goal, str)

    @pytest.mark.asyncio
    async def test_execute_search(self, engine, mock_search_engine):
        """Test executing search."""
        # Mock generate_search_engine_queries to return predictable values
        with patch.object(engine, 'generate_search_engine_queries') as mock_generate:
            mock_generate.return_value = asyncio.Future()
            mock_generate.return_value.set_result([
                "quantum computing hardware IBM Google",
                "quantum error correction recent developments"
            ])

            urls = await engine.execute_search("What are the latest developments in quantum computing?")

            assert isinstance(urls, list)
            assert len(urls) > 0
            assert all(isinstance(url, str) for url in urls)
            assert "https://research.ibm.com/blog/1000-qubit-processor" in urls
            mock_generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_scrape_content(self, engine, mock_firecrawl):
        """Test scraping content."""
        urls = [
            "https://research.ibm.com/blog/1000-qubit-processor",
            "https://quantumai.google/hardware"
        ]

        result = await engine.scrape_content(urls)

        assert isinstance(result, dict)
        assert "data" in result
        assert len(result["data"]) == 2
        assert "markdown" in result["data"][0]
        assert "metadata" in result["data"][0]
        assert result["data"][0]["metadata"]["url"] == urls[0]

    @pytest.mark.asyncio
    async def test_evaluate_sources(self, engine, mock_llm_client, sample_urls):
        """Test evaluating sources."""
        contents = [
            "IBM unveiled its newest quantum processor, the 1,121-qubit Condor, in December 2023.",
            "Google's Quantum AI team continues to build on their quantum supremacy experiments."
        ]

        evaluations = await engine.evaluate_sources(sample_urls[:2], contents)

        assert isinstance(evaluations, list)
        assert len(evaluations) == 1  # Our mock returns 1 evaluation
        assert "url" in evaluations[0]
        assert "credibility_rating" in evaluations[0]
        assert "relevance_rating" in evaluations[0]

    @pytest.mark.asyncio
    async def test_process_serp_result(self, engine, mock_llm_client, mock_scraped_content):
        """Test processing SERP results."""
        query = "quantum computing hardware developments"

        # Mock evaluate_sources to avoid actual API calls
        with patch.object(engine, 'evaluate_sources') as mock_evaluate:
            mock_evaluate.return_value = asyncio.Future()
            mock_evaluate.return_value.set_result([
                {
                    "url": "https://research.ibm.com/blog/1000-qubit-processor",
                    "title": "IBM Quantum Computing",
                    "credibility_rating": "high",
                    "relevance_rating": "high",
                    "justification": "Official company blog",
                    "key_points": ["1,121-qubit processor", "December 2023 release"]
                }
            ])

            learnings = await engine.process_serp_result(query, mock_scraped_content, 2)

            assert isinstance(learnings, Learnings)
            assert len(learnings.learnings) == 2
            assert len(learnings.follow_up_questions) == 2
            mock_evaluate.assert_called_once()

    @pytest.mark.asyncio
    async def test_detect_contradictions(self, engine):
        """Test detecting contradictions."""
        # Add existing learning to memory
        engine.memory.add_learning(
            "IBM's quantum computer shows positive performance growth with error rates decreasing by 50%."
        )

        # Test with contradictory new learning
        new_learning = "IBM's quantum computer shows negative performance results with error rates increasing."
        engine.detect_contradictions(new_learning)

        assert len(engine.memory.contradictions) == 1
        assert engine.memory.contradictions[0]["topic"] == "Performance"

        # Test with non-contradictory learning
        new_learning = "Google's quantum processors use superconducting qubits."
        engine.detect_contradictions(new_learning)

        # Should still have only 1 contradiction from before
        assert len(engine.memory.contradictions) == 1

    @pytest.mark.asyncio
    async def test_execute_query(self, engine, mock_search_engine, mock_firecrawl, mock_llm_client):
        """Test executing a single query."""
        serp_query = SerpQuery(
            query="quantum computing hardware IBM",
            research_goal="Identify IBM's latest quantum processor developments"
        )

        # Mock methods to avoid actual API calls
        with patch.object(engine, 'execute_search') as mock_execute_search, \
                patch.object(engine, 'process_serp_result') as mock_process:
            mock_execute_search.return_value = asyncio.Future()
            mock_execute_search.return_value.set_result([
                "https://research.ibm.com/blog/1000-qubit-processor"
            ])

            mock_process.return_value = asyncio.Future()
            mock_process.return_value.set_result(
                Learnings(
                    learnings=["IBM unveiled a 1,121-qubit processor."],
                    follow_up_questions=["What error correction methods are used?"]
                )
            )

            result = await engine.execute_query(serp_query, 2, 3)

            assert isinstance(result, dict)
            assert result["success"] is True
            assert "new_learnings" in result
            assert "follow_up_questions" in result
            assert len(result["follow_up_questions"]) == 1
            mock_execute_search.assert_called_once()
            mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_deep_research(self, engine, mock_search_engine, mock_firecrawl, mock_llm_client):
        """Test the deep research process."""
        # Mock methods to avoid actual API calls and control the flow
        with patch.object(engine, 'determine_auto_parameters') as mock_params, \
                patch.object(engine, 'generate_serp_queries') as mock_queries, \
                patch.object(engine, 'execute_query') as mock_execute:
            mock_params.return_value = asyncio.Future()
            mock_params.return_value.set_result((2, 3))

            mock_queries.return_value = asyncio.Future()
            mock_queries.return_value.set_result([
                SerpQuery(
                    query="quantum computing hardware IBM",
                    research_goal="Identify IBM's latest developments"
                ),
                SerpQuery(
                    query="quantum error correction recent progress",
                    research_goal="Understand error correction approaches"
                )
            ])

            # First query returns follow-up questions to trigger another iteration
            mock_execute.side_effect = [
                asyncio.Future(),
                asyncio.Future(),
                asyncio.Future(),  # For the follow-up query
            ]
            mock_execute.side_effect[0].set_result({
                "success": True,
                "new_learnings": ["IBM unveiled a 1,121-qubit processor."],
                "follow_up_questions": ["What error correction methods are used?"]
            })
            mock_execute.side_effect[1].set_result({
                "success": True,
                "new_learnings": ["Surface codes are promising for quantum error correction."],
                "follow_up_questions": []
            })
            mock_execute.side_effect[2].set_result({
                "success": True,
                "new_learnings": ["IBM uses a variation of surface codes for error correction."],
                "follow_up_questions": []
            })

            result = await engine.deep_research("What are the latest developments in quantum computing?")

            assert isinstance(result, dict)
            assert "learnings" in result
            assert "visited_urls" in result
            assert "chain_of_thought" in result
            assert "information_map" in result
            assert "contradictions" in result
            assert "source_evaluations" in result
            assert len(result["learnings"]) > 0
            mock_params.assert_called_once()
            assert mock_queries.call_count >= 1
            assert mock_execute.call_count >= 2