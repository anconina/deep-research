"""
Tests for the models module.
"""

import pytest
from pydantic import ValidationError

from deep_research.models import (
    ChainOfThoughtSummary,
    FollowUpQuestions,
    Report,
    SourceEvaluation,
    SourceEvaluations,
    InformationItem,
    InformationGroup,
    InformationMap,
    ResearchSummary,
    Learnings,
    SerpQuery,
    SerpQueries,
    SearchEngineQueries,
    ResearchResult,
    ResearchProgress,
    ResearchError,
    ResearchErrorLog
)


class TestModels:
    """Tests for the Pydantic models."""

    def test_chain_of_thought_summary(self):
        """Test ChainOfThoughtSummary model."""
        # Valid instance
        summary = ChainOfThoughtSummary(
            summary="The research process began by analyzing the quantum computing landscape..."
        )
        assert summary.summary.startswith("The research process")

        # Missing required field
        with pytest.raises(ValidationError):
            ChainOfThoughtSummary()

    def test_follow_up_questions(self):
        """Test FollowUpQuestions model."""
        # Valid instance
        questions = FollowUpQuestions(
            questions=[
                "What error correction methods are being used in IBM's quantum computers?",
                "How do different quantum hardware approaches compare in terms of qubit quality?"
            ]
        )
        assert len(questions.questions) == 2
        assert "error correction" in questions.questions[0]

        # Empty list is valid
        empty_questions = FollowUpQuestions(questions=[])
        assert len(empty_questions.questions) == 0

        # Missing required field
        with pytest.raises(ValidationError):
            FollowUpQuestions()

    def test_report(self):
        """Test Report model."""
        # Valid instance
        report = Report(
            markdown="# Quantum Computing Report\n\nThis report covers recent developments..."
        )
        assert report.markdown.startswith("# Quantum Computing Report")

        # Missing required field
        with pytest.raises(ValidationError):
            Report()

    def test_source_evaluation(self):
        """Test SourceEvaluation model."""
        # Valid instance
        eval = SourceEvaluation(
            url="https://research.ibm.com/blog/1000-qubit-processor",
            title="IBM Unveils 1,000+ Qubit Quantum Processor",
            credibility_rating="high",
            relevance_rating="high",
            justification="Official IBM research blog with technical details",
            key_points=["1,121-qubit Condor processor", "December 2023 release"]
        )
        assert eval.url == "https://research.ibm.com/blog/1000-qubit-processor"
        assert eval.credibility_rating == "high"
        assert len(eval.key_points) == 2

        # Invalid credibility rating
        with pytest.raises(ValidationError):
            SourceEvaluation(
                url="https://example.com",
                title="Example",
                credibility_rating="super-high",  # Invalid value
                relevance_rating="high",
                justification="Example justification"
            )

        # Invalid relevance rating
        with pytest.raises(ValidationError):
            SourceEvaluation(
                url="https://example.com",
                title="Example",
                credibility_rating="high",
                relevance_rating="super-high",  # Invalid value
                justification="Example justification"
            )

        # Missing required fields
        with pytest.raises(ValidationError):
            SourceEvaluation(
                url="https://example.com",
                title="Example",
                # Missing credibility_rating
                relevance_rating="high",
                justification="Example justification"
            )

    def test_source_evaluations(self):
        """Test SourceEvaluations model."""
        # Valid instance
        evals = SourceEvaluations(
            evaluations=[
                SourceEvaluation(
                    url="https://research.ibm.com/blog/1000-qubit-processor",
                    title="IBM Quantum",
                    credibility_rating="high",
                    relevance_rating="high",
                    justification="Official IBM research blog"
                ),
                SourceEvaluation(
                    url="https://quantumai.google/hardware",
                    title="Google Quantum AI",
                    credibility_rating="high",
                    relevance_rating="medium",
                    justification="Official Google research site"
                )
            ]
        )
        assert len(evals.evaluations) == 2
        assert evals.evaluations[0].url == "https://research.ibm.com/blog/1000-qubit-processor"

        # Empty list is valid
        empty_evals = SourceEvaluations(evaluations=[])
        assert len(empty_evals.evaluations) == 0

        # Missing required field
        with pytest.raises(ValidationError):
            SourceEvaluations()

    def test_information_item(self):
        """Test InformationItem model."""
        # Valid instance with all fields
        item = InformationItem(
            content="IBM unveiled a 1,121-qubit 'Condor' processor in December 2023.",
            source_urls=["https://research.ibm.com/blog/1000-qubit-processor"],
            confidence="high",
            tags=["IBM", "hardware", "quantum processor"]
        )
        assert item.content.startswith("IBM unveiled")
        assert item.confidence == "high"
        assert len(item.source_urls) == 1
        assert len(item.tags) == 3

        # Valid instance with minimal fields
        minimal_item = InformationItem(
            content="Quantum computers use qubits instead of classical bits."
        )
        assert minimal_item.content.startswith("Quantum computers")
        assert minimal_item.confidence == "medium"  # Default value
        assert len(minimal_item.source_urls) == 0  # Default empty list
        assert len(minimal_item.tags) == 0  # Default empty list

        # Invalid confidence level
        with pytest.raises(ValidationError):
            InformationItem(
                content="Test content",
                confidence="super-high"  # Invalid value
            )

        # Missing required content field
        with pytest.raises(ValidationError):
            InformationItem()

    def test_information_group(self):
        """Test InformationGroup model."""
        # Valid instance with all fields
        group = InformationGroup(
            topic="Quantum Hardware",
            consensus=[
                InformationItem(content="Superconducting qubits are widely used in quantum computers."),
                InformationItem(content="Most quantum processors require near absolute zero temperatures.")
            ],
            contradictions=[
                InformationItem(
                    content="There is disagreement about whether trapped-ion or superconducting qubits will prove superior.",
                    confidence="low"
                )
            ],
            gaps=["Limited information on the long-term stability of qubits."]
        )
        assert group.topic == "Quantum Hardware"
        assert len(group.consensus) == 2
        assert len(group.contradictions) == 1
        assert len(group.gaps) == 1

        # Valid instance with minimal fields
        minimal_group = InformationGroup(
            topic="Quantum Algorithms"
        )
        assert minimal_group.topic == "Quantum Algorithms"
        assert len(minimal_group.consensus) == 0  # Default empty list
        assert len(minimal_group.contradictions) == 0  # Default empty list
        assert len(minimal_group.gaps) == 0  # Default empty list

        # Missing required topic field
        with pytest.raises(ValidationError):
            InformationGroup()

    def test_information_map(self):
        """Test InformationMap model."""
        # Valid instance
        info_map = InformationMap(
            groups=[
                InformationGroup(
                    topic="Quantum Hardware",
                    consensus=[InformationItem(content="Superconducting qubits are widely used.")]
                ),
                InformationGroup(
                    topic="Quantum Algorithms",
                    consensus=[InformationItem(content="Shor's algorithm can factor large numbers efficiently.")]
                )
            ]
        )
        assert len(info_map.groups) == 2
        assert info_map.groups[0].topic == "Quantum Hardware"
        assert info_map.groups[1].topic == "Quantum Algorithms"

        # Empty list is valid
        empty_map = InformationMap(groups=[])
        assert len(empty_map.groups) == 0

        # Missing required field
        with pytest.raises(ValidationError):
            InformationMap()

    def test_research_summary(self):
        """Test ResearchSummary model."""
        # Valid instance with all fields
        summary = ResearchSummary(
            key_findings=[
                "IBM unveiled a 1,121-qubit 'Condor' processor in December 2023.",
                "Quantum error correction remains a critical challenge."
            ],
            themes=["Hardware scaling", "Error correction", "Quantum supremacy"],
            recommendations=["Focus on error correction research", "Monitor IBM's quantum roadmap"],
            future_directions=["Explore hybrid quantum-classical algorithms", "Investigate fault-tolerant approaches"]
        )
        assert len(summary.key_findings) == 2
        assert len(summary.themes) == 3
        assert len(summary.recommendations) == 2
        assert len(summary.future_directions) == 2

        # Valid instance with minimal fields
        minimal_summary = ResearchSummary(
            key_findings=["Quantum computers show promise for certain computational problems."]
        )
        assert len(minimal_summary.key_findings) == 1
        assert len(minimal_summary.themes) == 0  # Default empty list
        assert len(minimal_summary.recommendations) == 0  # Default empty list
        assert len(minimal_summary.future_directions) == 0  # Default empty list

        # Missing required key_findings field
        with pytest.raises(ValidationError):
            ResearchSummary()

    def test_learnings(self):
        """Test Learnings model."""
        # Valid instance
        learnings = Learnings(
            learnings=[
                "IBM unveiled a 1,121-qubit 'Condor' processor in December 2023.",
                "Quantum error correction remains a critical challenge."
            ],
            follow_up_questions=[
                "What error correction methods are being investigated?",
                "How do different quantum hardware approaches compare?"
            ]
        )
        assert len(learnings.learnings) == 2
        assert len(learnings.follow_up_questions) == 2

        # Missing required fields
        with pytest.raises(ValidationError):
            Learnings(learnings=["Test learning"])  # Missing follow_up_questions

        with pytest.raises(ValidationError):
            Learnings(follow_up_questions=["Test question"])  # Missing learnings

    def test_serp_query(self):
        """Test SerpQuery model."""
        # Valid instance
        query = SerpQuery(
            query="quantum computing hardware IBM Google",
            research_goal="Identify latest quantum processor developments"
        )
        assert query.query == "quantum computing hardware IBM Google"
        assert query.research_goal == "Identify latest quantum processor developments"

        # Missing required fields
        with pytest.raises(ValidationError):
            SerpQuery(query="Test query")  # Missing research_goal

        with pytest.raises(ValidationError):
            SerpQuery(research_goal="Test goal")  # Missing query

    def test_serp_queries(self):
        """Test SerpQueries model."""
        # Valid instance
        queries = SerpQueries(
            queries=[
                SerpQuery(
                    query="quantum computing hardware IBM Google",
                    research_goal="Identify latest quantum processor developments"
                ),
                SerpQuery(
                    query="quantum error correction surface codes",
                    research_goal="Understand error correction approaches"
                )
            ]
        )
        assert len(queries.queries) == 2
        assert queries.queries[0].query == "quantum computing hardware IBM Google"


    def test_search_engine_queries(self):
        """Test SearchEngineQueries model."""
        # Valid instance
        queries = SearchEngineQueries(
            queries=[
                "quantum computing hardware IBM Google",
                "quantum error correction surface codes recent progress"
            ]
        )
        assert len(queries.queries) == 2
        assert queries.queries[0] == "quantum computing hardware IBM Google"


    def test_research_result(self):
        """Test ResearchResult model."""
        # Valid instance with minimal fields
        result = ResearchResult(
            query="Analyze the recent developments in quantum computing hardware."
        )
        assert result.query == "Analyze the recent developments in quantum computing hardware."
        assert len(result.learnings) == 0  # Default empty list
        assert len(result.visited_urls) == 0  # Default empty list
        assert len(result.chain_of_thought) == 0  # Default empty list

        # Valid instance with all fields
        full_result = ResearchResult(
            query="Analyze the recent developments in quantum computing hardware.",
            learnings=[
                "IBM unveiled a 1,121-qubit 'Condor' processor in December 2023.",
                "Quantum error correction remains a critical challenge."
            ],
            visited_urls=[
                "https://research.ibm.com/blog/1000-qubit-processor",
                "https://quantumai.google/hardware"
            ],
            chain_of_thought=[
                "[2024-03-10 12:00:00] Starting research on quantum computing hardware.",
                "[2024-03-10 12:10:25] Extracted 2 learnings about IBM's quantum processors."
            ],
            information_map={
                "Quantum Hardware": {
                    "consensus": ["Superconducting qubits are widely used."],
                    "contradictions": [],
                    "gaps": ["Limited information on long-term stability."]
                }
            },
            source_evaluations=[
                {
                    "url": "https://research.ibm.com/blog/1000-qubit-processor",
                    "title": "IBM Quantum",
                    "credibility_rating": "high",
                    "relevance_rating": "high",
                    "justification": "Official IBM research blog"
                }
            ]
        )
        assert full_result.query == "Analyze the recent developments in quantum computing hardware."
        assert len(full_result.learnings) == 2
        assert len(full_result.visited_urls) == 2
        assert len(full_result.chain_of_thought) == 2
        assert "Quantum Hardware" in full_result.information_map
        assert len(full_result.source_evaluations) == 1

        # Missing required query field
        with pytest.raises(ValidationError):
            ResearchResult()

    def test_research_progress(self):
        """Test ResearchProgress model."""
        # Valid instance
        progress = ResearchProgress(
            total_depth=3,
            current_depth=2,
            total_breadth=4,
            current_breadth=3,
            total_queries=12,
            completed_queries=6,
            current_query="quantum computing hardware IBM",
            elapsed_seconds=120.5,
            completion_percentage=50.0
        )
        assert progress.total_depth == 3
        assert progress.current_depth == 2
        assert progress.total_breadth == 4
        assert progress.current_breadth == 3
        assert progress.total_queries == 12
        assert progress.completed_queries == 6
        assert progress.current_query == "quantum computing hardware IBM"
        assert progress.elapsed_seconds == 120.5
        assert progress.completion_percentage == 50.0

        # Missing required fields
        with pytest.raises(ValidationError):
            ResearchProgress(
                total_depth=3,
                # Missing current_depth
                total_breadth=4,
                current_breadth=3
            )

    def test_research_error(self):
        """Test ResearchError model."""
        # Valid instance with all fields
        error = ResearchError(
            error_type="API Error",
            error_message="Failed to connect to search API",
            context="During SERP query execution",
            impact="Unable to retrieve search results for quantum computing query",
            resolution="Retried with alternative search endpoint",
            timestamp="2024-03-10T12:34:56"
        )
        assert error.error_type == "API Error"
        assert error.error_message == "Failed to connect to search API"
        assert error.context == "During SERP query execution"
        assert error.impact == "Unable to retrieve search results for quantum computing query"
        assert error.resolution == "Retried with alternative search endpoint"
        assert error.timestamp == "2024-03-10T12:34:56"

        # Valid instance with minimal fields
        minimal_error = ResearchError(
            error_type="Processing Error",
            error_message="Invalid data format",
            timestamp="2024-03-10T12:00:00"
        )
        assert minimal_error.error_type == "Processing Error"
        assert minimal_error.error_message == "Invalid data format"
        assert minimal_error.context == ""  # Default value
        assert minimal_error.impact == ""  # Default value
        assert minimal_error.resolution is None  # Default value
        assert minimal_error.timestamp == "2024-03-10T12:00:00"

        # Missing required fields
        with pytest.raises(ValidationError):
            ResearchError(
                error_type="API Error",
                # Missing error_message
                timestamp="2024-03-10T12:00:00"
            )

        with pytest.raises(ValidationError):
            ResearchError(
                error_type="API Error",
                error_message="Failed to connect to search API"
                # Missing timestamp
            )

    def test_research_error_log(self):
        """Test ResearchErrorLog model."""
        # Valid instance
        error_log = ResearchErrorLog(
            errors=[
                ResearchError(
                    error_type="API Error",
                    error_message="Failed to connect to search API",
                    timestamp="2024-03-10T12:34:56"
                ),
                ResearchError(
                    error_type="Processing Error",
                    error_message="Invalid data format",
                    timestamp="2024-03-10T12:45:00"
                )
            ]
        )
        assert len(error_log.errors) == 2
        assert error_log.errors[0].error_type == "API Error"
        assert error_log.errors[1].error_type == "Processing Error"

        # Empty error list is valid
        empty_log = ResearchErrorLog()
        assert len(empty_log.errors) == 0