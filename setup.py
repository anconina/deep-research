from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="deep-research",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="An automated multi-step research system with iterative refinement, source evaluation, and result synthesis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/deep-research",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "tiktoken>=0.6.0",
        "litellm>=1.0.0",
        "firecrawl>=0.1.0",
        "asyncio>=3.4.3",
        "aiohttp>=3.9.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "typing-extensions>=4.7.0",
        "pytz>=2023.3",
        "requests>=2.31.0",
        "tenacity>=8.2.2",
        "jsonschema>=4.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.3.1",
            "pytest-asyncio>=0.21.0",
            "black>=23.3.0",
            "isort>=5.12.0",
            "mypy>=1.3.0",
            "flake8>=6.0.0",
            "tox>=4.6.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.2.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "deep-research=deep_research.run:main",
        ],
    },
    package_data={
        "deep_research": ["py.typed"],
    },
)