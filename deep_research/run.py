import asyncio
import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
from deep_research.utils.logger import set_logger
from deep_research import deep_research, write_final_report, write_chain_of_thought_report


# Configure logging

set_logger(level=logging.INFO, log_to_file=True, log_file_path="research.log")
logger = logging.getLogger(__name__)


class ResearchSession:
    """Manage a complete research session with reporting and output files."""

    def __init__(self, query: str, breadth: Optional[int] = None, depth: Optional[int] = None,
                 auto_tune: bool = False, max_depth: int = 5, max_breadth: int = 8,
                 time_budget_seconds: Optional[int] = None, output_dir: str = "research_output"):
        """
        Initialize a research session.

        Args:
            query: Research question or topic
            breadth: Number of parallel queries to explore (optional with auto_tune)
            depth: Number of levels to explore (optional with auto_tune)
            auto_tune: Whether to automatically determine research parameters
            max_depth: Maximum allowed research depth when auto-tuning
            max_breadth: Maximum allowed research breadth when auto-tuning
            time_budget_seconds: Optional time budget in seconds for auto-tuning
            output_dir: Directory to save research output
        """
        self.query = query
        self.breadth = breadth
        self.depth = depth
        self.auto_tune = auto_tune
        self.max_depth = max_depth
        self.max_breadth = max_breadth
        self.time_budget_seconds = time_budget_seconds

        self.start_time = datetime.now()
        self.output_dir = Path(output_dir)
        self.session_id = self.start_time.strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.output_dir / f"session_{self.session_id}"

        # Create output directories
        self.session_dir.mkdir(parents=True, exist_ok=True)

    async def execute(self):
        """Execute the research session and generate reports."""
        try:
            # Log session start
            logger.info(f"Starting research session: {self.session_id}")
            logger.info(f"Query: {self.query}")

            if self.auto_tune:
                logger.info(f"Auto-tuning enabled - Max depth: {self.max_depth}, Max breadth: {self.max_breadth}")
                if self.time_budget_seconds:
                    logger.info(f"Time budget: {self.time_budget_seconds} seconds")
            else:
                logger.info(f"Fixed parameters - Depth: {self.depth}, Breadth: {self.breadth}")

            logger.info(f"Current date: {self.start_time.strftime('%Y-%m-%d')}")

            # Execute research
            logger.info("Creating research plan...")
            logger.info("Starting research with progress tracking...")

            research_result = await deep_research(
                query=self.query,
                breadth=self.breadth,
                depth=self.depth,
                auto_tune=self.auto_tune,
                max_depth=self.max_depth,
                max_breadth=self.max_breadth,
                time_budget_seconds=self.time_budget_seconds
            )

            # Extract research components
            learnings = research_result.get("learnings", [])
            visited_urls = research_result.get("visited_urls", [])
            chain_of_thought = research_result.get("chain_of_thought", [])
            information_map = research_result.get("information_map", {})
            contradictions = research_result.get("contradictions", [])
            source_evaluations = research_result.get("source_evaluations", [])

            # Log results summary
            logger.info(f"\n\nResearch completed with {len(learnings)} learnings from {len(visited_urls)} sources.")
            logger.info(f"Chain of thought contains {len(chain_of_thought)} reasoning steps.")
            logger.info(f"Detected {len(contradictions)} contradictions in the data.")

            # Save raw research data
            self.save_raw_data(research_result)

            # Generate final report
            logger.info("Writing final report...")
            final_report = await write_final_report(
                prompt=self.query,
                learnings=learnings,
                information_map=information_map,
                contradictions=contradictions,
                source_evaluations=source_evaluations
            )

            # Generate chain of thought report
            logger.info("Writing chain of thought report...")
            cot_report = await write_chain_of_thought_report(chain_of_thought=chain_of_thought)

            # Generate sources section
            sources_section = self.format_sources_section(visited_urls, source_evaluations)

            # Generate data quality issues section
            data_quality_section = self.format_data_quality_section(contradictions)

            # Generate auto-tuning section if auto-tuning was enabled
            auto_tuning_section = self.format_auto_tuning_section(chain_of_thought) if self.auto_tune else ""

            # Save all reports
            self.save_reports(final_report, cot_report, sources_section, data_quality_section, auto_tuning_section)

            # Display reports
            print("\n\nFinal Report:\n\n" + final_report)
            print("\n\nChain of Thought Report:\n\n" + cot_report)
            print("\n\nSources Section:\n\n" + sources_section)
            print("\n\nData Quality Issues:\n\n" + data_quality_section)
            if auto_tuning_section:
                print("\n\nAuto-Tuning Decisions:\n\n" + auto_tuning_section)

            # Log completion
            logger.info(f"Research session {self.session_id} completed successfully.")
            logger.info(f"Reports saved to {self.session_dir}")

            return {
                "final_report": final_report,
                "chain_of_thought_report": cot_report,
                "sources_section": sources_section,
                "data_quality_section": data_quality_section,
                "auto_tuning_section": auto_tuning_section if self.auto_tune else None,
                "research_result": research_result
            }

        except Exception as e:
            logger.error(f"Critical error in research session: {str(e)}")
            self.save_error_log(str(e))
            raise

    def save_raw_data(self, research_result: dict):
        """Save raw research data to JSON file."""
        try:
            raw_data_path = self.session_dir / "raw_research_data.json"
            with open(raw_data_path, 'w') as f:
                json.dump(research_result, f, indent=2)
            logger.info(f"Raw research data saved to {raw_data_path}")
        except Exception as e:
            logger.error(f"Error saving raw research data: {str(e)}")

    def save_reports(self, final_report: str, cot_report: str, sources_section: str,
                     data_quality_section: str, auto_tuning_section: str = ""):
        """Save all generated reports to files."""
        try:
            # Save final report
            final_report_path = self.session_dir / "final_report.md"
            with open(final_report_path, 'w') as f:
                f.write(final_report)
            logger.info(f"Final report saved to {final_report_path}")

            # Save chain of thought report
            cot_report_path = self.session_dir / "chain_of_thought_report.md"
            with open(cot_report_path, 'w') as f:
                f.write(cot_report)
            logger.info(f"Chain of thought report saved to {cot_report_path}")

            # Save sources section
            sources_path = self.session_dir / "sources.md"
            with open(sources_path, 'w') as f:
                f.write(sources_section)
            logger.info(f"Sources section saved to {sources_path}")

            # Save data quality issues
            quality_path = self.session_dir / "data_quality_issues.md"
            with open(quality_path, 'w') as f:
                f.write(data_quality_section)
            logger.info(f"Data quality issues saved to {quality_path}")

            # Save auto-tuning decisions if available
            if auto_tuning_section:
                tuning_path = self.session_dir / "auto_tuning_decisions.md"
                with open(tuning_path, 'w') as f:
                    f.write(auto_tuning_section)
                logger.info(f"Auto-tuning decisions saved to {tuning_path}")

            # Create combined report
            combined_report = f"""# Research Report: {self.query}

{final_report}

{data_quality_section}

{sources_section}

"""
            # Add auto-tuning section if available
            if auto_tuning_section:
                combined_report += f"\n{auto_tuning_section}\n"

            combined_report += f"""
---

# Research Process: Chain of Thought Analysis

{cot_report}
"""
            combined_path = self.session_dir / "combined_report.md"
            with open(combined_path, 'w') as f:
                f.write(combined_report)
            logger.info(f"Combined report saved to {combined_path}")

        except Exception as e:
            logger.error(f"Error saving reports: {str(e)}")

    def save_error_log(self, error_message: str):
        """Save error information to log file."""
        try:
            error_path = self.session_dir / "error_log.txt"
            with open(error_path, 'w') as f:
                f.write(f"Error occurred at {datetime.now().isoformat()}\n")
                f.write(f"Query: {self.query}\n")
                if self.auto_tune:
                    f.write(f"Auto-tuning enabled - Max depth: {self.max_depth}, Max breadth: {self.max_breadth}\n")
                    if self.time_budget_seconds:
                        f.write(f"Time budget: {self.time_budget_seconds} seconds\n")
                else:
                    f.write(f"Parameters - Depth: {self.depth}, Breadth: {self.breadth}\n")
                f.write(f"\nError message: {error_message}\n")
            logger.info(f"Error log saved to {error_path}")
        except Exception as e:
            logger.error(f"Error saving error log: {str(e)}")

    def format_sources_section(self, urls: list, source_evaluations: list = None) -> str:
        """Format the sources section for the report with credibility ratings."""
        sources_text = "## Sources\n\n"

        if not urls:
            sources_text += "No sources were used in this research.\n"
            return sources_text

        # Count sources
        sources_text += f"The research process consulted {len(urls)} sources:\n\n"

        # Create a mapping of URL to evaluation if available
        url_to_eval = {}
        if source_evaluations:
            for eval in source_evaluations:
                url_to_eval[eval.get('url')] = eval

        # List sources with credibility information when available
        for i, url in enumerate(urls):
            sources_text += f"{i + 1}. {url}"

            if url in url_to_eval:
                eval = url_to_eval[url]
                credibility = eval.get('credibility_rating', '').upper()
                relevance = eval.get('relevance_rating', '').upper()

                if credibility and relevance:
                    sources_text += f" [Credibility: {credibility}, Relevance: {relevance}]"

                    # Add key points if available
                    key_points = eval.get('key_points', [])
                    if key_points and len(key_points) > 0:
                        sources_text += "\n   Key points:"
                        for point in key_points[:3]:  # Limit to 3 key points
                            sources_text += f"\n   - {point}"

            sources_text += "\n\n"

        return sources_text

    def format_data_quality_section(self, contradictions: list) -> str:
        """Format a section detailing data quality issues found during research."""
        quality_text = "## Data Quality Assessment\n\n"

        if not contradictions:
            quality_text += "No significant data quality issues were detected during this research.\n"
            return quality_text

        # Add contradictions section
        quality_text += "### Detected Contradictions\n\n"
        quality_text += f"The research process identified {len(contradictions)} contradiction(s):\n\n"

        for i, contradiction in enumerate(contradictions):
            quality_text += f"**Contradiction {i + 1}**: {contradiction.get('topic')}\n"
            quality_text += f"* Claim 1: \"{contradiction.get('claim1')}\"\n"
            quality_text += f"* Claim 2: \"{contradiction.get('claim2')}\"\n"

            # Add sources if available
            if contradiction.get('source1') or contradiction.get('source2'):
                source1 = contradiction.get('source1', 'Unknown source')
                source2 = contradiction.get('source2', 'Unknown source')
                quality_text += f"* Sources: {source1} vs. {source2}\n"

            quality_text += "\n"

        # Add general guidance
        quality_text += """
### Research Quality Considerations

When interpreting the research findings, please consider:

1. **Temporal Context**: Information may be time-sensitive. The research was conducted on {date}.
2. **Source Credibility**: Not all sources have equal reliability. Source evaluations are provided in the Sources section.
3. **Factual vs. Speculative Content**: Projections and forecasts have been distinguished from verified facts where possible.
4. **Information Gaps**: Areas where data is incomplete or unclear have been highlighted.

These quality considerations have been incorporated into the analysis and recommendations in the main report.
""".format(date=self.start_time.strftime('%Y-%m-%d'))

        return quality_text

    def format_auto_tuning_section(self, chain_of_thought: list) -> str:
        """
        Format a section detailing auto-tuning decisions from the research process.

        Args:
            chain_of_thought: List of research reasoning steps

        Returns:
            Formatted markdown string with auto-tuning decisions
        """
        # Extract auto-tuning decisions from chain of thought
        auto_tuning_entries = []
        for entry in chain_of_thought:
            if "Auto-tuned parameters" in entry or "Auto-adjusted parameters" in entry:
                auto_tuning_entries.append(entry)

        if not auto_tuning_entries:
            return ""

        # Format the auto-tuning section
        tuning_text = "## Auto-Tuning Decisions\n\n"
        tuning_text += "The research process used automatic parameter tuning based on question complexity and information quality:\n\n"

        for entry in auto_tuning_entries:
            # Clean up the entry timestamp and format
            parts = entry.split("] ", 1)
            if len(parts) > 1:
                timestamp = parts[0].strip("[]")
                content = parts[1]
                tuning_text += f"- **{timestamp}**: {content}\n"
            else:
                tuning_text += f"- {entry}\n"

        # Add explanation
        tuning_text += """
### How Auto-Tuning Works

The research system automatically tunes its parameters by:

1. **Initial Assessment**: Analyzing question complexity to determine initial depth and breadth
2. **Dynamic Adjustment**: Adjusting parameters during research based on information quality
3. **Resource Optimization**: Focusing more effort on complex questions and less on simple ones
4. **Time Management**: Working within specified time constraints when provided

This approach helps optimize the research process to match the specific requirements of each query.
"""

        return tuning_text


