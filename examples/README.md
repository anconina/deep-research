# Deep Research Examples

This directory contains example scripts demonstrating how to use the Deep Research system.

## Basic Examples

### Basic Research

The `basic_research.py` script demonstrates the simplest way to use the Deep Research system through the `deep_research` function.

```bash
python examples/basic_research.py
```

Key features:
- Automatic parameter tuning
- Simple API with a single function call
- Basic result handling

### Advanced Research Session

The `advanced_research_session.py` script demonstrates more advanced usage with the `ResearchSession` class, which provides more control over the research process.

```bash
python examples/advanced_research_session.py --query "Your research question here"
```

Key features:
- Command-line interface with argument parsing
- Session-based research with detailed output
- Custom parameter configuration
- Time budget constraints
- Comprehensive report generation

## Command-Line Options

The advanced example accepts the following command-line options:

- `--query`: The research question to investigate
- `--auto-tune`: Enable automatic parameter tuning (default)
- `--manual-params`: Use manually specified depth and breadth
- `--breadth`: Research breadth - number of parallel queries to explore
- `--depth`: Research depth - number of levels to explore
- `--max-depth`: Maximum research depth for auto-tuning
- `--max-breadth`: Maximum research breadth for auto-tuning
- `--time-budget`: Time budget in seconds for auto-tuning (optional)
- `--output-dir`: Directory to save research output

## Example Usage

```bash
# Basic research with default parameters
python examples/basic_research.py

# Advanced research with a specific query
python examples/advanced_research_session.py --query "Analyze the impact of recent AI regulations on the tech industry"

# Advanced research with manual parameters
python examples/advanced_research_session.py --manual-params --depth 2 --breadth 3

# Advanced research with time budget
python examples/advanced_research_session.py --time-budget 300
```

## Extending the Examples

These examples can serve as a starting point for your own applications. Key ways to extend them:

1. **Custom Reporting**: Modify how results are processed and displayed
2. **Integration with Other Systems**: Use the research results as input for other processes
3. **Specialized Domains**: Add domain-specific processing logic
4. **User Interfaces**: Build web or desktop interfaces around the research functionality