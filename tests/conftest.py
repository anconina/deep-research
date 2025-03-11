"""
Common test fixtures and utilities for the Deep Research test suite.
"""

import asyncio
import json
import os

from typing import Dict, List
from unittest.mock import MagicMock, patch

import pytest


# Add path to the packages
import sys

from deep_research.models import Learnings, ChainOfThoughtSummary, SourceEvaluations, SerpQueries

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock environment variables
@pytest.fixture(scope="session", autouse=True)
def mock_env_vars():
    """Set up mock environment variables for testing."""
    with patch.dict(os.environ, {
        "OPENAI_API_KEY": "mock-openai-key",
        "TAVILY_API_KEY": "mock-tavily-key",
        "BING_API_KEY": "mock-bing-key",
        "FIRECRAWL_API_URL": "http://localhost:3002",
        "CONTEXT_SIZE": "16000",
        "DEFAULT_DEPTH": "3",
        "DEFAULT_BREADTH": "4",
        "MAX_DEPTH": "5",
        "MAX_BREADTH": "6",
        "ENABLE_AUTO_TUNE": "true",
        "RESEARCH_OUTPUT_DIR": "test_research_output",
    }):
        yield


# Mock data fixtures
@pytest.fixture
def sample_query() -> str:
    """Sample research query."""
    return "Analyze the recent developments in quantum computing hardware"


@pytest.fixture
def sample_learnings() -> List[str]:
    """Sample research learnings."""
    return [
        "IBM unveiled a 1,121-qubit 'Condor' quantum processor in December 2023, marking a significant milestone in quantum hardware scaling.",
        "Google's Quantum AI team announced a 70-qubit 'Bristlecone' quantum processor with a quantum volume of 2^70.",
        "Rigetti Computing has developed a modular approach to quantum processor design, allowing for scalable quantum systems through a chip-to-chip interconnect solution.",
        "IonQ is focusing on trapped-ion quantum computing, which they claim offers higher-quality qubits with longer coherence times compared to superconducting approaches.",
        "Quantum error correction remains a critical challenge, with several companies developing surface code implementations to address qubit instability."
    ]


@pytest.fixture
def sample_urls() -> List[str]:
    """Sample research URLs."""
    return [
        "https://research.ibm.com/blog/1000-qubit-processor",
        "https://quantumai.google/hardware",
        "https://www.rigetti.com/quantum-processors",
        "https://ionq.com/technology",
        "https://arxiv.org/abs/2301.12345"
    ]


@pytest.fixture
def sample_contradictions() -> List[Dict]:
    """Sample contradictions."""
    return [
        {
            "topic": "Quantum Supremacy Claims",
            "claim1": "Google claimed quantum supremacy in 2019 with their 53-qubit Sycamore processor.",
            "claim2": "IBM disputed Google's quantum supremacy claim, stating the same calculation could be performed on classical systems in 2.5 days.",
            "source1": "https://www.nature.com/articles/s41586-019-1666-5",
            "source2": "https://www.ibm.com/blogs/research/2019/10/quantum-supremacy-quantum-computing/"
        },
        {
            "topic": "Qubit Count Importance",
            "claim1": "Higher qubit counts are the primary metric for quantum computer advancement.",
            "claim2": "Quantum volume, which measures both qubit count and error rates, is a more meaningful metric than raw qubit count.",
            "source1": "https://example.com/qubit-race",
            "source2": "https://www.ibm.com/blogs/research/2020/01/quantum-volume-32/"
        }
    ]


@pytest.fixture
def sample_content() -> str:
    """Sample content from a web page."""
    return """
    # Recent Developments in Quantum Computing Hardware

    ## IBM's Latest Quantum Processor
    IBM unveiled its newest quantum processor, the 1,121-qubit Condor, in December 2023. This represents a major milestone in quantum hardware development. The company announced plans to release a 1,400+ qubit system by Q3 2024.

    ## Google's Quantum AI Initiative
    Google's Quantum AI team continues to build on their quantum supremacy experiments from 2019. Their 70-qubit Bristlecone processor demonstrates quantum volume of 2^70, according to their latest research papers.

    ## Error Correction Progress
    Quantum error correction remains a significant challenge in building practical quantum computers. Recent developments in surface code implementations show promising results in extending coherence times.

    ## Industry Outlook
    The quantum computing hardware industry is projected to reach $1.3 billion by 2030, with an anticipated growth rate of 25% year-over-year.
    """


@pytest.fixture
def mock_search_results() -> Dict:
    """Mock search results."""
    return {
        "data": [
            {
                "title": "IBM Quantum Computing",
                "href": "https://research.ibm.com/blog/1000-qubit-processor",
                "snippet": "IBM unveiled its newest quantum processor, the 1,121-qubit Condor, in December 2023."
            },
            {
                "title": "Google Quantum AI",
                "href": "https://quantumai.google/hardware",
                "snippet": "Google's Quantum AI team continues to build on their quantum supremacy experiments."
            }
        ]
    }


