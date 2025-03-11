"""
Centralized prompt management for the deep research system.

This module contains all prompts used throughout the application, providing a single
location for managing, updating, and customizing research-related prompts.
"""

from datetime import datetime
from typing import Dict, Optional, List


class PromptManager:
    """
    Manage and customize prompts for the deep research system.

    This class centralizes all prompts used in the research process, allowing for:
    - Domain-specific customizations (finance, science, policy, etc.)
    - Consistent prompt formatting
    - Single point of maintenance for prompt content
    """

    def __init__(self, domain: Optional[str] = None):
        """
        Initialize the prompt manager.

        Args:
            domain: Optional domain specialization (finance, science, policy, engineering, consumer)
        """
        self.domain = domain
        if not self.domain:
            self.domain = "finance"

        self.timestamp = datetime.now().isoformat()

    def get_system_prompt(self) -> str:
        """Generate the system prompt with domain-specific adaptations if needed."""
        base_prompt = f"""You are an expert research analyst with a focus on deep, multi-step research. Today is {self.timestamp}. When responding, adhere to the following refined guidelines:

- **Data Relevance:** Focus exclusively on data and insights directly pertinent to the user's inquiry.
- **Rigorous Analysis:** Conduct an in-depth, systematic examination of the relevant information by extracting, analyzing, and synthesizing only context-specific data.
- **Evidence-Based Insights:** Deliver precise, highly accurate conclusions supported by detailed, verifiable evidence.
- **Progressive Learning:** Incorporate and build upon insights from previous analyses to continually refine your understanding and approach.
- **Innovative Directions:** Propose creative solutions and novel research pathways.
- **Structured Presentation:** Organize your response with a clear, logical framework.
- **Iterative Refinement:** Anticipate follow-up inquiries by refining your analysis based solely on data relevant to the research question.
- **Chain-of-Thought:** Include a detailed chain-of-thought reasoning section that outlines every step of your analysis, including how sources were selected, analyzed, and synthesized.
"""

        # Add domain-specific adaptations if a domain is specified
        if self.domain:
            domain_adaptation = self._get_domain_adaptation()
            if domain_adaptation:
                base_prompt += f"\n\n{domain_adaptation}"

        return base_prompt

    def _get_domain_adaptation(self) -> str:
        """Get domain-specific prompt adaptations."""
        domain_adaptations = {
            "finance": """**Finance Domain Adaptations:**
- Prioritize quantitative data, financial metrics, and time-sensitive information
- Pay special attention to market trends, economic indicators, and regulatory context
- Distinguish between historical performance and forward-looking projections
- Assess risk factors and uncertainty in financial analyses
- Consider both technical and fundamental analysis perspectives
- Note the credibility and expertise of financial information sources""",

            "science": """**Science Domain Adaptations:**
- Evaluate methodology rigor and experimental design in scientific sources
- Assess sample sizes, statistical significance, and replication status
- Distinguish between peer-reviewed research and preliminary findings
- Track consensus across multiple scientific studies
- Consider limitations and constraints of scientific methods used
- Note conflicts of interest in research funding when apparent""",

            "policy": """**Policy Domain Adaptations:**
- Balance perspectives from diverse stakeholders and interest groups
- Consider historical context and policy precedents
- Evaluate implementation feasibility and practical constraints
- Assess both intended outcomes and potential unintended consequences
- Distinguish between evidence-based policy analysis and advocacy positions
- Consider regulatory frameworks and legal considerations""",

            "engineering": """**Engineering Domain Adaptations:**
- Prioritize technical specifications, performance metrics, and practical applications
- Evaluate technical feasibility and implementation challenges
- Consider scalability, maintainability, and system integration aspects
- Assess technology readiness levels and maturity of solutions
- Evaluate trade-offs between different engineering approaches
- Consider both theoretical principles and real-world applications""",

            "consumer": """**Consumer Research Adaptations:**
- Evaluate product features, user experiences, and reliability data
- Consider price-to-value relationships and competitive positioning
- Assess both expert reviews and user feedback
- Consider product lifecycle, longevity, and support infrastructure
- Evaluate brand reputation and customer service quality
- Balance objective performance metrics with subjective user preferences"""
        }

        return domain_adaptations.get(self.domain.lower(), "")

    def get_chain_of_thought_prompt(self) -> str:
        """Generate the chain of thought prompt."""
        return """Based on the provided chain-of-thought context below:
    Please provide a well-organized detailed summary that outlines every reasoning step taken during the research process. 
    Include how each source was analyzed, the logic behind follow-up queries, and the synthesis of insights that led to your final conclusions.

    Your summary should:
    1. Chronicle the research journey from initial queries to final insights
    2. Explain how the initial research plan was adapted based on emerging information
    3. Detail how information was verified across multiple sources
    4. Identify key decision points and explain the rationale for choices made
    5. Describe how contradictory information was reconciled
    6. Note any research paths that were abandoned and explain why
    7. Highlight methodological insights gained that could improve future research
    """

    def get_narrative_report_prompt(self) -> str:
        """Generate the narrative report prompt with domain-specific adaptations if needed."""
        base_prompt = """Create a comprehensive, markdown-formatted final report based solely on the user's prompt and the research learnings. The report should be structured with the following sections:

## Introduction
- Brief overview of the research objectives
- Context and background for the research question
- Scope and limitations of the research

## Methodology
- Detailed explanation of the research process
- Search strategy and query generation approach
- Source selection and evaluation criteria
- Iterations and refinements in the research approach

## Findings
- Key insights and learnings, supported by data and analysis
- Organization by themes or sub-questions
- Clear distinction between facts, consensus views, and speculative insights
- Acknowledgment of contradictions or disagreements across sources

## Analysis
- Synthesis of findings into a coherent narrative
- Identification of patterns, trends, and connections
- Assessment of the significance and implications of findings

## Recommendations
- Actionable conclusions and suggestions based on the research
- Strategic or tactical recommendations tailored to the research question

## Future Research Directions
- Identified information gaps
- Promising areas for further investigation
- Suggested methodologies for addressing remaining questions

Ensure clarity, precision, and a logical flow throughout the report. Use succinct language while maintaining comprehensive coverage of important topics.
"""

        # Add domain-specific adaptations for report structure if needed
        if self.domain:
            domain_report_adaptation = self._get_domain_report_adaptation()
            if domain_report_adaptation:
                base_prompt += f"\n\n{domain_report_adaptation}"

        return base_prompt

    def _get_domain_report_adaptation(self) -> str:
        """Get domain-specific report prompt adaptations."""
        domain_report_adaptations = {
            "finance": """**Financial Report Structure:**
- Include a 'Market Context' section that situates findings within current economic conditions
- Add a 'Risk Assessment' section that evaluates potential downside scenarios
- Ensure recommendations include time horizons and risk tolerance considerations
- Include relevant financial metrics, performance indicators, and comparative benchmarks
- Distinguish clearly between historical analysis and forward-looking projections""",

            "science": """**Scientific Report Structure:**
- Include a 'Literature Review' section that surveys the existing research landscape
- Add a 'Methodological Assessment' section that evaluates the quality of scientific evidence
- Ensure findings distinguish between robust conclusions and preliminary hypotheses
- Include a discussion of methodological limitations and their impact on conclusions
- Consider alternative explanations for observed patterns and findings""",

            "policy": """**Policy Report Structure:**
- Include a 'Stakeholder Analysis' section that maps interests and positions
- Add a 'Policy Options' section that clearly outlines alternative approaches
- Ensure recommendations consider implementation challenges and political feasibility
- Include criteria for policy evaluation and metrics for success
- Consider both short-term outcomes and long-term implications""",

            "engineering": """**Engineering Report Structure:**
- Include a 'Technical Specifications' section with relevant performance parameters
- Add a 'Comparative Analysis' section that evaluates competing solutions
- Ensure recommendations include implementation roadmaps and resource requirements
- Include discussion of scalability, maintainability, and integration considerations
- Consider technical limitations and potential opportunities for innovation""",

            "consumer": """**Consumer Research Report Structure:**
- Include a 'Product Comparison' section that evaluates alternatives
- Add a 'Value Assessment' section that analyzes price-to-performance ratios
- Ensure recommendations include considerations for different user segments
- Include both objective performance metrics and subjective user experience factors
- Consider product lifecycle, longevity, and support ecosystem"""
        }

        return domain_report_adaptations.get(self.domain.lower(), "")

    # SERP Query Generation Prompts
    def get_serp_queries_prompt(self, query: str, num_queries: int = 3, learnings: List[str] = None) -> str:
        """
        Generate a prompt for SERP query generation based on a research question.

        Args:
            query: The research question or topic
            num_queries: The number of queries to generate
            learnings: Previous research learnings to guide query generation

        Returns:
            Formatted prompt for generating search engine queries
        """
        # Include learnings from previous research if available
        learnings_context = ""
        if learnings and len(learnings) > 0:
            learnings_context = (
                    "\n**Learnings from Previous Research for Guiding Focused Query Generation:**\n<learnings>\n"
                    + "\n\n".join(learnings) + "\n</learnings>"
            )

        return f"""\
        Based on the user-provided prompt, generate a concise set of SERP queries that are exclusively aligned with the request. 
        These queries should directly pertain to extracting, analyzing, and synthesizing information relevant to the user's specified topic, 
        and must always include the full entity name mentioned in the prompt. The queries should foster deep, innovative research and rigorous 
        analysis while ensuring a tight focus on the context and scope outlined in the prompt.

        For each query, provide:
        1. The search query text optimized for search engines
        2. The specific research goal this query addresses
        3. How this query differs from and complements other queries in the set

        Limit the output to a maximum of {num_queries} queries. If the user's prompt is already clear and well-defined, 
        feel free to return fewer queries, ensuring that each query is strictly aligned with the request and that full entity names are explicitly specified.

        **User Prompt:**  
        <prompt>{query}</prompt>
        {learnings_context}
        """

    def get_search_engine_queries_prompt(self, prompt: str) -> str:
        """
        Generate a prompt for decomposing a complex research question into specific search engine queries.

        Args:
            prompt: The research question or topic

        Returns:
            Formatted prompt for generating specific search engine queries
        """
        return f"""
        You are a specialized assistant tasked with decomposing a complex user prompt into targeted search engine queries. Follow these steps:

        1. **Analyze the Query:** Identify the main topics, subtopics, and relevant keywords.
        2. **Identify Components:** Break the prompt into essential parts.
        3. **Generate Focused Search Queries:** Craft concise queries that are clear, specific, and include the full entity names.
        4. **Ensure Diversity:** Create queries that approach the topic from different angles.
        5. **Present the Queries Clearly:** List the generated queries in a numbered format.

        # User's prompt:
        <prompt>{prompt}</prompt>
        """

    def get_source_evaluation_prompt(self, sources_content: str) -> str:
        """
        Generate a prompt for evaluating the credibility and relevance of sources.

        Args:
            sources_content: Formatted content from sources to evaluate

        Returns:
            Formatted prompt for source evaluation
        """
        return f"""\
        Evaluate the credibility and relevance of the provided sources based on the following criteria:

        1. **Credibility Assessment:**
           - Publisher reputation and editorial standards
           - Currency and timeliness of information
           - Presence of supporting evidence
           - Transparency about methodologies
           - Balanced presentation vs. bias

        2. **Relevance Assessment:**
           - Direct alignment with the research topic
           - Depth of coverage on the specific topic
           - Uniqueness of perspective or information
           - Potential biases that may affect interpretation

        For each source, provide:
        - An overall credibility rating (high, medium, low)
        - An overall relevance rating (high, medium, low)
        - Brief justification for the ratings
        - Key points extracted from the source

        Sources to evaluate:
        {sources_content}
        """

    def get_serp_result_processing_prompt(self, query: str, contents_str: str,
                                          num_learnings: int = 3,
                                          current_date: str = None,
                                          validation_context: str = "") -> str:
        """
        Generate a prompt for processing search results to extract relevant learnings.

        Args:
            query: The search query that produced the results
            contents_str: Formatted content from search results
            num_learnings: Number of key learnings to extract
            current_date: Current date for temporal context
            validation_context: Additional validation issues to consider

        Returns:
            Formatted prompt for processing search results
        """
        current_date = current_date or datetime.now().strftime('%Y-%m-%d')

        return f"""\
        Analyze the following SERP content for the query <query>{query}</query> and extract, analyze, and synthesize insights that are exclusively relevant to the user's request. 

        For each insight:
        1. Ensure it is succinct, evidence-backed, and directly tied to the specifics of the query
        2. Always specify the full entity name to ensure clarity and precision, avoiding abbreviations or partial names
        3. Include relevant metrics, dates, and other specific data points
        4. Distinguish between well-established facts, consensus views, and contested or speculative claims
        5. Note any contradictions or disagreements across sources
        6. Identify information gaps that might require further research
        7. Be especially cautious with temporal statements (past/present/future events)
        8. Flag any unreasonably precise long-term projections
        9. Consider current date context ({current_date}) when evaluating time-sensitive information

        Return up to {num_learnings} high-quality insights, but fewer if the content is clear and concise.

        Also generate follow-up questions that would help fill important information gaps or resolve contradictions.

        {validation_context}
        SERP Content:

        <contents>
        {contents_str}
        </contents>"""

    def get_enhanced_chain_of_thought_prompt(self, chain_of_thought_string: str) -> str:
        """
        Generate an enhanced prompt for creating a chain of thought summary.

        Args:
            chain_of_thought_string: The chain of thought reasoning steps as a string

        Returns:
            Formatted prompt for generating a chain of thought summary
        """
        base_prompt = self.get_chain_of_thought_prompt()

        return f"""\
        {base_prompt}

        ## Guidelines for the Chain-of-Thought Summary:

        1. **Structure the Summary Chronologically:** Organize the summary to reflect the sequential flow of the research process.
        2. **Highlight Decision Points:** Emphasize key decision points and the rationale behind them.
        3. **Trace Query Evolution:** Show how queries evolved through iterations and why changes were made.
        4. **Explain Source Selection:** Describe how sources were evaluated and selected.
        5. **Document Synthesis Process:** Explain how information from different sources was combined and analyzed.
        6. **Identify Dead Ends:** Note any research paths that were abandoned and explain why.
        7. **Extract Methodological Insights:** Highlight procedural lessons that could improve future research.
        8. **Document Validation Challenges:** Explain how validation issues and contradictions were detected and handled.

        **Chain-of-Thought Summary:**  
        <chain_of_thought>{chain_of_thought_string}</chain_of_thought>
        """

    def get_enhanced_report_prompt(self, prompt: str, learnings_string: str,
                                   current_date: str = None,
                                   information_map_string: str = "",
                                   contradictions_string: str = "",
                                   evaluations_string: str = "") -> str:
        """
        Generate an enhanced prompt for creating the final research report.

        Args:
            prompt: The original research question
            learnings_string: Formatted learnings from the research
            current_date: Current date for temporal context
            information_map_string: Formatted information map
            contradictions_string: Formatted contradictions
            evaluations_string: Formatted source evaluations

        Returns:
            Formatted prompt for generating the final report
        """
        current_date = current_date or datetime.now().strftime('%Y-%m-%d')
        base_prompt = self.get_narrative_report_prompt()

        return f"""\
        {base_prompt}

        ## Enhanced Report Structure Guidelines:

        1. **Introduction**
           - Clearly state the research objective
           - Provide context for the research question
           - Outline the scope and limitations of the research
           - Acknowledge the current date context ({current_date})

        2. **Methodology**
           - Detail the multi-stage research approach used
           - Explain the query generation and refinement process
           - Describe the source selection and evaluation criteria
           - Explain how contradictory information was handled
           - Note the breadth and depth parameters of the research

        3. **Data Quality Assessment**
           - Evaluate source credibility and reliability
           - Note temporal inconsistencies or contradictions
           - Distinguish between factual, speculative, and opinion-based content
           - Acknowledge limitations in available data

        4. **Findings**
           - Organize insights by theme or sub-question
           - Distinguish between established facts, emerging consensus, and contested claims
           - Highlight patterns, trends, and connections across sources
           - Address contradictions and alternative interpretations
           - Clearly label speculative projections vs. verified data

        5. **Analysis and Implications**
           - Synthesize key insights into higher-level understanding
           - Discuss the significance of the findings
           - Explore practical applications or theoretical implications

        6. **Recommendations**
           - Provide actionable recommendations based on the research
           - Suggest strategies for addressing identified challenges

        7. **Future Research Directions**
           - Identify remaining information gaps
           - Suggest methodologies for addressing open questions

        **User Prompt:**  
        <prompt>{prompt}</prompt>

        **Research Learnings:**  
        <learnings>{learnings_string}</learnings>

        {information_map_string}
        {contradictions_string}
        {evaluations_string}
        """

    def get_follow_up_questions_prompt(self, num_questions: int = 3) -> str:
        """Generate a prompt for creating follow-up questions."""
        return f"""Based on the research findings so far, generate {num_questions} focused follow-up questions that would help:

        1. Fill critical information gaps in the current research
        2. Resolve contradictions or inconsistencies in the information gathered
        3. Explore promising tangential topics that emerged during research
        4. Deepen understanding of key concepts or relationships
        5. Test alternative hypotheses or interpretations of the findings

        Each question should be:
        - Specific and targeted (not overly broad)
        - Directly relevant to advancing the main research objective
        - Formulated to yield new insights beyond what has already been discovered
        - Designed to challenge assumptions or explore alternative perspectives
        """


