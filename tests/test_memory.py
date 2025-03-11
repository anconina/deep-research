"""
Tests for the memory module.
"""

import pytest
from datetime import datetime

from deep_research.memory import ResearchMemory


class TestResearchMemory:
    """Tests for the ResearchMemory class."""

    @pytest.fixture
    def memory(self):
        """Return a ResearchMemory instance for testing."""
        return ResearchMemory()

    def test_add_learning(self, memory):
        """Test adding a learning to memory."""
        learning = "Quantum computers use qubits instead of classical bits."
        memory.add_learning(learning)

        assert learning in memory.learnings
        assert len(memory.learnings) == 1

        # Adding the same learning again should not create a duplicate
        memory.add_learning(learning)
        assert len(memory.learnings) == 1

        # Adding a different learning should work
        learning2 = "Quantum computers can solve certain problems exponentially faster than classical computers."
        memory.add_learning(learning2)
        assert len(memory.learnings) == 2
        assert learning2 in memory.learnings

    def test_add_learnings(self, memory):
        """Test adding multiple learnings to memory."""
        learnings = [
            "Quantum computers use qubits instead of classical bits.",
            "Quantum computers can solve certain problems exponentially faster than classical computers.",
            "Quantum decoherence is a major challenge in building practical quantum computers."
        ]

        memory.add_learnings(learnings)

        assert len(memory.learnings) == 3
        for learning in learnings:
            assert learning in memory.learnings

        # Adding a mix of new and existing learnings
        more_learnings = [
            "Quantum computers use qubits instead of classical bits.",  # Duplicate
            "Quantum error correction is essential for fault-tolerant quantum computing."  # New
        ]

        memory.add_learnings(more_learnings)
        assert len(memory.learnings) == 4  # Only one new learning should be added

    def test_add_url(self, memory):
        """Test adding a URL to memory."""
        url = "https://research.ibm.com/blog/1000-qubit-processor"
        memory.add_url(url)

        assert url in memory.visited_urls
        assert len(memory.visited_urls) == 1

        # Adding the same URL again should not create a duplicate
        memory.add_url(url)
        assert len(memory.visited_urls) == 1

        # Adding a different URL should work
        url2 = "https://quantumai.google/hardware"
        memory.add_url(url2)
        assert len(memory.visited_urls) == 2
        assert url2 in memory.visited_urls

    def test_add_urls(self, memory):
        """Test adding multiple URLs to memory."""
        urls = [
            "https://research.ibm.com/blog/1000-qubit-processor",
            "https://quantumai.google/hardware",
            "https://www.rigetti.com/quantum-processors"
        ]

        memory.add_urls(urls)

        assert len(memory.visited_urls) == 3
        for url in urls:
            assert url in memory.visited_urls

        # Adding a mix of new and existing URLs
        more_urls = [
            "https://research.ibm.com/blog/1000-qubit-processor",  # Duplicate
            "https://ionq.com/technology"  # New
        ]

        memory.add_urls(more_urls)
        assert len(memory.visited_urls) == 4  # Only one new URL should be added

    def test_add_thought(self, memory):
        """Test adding a thought to the chain of thought."""
        thought = "Analyzing quantum computing hardware landscape."
        memory.add_thought(thought)

        assert len(memory.chain_of_thought) == 1
        assert thought in memory.chain_of_thought[0]
        # Timestamp should be included in the chain of thought entry
        assert "[" in memory.chain_of_thought[0] and "]" in memory.chain_of_thought[0]

        # Adding another thought should append to the chain
        thought2 = "Exploring quantum error correction techniques."
        memory.add_thought(thought2)
        assert len(memory.chain_of_thought) == 2
        assert thought2 in memory.chain_of_thought[1]

    def test_add_contradiction(self, memory):
        """Test adding a contradiction to memory."""
        topic = "Quantum Supremacy"
        claim1 = "Google achieved quantum supremacy in 2019."
        claim2 = "IBM disputed Google's quantum supremacy claim, stating the same calculation could be performed on classical systems."
        source1 = "https://www.nature.com/articles/s41586-019-1666-5"
        source2 = "https://www.ibm.com/blogs/research/2019/10/quantum-supremacy-quantum-computing/"

        memory.add_contradiction(topic, claim1, claim2, source1, source2)

        assert len(memory.contradictions) == 1
        contradiction = memory.contradictions[0]
        assert contradiction["topic"] == topic
        assert contradiction["claim1"] == claim1
        assert contradiction["claim2"] == claim2
        assert contradiction["source1"] == source1
        assert contradiction["source2"] == source2
        assert "timestamp" in contradiction

        # The contradiction should also be added to the chain of thought
        assert len(memory.chain_of_thought) == 1
        assert "Contradiction detected" in memory.chain_of_thought[0]
        assert topic in memory.chain_of_thought[0]

    def test_add_source_evaluation(self, memory):
        """Test adding a source evaluation to memory."""
        evaluation = {
            "url": "https://research.ibm.com/blog/1000-qubit-processor",
            "title": "IBM Unveils 1,000+ Qubit Quantum Processor",
            "credibility_rating": "high",
            "relevance_rating": "high",
            "justification": "Official IBM research blog with technical details",
            "key_points": ["1,121-qubit Condor processor", "December 2023 release"]
        }

        memory.add_source_evaluation(evaluation)

        assert len(memory.source_evaluations) == 1
        assert memory.source_evaluations[0] == evaluation

        # Adding another evaluation should append to the list
        evaluation2 = {
            "url": "https://quantumai.google/hardware",
            "title": "Google Quantum AI Hardware",
            "credibility_rating": "high",
            "relevance_rating": "medium",
            "justification": "Official Google research site",
            "key_points": ["Sycamore processor", "Quantum supremacy experiment"]
        }

        memory.add_source_evaluation(evaluation2)
        assert len(memory.source_evaluations) == 2
        assert memory.source_evaluations[1] == evaluation2

    def test_update_information_map(self, memory):
        """Test updating the information map."""
        # Test adding consensus information
        topic = "Quantum Hardware"
        info_type = "consensus"
        content = "IBM and Google are both pursuing superconducting qubit approaches."

        memory.update_information_map(topic, info_type, content)

        assert topic in memory.information_map
        assert info_type in memory.information_map[topic]
        assert content in memory.information_map[topic][info_type]

        # Test adding contradictions
        info_type = "contradictions"
        content = "Different claims about quantum supremacy achievements."

        memory.update_information_map(topic, info_type, content)

        assert info_type in memory.information_map[topic]
        assert content in memory.information_map[topic][info_type]

        # Test adding gaps
        info_type = "gaps"
        content = "Limited information on long-term qubit stability."

        memory.update_information_map(topic, info_type, content)

        assert info_type in memory.information_map[topic]
        assert content in memory.information_map[topic][info_type]

        # Test adding a list of content
        info_type = "consensus"
        content_list = [
            "Most quantum computers operate at near absolute zero temperatures.",
            "Quantum error correction is essential for scaling quantum computers."
        ]

        memory.update_information_map(topic, info_type, content_list)

        for item in content_list:
            assert item in memory.information_map[topic][info_type]