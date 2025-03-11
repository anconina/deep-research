# Deep Research

An automated multi-step research system for executing deep, comprehensive research with iterative refinement, source evaluation, and result synthesis.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Deep Research is a powerful automated research system designed to intelligently explore topics through multi-step, iterative processes. It combines advanced LLM capabilities with search automation, web scraping, and structured data analysis to provide comprehensive, credible, and nuanced research results.

## Features

- **Multi-step research process**: Automatically follows promising research paths with configurable depth and breadth
- **Auto-tuning**: Dynamically adjusts research parameters based on topic complexity and information quality
- **Source credibility evaluation**: Automatically assesses the credibility and relevance of sources
- **Contradiction detection**: Identifies and highlights contradictory information across sources
- **Temporal validation**: Validates time-related information for consistency
- **Detailed reporting**: Generates comprehensive final reports and chain-of-thought analysis
- **Progress tracking**: Real-time progress monitoring throughout the research process

## Installation

### Prerequisites

- Python 3.9 or higher
- API keys for search and LLM services

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/anconina/deep-research.git
   cd deep-research
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

4. Create a `.env` file with your API keys (see `.env.example` for template)

## Quick Start

```python
import asyncio
from deep_research import deep_research

async def research_example():
    result = await deep_research(
        query="Analyze the recent developments in quantum computing hardware",
        auto_tune=True,  # Enable automatic parameter tuning
        max_depth=5,     # Maximum research depth
        max_breadth=8    # Maximum research breadth
    )
    
    # Print key findings
    print("Key Learnings:")
    for i, learning in enumerate(result["learnings"]):
        print(f"{i+1}. {learning}")

# Run the research
asyncio.run(research_example())
```

## Advanced Usage

### Research Session

For more control over the research process and output, use the `ResearchSession` class:

```python
import asyncio
from deep_research.run import ResearchSession

async def advanced_research():
    session = ResearchSession(
        query="Gather the latest Microsoft (MSFT) press releases and corporate news",
        auto_tune=True,
        max_depth=4,
        max_breadth=6,
        time_budget_seconds=300,  # Optional time limit in seconds
        output_dir="research_results"
    )
    
    result = await session.execute()
    
    # The result contains various reports and raw data
    print(result["final_report"])

asyncio.run(advanced_research())
```

### Custom Research Engine

For complete customization:

```python
from deep_research.engine import ResearchEngine

# Initialize with custom parameters
engine = ResearchEngine(
    auto_tune=True,
    max_depth=5,
    max_breadth=8,
    time_budget_seconds=600
)

# Execute research with complete control
result = await engine.deep_research(
    query="Your research query",
    depth=3,  # Override auto-tuning if desired
    breadth=5
)
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```
# API Keys
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key

# Configuration
CONTEXT_SIZE=128000
```

### Research Parameters

- **Depth**: Number of levels of follow-up queries to explore (1-5 recommended)
- **Breadth**: Number of parallel queries to explore per level (2-8 recommended)
- **Auto-tune**: When enabled, automatically determines optimal depth and breadth
- **Time budget**: Optional time limit in seconds for the research process

## Output

The research process generates:

- **Final Report**: Comprehensive markdown report with findings, analysis, and recommendations
- **Chain of Thought Report**: Detailed explanation of the research reasoning process
- **Sources Section**: List of sources with credibility and relevance ratings
- **Data Quality Issues**: Analysis of contradictions and information gaps
- **Auto-Tuning Decisions**: If auto-tuning is enabled, explanation of parameter decisions

## Project Structure

```
deep_research/
├── __init__.py                # Package initialization
├── api.py                     # Public API functions
├── auto_tuning.py             # Parameter auto-tuning functionality
├── content_classifier.py      # Content validation and classification
├── engine.py                  # Core research engine
├── memory.py                  # Research memory management
├── models.py                  # Pydantic data models
├── progress.py                # Research progress tracking
├── prompts.py                 # Centralized prompt management
├── reporting.py               # Report generation functionality
├── run.py                     # Research session handling
└── search_engines/            # Search engine integrations
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
