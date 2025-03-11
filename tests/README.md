# Deep Research Test Suite

This directory contains comprehensive tests for the Deep Research system.

## Test Structure

The tests are organized to match the module structure of the main package:

- `test_auto_tuning.py` - Tests for automatic parameter tuning functionality
- `test_content_classifier.py` - Tests for content classification and validation
- `test_engine.py` - Tests for the core research engine
- `test_memory.py` - Tests for research memory management
- `test_reporting.py` - Tests for report generation
- `test_api.py` - Tests for the public API functions
- `test_progress.py` - Tests for progress tracking
- `test_models.py` - Tests for data models

## Running Tests

To run all tests:

```bash
pytest
```

To run a specific test file:

```bash
pytest tests/test_engine.py
```

To run tests with coverage report:

```bash
pytest --cov=deep_research
```

## Test Fixtures

Common test fixtures are defined in `conftest.py`, including:

- Mock data (queries, learnings, URLs, content)
- Mock LLM client responses
- Mock search engine responses
- Mock web scraping responses
- Event loop for asyncio tests

## Test Categories

The tests are organized into categories using pytest marks:

- Unit tests that test individual functions
- Integration tests that test multiple components together
- Asyncio tests that test asynchronous functions

## Adding New Tests

When adding new functionality to the Deep Research system:

1. Create a corresponding test file if it doesn't exist
2. Add test methods for normal cases, edge cases, and error handling
3. Use the existing mock fixtures where possible
4. Ensure all tests are properly isolated and don't depend on external services