async def run(query: str, breadth: Optional[int] = None, depth: Optional[int] = None,
              auto_tune: bool = False, max_depth: int = 5, max_breadth: int = 8,
              time_budget_seconds: Optional[int] = None, output_dir: str = "research_output"):
    """Run a complete research session."""
    session = ResearchSession(
        query=query,
        breadth=breadth,
        depth=depth,
        auto_tune=auto_tune,
        max_depth=max_depth,
        max_breadth=max_breadth,
        time_budget_seconds=time_budget_seconds,
        output_dir=output_dir
    )
    return await session.execute()


query = "Gather the latest Microsoft (MSFT) press releases from financial news websites include updates on their earnings, product launches, acquisitions, and other corporate news."

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Deep Research Agent')
    parser.add_argument('--query', type=str, required=False,
                        default=query,
                        help='The research query to investigate')

    # Add parameter selection group
    param_group = parser.add_mutually_exclusive_group()
    param_group.add_argument('--auto-tune', action='store_true', default=True,
                             help='Enable automatic parameter tuning')
    param_group.add_argument('--manual-params', action='store_true',
                             help='Use manually specified depth and breadth')

    # Parameters for manual mode
    parser.add_argument('--breadth', type=int, default=4,
                        help='Research breadth - number of parallel queries to explore (manual mode)')
    parser.add_argument('--depth', type=int, default=3,
                        help='Research depth - number of levels to explore (manual mode)')

    # Parameters for auto-tuning
    parser.add_argument('--max-depth', type=int, default=5,
                        help='Maximum research depth for auto-tuning')
    parser.add_argument('--max-breadth', type=int, default=8,
                        help='Maximum research breadth for auto-tuning')
    parser.add_argument('--time-budget', type=int, default=None,
                        help='Time budget in seconds for auto-tuning (optional)')

    parser.add_argument('--output-dir', type=str, default="research_output",
                        help='Directory to save research output')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    logger.info(f"Deep Research Agent starting with query: {args.query}")

    # Determine if we're using auto-tuning or manual parameters
    auto_tune = args.auto_tune

    if auto_tune:
        logger.info(f"Auto-tuning enabled - Max depth: {args.max_depth}, Max breadth: {args.max_breadth}")
        if args.time_budget:
            logger.info(f"Time budget: {args.time_budget} seconds")

        # When auto-tuning, pass None for depth and breadth
        depth = None
        breadth = None
    else:
        # In manual mode, use the specified parameters
        depth = args.depth
        breadth = args.breadth
        logger.info(f"Manual parameters - Depth: {depth}, Breadth: {breadth}")

    logger.info(f"Output directory: {args.output_dir}")

    asyncio.run(run(
        query=args.query,
        breadth=breadth,
        depth=depth,
        auto_tune=auto_tune,
        max_depth=args.max_depth,
        max_breadth=args.max_breadth,
        time_budget_seconds=args.time_budget,
        output_dir=args.output_dir
    ))