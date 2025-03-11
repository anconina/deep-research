"""
Basic research example using the Deep Research system.

This example demonstrates how to use the deep_research function to execute
a simple research task with automatic parameter tuning.
"""

import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

from deep_research.utils.logger import set_logger

# Load environment variables from .env file
load_dotenv()

# Import the deep_research function
from deep_research import deep_research

# Configure logging

set_logger(level=logging.INFO, log_to_file=True, log_file_path="research.log")

logger = logging.getLogger(__name__)


async def run_research():
    """Execute a research task and display the results."""
    try:
        # Define the research query
        query = "Analyze the recent developments in quantum computing hardware, focusing on IBM, Google, and other major players."

        logger.info(f"Starting research on: {query}")

        # Execute the research with automatic parameter tuning
        result = await deep_research(
            query=query,
            auto_tune=True,  # Enable automatic parameter tuning
            max_depth=4,  # Maximum research depth
            max_breadth=6  # Maximum research breadth
        )

        # Extract key components from the result
        learnings = result.get("learnings", [])
        visited_urls = result.get("visited_urls", [])
        contradictions = result.get("contradictions", [])

        # Display key findings
        print("\n\n=== KEY FINDINGS ===\n")
        for i, learning in enumerate(learnings):
            print(f"{i + 1}. {learning}")

        # Display sources
        print("\n\n=== SOURCES ===\n")
        for i, url in enumerate(visited_urls):
            print(f"{i + 1}. {url}")

        # Display contradictions if any
        if contradictions:
            print("\n\n=== CONTRADICTIONS ===\n")
            for i, contradiction in enumerate(contradictions):
                print(f"{i + 1}. Topic: {contradiction.get('topic')}")
                print(f"   Claim 1: {contradiction.get('claim1')}")
                print(f"   Claim 2: {contradiction.get('claim2')}")
                print()

        # Save results to file
        output_dir = Path("research_results")
        output_dir.mkdir(exist_ok=True)

        with open(output_dir / "learnings.txt", "w") as f:
            for learning in learnings:
                f.write(f"- {learning}\n")

        with open(output_dir / "sources.txt", "w") as f:
            for url in visited_urls:
                f.write(f"{url}\n")

        logger.info(f"Research completed with {len(learnings)} learnings from {len(visited_urls)} sources.")

        return result

    except Exception as e:
        logger.error(f"Research failed: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(run_research())
    except KeyboardInterrupt:
        logger.info("Research interrupted by user.")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")