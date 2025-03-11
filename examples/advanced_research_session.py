"""
Advanced research example using the ResearchSession class.

This example demonstrates how to use the ResearchSession class for more control
over the research process, including output customization and session management.
"""

import asyncio
import logging
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from deep_research.utils.logger import set_logger

# Load environment variables from .env file
load_dotenv()

# Import the ResearchSession class
from deep_research.run import ResearchSession

# Configure logging

set_logger(level=logging.INFO, log_to_file=True, log_file_path="research_session.log")
logger = logging.getLogger(__name__)


async def run_research_session(query: str, output_dir: str = "research_output",
                               auto_tune: bool = True, depth: int = None,
                               breadth: int = None, time_budget: int = None):
    """
    Execute a research session with customizable parameters.

    Args:
        query: The research question or topic
        output_dir: Directory to save research output
        auto_tune: Whether to automatically determine research parameters
        depth: Fixed research depth (only used if auto_tune is False)
        breadth: Fixed research breadth (only used if auto_tune is False)
        time_budget: Optional time budget in seconds

    Returns:
        Dictionary containing research results and reports
    """
    try:
        logger.info(f"Starting research session on: {query}")
        logger.info(f"Auto-tuning: {auto_tune}")
        if auto_tune:
            logger.info(f"Max depth: {depth or 5}, Max breadth: {breadth or 8}")
            if time_budget:
                logger.info(f"Time budget: {time_budget} seconds")
        else:
            logger.info(f"Fixed depth: {depth}, Fixed breadth: {breadth}")

        # Initialize the research session
        session = ResearchSession(
            query=query,
            breadth=breadth,
            depth=depth,
            auto_tune=auto_tune,
            max_depth=depth or 5,
            max_breadth=breadth or 8,
            time_budget_seconds=time_budget,
            output_dir=output_dir
        )

        # Execute the research session
        result = await session.execute()

        # Print key sections of the report
        print("\n\n=== FINAL REPORT ===\n")
        print(result["final_report"])

        print("\n\n=== DATA QUALITY ISSUES ===\n")
        print(result["data_quality_section"])

        print("\n\n=== SOURCES ===\n")
        print(result["sources_section"])

        if result["auto_tuning_section"]:
            print("\n\n=== AUTO-TUNING DECISIONS ===\n")
            print(result["auto_tuning_section"])

        logger.info(f"Research session completed successfully.")
        logger.info(f"Reports saved to {session.session_dir}")

        return result

    except Exception as e:
        logger.error(f"Research session failed: {str(e)}")
        raise


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Advanced Deep Research Example')
    parser.add_argument('--query', type=str, required=False,
                        default="Analyze the financial performance of Microsoft (MSFT) in the last fiscal year, including revenue, profit margins, and growth trends.",
                        help='The research query to investigate')

    # Add parameter selection group
    param_group = parser.add_mutually_exclusive_group()
    param_group.add_argument('--auto-tune', action='store_true', default=True,
                             help='Enable automatic parameter tuning')
    param_group.add_argument('--manual-params', action='store_true',
                             help='Use manually specified depth and breadth')

    # Parameters for manual mode
    parser.add_argument('--breadth', type=int, default=4,
                        help='Research breadth - number of parallel queries to explore')
    parser.add_argument('--depth', type=int, default=3,
                        help='Research depth - number of levels to explore')

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

    # Determine whether to use auto-tuning or manual parameters
    auto_tune = not args.manual_params

    if auto_tune:
        # When auto-tuning, use max_depth and max_breadth as limits
        depth = args.max_depth
        breadth = args.max_breadth
    else:
        # In manual mode, use the specified parameters directly
        depth = args.depth
        breadth = args.breadth

    try:
        asyncio.run(run_research_session(
            query=args.query,
            output_dir=args.output_dir,
            auto_tune=auto_tune,
            depth=depth,
            breadth=breadth,
            time_budget=args.time_budget
        ))
    except KeyboardInterrupt:
        logger.info("Research session interrupted by user.")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")