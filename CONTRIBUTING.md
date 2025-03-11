# Contributing to Deep Research

First off, thank you for considering contributing to Deep Research! It's people like you that make this project such a valuable tool for automated research.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report. Following these guidelines helps maintainers understand your report, reproduce the behavior, and find related reports.

**Before Submitting A Bug Report:**

* Check the documentation for tips on common issues.
* Check if the bug has already been reported in the issues.
* Ensure your environment meets the requirements (Python 3.9+, required packages).

**How to Submit a Good Bug Report:**
* Use a clear and descriptive title.
* Describe the exact steps to reproduce the problem.
* Provide specific examples to demonstrate the steps.
* Describe the behavior you observed after following the steps.
* Explain which behavior you expected to see instead and why.
* Include screenshots and animated GIFs if possible.
* Include details about your environment.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion, including completely new features and minor improvements to existing functionality.

**Before Submitting An Enhancement Suggestion:**

* Check if the enhancement has already been suggested in the issues.
* Check if the functionality already exists but isn't documented.

**How to Submit a Good Enhancement Suggestion:**
* Use a clear and descriptive title.
* Provide a step-by-step description of the suggested enhancement.
* Provide specific examples to demonstrate the steps.
* Describe the current behavior and explain which behavior you expected to see instead.
* Explain why this enhancement would be useful to most users.

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Follow the Python style guide (PEP 8)
* Include appropriate tests
* Update or add documentation as needed
* Ensure all CI checks pass

## Development Environment Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/anconina/deep-research.git`
3. Create a virtual environment:
   ```bash
   cd deep-research
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Coding Guidelines

### Style Guide

* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
* Use [Black](https://black.readthedocs.io/en/stable/) for code formatting
* Use [isort](https://pycqa.github.io/isort/) for import sorting
* Type annotations should be used for all public functions (using [typing](https://docs.python.org/3/library/typing.html))

### Testing

* Write tests for all new features and bug fixes
* Ensure all tests pass before submitting a PR
* Aim for high code coverage (at least 80%)
* Use pytest fixtures for test setup/teardown
* Mock external dependencies

### Documentation

* Update documentation for all new features
* Add docstrings to all public functions (Google style)
* Keep the README up-to-date

## Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* First line should be 50 characters or less
* Reference issues and pull requests after the first line
* Consider starting the commit message with an applicable emoji:
    * 🎨 `:art:` when improving the format/structure of the code
    * 🐛 `:bug:` when fixing a bug
    * 📝 `:memo:` when adding or updating documentation
    * ✨ `:sparkles:` when adding a new feature
    * ⚡️ `:zap:` when improving performance
    * 🧪 `:test_tube:` when adding tests

## Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2. Update the README.md with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations, and container parameters.
3. Increase the version numbers in any examples files and the README.md to the new version that this Pull Request would represent. The versioning scheme we use is [SemVer](http://semver.org/).
4. The PR will be merged once you have the sign-off of at least one maintainer, or if you do not have permission to do that, you may request the maintainer to merge it for you.

## Release Process

1. Update the CHANGELOG.md with the release notes
2. Update the version number in setup.py and pyproject.toml
3. Create a release on GitHub
4. The CI/CD pipeline will automatically build and publish the package to PyPI

## Questions?

Feel free to contact the project maintainers if you have any questions.
