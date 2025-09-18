#!/usr/bin/env python3
"""
Setup script for code-review-mcp package.
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = [
    "mcp>=1.0.0",
    "pydantic>=2.0.0", 
    "typing-extensions>=4.8.0"
]

setup(
    name="code-review-mcp",
    version="0.2.1",
    author="Bobby Muljono",
    author_email="bobbymul93@gmail.com",
    description="MCP server for automated code review and bug detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bobbymuls/code-review-mcp",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "code-review-mcp=code_review_mcp.server:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/bobbymuls/code-review-mcp/issues",
        "Source": "https://github.com/bobbymuls/code-review-mcp",
    },
)
