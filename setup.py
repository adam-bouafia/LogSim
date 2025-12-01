"""
logpress - Semantic Log Compression System
Setup configuration for package installation
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text(encoding="utf-8").split("\n")
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="LogPress",
    version="1.1.0",
    author="Adam Bouafia",
    author_email="adam.bouafia@example.com",
    description="Semantic log compression library with automatic schema extraction and queryable compression",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adam-bouafia/logpress",
    project_urls={
        "Bug Tracker": "https://github.com/adam-bouafia/logpress/issues",
        "Documentation": "https://github.com/adam-bouafia/logpress#readme",
        "Source Code": "https://github.com/adam-bouafia/logpress",
        "Changelog": "https://github.com/adam-bouafia/logpress/releases",
        "Examples": "https://github.com/adam-bouafia/logpress/tree/main/examples",
    },
    keywords=[
        "log-compression",
        "log-analysis",
        "schema-extraction",
        "semantic-compression",
        "log-parsing",
        "log-management",
        "system-logs",
        "apache-logs",
        "syslog",
        "queryable-compression",
        "log-mining",
        "log-templates",
    ],
    # Only include the packages under 'logpress' namespace. Historically this
    # repository included a legacy 'logsim' package namespace; we only want
    # packages for 'logpress' in new releases.
    packages=find_packages(include=["logpress", "logpress.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Logging",
        "Topic :: System :: Archiving :: Compression",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-benchmark>=4.0.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "web": [
            # Flask REST API server (example 07_flask_api.py)
            # Enables HTTP endpoints for remote log compression/querying
            "flask>=3.0.0",
        ],
        "api": [
            # FastAPI + async server (example 08_fastapi_service.py)
            # Modern API with OpenAPI docs, better for production deployments
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
            "aiofiles>=23.0.0",
            "python-multipart>=0.0.6",
        ],
        "monitoring": [
            # File system monitoring (example 09_log_rotation_handler.py)
            # Auto-compress logs when they rotate in production environments
            "watchdog>=3.0.0",
        ],
        "all": [
            # Install all optional dependencies
            "flask>=3.0.0",
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
            "aiofiles>=23.0.0",
            "python-multipart>=0.0.6",
            "watchdog>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "logpress=logpress.__main__:cli",
        ],
    },
    package_data={
        "": ["*.md", "*.txt"],
    },
    include_package_data=True,
    zip_safe=False,
    license="MIT",
)