@pytest.fixture
def mock_scraped_content() -> Dict:
    """Mock scraped content from URLs."""
    return {
        "data": [
            {
                "markdown": "# IBM Quantum Computing\n\nIBM unveiled its newest quantum processor, the 1,121-qubit Condor, in December 2023.",
                "metadata": {
                    "url": "https://research.ibm.com/blog/1000-qubit-processor",
                    "statusCode": 200
                }
            },
            {
                "markdown": "# Google Quantum AI\n\nGoogle's Quantum AI team continues to build on their quantum supremacy experiments.",
                "metadata": {
                    "url": "https://quantumai.google/hardware",
                    "statusCode": 200
                }
            }
        ]
    }


# Mock for LLM client
class MockLLMResponse:
    """Mock response from LLM API."""

    def __init__(self, content):
        self.choices = [MagicMock(message={"content": json.dumps(content)})]


@pytest.fixture
def mock_llm_client():
    """Mock for LLM client."""
    with patch('deep_research.llm.acompletion') as mock:
        # Configure the mock to return a specific response
        async def mock_acompletion(*args, **kwargs):
            # Different responses based on the schema parameter
            schema = kwargs.get('response_format', None)
            prompt = kwargs.get('messages', [{}])[-1].get('content', '')

            if schema.__name__ == Learnings.__name__ :
                return MockLLMResponse({
                    "learnings": [
                        "IBM unveiled a 1,121-qubit 'Condor' processor.",
                        "Google's Quantum AI team announced a 70-qubit 'Bristlecone' processor."
                    ],
                    "follow_up_questions": [
                        "What error correction methods are being used?",
                        "How do different quantum hardware approaches compare?"
                    ]
                })
            elif schema.__name__ == ChainOfThoughtSummary.__name__ :
                return MockLLMResponse({
                    "summary": "The research process began by analyzing the quantum computing landscape..."
                })
            elif schema.__name__ == SourceEvaluations.__name__ :
                return MockLLMResponse({
                    "evaluations": [
                        {
                            "url": "https://research.ibm.com/blog/1000-qubit-processor",
                            "title": "IBM Quantum Computing",
                            "credibility_rating": "high",
                            "relevance_rating": "high",
                            "justification": "Official company research blog",
                            "key_points": ["1,121-qubit processor", "December 2023 release"]
                        }
                    ]
                })
            elif schema.__name__ == SerpQueries.__name__:
                return MockLLMResponse({
                    "queries": [
                        {
                            "query": "recent quantum computing hardware advancements IBM Google",
                            "research_goal": "Identify latest quantum processor developments"
                        },
                        {
                            "query": "quantum error correction surface codes recent progress",
                            "research_goal": "Understand error correction approaches"
                        }
                    ]
                })
            else:
                return MockLLMResponse({
                    "markdown": "# Quantum Computing Hardware Report\n\nThis report summarizes recent developments..."
                })

        mock.side_effect = mock_acompletion
        yield mock


# Mock for search engine
@pytest.fixture
def mock_search_engine():
    """Mock for search engine."""
    with patch('deep_research.search_engines.tavily.tavily_search.TavilySearch') as mock:
        instance = mock.return_value

        async def mock_search(*args, **kwargs):
            return [
                {
                    "title": "IBM Quantum Computing",
                    "href": "https://research.ibm.com/blog/1000-qubit-processor",
                    "snippet": "IBM unveiled its newest quantum processor, the 1,121-qubit Condor, in December 2023."
                },
                {
                    "title": "Google Quantum AI",
                    "href": "https://quantumai.google/hardware",
                    "snippet": "Google's Quantum AI team continues to build on their quantum supremacy experiments."
                }
            ]

        instance.search.side_effect = mock_search
        yield instance


# Mock for firecrawl
@pytest.fixture
def mock_firecrawl():
    """Mock for firecrawl."""
    with patch('deep_research.engine.firecrawl') as mock:
        mock.batch_scrape_urls.return_value = {
            "data": [
                {
                    "markdown": "# IBM Quantum Computing\n\nIBM unveiled its newest quantum processor, the 1,121-qubit Condor, in December 2023.",
                    "metadata": {
                        "url": "https://research.ibm.com/blog/1000-qubit-processor",
                        "statusCode": 200
                    }
                },
                {
                    "markdown": "# Google Quantum AI\n\nGoogle's Quantum AI team continues to build on their quantum supremacy experiments.",
                    "metadata": {
                        "url": "https://quantumai.google/hardware",
                        "statusCode": 200
                    }
                }
            ]
        }
        yield mock


# Event loop fixture for asyncio tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()