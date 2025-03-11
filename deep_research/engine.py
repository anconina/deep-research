"""
Core research engine functionality.

This module contains the ResearchEngine class that orchestrates the entire
research process, including query generation, search execution, content
scraping, analysis, and result synthesis.
"""

import logging
import math
import os
import re
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from firecrawl import FirecrawlApp

from deep_research.llm import trim_prompt, generate_object

# Import search engines
from deep_research.search_engines.bing.bing import BingSearch
from deep_research.search_engines.duckduckgo.duckduckgo import Duckduckgo
from deep_research.search_engines.tavily.tavily_search import TavilySearch

# Import pydantic models
from deep_research.models import (
    Learnings,
    SerpQueries,
    SerpQuery,
    SearchEngineQueries,
    SourceEvaluations
)

# Import local modules
from deep_research.memory import ResearchMemory
from deep_research.progress import ResearchProgress
from deep_research.content_classifier import ContentClassifier
from deep_research.prompts import system_prompt, get_prompt
from deep_research.auto_tuning import AutoTuner


# Configure logging
logger = logging.getLogger(__name__)

# Initialize web scraping client
firecrawl = FirecrawlApp()


class ResearchEngine:
    """
    Core engine for executing the deep research process.

    This class orchestrates the entire research process, including:
    - Query generation and execution
    - Content scraping and validation
    - Source evaluation
    - Learning extraction
    - Contradiction detection
    - Information synthesis
    - Automatic parameter tuning
    """

    def __init__(self, auto_tune: bool = False, max_depth: int = 5, max_breadth: int = 8,
                 time_budget_seconds: int = None):
        """
        Initialize the research engine with memory and content validation systems.

        Args:
            auto_tune: Whether to automatically determine research depth/breadth
            max_depth: Maximum allowed research depth when auto-tuning
            max_breadth: Maximum allowed research breadth when auto-tuning
            time_budget_seconds: Optional time budget in seconds for auto-tuning
        """
        self.model = os.environ['LLM_MODEL_NAME']
        self.memory = ResearchMemory()
        self.progress = None
        self.content_classifier = ContentClassifier(self.memory.current_date)
        self.auto_tune = auto_tune

        # Initialize auto-tuner if auto_tune is enabled
        if auto_tune:
            self.auto_tuner = AutoTuner(
                max_depth=max_depth,
                max_breadth=max_breadth,
                time_budget_seconds=time_budget_seconds
            )
        else:
            self.auto_tuner = None

    async def determine_auto_parameters(self, query: str) -> Tuple[int, int]:
        """
        Determine optimal research parameters automatically.

        Args:
            query: The research question

        Returns:
            Tuple of (depth, breadth)
        """
        if not self.auto_tune or not self.auto_tuner:
            return 2, 4  # Default values if auto-tuning is disabled

        # Analyze question complexity
        complexity_metrics = await self.auto_tuner.analyze_question_complexity(query)

        # Determine initial parameters based on complexity
        depth, breadth = self.auto_tuner.determine_initial_parameters(complexity_metrics)

        self.memory.add_thought(
            f"Auto-tuned parameters - Initial depth: {depth}, breadth: {breadth} " +
            f"(complexity score: {complexity_metrics['complexity_score']:.2f})"
        )

        return depth, breadth

    async def adjust_parameters(self, current_depth: int, current_breadth: int) -> Tuple[int, int]:
        """
        Adjust research parameters based on ongoing results.

        Args:
            current_depth: Current research depth
            current_breadth: Current research breadth

        Returns:
            Tuple of (new_depth, new_breadth)
        """
        if not self.auto_tune or not self.auto_tuner:
            return current_depth, current_breadth

        # Estimate information quality
        info_quality = self.auto_tuner.estimate_info_quality(
            self.memory.learnings,
            self.memory.contradictions
        )

        # Get time usage fraction
        time_usage = self.auto_tuner.get_time_usage_fraction()

        # Adjust parameters
        new_depth, new_breadth = self.auto_tuner.adjust_parameters(
            current_depth,
            current_breadth,
            info_quality,
            time_usage
        )

        if new_depth != current_depth or new_breadth != current_breadth:
            self.memory.add_thought(
                f"Auto-adjusted parameters - New depth: {new_depth}, breadth: {new_breadth} " +
                f"(info quality: {info_quality:.2f}, time usage: {time_usage:.2f})"
            )

        return new_depth, new_breadth

    async def generate_serp_queries(self, query: str, num_queries: int = 3) -> List[SerpQuery]:
        """
        Generate search engine queries based on the research question and current learnings.

        Args:
            query: The research question or topic
            num_queries: Number of queries to generate

        Returns:
            List of SerpQuery objects
        """
        self.memory.add_thought(f"Generating SERP queries for: {query}")

        # Generate prompt using the centralized prompt management
        prompt_text = get_prompt(
            prompt_type="serp_queries",
            query=query,
            num_queries=num_queries,
            learnings=self.memory.learnings
        )

        try:
            result = await generate_object(
                model=self.model,
                system=system_prompt(),
                prompt=prompt_text,
                schema=SerpQueries,
            )

            serp_queries = SerpQueries.model_validate_json(result)
            query_count = len(serp_queries.queries)

            self.memory.add_thought(f"Generated {query_count} SERP queries")
            for i, q in enumerate(serp_queries.queries):
                self.memory.add_thought(f"Query {i + 1}: {q.query} - Goal: {q.research_goal}")

            return serp_queries.queries[:num_queries]

        except Exception as e:
            error_msg = f"Error generating SERP queries: {str(e)}"
            logger.error(error_msg)
            self.memory.add_thought(error_msg)
            return []

    async def generate_search_engine_queries(self, prompt: str) -> List[str]:
        """
        Generate specific search engine queries to maximize result relevance.

        Args:
            prompt: The research question or topic

        Returns:
            List of search engine query strings
        """
        self.memory.add_thought(f"Decomposing research prompt into specific search queries")

        # Generate prompt using the centralized prompt management
        system_prompt_text = get_prompt(
            prompt_type="search_engine_queries",
            prompt=prompt
        )

        try:
            res = await generate_object(
                model=self.model,
                system=system_prompt_text,
                prompt="",
                schema=SearchEngineQueries,
            )

            queries = SearchEngineQueries.model_validate_json(res)
            self.memory.add_thought(f"Generated {len(queries.queries)} search engine queries")
            return queries.queries

        except Exception as e:
            error_msg = f"Error generating search engine queries: {str(e)}"
            logger.error(error_msg)
            self.memory.add_thought(error_msg)
            return []

    async def execute_search(self, query: str, max_results: int = 4) -> List[str]:
        """
        Execute search and retrieve relevant URLs.

        Args:
            query: The search query
            max_results: Maximum number of results per search query

        Returns:
            List of unique URLs from search results
        """
        self.memory.add_thought(f"Executing search for query: {query}")

        try:
            # Generate specific search queries from the SERP query
            search_queries = await self.generate_search_engine_queries(query)

            # Collect URLs from multiple search queries
            all_urls = []
            for search_query in search_queries:
                self.memory.add_thought(f"Searching for: {search_query}")
                search_engine = TavilySearch(search_query)
                search_results = await search_engine.search(max_results=max_results)

                # Extract URLs from search results
                urls = [result.get("href") for result in search_results if "href" in result]
                all_urls.extend(urls)

                self.memory.add_thought(f"Found {len(urls)} results for query: {search_query}")

            # Remove duplicates while preserving order
            unique_urls = []
            for url in all_urls:
                if url not in unique_urls:
                    unique_urls.append(url)

            self.memory.add_thought(f"Collected {len(unique_urls)} unique URLs across all search queries")
            return unique_urls

        except Exception as e:
            error_msg = f"Error executing search: {str(e)}"
            logger.error(error_msg)
            self.memory.add_thought(error_msg)
            return []

    async def scrape_content(self, urls: List[str]) -> Dict:
        """
        Scrape content from the provided URLs.

        Args:
            urls: List of URLs to scrape

        Returns:
            Dictionary containing scraped content and metadata
        """
        self.memory.add_thought(f"Scraping content from {len(urls)} URLs")

        try:
            # Configure scraping parameters
            params = {
                "formats": ["markdown"],
                "onlyMainContent": True,
                "timeout": 30000
            }

            # Execute batch scraping
            result = firecrawl.batch_scrape_urls(urls, params=params)

            # Track successfully scraped URLs
            successful_urls = []
            for item in result.get("data", []):
                metadata = item.get("metadata", {})
                status_code = metadata.get("statusCode")
                url = metadata.get("url", "unknown")

                if status_code == 200:
                    successful_urls.append(url)
                else:
                    self.memory.add_thought(f"Failed to scrape URL {url}: Status {status_code}")

            self.memory.add_thought(f"Successfully scraped {len(successful_urls)} out of {len(urls)} URLs")
            return result

        except Exception as e:
            error_msg = f"Error scraping content: {str(e)}"
            logger.error(error_msg)
            self.memory.add_thought(error_msg)
            return {"data": []}

    async def evaluate_sources(self, urls: List[str], contents: List[str]) -> List[Dict]:
        """
        Evaluate the credibility and relevance of sources.

        Args:
            urls: List of source URLs
            contents: List of source contents corresponding to URLs

        Returns:
            List of source evaluation dictionaries
        """
        self.memory.add_thought(f"Evaluating credibility and relevance of {len(urls)} sources")

        if not urls or not contents or len(urls) != len(contents):
            self.memory.add_thought("Cannot evaluate sources: mismatch between URLs and contents")
            return []

        evaluations = []

        # Prepare the content for source evaluation
        sources_content = ""
        for i, (url, content) in enumerate(zip(urls, contents)):
            # Trim content to avoid token limits
            trimmed_content = trim_prompt(content, 1000)  # Short excerpt for evaluation
            sources_content += f"<source id='{i + 1}'>\n<url>{url}</url>\n<content>{trimmed_content}</content>\n</source>\n\n"

        # Generate prompt using the centralized prompt management
        prompt_text = get_prompt(
            prompt_type="source_evaluation",
            sources_content=sources_content
        )

        try:
            res = await generate_object(
                model=self.model,
                system=system_prompt(),
                prompt=prompt_text,
                schema=SourceEvaluations,
            )

            source_evaluations = SourceEvaluations.model_validate_json(res)

            # Convert Pydantic models to dictionaries for storage
            for eval in source_evaluations.evaluations:
                eval_dict = eval.model_dump()
                evaluations.append(eval_dict)
                self.memory.add_source_evaluation(eval_dict)

                self.memory.add_thought(
                    f"Source evaluation - URL: {eval.url} - Credibility: {eval.credibility_rating}, "
                    f"Relevance: {eval.relevance_rating}"
                )

            return evaluations

        except Exception as e:
            error_msg = f"Error evaluating sources: {str(e)}"
            logger.error(error_msg)
            self.memory.add_thought(error_msg)
            return []

    async def process_serp_result(self, query: str, result: Dict, num_learnings: int = 3) -> Optional[Learnings]:
        """
        Process search results to extract relevant learnings with enhanced validation.

        Args:
            query: The search query
            result: Dictionary containing search results
            num_learnings: Number of key learnings to extract

        Returns:
            Learnings object containing extracted learnings and follow-up questions
        """
        self.memory.add_thought(f"Processing search results for query: {query}")

        # Extract content from successful scrapes
        contents = []
        urls = []
        for item in result.get("data", []):
            metadata = item.get("metadata", {})
            status_code = metadata.get("statusCode")
            url = metadata.get("url", "unknown")

            if status_code == 200:
                content = item.get("markdown", "")
                if content:
                    # Trim content to avoid token limits
                    trimmed_content = trim_prompt(content, 25000)
                    contents.append(trimmed_content)
                    urls.append(url)

        if not contents:
            self.memory.add_thought("No valid content found in search results")
            return None

        self.memory.add_thought(f"Analyzing {len(contents)} content sources")

        # Evaluate source credibility and relevance
        await self.evaluate_sources(urls, contents)

        # Perform content validation
        validation_issues = []
        for i, content in enumerate(contents):
            # Check for temporal consistency
            temporal_valid, temporal_msg = self.content_classifier.validate_temporal_consistency(content)
            if not temporal_valid:
                self.memory.add_thought(f"Temporal inconsistency in source {urls[i]}: {temporal_msg}")
                validation_issues.append(f"Source {urls[i]}: {temporal_msg}")

            # Check for numerical reasonableness
            numerical_valid, numerical_msg = self.content_classifier.validate_numerical_reasonableness(content)
            if not numerical_valid:
                self.memory.add_thought(f"Numerical issue in source {urls[i]}: {numerical_msg}")
                validation_issues.append(f"Source {urls[i]}: {numerical_msg}")

            # Classify content type
            content_type = self.content_classifier.classify_content_type(content)
            self.memory.add_thought(f"Content from {urls[i]} classified as: {content_type}")

        # Format contents for analysis
        contents_str = "\n".join([f"<content>\n{content}\n</content>" for content in contents])

        # Add validation issues to the prompt if any were found
        validation_context = ""
        if validation_issues:
            validation_context = "\n**Content Validation Issues:**\n<validation_issues>\n" + "\n".join(
                validation_issues) + "\n</validation_issues>\n"
            self.memory.add_thought(f"Including {len(validation_issues)} validation issues in analysis prompt")

        # Generate prompt using the centralized prompt management
        prompt_text = get_prompt(
            prompt_type="serp_result_processing",
            query=query,
            contents_str=contents_str,
            num_learnings=num_learnings,
            current_date=self.memory.current_date.strftime('%Y-%m-%d'),
            validation_context=validation_context
        )

        try:
            res = await generate_object(
                model=self.model,
                system=system_prompt(),
                prompt=prompt_text,
                schema=Learnings,
            )

            learnings = Learnings.model_validate_json(res)

            self.memory.add_thought(f"Extracted {len(learnings.learnings)} learnings")
            self.memory.add_thought(f"Generated {len(learnings.follow_up_questions)} follow-up questions")

            # Log the extracted learnings
            for i, learning in enumerate(learnings.learnings):
                self.memory.add_thought(f"Learning {i + 1}: {learning[:100]}...")

                # Detect potential contradictions with existing learnings
                self.detect_contradictions(learning)

            return learnings

        except Exception as e:
            error_msg = f"Error processing search results: {str(e)}"
            logger.error(error_msg)
            self.memory.add_thought(error_msg)
            return None

    def detect_contradictions(self, new_learning: str) -> None:
        """
        Detect potential contradictions between new learning and existing learnings.

        Args:
            new_learning: New learning to check for contradictions
        """
        # Skip if no existing learnings
        if not self.memory.learnings:
            return

        # Keywords that might indicate a similar topic
        performance_keywords = ["performance", "growth", "revenue", "sales", "profit", "loss"]
        event_keywords = ["scheduled", "upcoming", "announced", "launched"]
        layoff_keywords = ["layoff", "job cut", "firing", "downsizing"]

        # Check for contradictions on performance
        if any(keyword in new_learning.lower() for keyword in performance_keywords):
            for existing in self.memory.learnings:
                if any(keyword in existing.lower() for keyword in performance_keywords):
                    # If both talk about performance but with opposite sentiment
                    positive_terms = ["growth", "increase", "positive", "strong", "success"]
                    negative_terms = ["decline", "decrease", "negative", "weak", "failure"]

                    new_positive = any(term in new_learning.lower() for term in positive_terms)
                    new_negative = any(term in new_learning.lower() for term in negative_terms)
                    existing_positive = any(term in existing.lower() for term in positive_terms)
                    existing_negative = any(term in existing.lower() for term in negative_terms)

                    if (new_positive and existing_negative) or (new_negative and existing_positive):
                        self.memory.add_contradiction("Performance", existing, new_learning)

        # Check for contradictions on events/dates
        if any(keyword in new_learning.lower() for keyword in event_keywords):
            for existing in self.memory.learnings:
                if any(keyword in existing.lower() for keyword in event_keywords):
                    # If both mention dates but they're different
                    date_pattern = r"(january|february|march|april|may|june|july|august|september|october|november|december).{0,10}(20\d\d)"
                    new_dates = re.findall(date_pattern, new_learning.lower())
                    existing_dates = re.findall(date_pattern, existing.lower())

                    if new_dates and existing_dates and new_dates != existing_dates:
                        self.memory.add_contradiction("Event Dates", existing, new_learning)

        # Check for contradictions on layoffs
        if any(keyword in new_learning.lower() for keyword in layoff_keywords):
            for existing in self.memory.learnings:
                if any(keyword in existing.lower() for keyword in layoff_keywords):
                    # If one mentions plans and the other mentions it already happened
                    plan_terms = ["plan", "will", "future", "expected", "upcoming"]
                    past_terms = ["completed", "announced", "executed", "implemented"]

                    new_plan = any(term in new_learning.lower() for term in plan_terms)
                    new_past = any(term in new_learning.lower() for term in past_terms)
                    existing_plan = any(term in existing.lower() for term in plan_terms)
                    existing_past = any(term in existing.lower() for term in past_terms)

                    if (new_plan and existing_past) or (new_past and existing_plan):
                        self.memory.add_contradiction("Layoff Timeline", existing, new_learning)

    async def execute_query(self, serp_query: SerpQuery, current_depth: int, current_breadth: int) -> Dict:
        """
        Execute a single search query and process the results.

        Args:
            serp_query: SerpQuery object containing the query and research goal
            current_depth: Current depth level of the research
            current_breadth: Current breadth level of the research

        Returns:
            Dictionary containing execution results
        """
        self.memory.add_thought(f"Executing research query: {serp_query.query}")
        self.memory.add_thought(f"Research goal: {serp_query.research_goal}")

        try:
            # Update progress tracking
            if self.progress:
                self.progress.update({
                    "current_query": serp_query.query,
                    "current_depth": current_depth,
                    "current_breadth": current_breadth
                })

            # Step 1: Execute search and get URLs
            search_urls = await self.execute_search(serp_query.query)

            if not search_urls:
                self.memory.add_thought("No search results found. Cannot proceed with this query.")
                return {"success": False, "reason": "No search results found"}

            # Step 2: Scrape content from URLs
            search_result = await self.scrape_content(search_urls)

            # Extract successfully scraped URLs
            successful_urls = []
            for item in search_result.get("data", []):
                metadata = item.get("metadata", {})
                status_code = metadata.get("statusCode")
                url = metadata.get("url", "unknown")

                if status_code == 200:
                    successful_urls.append(url)

            # Step 3: Process the search results
            new_learnings_obj = await self.process_serp_result(
                query=serp_query.query,
                result=search_result,
                num_learnings=current_breadth,
            )

            # Update research memory
            self.memory.add_urls(successful_urls)

            if new_learnings_obj:
                self.memory.add_learnings(new_learnings_obj.learnings)

                # Generate follow-up query if we have learnings and more depth to explore
                if current_depth > 1:
                    follow_up_questions = new_learnings_obj.follow_up_questions

                    self.memory.add_thought(
                        f"Identified {len(follow_up_questions)} follow-up questions for deeper research")
                    for i, question in enumerate(follow_up_questions):
                        self.memory.add_thought(f"Follow-up {i + 1}: {question}")

                    # Use the follow-up questions to guide the next iteration
                    return {
                        "success": True,
                        "new_learnings": new_learnings_obj.learnings,
                        "follow_up_questions": follow_up_questions
                    }

            return {"success": True, "new_learnings": []}

        except Exception as e:
            error_msg = f"Error executing query '{serp_query.query}': {str(e)}"
            logger.error(error_msg)
            self.memory.add_thought(error_msg)
            return {"success": False, "reason": str(e)}

    async def deep_research(self, query: str, breadth: int = None, depth: int = None) -> Dict:
        """
        Execute the deep research process with configurable or automatic breadth and depth.

        Args:
            query: The research question or topic
            breadth: How many parallel queries to explore (breadth of research)
                   If None and auto_tune is True, breadth will be determined automatically.
            depth: How many levels of follow-up queries to explore (depth of research)
                  If None and auto_tune is True, depth will be determined automatically.

        Returns:
            Dictionary containing research results, including learnings, visited URLs, and chain of thought
        """
        # Use automatic parameter determination if enabled and parameters not explicitly provided
        if self.auto_tune and (breadth is None or depth is None):
            auto_depth, auto_breadth = await self.determine_auto_parameters(query)
            depth = depth or auto_depth
            breadth = breadth or auto_breadth
        else:
            # Use default values if not specified
            depth = depth or 2
            breadth = breadth or 4

        # Initialize progress tracking
        self.progress = ResearchProgress(initial_depth=depth, initial_breadth=breadth)

        # If auto-tuning is enabled, set the start time for time budget tracking
        if self.auto_tune and self.auto_tuner:
            self.auto_tuner.start_time = asyncio.get_event_loop().time()

        # Record the start of research
        self.memory.add_thought(f"Starting deep research on: {query}")
        self.memory.add_thought(f"Research parameters - Breadth: {breadth}, Depth: {depth}")
        self.memory.add_thought(f"Current date context: {self.memory.current_date.strftime('%Y-%m-%d')}")

        # Set up the async tasks for executing research
        async def execute_research_iteration(iteration_query: str, current_depth: int, current_breadth: int) -> None:
            """Execute a single iteration of the research process."""
            self.memory.add_thought(
                f"Starting research iteration at depth {current_depth} with breadth {current_breadth}")
            self.memory.add_thought(f"Iteration query: {iteration_query}")

            # Generate search queries
            serp_queries = await self.generate_serp_queries(query=iteration_query, num_queries=current_breadth)

            if not serp_queries:
                self.memory.add_thought("Failed to generate search queries. Ending this research path.")
                return

            # Update progress tracking
            if self.progress:
                self.progress.update({
                    "total_queries": self.progress.total_queries + len(serp_queries)
                })

            # Execute each query
            for serp_query in serp_queries:
                query_result = await self.execute_query(serp_query, current_depth, current_breadth)

                # Update progress tracking
                if self.progress:
                    self.progress.update({
                        "completed_queries": self.progress.completed_queries + 1
                    })

                # If query was successful and we have more depth to explore
                if query_result.get("success", False) and current_depth > 1 and query_result.get("follow_up_questions",
                                                                                                 []):
                    follow_up_questions = query_result.get("follow_up_questions", [])

                    # If auto-tuning is enabled, adjust parameters based on results so far
                    if self.auto_tune:
                        new_depth, new_breadth = await self.adjust_parameters(current_depth - 1, current_breadth)
                    else:
                        # Calculate the new breadth and depth for the next iteration using static approach
                        new_breadth = max(1, math.ceil(current_breadth / 2))
                        new_depth = current_depth - 1

                    # Construct the next iteration query
                    next_query = (
                            f"Previous research goal: {serp_query.research_goal}\n"
                            f"Follow-up research directions:\n" + "\n".join(follow_up_questions[:3])
                    ).strip()

                    # Execute the next iteration
                    await execute_research_iteration(next_query, new_depth, new_breadth)

        # Start the main research process
        await execute_research_iteration(query, depth, breadth)

        # Return the final research results
        self.memory.add_thought("Research process completed")
        return {
            "learnings": self.memory.learnings,
            "visited_urls": self.memory.visited_urls,
            "chain_of_thought": self.memory.chain_of_thought,
            "information_map": self.memory.information_map,
            "contradictions": self.memory.contradictions,
            "source_evaluations": self.memory.source_evaluations
        }