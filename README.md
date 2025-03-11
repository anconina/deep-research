# Deep Research

<div align="center">

[deep_research_banner.webp](assets/deep_research_banner.webp)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**An automated multi-step research system with iterative refinement, source evaluation, and result synthesis.**

</div>

## 🌟 Overview

Deep Research is an advanced research automation system that conducts comprehensive, multi-step research processes with depth and precision. It evaluates sources, detects contradictions, validates information, and synthesizes findings into well-structured reports.

The system employs auto-tuning algorithms to optimize research parameters based on question complexity and information quality, ensuring the most effective allocation of computational resources during the research process.

## ✨ Key Features

- **Multi-step research** with configurable depth and breadth
- **Automatic parameter tuning** based on question complexity
- **Source evaluation** for credibility and relevance
- **Contradiction detection** across multiple sources
- **Content validation** for temporal consistency and numerical reasonableness
- **Comprehensive reporting** with chain-of-thought reasoning
- **Information synthesis** organized by topics and themes
- **Research memory** for progressive knowledge accumulation

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/anconina/deep-research.git
cd deep-research

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configurations
```

### Requirements

- Python 3.7+
- API keys for search services (e.g., Tavily, Bing)
- LLM access (via litellm)

## 🚀 Quick Start

### Basic Research Example

```python
import asyncio
from deep_research import deep_research

async def run_simple_research():
    query = "Analyze recent developments in quantum computing hardware"
    
    # Execute research with automatic parameter tuning
    result = await deep_research(
        query=query,
        auto_tune=True,
        max_depth=4,
        max_breadth=6
    )
    
    # Print key learnings
    for i, learning in enumerate(result["learnings"]):
        print(f"{i+1}. {learning}")

if __name__ == "__main__":
    asyncio.run(run_simple_research())
```

### Advanced Research Session

```python
import asyncio
from deep_research.run import ResearchSession

async def run_advanced_research():
    # Initialize a research session
    session = ResearchSession(
        query="Analyze the financial performance of Microsoft (MSFT) in the last fiscal year",
        auto_tune=True,
        max_depth=5,
        max_breadth=8,
        output_dir="research_output"
    )
    
    # Execute research and generate reports
    result = await session.execute()
    
    print("Research completed! Reports saved to:", session.session_dir)

if __name__ == "__main__":
    asyncio.run(run_advanced_research())
```

## 🔧 Command Line Usage

The system provides a command-line interface for easy execution:

```bash
# Basic usage with default parameters
python -m deep_research.run --query "Your research question here"

# Advanced usage with auto-tuning
python -m deep_research.run --query "Your research question here" --auto-tune --max-depth 5 --max-breadth 8

# Using fixed parameters
python -m deep_research.run --query "Your research question here" --manual-params --depth 3 --breadth 4

# Setting a time budget (in seconds)
python -m deep_research.run --query "Your research question here" --time-budget 300
```

## 📚 API Documentation

### Main Functions

#### `deep_research()`

```python
async def deep_research(
    query: str, 
    breadth: Optional[int] = None, 
    depth: Optional[int] = None,
    auto_tune: bool = False, 
    max_depth: int = 5,
    max_breadth: int = 8, 
    time_budget_seconds: Optional[int] = None
) -> Dict
```

- **query**: The research question or topic
- **breadth**: How many parallel queries to explore (if None and auto_tune is True, determined automatically)
- **depth**: How many levels of follow-up queries to explore (if None and auto_tune is True, determined automatically)
- **auto_tune**: Whether to automatically determine research parameters
- **max_depth**: Maximum allowed research depth when auto-tuning
- **max_breadth**: Maximum allowed research breadth when auto-tuning
- **time_budget_seconds**: Optional time budget in seconds for auto-tuning

Returns a dictionary containing:
- `learnings`: List of research learnings
- `visited_urls`: List of visited URLs
- `chain_of_thought`: List of reasoning steps
- `information_map`: Dictionary mapping topics to consensus, contradictions, and gaps
- `contradictions`: List of detected contradictions
- `source_evaluations`: List of source evaluations

#### Report Generation

```python
async def write_final_report(
    prompt: str, 
    learnings: List[str], 
    information_map: Dict = None,
    contradictions: List[Dict] = None, 
    source_evaluations: List[Dict] = None
) -> str
```

```python
async def write_chain_of_thought_report(chain_of_thought: List[str]) -> str
```

## 🏗️ System Architecture

Deep Research is composed of several interconnected components:

```
┌────────────────────┐      ┌────────────────────┐
│   Research API     │◄────►│   Research Engine  │
└────────────────────┘      └─────────┬──────────┘
                                     │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
┌───────▼──────────┐     ┌──────────▼──────────┐     ┌─────────▼──────────┐
│  Auto Tuner      │     │  Content Classifier │     │  Research Memory   │
└──────────────────┘     └─────────────────────┘     └────────────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
                           ┌────────▼───────┐
                           │ Prompt Manager │
                           └────────────────┘
```

### Key Components:

- **ResearchEngine**: Orchestrates the research process, including query generation, search execution, content analysis, and result synthesis.
- **AutoTuner**: Analyzes question complexity and information quality to determine optimal research parameters.
- **ContentClassifier**: Validates content for temporal consistency, numerical reasonableness, and classifies content types.
- **ResearchMemory**: Stores and manages research findings, sources, contradictions, and information maps.
- **PromptManager**: Manages and customizes prompts used throughout the research process.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- FireCrawl for web content scraping
- LiteLLM for LLM integration
- Tavily, Bing and DuckDuckGo for search capabilities