# Function to get the system prompt
def system_prompt(domain: Optional[str] = None) -> str:
    """Get the system prompt with optional domain specialization."""
    prompt_manager = PromptManager(domain=domain)
    return prompt_manager.get_system_prompt()


# Function to get the chain of thought prompt
def chain_of_thought_prompt() -> str:
    """Get the chain of thought prompt."""
    prompt_manager = PromptManager()
    return prompt_manager.get_chain_of_thought_prompt()


# Function to get the narrative report prompt
def narrative_report_prompt(domain: Optional[str] = None) -> str:
    """Get the narrative report prompt with optional domain specialization."""
    prompt_manager = PromptManager(domain=domain)
    return prompt_manager.get_narrative_report_prompt()


# Function to get a specific prompt with optional parameters
def get_prompt(prompt_type: str, **kwargs) -> str:
    """
    Get a specific prompt with optional parameters.

    Args:
        prompt_type: Type of prompt to retrieve
        **kwargs: Parameters specific to the prompt type

    Returns:
        Formatted prompt string
    """
    prompt_manager = PromptManager(domain=kwargs.get('domain'))

    if prompt_type == "serp_queries":
        return prompt_manager.get_serp_queries_prompt(
            query=kwargs.get('query', ''),
            num_queries=kwargs.get('num_queries', 3),
            learnings=kwargs.get('learnings', [])
        )
    elif prompt_type == "search_engine_queries":
        return prompt_manager.get_search_engine_queries_prompt(
            prompt=kwargs.get('prompt', '')
        )
    elif prompt_type == "source_evaluation":
        return prompt_manager.get_source_evaluation_prompt(
            sources_content=kwargs.get('sources_content', '')
        )
    elif prompt_type == "serp_result_processing":
        return prompt_manager.get_serp_result_processing_prompt(
            query=kwargs.get('query', ''),
            contents_str=kwargs.get('contents_str', ''),
            num_learnings=kwargs.get('num_learnings', 3),
            current_date=kwargs.get('current_date'),
            validation_context=kwargs.get('validation_context', '')
        )
    elif prompt_type == "enhanced_chain_of_thought":
        return prompt_manager.get_enhanced_chain_of_thought_prompt(
            chain_of_thought_string=kwargs.get('chain_of_thought_string', '')
        )
    elif prompt_type == "enhanced_report":
        return prompt_manager.get_enhanced_report_prompt(
            prompt=kwargs.get('prompt', ''),
            learnings_string=kwargs.get('learnings_string', ''),
            current_date=kwargs.get('current_date'),
            information_map_string=kwargs.get('information_map_string', ''),
            contradictions_string=kwargs.get('contradictions_string', ''),
            evaluations_string=kwargs.get('evaluations_string', '')
        )
    elif prompt_type == "follow_up_questions":
        return prompt_manager.get_follow_up_questions_prompt(
            num_questions=kwargs.get('num_questions', 3)
        )
    else:
        raise ValueError(f"Unknown prompt type: {prompt_type}")