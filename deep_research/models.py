from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field, validator, field_validator


class ChainOfThoughtSummary(BaseModel):
    """Summary of the research reasoning process."""
    summary: str = Field(
        description="Detailed chain-of-thought markdown-formatted summary explaining the reasoning steps."
    )


class FollowUpQuestions(BaseModel):
    """Questions for further research."""
    questions: List[str] = Field(
        description="Follow up questions to clarify the research direction."
    )


class FollowUpQuestionsAnswer(BaseModel):
    """Answers to follow-up questions."""
    answer: List[str] = Field(
        description="Follow up question answer."
    )


class Report(BaseModel):
    """Final research report."""
    markdown: str = Field(
        description="Final report on the topic in Markdown."
    )


class SourceEvaluation(BaseModel):
    """Evaluation of a research source."""
    url: str = Field(
        description="URL of the source."
    )
    title: str = Field(
        description="Title of the source."
    )
    credibility_rating: str = Field(
        description="Credibility rating of the source (high, medium-high, medium, low)."
    )
    relevance_rating: str = Field(
        description="Relevance rating of the source (high, medium-high, medium, low)."
    )
    justification: str = Field(
        description="Justification for the ratings."
    )
    key_points: List[str] = Field(
        description="Key points extracted from the source.",
        default_factory=list
    )

    @field_validator('credibility_rating')
    def validate_credibility_rating(cls, v):
        valid_ratings = ['high', 'medium-high', 'medium', 'low']
        if v.lower() not in valid_ratings:
            raise ValueError(f"Credibility rating must be one of: {', '.join(valid_ratings)}")
        return v.lower()

    @field_validator('relevance_rating')
    def validate_relevance_rating(cls, v):
        valid_ratings = ['high', 'medium-high', 'medium', 'low']
        if v.lower() not in valid_ratings:
            raise ValueError(f"Relevance rating must be one of: {', '.join(valid_ratings)}")
        return v.lower()


class SourceEvaluations(BaseModel):
    """Collection of source evaluations."""
    evaluations: List[SourceEvaluation] = Field(
        description="List of source evaluations."
    )


class InformationItem(BaseModel):
    """Single piece of information extracted from sources."""
    content: str = Field(
        description="The information content."
    )
    source_urls: List[str] = Field(
        description="URLs of sources supporting this information.",
        default_factory=list
    )
    confidence: str = Field(
        description="Confidence level (high, medium, low).",
        default="medium"
    )
    tags: List[str] = Field(
        description="Tags categorizing this information.",
        default_factory=list
    )

    @field_validator('confidence')
    def validate_confidence(cls, v):
        valid_levels = ['high', 'medium', 'low']
        if v.lower() not in valid_levels:
            raise ValueError(f"Confidence must be one of: {', '.join(valid_levels)}")
        return v.lower()


class InformationGroup(BaseModel):
    """Group of related information items."""
    topic: str = Field(
        description="Topic of this information group."
    )
    consensus: List[InformationItem] = Field(
        description="Information with general agreement across sources.",
        default_factory=list
    )
    contradictions: List[InformationItem] = Field(
        description="Information with disagreement across sources.",
        default_factory=list
    )
    gaps: List[str] = Field(
        description="Identified information gaps requiring further research.",
        default_factory=list
    )


class InformationMap(BaseModel):
    """Map of information groups by topic."""
    groups: List[InformationGroup] = Field(
        description="Information groups organized by topic."
    )


class ResearchSummary(BaseModel):
    """Summary of research findings."""
    key_findings: List[str] = Field(
        description="List of key findings from the research."
    )
    themes: List[str] = Field(
        description="Major themes identified in the research.",
        default_factory=list
    )
    recommendations: List[str] = Field(
        description="Recommendations based on the research.",
        default_factory=list
    )
    future_directions: List[str] = Field(
        description="Suggested directions for future research.",
        default_factory=list
    )


class Learnings(BaseModel):
    """Learnings extracted from research."""
    learnings: List[str] = Field(
        description="List of learnings for context-specific, deep-dive research."
    )
    follow_up_questions: List[str] = Field(
        description="Follow-up questions to further refine research based strictly on relevant data."
    )


class SerpQuery(BaseModel):
    """Query for a search engine."""
    query: str = Field(
        description="A SERP query designed for context-specific, innovative research."
    )
    research_goal: str = Field(
        description="A description of the primary research goal and further directions for deep-dive analysis strictly based on the user's request."
    )


class SerpQueries(BaseModel):
    """Collection of search engine queries."""
    queries: List[SerpQuery] = Field(
        description="List of SERP queries for rigorous, context-specific research."
    )


class SearchEngineQueries(BaseModel):
    """Simple list of search engine queries."""
    queries: List[str] = Field(
        description="List of search engine queries."
    )


class ResearchResult(BaseModel):
    """Complete research result including all components."""
    query: str = Field(
        description="Original research query."
    )
    learnings: List[str] = Field(
        description="List of research learnings.",
        default_factory=list
    )
    visited_urls: List[str] = Field(
        description="List of visited URLs.",
        default_factory=list
    )
    chain_of_thought: List[str] = Field(
        description="Chain of thought reasoning steps.",
        default_factory=list
    )
    information_map: Dict[str, Dict[str, List[Union[str, Dict]]]] = Field(
        description="Information map organized by topic.",
        default_factory=dict
    )
    source_evaluations: List[Dict[str, Any]] = Field(
        description="Evaluations of research sources.",
        default_factory=list
    )


class ResearchProgress(BaseModel):
    """Progress tracking for the research process."""
    total_depth: int = Field(
        description="Total planned research depth."
    )
    current_depth: int = Field(
        description="Current research depth."
    )
    total_breadth: int = Field(
        description="Total planned research breadth."
    )
    current_breadth: int = Field(
        description="Current research breadth."
    )
    total_queries: int = Field(
        description="Total number of queries planned.",
        default=0
    )
    completed_queries: int = Field(
        description="Number of completed queries.",
        default=0
    )
    current_query: str = Field(
        description="Current query being processed.",
        default=""
    )
    elapsed_seconds: float = Field(
        description="Elapsed time in seconds.",
        default=0.0
    )
    completion_percentage: float = Field(
        description="Percentage of completion.",
        default=0.0
    )

class ResearchError(BaseModel):
    """Error that occurred during research."""
    error_type: str = Field(
        description="Type of error."
    )
    error_message: str = Field(
        description="Error message."
    )
    context: str = Field(
        description="Context in which the error occurred.",
        default=""
    )
    impact: str = Field(
        description="Impact on the research process.",
        default=""
    )
    resolution: Optional[str] = Field(
        description="Resolution or workaround applied.",
        default=None
    )
    timestamp: str = Field(
        description="Timestamp when the error occurred."
    )


class ResearchErrorLog(BaseModel):
    """Log of errors that occurred during research."""
    errors: List[ResearchError] = Field(
        description="List of research errors.",
        default_factory=list
    )