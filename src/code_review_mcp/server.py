#!/usr/bin/env python3
"""
Code Review MCP Server

A comprehensive Model Context Protocol (MCP) server that provides intelligent
code analysis capabilities for multiple programming languages. This server offers:

- **Security Analysis**: Detects code injection, hardcoded secrets, and vulnerabilities
- **Performance Optimization**: Identifies inefficient patterns and suggests improvements
- **Bug Detection**: Catches syntax errors, logic issues, and potential runtime problems
- **Code Quality**: Enforces style guidelines and best practices
- **Multi-language Support**: Python, JavaScript, TypeScript, Java, and more

The server integrates seamlessly with Cursor IDE through the MCP protocol,
providing real-time code analysis without leaving your development environment.

Author: Bobby Muljono
Version: 0.2.1
License: Apache 2.0
"""

import ast
import asyncio
import logging
import os
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Tuple, Union

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from pydantic import BaseModel, Field, field_validator

# Configure logging - using DEBUG level for detailed path debugging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# Custom Exception Classes for Better Error Handling
class CodeAnalysisError(Exception):
    """Base exception for code analysis operations."""

    pass


class FileReadError(CodeAnalysisError):
    """Exception raised when file reading operations fail."""

    pass


class LanguageDetectionError(CodeAnalysisError):
    """Exception raised when language detection fails."""

    pass


class SyntaxAnalysisError(CodeAnalysisError):
    """Exception raised during syntax analysis."""

    pass


# Precompiled regex patterns for better performance
@lru_cache(maxsize=None)
def get_compiled_patterns() -> Dict[str, List[Tuple[Pattern, str, str]]]:
    """Get precompiled regex patterns for security and performance analysis.

    Returns:
        Dict[str, List[Tuple[Pattern, str, str]]]: Compiled patterns by language
    """
    return {
        "python": [
            # Security patterns
            (
                re.compile(r"eval\(", re.IGNORECASE),
                "high",
                "Use of eval() can lead to code injection",
            ),
            (
                re.compile(r"exec\(", re.IGNORECASE),
                "high",
                "Use of exec() can lead to code injection",
            ),
            (
                re.compile(r"pickle\.loads?\(", re.IGNORECASE),
                "medium",
                "Pickle deserialization can be unsafe",
            ),
            (
                re.compile(r"subprocess\.call\([^)]*shell=True", re.IGNORECASE),
                "medium",
                "Shell injection risk",
            ),
            (
                re.compile(r"os\.system\(", re.IGNORECASE),
                "high",
                "Command injection vulnerability",
            ),
            (
                re.compile(r'password\s*=\s*["\'][^"\']*["\']', re.IGNORECASE),
                "critical",
                "Hardcoded password detected",
            ),
            (
                re.compile(r'api_key\s*=\s*["\'][^"\']*["\']', re.IGNORECASE),
                "high",
                "Hardcoded API key detected",
            ),
            # Enhanced configuration-based credential patterns
            (
                re.compile(r'["\'][a-zA-Z0-9]{32,}["\']', re.IGNORECASE),
                "critical",
                "Potential hardcoded secret or token (32+ chars)",
            ),
            (
                re.compile(r'["\']apiKey["\']?\s*:\s*["\'][a-zA-Z0-9]{32,}["\']', re.IGNORECASE),
                "critical",
                "Hardcoded API key detected in configuration object",
            ),
            (
                re.compile(
                    r'["\'](?:api[_-]?key|access[_-]?token|secret[_-]?key|auth[_-]?token)["\']?\s*:\s*["\'][a-zA-Z0-9]{20,}["\']',
                    re.IGNORECASE,
                ),
                "critical",
                "Hardcoded credential detected in configuration object",
            ),
            (
                re.compile(r'baseURL["\']?\s*:\s*["\']https?://[^"\']*internal[^"\']*["\']', re.IGNORECASE),
                "medium",
                "Internal service URL exposure",
            ),
            (
                re.compile(
                    r'def\s+\w+\([^)]*\):[^{]*\w+\s*=\s*\w+\[["\'][^"\']+["\']\](?!\s*if|\s*try)', re.IGNORECASE
                ),
                "medium",
                "Missing input validation - direct dictionary access without checks",
            ),
            # API calls assessment patterns
            (
                re.compile(r"requests\.get\([^)]*\)(?!\s*\.raise_for_status)", re.IGNORECASE),
                "medium",
                "API call without status code checking - add .raise_for_status()",
            ),
            (
                re.compile(r"requests\.post\([^)]*\)(?!\s*\.raise_for_status)", re.IGNORECASE),
                "medium",
                "API call without status code checking - add .raise_for_status()",
            ),
            (
                re.compile(
                    r"requests\.(get|post|put|delete)\([^)]*timeout\s*=\s*None",
                    re.IGNORECASE,
                ),
                "high",
                "API call without timeout - potential hanging requests",
            ),
            (
                re.compile(
                    r"requests\.(get|post|put|delete)\([^)]*(?!.*timeout)",
                    re.IGNORECASE,
                ),
                "medium",
                "API call without timeout parameter",
            ),
            (
                re.compile(r"\.json\(\)(?!\s*except)", re.IGNORECASE),
                "medium",
                "JSON parsing without exception handling",
            ),
            (
                re.compile(r"time\.sleep\(\d+\)", re.IGNORECASE),
                "low",
                "Fixed sleep in retry logic - consider exponential backoff",
            ),
            (
                re.compile(r"while.*requests\.(get|post)", re.IGNORECASE),
                "medium",
                "Potential infinite retry loop without proper backoff",
            ),
            # Enhanced API and service integration patterns
            (
                re.compile(r"max_calls\s*=\s*\d+", re.IGNORECASE),
                "low",
                "Hardcoded API call limits - consider making configurable",
            ),
            (
                re.compile(r"page_size\s*=\s*\d+", re.IGNORECASE),
                "low",
                "Hardcoded page size - consider making configurable",
            ),
            (
                re.compile(r"for.*range\(max_calls\).*client\.", re.IGNORECASE),
                "medium",
                "API pagination without proper error handling or circuit breaker",
            ),
            (
                re.compile(r"for.*range\(\d+\).*\.(get|post|call)", re.IGNORECASE),
                "medium",
                "Loop with API calls - ensure proper rate limiting and error handling",
            ),
            (
                re.compile(r"client\.\w+\([^)]*\)(?!.*except|.*try)", re.IGNORECASE),
                "medium",
                "API client call without exception handling",
            ),
            (
                re.compile(r"\.refresh\(\)(?!.*except|.*try)", re.IGNORECASE),
                "low",
                "Token refresh without error handling",
            ),
            # LLM integration assessment patterns
            (
                re.compile(
                    r"openai\.chat\.completions\.create\([^)]*max_tokens\s*=\s*\d{4,}",
                    re.IGNORECASE,
                ),
                "medium",
                "Very high max_tokens - consider cost implications",
            ),
            (
                re.compile(
                    r"openai\.chat\.completions\.create\([^)]*temperature\s*=\s*[01]\.",
                    re.IGNORECASE,
                ),
                "low",
                "Consider temperature settings for deterministic vs creative outputs",
            ),
            (
                re.compile(r'f["\'].*\{.*\}.*["\'](?=.*openai|.*llm|.*prompt)', re.IGNORECASE),
                "medium",
                "Dynamic prompt construction - validate input sanitization",
            ),
            (
                re.compile(r"prompt\s*\+=\s*.*user.*input", re.IGNORECASE),
                "high",
                "User input directly in prompt - potential prompt injection",
            ),
            (
                re.compile(r"messages\s*=\s*\[.*\{[^}]*user[^}]*\}", re.IGNORECASE),
                "low",
                "Consider system message for better LLM guidance",
            ),
            (
                re.compile(r"\.choices\[0\]\.message\.content(?!\s*\.strip)", re.IGNORECASE),
                "low",
                "LLM response without stripping whitespace",
            ),
            # DataFrame operations evaluation patterns
            (
                re.compile(r"\.iterrows\(\)", re.IGNORECASE),
                "high",
                "Avoid iterrows() - use vectorized operations or .apply()",
            ),
            (
                re.compile(r"\.itertuples\(\)", re.IGNORECASE),
                "medium",
                "Consider vectorized operations instead of itertuples()",
            ),
            (
                re.compile(r"for.*in.*\.iterrows", re.IGNORECASE),
                "high",
                "Loop with iterrows() is very slow - use vectorized operations",
            ),
            (
                re.compile(r"pd\.concat\(\[.*for.*in.*\]", re.IGNORECASE),
                "high",
                "List comprehension with concat is inefficient - collect data first",
            ),
            (
                re.compile(r"\.append\(.*\)\s*(?=.*loop|.*for)", re.IGNORECASE),
                "high",
                "DataFrame.append() in loop is very slow - collect and concat",
            ),
            (
                re.compile(r"\.loc\[.*,.*\]\s*=.*(?=.*loop|.*for)", re.IGNORECASE),
                "medium",
                "Setting values in loop - consider vectorized assignment",
            ),
            (
                re.compile(r"pd\.read_csv\([^)]*(?!.*chunksize)", re.IGNORECASE),
                "medium",
                "Large CSV without chunking - consider memory usage",
            ),
            (
                re.compile(r"\.groupby\([^)]*\)\.apply\(", re.IGNORECASE),
                "low",
                "Consider .agg() or .transform() instead of .apply() for better performance",
            ),
            # Enhanced pandas and data processing performance patterns
            (
                re.compile(r"\.copy\(\).*\.copy\(\)", re.IGNORECASE),
                "high",
                "Multiple DataFrame copies - consolidate operations to reduce memory usage",
            ),
            (
                re.compile(r"\.astype\([^)]+\)\.astype\([^)]+\)", re.IGNORECASE),
                "medium",
                "Chained type conversions - optimize data types upfront",
            ),
            (
                re.compile(r"pd\.to_numeric.*\.astype.*\.astype", re.IGNORECASE),
                "high",
                "Inefficient type conversion chain - consolidate type operations",
            ),
            (
                re.compile(r"\.merge\([^)]*\).*\.drop\(columns=", re.IGNORECASE),
                "medium",
                "Merge followed by column drop - optimize join to exclude unwanted columns",
            ),
            (
                re.compile(r"\.fillna\([^)]*\)\.fillna\([^)]*\)", re.IGNORECASE),
                "low",
                "Multiple fillna operations - consider single operation with dict",
            ),
            (
                re.compile(r"\.reset_index\([^)]*\)\.reset_index\([^)]*\)", re.IGNORECASE),
                "low",
                "Multiple reset_index operations - consolidate into single call",
            ),
            (
                re.compile(r"\.astype\(['\"]string['\"]\)", re.IGNORECASE),
                "low",
                "Consider using 'str' instead of 'string' dtype for better performance",
            ),
            (
                re.compile(r"\.to_dict\(orient=['\"]records['\"]\)", re.IGNORECASE),
                "medium",
                "to_dict with records orientation can be memory intensive for large DataFrames",
            ),
            (
                re.compile(r"json\.loads\(.*\.to_dict\(", re.IGNORECASE),
                "medium",
                "Unnecessary JSON serialization/deserialization - work with dict directly",
            ),
            # Google Sheets integration patterns
            (
                re.compile(r"gspread.*\.open\([^)]*\)(?!.*try)", re.IGNORECASE),
                "medium",
                "Google Sheets operation without error handling",
            ),
            (
                re.compile(r"sheet\.update\([^)]*\)(?!.*batch)", re.IGNORECASE),
                "high",
                "Single cell updates are slow - use batch_update()",
            ),
            (
                re.compile(r"sheet\.get_all_records\(\)(?!.*limit)", re.IGNORECASE),
                "medium",
                "Getting all records without limit - consider memory usage",
            ),
            (
                re.compile(r"time\.sleep\(\d+\).*(?=.*gspread|.*sheet)", re.IGNORECASE),
                "low",
                "Fixed sleep for rate limiting - consider smart rate limiting",
            ),
            (
                re.compile(r"for.*sheet\.(update|append_row)", re.IGNORECASE),
                "high",
                "Multiple API calls in loop - use batch operations",
            ),
            # Performance patterns
            (
                re.compile(r"for .+ in .+:\s*if .+:\s*break"),
                "medium",
                "Consider using next() or any() instead of loop with break",
            ),
            (
                re.compile(r"\.append\(.+\)\s*$"),
                "low",
                "Consider list comprehension for better performance",
            ),
            (
                re.compile(r"\+= \[.+\]"),
                "medium",
                "Use extend() instead of += for list concatenation",
            ),
            (
                re.compile(r"len\(.+\) == 0"),
                "low",
                'Use "not sequence" instead of "len(sequence) == 0"',
            ),
        ],
        "javascript": [
            # Security patterns
            (
                re.compile(r"eval\(", re.IGNORECASE),
                "high",
                "Use of eval() can lead to code injection",
            ),
            (
                re.compile(r"innerHTML\s*=", re.IGNORECASE),
                "medium",
                "Potential XSS vulnerability",
            ),
            (
                re.compile(r"document\.write\(", re.IGNORECASE),
                "medium",
                "Potential XSS vulnerability",
            ),
            (
                re.compile(r'password\s*[=:]\s*["\'][^"\']*["\']', re.IGNORECASE),
                "critical",
                "Hardcoded password detected",
            ),
            (
                re.compile(r'api_key\s*[=:]\s*["\'][^"\']*["\']', re.IGNORECASE),
                "high",
                "Hardcoded API key detected",
            ),
            # API calls assessment patterns for JavaScript
            (
                re.compile(r"fetch\([^)]*\)(?!\s*\.then.*catch)", re.IGNORECASE),
                "medium",
                "Fetch without proper error handling - add .catch()",
            ),
            (
                re.compile(r"fetch\([^)]*\)\.then\([^)]*\)(?!\s*\.catch)", re.IGNORECASE),
                "medium",
                "Fetch promise chain without .catch() error handling",
            ),
            (
                re.compile(r"\.json\(\)(?!\s*\.catch)", re.IGNORECASE),
                "medium",
                "JSON parsing without error handling",
            ),
            (
                re.compile(r"axios\.(get|post)\([^)]*\)(?!\s*\.catch)", re.IGNORECASE),
                "medium",
                "Axios request without error handling",
            ),
            (
                re.compile(r"setTimeout.*fetch\(", re.IGNORECASE),
                "low",
                "Fixed delay retry - consider exponential backoff",
            ),
            (
                re.compile(r"while.*fetch\(", re.IGNORECASE),
                "medium",
                "Potential infinite retry loop",
            ),
            # LLM integration patterns for JavaScript
            (
                re.compile(r"openai.*maxTokens.*[5-9]\d{3,}", re.IGNORECASE),
                "medium",
                "Very high maxTokens - consider cost implications",
            ),
            (
                re.compile(r"prompt.*\+.*userInput", re.IGNORECASE),
                "high",
                "User input directly in prompt - validate for prompt injection",
            ),
            (
                re.compile(r"`.*\$\{.*userInput.*\}.*`(?=.*openai|.*llm)", re.IGNORECASE),
                "high",
                "Template literal with user input in LLM prompt",
            ),
            (
                re.compile(r"messages.*push.*\{.*role.*user.*content.*userInput", re.IGNORECASE),
                "medium",
                "User input in LLM messages - sanitize input",
            ),
            # JSON handling patterns
            (
                re.compile(r"JSON\.parse\([^)]*\)(?!\s*catch)", re.IGNORECASE),
                "medium",
                "JSON.parse without try-catch error handling",
            ),
            (
                re.compile(r"JSON\.stringify\([^)]*undefined", re.IGNORECASE),
                "low",
                "JSON.stringify with undefined values - consider replacer function",
            ),
            # Performance patterns
            (
                re.compile(r"for\s*\(.+\s+in\s+.+\)"),
                "medium",
                "Consider for...of or forEach for arrays",
            ),
            (
                re.compile(r"\$\(.+\)\.each"),
                "medium",
                "Consider native forEach instead of jQuery each",
            ),
            (
                re.compile(r"document\.getElementById"),
                "low",
                "Consider caching DOM queries",
            ),
        ],
    }


class CodeIssue(BaseModel):
    """Represents a code issue found during review.

    This model encapsulates all information about a detected code issue,
    including its severity, location, and suggested remediation.

    Attributes:
        severity (str): Issue severity level (critical/high/medium/low)
        category (str): Issue category (bug/security/performance/style)
        message (str): Human-readable description of the issue
        line (Optional[int]): Line number where the issue occurs (1-indexed)
        column (Optional[int]): Column number where the issue occurs (0-indexed)
        suggestion (Optional[str]): Suggested fix or remediation advice
    """

    severity: str = Field(
        description="Severity level: critical, high, medium, low",
        pattern=r"^(critical|high|medium|low)$",
    )
    category: str = Field(
        description="Issue category: bug, security, performance, style",
        pattern=r"^(bug|security|performance|style)$",
    )
    message: str = Field(description="Description of the issue", min_length=1, max_length=500)
    line: Optional[int] = Field(
        default=None,
        description="Line number where issue occurs",
        ge=1,  # Line numbers start at 1
    )
    column: Optional[int] = Field(
        default=None,
        description="Column number where issue occurs",
        ge=0,  # Column numbers start at 0
    )
    suggestion: Optional[str] = Field(default=None, description="Suggested fix", max_length=1000)

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        """Validate severity level."""
        valid_severities = {"critical", "high", "medium", "low"}
        if v.lower() not in valid_severities:
            raise ValueError(f"Severity must be one of: {valid_severities}")
        return v.lower()

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate issue category."""
        valid_categories = {"bug", "security", "performance", "style"}
        if v.lower() not in valid_categories:
            raise ValueError(f"Category must be one of: {valid_categories}")
        return v.lower()


# Initialize the MCP server
server = Server("code-review-mcp")
logger.info("Code Review MCP Server initialized")


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all available analysis tools provided by this MCP server.

    Returns a comprehensive list of code analysis tools that can be invoked
    by MCP clients. Each tool is configured with detailed input schemas
    to ensure proper parameter validation.

    Returns:
        List[types.Tool]: List of available MCP tools including:
            - review_code: Comprehensive code analysis
            - analyze_security: Security-focused analysis
            - check_performance: Performance optimization analysis

    Raises:
        Exception: If tool configuration is invalid
    """
    logger.debug("Listing available analysis tools")
    return [
        types.Tool(
            name="review_code",
            description="Analyze code for potential bugs, security issues, and improvements",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the code file to review",
                    },
                    "code_content": {
                        "type": "string",
                        "description": "Code content to review (alternative to file_path)",
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language (auto-detected if not provided)",
                    },
                    "severity_filter": {
                        "type": "string",
                        "enum": ["all", "critical", "high", "medium", "low"],
                        "description": "Minimum severity level to include in results",
                        "default": "all",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        ),
        types.Tool(
            name="analyze_security",
            description="Perform focused security analysis on code",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the code file to analyze",
                    },
                    "code_content": {
                        "type": "string",
                        "description": "Code content to analyze (alternative to file_path)",
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        ),
        types.Tool(
            name="analyze_llm_invoke",
            description="Critique LLM integration: prompt engineering, model choice, and parameters",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the code file to analyze",
                    },
                    "code_content": {
                        "type": "string",
                        "description": "Code content to analyze (alternative to file_path)",
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        ),
        types.Tool(
            name="analyze_api_handling",
            description="Analyze API calls, error handling, timeouts, and retry strategies",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the code file to analyze",
                    },
                    "code_content": {
                        "type": "string",
                        "description": "Code content to analyze (alternative to file_path)",
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        ),
        types.Tool(
            name="check_performance",
            description="Analyze code for performance issues including DataFrame operations and optimization opportunities",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the code file to analyze",
                    },
                    "code_content": {
                        "type": "string",
                        "description": "Code content to analyze (alternative to file_path)",
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        ),
        types.Tool(
            name="analyze_data_processing",
            description="Specialized analysis for data processing pipelines, pandas operations, and memory optimization",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the code file to analyze",
                    },
                    "code_content": {
                        "type": "string",
                        "description": "Code content to analyze (alternative to file_path)",
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Optional[Dict[str, Any]]
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """Route tool calls to appropriate analysis functions.

    This is the main entry point for all tool invocations. It validates
    the tool name and routes the request to the corresponding analysis
    function with proper error handling.

    Args:
        name (str): Name of the tool to invoke
        arguments (Optional[Dict[str, Any]]): Tool arguments/parameters

    Returns:
        List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
            Analysis results formatted for MCP protocol

    Raises:
        ValueError: If tool name is not recognized
        Exception: If tool execution fails
    """
    logger.info(f"Tool call received: {name}")

    if arguments is None:
        arguments = {}

    if name == "review_code":
        return await review_code(arguments)
    elif name == "analyze_security":
        return await analyze_security(arguments)
    elif name == "analyze_llm_invoke":
        return await analyze_llm_invoke(arguments)
    elif name == "analyze_api_handling":
        return await analyze_api_handling(arguments)
    elif name == "check_performance":
        return await check_performance(arguments)
    elif name == "analyze_data_processing":
        return await analyze_data_processing(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


def find_workspace_root(start_path: Optional[str] = None) -> str:
    """Intelligently locate the workspace root directory.

    Searches upward from the starting directory to find common project markers
    such as .git, pyproject.toml, package.json, etc. This ensures relative
    file paths are resolved correctly regardless of where the server is run.

    Args:
        start_path (Optional[str]): Directory to start searching from.
            Defaults to the directory containing this script.

    Returns:
        str: Absolute path to the detected workspace root directory

    Note:
        Falls back to current working directory if no project markers found
    """
    logger.debug(f"=== FIND_WORKSPACE_ROOT DEBUG ===")
    logger.debug(f"Input start_path: {start_path}")
    logger.debug(f"Current working directory: {os.getcwd()}")
    logger.debug(f"__file__ location: {__file__}")
    logger.debug(f"Absolute __file__: {os.path.abspath(__file__)}")

    if start_path is None:
        # Start from the directory containing this server.py file
        start_path = os.path.dirname(os.path.abspath(__file__))
        logger.debug(f"Using script directory as start_path: {start_path}")

    current_path = os.path.abspath(start_path)
    logger.debug(f"Starting search from absolute path: {current_path}")

    # Common project markers to look for
    markers = [
        ".git",
        "pyproject.toml",
        "setup.py",
        "requirements.txt",
        "mcp.json",
        ".gitignore",
    ]
    logger.debug(f"Looking for markers: {markers}")

    search_count = 0
    while current_path != os.path.dirname(current_path):  # Not at root
        search_count += 1
        logger.debug(f"Search iteration {search_count}: checking {current_path}")
        logger.debug(f"Directory exists: {os.path.exists(current_path)}")

        if os.path.exists(current_path):
            try:
                dir_contents = os.listdir(current_path)
                logger.debug(f"Directory contents: {dir_contents}")
            except PermissionError:
                logger.debug(f"Permission denied listing directory: {current_path}")

        for marker in markers:
            marker_path = os.path.join(current_path, marker)
            marker_exists = os.path.exists(marker_path)
            logger.debug(f"  Checking marker {marker} at {marker_path}: {marker_exists}")
            if marker_exists:
                logger.debug(f"Found workspace root at: {current_path}")
                return current_path
        current_path = os.path.dirname(current_path)

    # Fallback: go up from server.py location to find project root
    # server.py is in src/code_review_mcp/, so project root is 2 levels up
    server_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(server_dir))
    pyproject_path = os.path.join(project_root, "pyproject.toml")
    logger.debug(f"Fallback check - server_dir: {server_dir}")
    logger.debug(f"Fallback check - project_root: {project_root}")
    logger.debug(f"Fallback check - pyproject.toml at: {pyproject_path}")
    logger.debug(f"Fallback check - pyproject.toml exists: {os.path.exists(pyproject_path)}")

    if os.path.exists(pyproject_path):
        logger.debug(f"Using fallback project root: {project_root}")
        return project_root

    # Final fallback to current working directory
    final_fallback = os.getcwd()
    logger.debug(f"Using final fallback (cwd): {final_fallback}")
    return final_fallback


async def get_code_info(
    arguments: Dict[str, Any],
) -> Tuple[str, Optional[str], Optional[str]]:
    """Extract and validate code content from tool arguments.

    Handles both direct code content and file path inputs. For file paths,
    automatically reads the file content while supporting both absolute
    and workspace-relative paths.

    Args:
        arguments (Dict[str, Any]): Tool arguments containing either:
            - code_content: Direct code string
            - file_path: Path to code file (absolute or relative)
            - language: Programming language hint

    Returns:
        Tuple[str, Optional[str], Optional[str]]: A tuple containing:
            - code_content: The actual code to analyze
            - file_path: Original file path (if provided)
            - language: Programming language (if specified)

    Note:
        Gracefully handles file reading errors by returning empty content
    """
    logger.debug("=== GET_CODE_INFO DEBUG ===")
    logger.debug(f"Input arguments: {arguments}")

    code_content = arguments.get("code_content", "")
    file_path = arguments.get("file_path")
    language = arguments.get("language")

    logger.debug(f"Extracted code_content length: {len(code_content) if code_content else 0}")
    logger.debug(f"Extracted file_path: {file_path}")
    logger.debug(f"Extracted language: {language}")

    # If file_path is provided but no code_content, try to read the file
    if file_path and not code_content:
        logger.debug(f"Attempting to read file: {file_path}")
        logger.debug(f"File path is absolute: {os.path.isabs(file_path)}")

        try:
            # Handle both absolute and relative paths
            if os.path.isabs(file_path):
                abs_file_path = file_path
                logger.debug(f"Using absolute path as-is: {abs_file_path}")
            else:
                # For relative paths, resolve from workspace root
                workspace_root = find_workspace_root()
                abs_file_path = os.path.join(workspace_root, file_path)
                logger.debug(f"Resolved relative path - workspace_root: {workspace_root}")
                logger.debug(f"Resolved relative path - joined: {abs_file_path}")

            # Normalize the path for the current OS
            abs_file_path = os.path.normpath(abs_file_path)
            logger.debug(f"Normalized path: {abs_file_path}")

            # Check path components
            logger.debug(f"Path exists: {os.path.exists(abs_file_path)}")
            logger.debug(f"Path is file: {os.path.isfile(abs_file_path)}")
            logger.debug(f"Path is dir: {os.path.isdir(abs_file_path)}")

            # Check parent directory
            parent_dir = os.path.dirname(abs_file_path)
            logger.debug(f"Parent directory: {parent_dir}")
            logger.debug(f"Parent directory exists: {os.path.exists(parent_dir)}")

            if os.path.exists(parent_dir):
                try:
                    parent_contents = os.listdir(parent_dir)
                    logger.debug(f"Parent directory contents: {parent_contents}")

                    # Check if our target file is in the directory listing
                    target_filename = os.path.basename(abs_file_path)
                    logger.debug(f"Target filename: {target_filename}")
                    logger.debug(f"Target file in parent directory: {target_filename in parent_contents}")

                except PermissionError:
                    logger.debug(f"Permission denied listing parent directory: {parent_dir}")

            # Try to get file stats
            try:
                file_stat = os.stat(abs_file_path)
                logger.debug(f"File stat - size: {file_stat.st_size} bytes")
                logger.debug(f"File stat - mode: {oct(file_stat.st_mode)}")
            except (FileNotFoundError, PermissionError) as stat_e:
                logger.debug(f"Could not get file stats: {stat_e}")

            logger.debug(f"Attempting to open file: {abs_file_path}")
            with open(abs_file_path, "r", encoding="utf-8") as f:
                code_content = f.read()
                logger.debug(f"Successfully read {len(code_content)} characters from file")

        except FileNotFoundError as e:
            logger.error(f"=== FILE NOT FOUND ERROR ===")
            logger.error(f"Original file_path: {file_path}")
            logger.error(f"Resolved abs_file_path: {abs_file_path}")
            logger.error(f"Error details: {e}")
            raise FileReadError(f"File not found: {file_path}") from e
        except PermissionError as e:
            logger.error(f"=== PERMISSION ERROR ===")
            logger.error(f"Original file_path: {file_path}")
            logger.error(f"Resolved abs_file_path: {abs_file_path}")
            logger.error(f"Error details: {e}")
            raise FileReadError(f"Permission denied: {file_path}") from e
        except UnicodeDecodeError as e:
            logger.error(f"=== ENCODING ERROR ===")
            logger.error(f"Original file_path: {file_path}")
            logger.error(f"Resolved abs_file_path: {abs_file_path}")
            logger.error(f"Error details: {e}")
            raise FileReadError(f"File encoding error: {file_path}") from e
        except Exception as e:
            logger.error(f"=== UNEXPECTED ERROR ===")
            logger.error(f"Original file_path: {file_path}")
            logger.error(f"Resolved abs_file_path: {abs_file_path}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {e}")
            # For backwards compatibility, continue with empty content
            pass

    logger.debug(f"Final code_content length: {len(code_content) if code_content else 0}")
    return code_content, file_path, language


@lru_cache(maxsize=128)
def detect_language(file_path: Optional[str], code_content: str) -> str:
    """Intelligently detect the programming language of code.

    Uses a two-stage detection process:
    1. File extension mapping for quick identification
    2. Content analysis for files without clear extensions

    Args:
        file_path (Optional[str]): File path with potential extension
        code_content (str): Source code content for analysis

    Returns:
        str: Detected language identifier (e.g., 'python', 'javascript')
            Returns 'unknown' if language cannot be determined

    Note:
        Results are cached for performance with frequently analyzed files
    """
    logger.debug(f"Detecting language for: {file_path or 'inline code'}")
    if file_path:
        ext = Path(file_path).suffix.lower()
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".html": "html",
            ".css": "css",
            ".sql": "sql",
            ".sh": "bash",
            ".ps1": "powershell",
        }
        if ext in lang_map:
            return lang_map[ext]

    # Basic content-based detection
    if "def " in code_content and "import " in code_content:
        return "python"
    elif "function " in code_content and ("var " in code_content or "let " in code_content):
        return "javascript"
    elif "public class " in code_content:
        return "java"

    return "unknown"


async def analyze_syntax(code_content: str, language: str) -> List[CodeIssue]:
    """Perform syntax analysis to detect structural code problems.

    Validates code syntax using language-specific parsers and identifies
    basic structural issues that would prevent code execution.

    Args:
        code_content (str): Source code to analyze
        language (str): Programming language identifier

    Returns:
        List[CodeIssue]: List of detected syntax and structural issues

    Note:
        Currently supports comprehensive Python syntax analysis.
        Other languages have basic validation.
    """
    logger.debug(f"Analyzing syntax for {language} code")
    issues = []

    if language == "python":
        try:
            ast.parse(code_content)
        except SyntaxError as e:
            logger.debug(f"Python syntax error detected: {e.msg} at line {e.lineno}")
            issues.append(
                CodeIssue(
                    severity="critical",
                    category="bug",
                    message=f"Syntax error: {e.msg}",
                    line=e.lineno,
                    column=e.offset,
                    suggestion="Fix the syntax error to make the code runnable",
                )
            )
        except Exception as e:
            logger.error(f"Unexpected error during Python syntax analysis: {e}")
            raise SyntaxAnalysisError(f"Failed to analyze Python syntax: {e}") from e

    return issues


async def analyze_security_issues(code_content: str, language: str) -> List[CodeIssue]:
    """Comprehensive security vulnerability analysis.

    Scans code for common security anti-patterns including:
    - Code injection vulnerabilities (eval, exec)
    - Hardcoded credentials and API keys
    - Cross-site scripting (XSS) risks
    - Command injection vulnerabilities
    - Unsafe deserialization patterns

    Args:
        code_content (str): Source code to analyze for security issues
        language (str): Programming language for language-specific checks

    Returns:
        List[CodeIssue]: Security issues found, ordered by severity

    Note:
        Uses precompiled regex patterns for optimal performance
    """
    logger.debug(f"Analyzing security issues for {language} code")
    issues = []
    lines = code_content.split("\n")

    # Get precompiled patterns for better performance
    all_patterns = get_compiled_patterns()
    patterns = all_patterns.get(language, [])

    # Filter for security patterns only
    security_patterns = [
        (pattern, severity, message)
        for pattern, severity, message in patterns
        if any(
            keyword in message.lower()
            for keyword in [
                "injection",
                "password",
                "api_key",
                "xss",
                "vulnerability",
                "unsafe",
            ]
        )
    ]

    for i, line in enumerate(lines, 1):
        for pattern, severity, message in security_patterns:
            if pattern.search(line):
                issues.append(
                    CodeIssue(
                        severity=severity,
                        category="security",
                        message=message,
                        line=i,
                        suggestion="Review this line for security implications",
                    )
                )

    return issues


async def analyze_performance_issues(code_content: str, language: str) -> List[CodeIssue]:
    """Identify performance bottlenecks and optimization opportunities.

    Detects common performance anti-patterns such as:
    - Inefficient loops and iterations
    - Suboptimal data structure usage
    - Unnecessary computations
    - Memory-intensive operations
    - Slow DOM manipulations (JavaScript)

    Args:
        code_content (str): Source code to analyze for performance issues
        language (str): Programming language for targeted optimizations

    Returns:
        List[CodeIssue]: Performance issues with optimization suggestions

    Note:
        Focuses on algorithmic improvements and language-specific optimizations
    """
    logger.debug(f"Analyzing performance issues for {language} code")
    issues = []
    lines = code_content.split("\n")

    # Get precompiled patterns for better performance
    all_patterns = get_compiled_patterns()
    patterns = all_patterns.get(language, [])

    # Filter for performance patterns only
    performance_patterns = [
        (pattern, severity, message)
        for pattern, severity, message in patterns
        if any(
            keyword in message.lower()
            for keyword in [
                "performance",
                "optimization",
                "consider",
                "instead",
                "better",
                "caching",
                "vectorized",
                "slow",
                "inefficient",
                "iterrows",
                "dataframe",
                "append",
            ]
        )
    ]

    for i, line in enumerate(lines, 1):
        for pattern, severity, message in performance_patterns:
            if pattern.search(line):
                issues.append(
                    CodeIssue(
                        severity=severity,
                        category="performance",
                        message=message,
                        line=i,
                        suggestion="Consider optimization for better performance",
                    )
                )

    return issues


async def analyze_style_issues(code_content: str, language: str) -> List[CodeIssue]:
    """Enforce code style and maintainability standards.

    Checks code against established style guidelines including:
    - Line length limits
    - Documentation requirements (docstrings)
    - Naming convention compliance
    - Code complexity metrics
    - Consistency in formatting

    Args:
        code_content (str): Source code to analyze for style issues
        language (str): Programming language for language-specific style rules

    Returns:
        List[CodeIssue]: Style violations with improvement suggestions

    Note:
        Promotes code readability and maintainability best practices
    """
    logger.debug(f"Analyzing style issues for {language} code")
    issues = []
    lines = code_content.split("\n")

    # Check line length
    max_line_length = 100
    for i, line in enumerate(lines, 1):
        if len(line) > max_line_length:
            issues.append(
                CodeIssue(
                    severity="low",
                    category="style",
                    message=f"Line too long ({len(line)} characters)",
                    line=i,
                    suggestion=f"Keep lines under {max_line_length} characters",
                )
            )

    # Language-specific style checks
    if language == "python":
        for i, line in enumerate(lines, 1):
            # Check for missing docstrings in functions/classes
            if re.match(r"^\s*(def|class)\s+", line) and i < len(lines):
                next_line = lines[i] if i < len(lines) else ""
                if not re.match(r'^\s*["\']', next_line.strip()):
                    issues.append(
                        CodeIssue(
                            severity="low",
                            category="style",
                            message="Missing docstring",
                            line=i,
                            suggestion="Add docstring to describe the function/class",
                        )
                    )

    return issues


def calculate_metrics(code_content: str, language: str) -> Dict[str, Any]:
    """Calculate comprehensive code quality and complexity metrics.

    Computes various metrics to assess code quality and complexity:
    - Lines of code (total, non-empty, comments)
    - Function and class counts
    - Complexity indicators
    - Documentation coverage

    Args:
        code_content (str): Source code to analyze
        language (str): Programming language for accurate parsing

    Returns:
        Dict[str, Any]: Dictionary containing calculated metrics:
            - total_lines: Total number of lines
            - non_empty_lines: Lines with actual content
            - comment_lines: Lines containing comments
            - function_count: Number of function definitions
            - class_count: Number of class definitions

    Note:
        Metrics help assess code maintainability and complexity
    """
    logger.debug(f"Calculating metrics for {language} code")
    lines = code_content.split("\n")

    metrics = {
        "total_lines": len(lines),
        "non_empty_lines": len([line for line in lines if line.strip()]),
        "comment_lines": 0,
        "function_count": 0,
        "class_count": 0,
    }

    if language == "python":
        metrics["comment_lines"] = len([line for line in lines if line.strip().startswith("#")])
        metrics["function_count"] = len(re.findall(r"^\s*def\s+", code_content, re.MULTILINE))
        metrics["class_count"] = len(re.findall(r"^\s*class\s+", code_content, re.MULTILINE))
    elif language == "javascript":
        metrics["comment_lines"] = len([line for line in lines if line.strip().startswith("//")])
        metrics["function_count"] = len(re.findall(r"function\s+\w+|\w+\s*=>|\w+:\s*function", code_content))
        metrics["class_count"] = len(re.findall(r"class\s+\w+", code_content))

    return metrics


def format_review_result(file_path: str, language: str, issues: List[CodeIssue], metrics: Dict[str, Any]) -> str:
    """Format comprehensive code review results for display.

    Creates a human-readable report combining code metrics, issue summaries,
    and detailed findings with actionable recommendations.

    Args:
        file_path (str): Path or identifier of the analyzed code
        language (str): Detected or specified programming language
        issues (List[CodeIssue]): All detected code issues
        metrics (Dict[str, Any]): Calculated code quality metrics

    Returns:
        str: Formatted markdown report with:
            - Code metrics summary
            - Issue counts by severity and category
            - Detailed issue descriptions with line numbers
            - Actionable improvement suggestions

    Note:
        Uses emoji and markdown formatting for enhanced readability
    """
    logger.debug(f"Formatting review results for {file_path}")
    output = f"🔍 **Code Review Results for {file_path}**\n\n"
    output += f"**Language:** {language}\n\n"

    # Metrics
    output += "📊 **Code Metrics:**\n"
    for key, value in metrics.items():
        output += f"  - {key.replace('_', ' ').title()}: {value}\n"
    output += "\n"

    # Issues summary
    if issues:
        severity_counts = {}
        category_counts = {}

        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1

        output += "⚠️ **Issues Summary:**\n"
        for severity, count in severity_counts.items():
            output += f"  - {severity.title()}: {count}\n"
        output += "\n"

        output += "📋 **Issues by Category:**\n"
        for category, count in category_counts.items():
            output += f"  - {category.title()}: {count}\n"
        output += "\n"

        # Detailed issues
        output += "🔍 **Detailed Issues:**\n\n"
        for i, issue in enumerate(issues, 1):
            output += f"**{i}. {issue.severity.upper()} - {issue.category.upper()}**\n"
            output += f"   {issue.message}\n"
            if issue.line:
                output += f"   📍 Line {issue.line}\n"
            if issue.suggestion:
                output += f"   💡 {issue.suggestion}\n"
            output += "\n"
    else:
        output += "✅ **No issues detected!** Your code looks good.\n"

    return output


async def review_code(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Perform comprehensive multi-dimensional code analysis.

    This is the primary analysis function that orchestrates all code review
    activities including syntax validation, security analysis, performance
    optimization, and style checking.

    Args:
        arguments (Dict[str, Any]): Analysis parameters including:
            - file_path or code_content: Code to analyze
            - language: Programming language (optional, auto-detected)
            - severity_filter: Minimum severity level to report

    Returns:
        List[types.TextContent]: Formatted analysis results with:
            - Comprehensive issue report
            - Code quality metrics
            - Actionable recommendations

    Raises:
        Exception: If analysis fails due to invalid input or internal error

    Note:
        Combines all analysis types for complete code assessment
    """
    logger.info("Starting comprehensive code review")
    try:
        try:
            code_content, file_path, language = await get_code_info(arguments)
        except FileReadError as e:
            logger.error(f"File read error during code review: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=f"📁 **File Read Error**\n\n{str(e)}\n\nPlease check the file path and permissions.",
                )
            ]

        if not code_content:
            # Provide more detailed error information
            error_msg = "📝 **No Code Content**\n\nError: No code content provided or file not found."
            if file_path:
                if os.path.isabs(file_path):
                    error_msg += f"\n\n🔍 **Debug Info:**\n- Tried absolute path: `{file_path}`"
                else:
                    workspace_root = find_workspace_root()
                    attempted_path = os.path.normpath(os.path.join(workspace_root, file_path))
                    error_msg += f"\n\n🔍 **Debug Info:**"
                    error_msg += f"\n- Tried relative path: `{file_path}`"
                    error_msg += f"\n- Workspace root detected: `{workspace_root}`"
                    error_msg += f"\n- Resolved to: `{attempted_path}`"
                    error_msg += f"\n- File exists: {os.path.exists(attempted_path)}"
                    error_msg += f"\n- Current working directory: `{os.getcwd()}`"

            logger.warning(f"No code content found for analysis: {file_path or 'inline code'}")
            return [types.TextContent(type="text", text=error_msg)]

        # Detect language if not provided
        if not language:
            language = detect_language(file_path, code_content)

        # Perform analysis
        issues = []
        issues.extend(await analyze_syntax(code_content, language))
        issues.extend(await analyze_security_issues(code_content, language))
        issues.extend(await analyze_performance_issues(code_content, language))
        issues.extend(await analyze_style_issues(code_content, language))

        # Filter by severity if requested
        severity_filter = arguments.get("severity_filter", "all")
        if severity_filter != "all":
            severity_levels = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            min_level = severity_levels.get(severity_filter, 0)
            issues = [issue for issue in issues if severity_levels.get(issue.severity, 0) >= min_level]

        # Calculate metrics
        metrics = calculate_metrics(code_content, language)

        # Format result
        result_text = format_review_result(file_path or "inline_code", language, issues, metrics)

        return [types.TextContent(type="text", text=result_text)]

    except SyntaxAnalysisError as e:
        logger.error(f"Syntax analysis failed: {e}")
        return [
            types.TextContent(
                type="text",
                text=f"🚫 **Syntax Analysis Error**\n\n{str(e)}\n\nPlease check your code syntax.",
            )
        ]
    except Exception as e:
        logger.error(f"Unexpected error during code review: {e}", exc_info=True)
        return [
            types.TextContent(
                type="text",
                text=f"⚠️ **Analysis Error**\n\nAn unexpected error occurred during code review: {str(e)}\n\nPlease try again or contact support if the issue persists.",
            )
        ]


async def analyze_security(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Perform focused security vulnerability assessment.

    Dedicated security analysis tool that concentrates exclusively on
    identifying security risks and vulnerabilities in code.

    Args:
        arguments (Dict[str, Any]): Analysis parameters including:
            - file_path or code_content: Code to analyze
            - language: Programming language (optional, auto-detected)

    Returns:
        List[types.TextContent]: Security-focused analysis results with:
            - Detailed vulnerability descriptions
            - Risk assessment and severity levels
            - Specific remediation guidance

    Raises:
        Exception: If security analysis fails

    Note:
        Specialized for security professionals and security-conscious developers
    """
    logger.info("Starting focused security analysis")
    try:
        try:
            code_content, file_path, language = await get_code_info(arguments)
        except FileReadError as e:
            logger.error(f"File read error during security analysis: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=f"🔒 **Security Analysis Failed**\n\nFile read error: {str(e)}",
                )
            ]

        if not code_content:
            logger.warning("No code content provided for security analysis")
            return [
                types.TextContent(
                    type="text",
                    text="🔒 **Security Analysis**\n\nError: No code content provided or file not found.",
                )
            ]

        if not language:
            language = detect_language(file_path, code_content)

        issues = await analyze_security_issues(code_content, language)

        if not issues:
            return [
                types.TextContent(
                    type="text",
                    text="✅ No security issues detected in the provided code.",
                )
            ]

        result_text = "🔒 **Security Analysis Results:**\n\n"
        for issue in issues:
            result_text += f"**{issue.severity.upper()}** - {issue.message}\n"
            if issue.line:
                result_text += f"   📍 Line {issue.line}\n"
            if issue.suggestion:
                result_text += f"   💡 Suggestion: {issue.suggestion}\n"
            result_text += "\n"

        return [types.TextContent(type="text", text=result_text)]

    except Exception as e:
        logger.error(f"Unexpected error during security analysis: {e}", exc_info=True)
        return [
            types.TextContent(
                type="text",
                text=f"🔒 **Security Analysis Error**\n\nAn unexpected error occurred: {str(e)}\n\nPlease try again or contact support.",
            )
        ]


async def analyze_llm_invoke(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Critique LLM integration including prompt engineering, model choice, and parameters.

    Specialized analysis for LLM usage focusing on:
    - Prompt engineering best practices
    - Model parameter optimization (tokens, temperature, etc.)
    - Security issues (prompt injection, user input validation)
    - Cost optimization strategies
    - Response handling and processing

    Args:
        arguments (Dict[str, Any]): Analysis parameters including:
            - file_path or code_content: Code to analyze
            - language: Programming language (optional, auto-detected)

    Returns:
        List[types.TextContent]: LLM integration analysis results

    Raises:
        Exception: If analysis fails

    Note:
        Tailored for AI engineers and developers working with LLMs
    """
    logger.info("Starting LLM integration analysis")
    try:
        try:
            code_content, file_path, language = await get_code_info(arguments)
        except FileReadError as e:
            logger.error(f"File read error during LLM analysis: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=f"🤖 **LLM Analysis Failed**\n\nFile read error: {str(e)}",
                )
            ]

        if not code_content:
            logger.warning("No code content provided for LLM analysis")
            return [
                types.TextContent(
                    type="text",
                    text="🤖 **LLM Integration Analysis**\n\nError: No code content provided or file not found.",
                )
            ]

        if not language:
            language = detect_language(file_path, code_content)

        # Get patterns related to LLM integration
        all_patterns = get_compiled_patterns()
        patterns = all_patterns.get(language, [])

        llm_patterns = [
            (pattern, severity, message)
            for pattern, severity, message in patterns
            if any(
                keyword in message.lower()
                for keyword in [
                    "llm",
                    "openai",
                    "prompt",
                    "tokens",
                    "temperature",
                    "user input",
                    "guidance",
                    "choices",
                ]
            )
        ]

        # Analyze code
        issues = []
        lines = code_content.split("\n")

        for i, line in enumerate(lines, 1):
            for pattern, severity, message in llm_patterns:
                if pattern.search(line):
                    # Categorize issues more specifically for LLM context
                    if "user input" in message.lower() or "injection" in message.lower():
                        category = "security"
                        suggestion = "Sanitize user input and validate prompts to prevent injection attacks"
                    elif "tokens" in message.lower() or "cost" in message.lower():
                        category = "performance"
                        suggestion = "Review token usage and costs for optimization"
                    elif "guidance" in message.lower() or "system" in message.lower():
                        category = "style"
                        suggestion = "Add system messages for better LLM guidance and consistency"
                    else:
                        category = "performance"
                        suggestion = "Review LLM integration for best practices"

                    issues.append(
                        CodeIssue(
                            severity=severity,
                            category=category,
                            message=message,
                            line=i,
                            suggestion=suggestion,
                        )
                    )

        if not issues:
            return [
                types.TextContent(
                    type="text",
                    text="✅ No LLM integration issues detected! Your LLM usage looks good.",
                )
            ]

        # Format results specifically for LLM analysis
        result_text = "🤖 **LLM Integration Analysis Results:**\n\n"

        # Group by issue type
        security_issues = [i for i in issues if i.category == "security"]
        performance_issues = [i for i in issues if i.category == "performance"]
        style_issues = [i for i in issues if i.category == "style"]

        if security_issues:
            result_text += "🔒 **Security & Prompt Safety:**\n"
            for issue in security_issues:
                result_text += f"- **{issue.severity.upper()}** (Line {issue.line}): {issue.message}\n"
                result_text += f"  💡 {issue.suggestion}\n\n"

        if performance_issues:
            result_text += "⚡ **Performance & Cost Optimization:**\n"
            for issue in performance_issues:
                result_text += f"- **{issue.severity.upper()}** (Line {issue.line}): {issue.message}\n"
                result_text += f"  💡 {issue.suggestion}\n\n"

        if style_issues:
            result_text += "📝 **Prompt Engineering & Best Practices:**\n"
            for issue in style_issues:
                result_text += f"- **{issue.severity.upper()}** (Line {issue.line}): {issue.message}\n"
                result_text += f"  💡 {issue.suggestion}\n\n"

        # Add LLM-specific recommendations
        result_text += "💡 **LLM Best Practices Checklist:**\n"
        result_text += "- ✅ Use system messages to set context and behavior\n"
        result_text += "- ✅ Validate and sanitize all user inputs in prompts\n"
        result_text += "- ✅ Monitor token usage and implement cost controls\n"
        result_text += "- ✅ Handle API errors and rate limits gracefully\n"
        result_text += "- ✅ Strip and validate LLM responses before use\n"

        return [types.TextContent(type="text", text=result_text)]

    except Exception as e:
        logger.error(f"Unexpected error during LLM analysis: {e}", exc_info=True)
        return [
            types.TextContent(
                type="text",
                text=f"🤖 **LLM Analysis Error**\n\nAn unexpected error occurred: {str(e)}\n\nPlease try again or contact support.",
            )
        ]


async def analyze_api_handling(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Analyze API calls, error handling, timeouts, and retry strategies.

    Specialized analysis for API integration focusing on:
    - Proper error handling and status code checking
    - Timeout configuration and retry strategies
    - JSON parsing and response validation
    - Rate limiting and performance optimization
    - Security best practices for API calls

    Args:
        arguments (Dict[str, Any]): Analysis parameters including:
            - file_path or code_content: Code to analyze
            - language: Programming language (optional, auto-detected)

    Returns:
        List[types.TextContent]: API handling analysis results

    Raises:
        Exception: If analysis fails

    Note:
        Tailored for developers working with REST APIs and web services
    """
    logger.info("Starting API handling analysis")
    try:
        try:
            code_content, file_path, language = await get_code_info(arguments)
        except FileReadError as e:
            logger.error(f"File read error during API analysis: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=f"🌐 **API Analysis Failed**\n\nFile read error: {str(e)}",
                )
            ]

        if not code_content:
            logger.warning("No code content provided for API analysis")
            return [
                types.TextContent(
                    type="text",
                    text="🌐 **API Handling Analysis**\n\nError: No code content provided or file not found.",
                )
            ]

        if not language:
            language = detect_language(file_path, code_content)

        # Get patterns related to API handling
        all_patterns = get_compiled_patterns()
        patterns = all_patterns.get(language, [])

        api_patterns = [
            (pattern, severity, message)
            for pattern, severity, message in patterns
            if any(
                keyword in message.lower()
                for keyword in [
                    "api",
                    "requests",
                    "fetch",
                    "timeout",
                    "json",
                    "status",
                    "retry",
                    "axios",
                    "error handling",
                ]
            )
        ]

        # Analyze code
        issues = []
        lines = code_content.split("\n")

        for i, line in enumerate(lines, 1):
            for pattern, severity, message in api_patterns:
                if pattern.search(line):
                    # Categorize issues specifically for API context
                    if "timeout" in message.lower() or "hanging" in message.lower():
                        category = "performance"
                        suggestion = "Add timeout parameters to prevent hanging requests"
                    elif "status" in message.lower() or "error handling" in message.lower():
                        category = "bug"
                        suggestion = "Add proper error handling and status code checking"
                    elif "json" in message.lower():
                        category = "bug"
                        suggestion = "Add try-catch blocks around JSON parsing operations"
                    elif "retry" in message.lower() or "backoff" in message.lower():
                        category = "performance"
                        suggestion = "Implement exponential backoff for retry strategies"
                    else:
                        category = "performance"
                        suggestion = "Review API integration for best practices"

                    issues.append(
                        CodeIssue(
                            severity=severity,
                            category=category,
                            message=message,
                            line=i,
                            suggestion=suggestion,
                        )
                    )

        if not issues:
            return [
                types.TextContent(
                    type="text",
                    text="✅ No API handling issues detected! Your API integration looks robust.",
                )
            ]

        # Format results specifically for API analysis
        result_text = "🌐 **API Handling Analysis Results:**\n\n"

        # Group by issue type
        bug_issues = [i for i in issues if i.category == "bug"]
        performance_issues = [i for i in issues if i.category == "performance"]
        security_issues = [i for i in issues if i.category == "security"]

        if bug_issues:
            result_text += "🐛 **Error Handling & Reliability:**\n"
            for issue in bug_issues:
                result_text += f"- **{issue.severity.upper()}** (Line {issue.line}): {issue.message}\n"
                result_text += f"  💡 {issue.suggestion}\n\n"

        if performance_issues:
            result_text += "⚡ **Performance & Timeouts:**\n"
            for issue in performance_issues:
                result_text += f"- **{issue.severity.upper()}** (Line {issue.line}): {issue.message}\n"
                result_text += f"  💡 {issue.suggestion}\n\n"

        if security_issues:
            result_text += "🔒 **Security & Best Practices:**\n"
            for issue in security_issues:
                result_text += f"- **{issue.severity.upper()}** (Line {issue.line}): {issue.message}\n"
                result_text += f"  💡 {issue.suggestion}\n\n"

        # Add API-specific recommendations
        result_text += "💡 **API Integration Best Practices Checklist:**\n"
        result_text += "- ✅ Always set timeout values for API calls\n"
        result_text += "- ✅ Check HTTP status codes and handle errors gracefully\n"
        result_text += "- ✅ Implement exponential backoff for retry logic\n"
        result_text += "- ✅ Validate JSON responses before processing\n"
        result_text += "- ✅ Use appropriate HTTP methods and headers\n"
        result_text += "- ✅ Implement rate limiting and respect API quotas\n"

        return [types.TextContent(type="text", text=result_text)]

    except Exception as e:
        logger.error(f"Unexpected error during API analysis: {e}", exc_info=True)
        return [
            types.TextContent(
                type="text",
                text=f"🌐 **API Analysis Error**\n\nAn unexpected error occurred: {str(e)}\n\nPlease try again or contact support.",
            )
        ]


async def check_performance(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Perform comprehensive performance optimization analysis including DataFrame operations.

    Specialized tool for identifying performance bottlenecks and suggesting
    optimizations to improve code execution speed and resource efficiency.
    Now includes specific analysis for DataFrame operations and data processing.

    Args:
        arguments (Dict[str, Any]): Analysis parameters including:
            - file_path or code_content: Code to analyze
            - language: Programming language (optional, auto-detected)

    Returns:
        List[types.TextContent]: Performance analysis results with:
            - General performance bottlenecks and inefficiencies
            - DataFrame operation optimizations (pandas, iterrows, etc.)
            - Memory usage improvements
            - Specific optimization recommendations

    Raises:
        Exception: If performance analysis fails

    Note:
        Includes specialized DataFrame analysis for data science workflows
    """
    logger.info("Starting performance optimization analysis")
    try:
        try:
            code_content, file_path, language = await get_code_info(arguments)
        except FileReadError as e:
            logger.error(f"File read error during performance analysis: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=f"⚡ **Performance Analysis Failed**\n\nFile read error: {str(e)}",
                )
            ]

        if not code_content:
            logger.warning("No code content provided for performance analysis")
            return [
                types.TextContent(
                    type="text",
                    text="⚡ **Performance Analysis**\n\nError: No code content provided or file not found.",
                )
            ]

        if not language:
            language = detect_language(file_path, code_content)

        issues = await analyze_performance_issues(code_content, language)

        if not issues:
            return [
                types.TextContent(
                    type="text",
                    text="✅ No performance issues detected in the provided code.",
                )
            ]

        # Categorize issues for better presentation
        dataframe_issues = [
            i
            for i in issues
            if any(
                keyword in i.message.lower()
                for keyword in [
                    "dataframe",
                    "iterrows",
                    "pandas",
                    "concat",
                    "append",
                    "vectorized",
                ]
            )
        ]
        general_issues = [i for i in issues if i not in dataframe_issues]

        result_text = "⚡ **Performance Analysis Results:**\n\n"

        if dataframe_issues:
            result_text += "📈 **DataFrame Performance Issues:**\n"
            for issue in dataframe_issues:
                result_text += f"**{issue.severity.upper()}** - {issue.message}\n"
                if issue.line:
                    result_text += f"   📍 Line {issue.line}\n"
                if issue.suggestion:
                    result_text += f"   💡 Suggestion: {issue.suggestion}\n"
                result_text += "\n"

        if general_issues:
            result_text += "⚡ **General Performance Issues:**\n"
            for issue in general_issues:
                result_text += f"**{issue.severity.upper()}** - {issue.message}\n"
                if issue.line:
                    result_text += f"   📍 Line {issue.line}\n"
                if issue.suggestion:
                    result_text += f"   💡 Suggestion: {issue.suggestion}\n"
                result_text += "\n"

        # Add DataFrame-specific tips if relevant
        if dataframe_issues:
            result_text += "📊 **DataFrame Optimization Tips:**\n"
            result_text += "- Use vectorized operations instead of iterrows()\n"
            result_text += "- Prefer .loc/.iloc for setting values instead of loops\n"
            result_text += "- Use pd.concat() with list of DataFrames instead of append()\n"
            result_text += "- Consider chunking for large CSV files\n\n"

        return [types.TextContent(type="text", text=result_text)]

    except Exception as e:
        logger.error(f"Unexpected error during performance analysis: {e}", exc_info=True)
        return [
            types.TextContent(
                type="text",
                text=f"⚡ **Performance Analysis Error**\n\nAn unexpected error occurred: {str(e)}\n\nPlease try again or contact support.",
            )
        ]


async def analyze_data_processing(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Specialized analysis for data processing pipelines, pandas operations, and memory optimization.

    Focuses specifically on data processing workflows including:
    - DataFrame operation efficiency and memory usage
    - Data type optimization and conversion chains
    - Pipeline structure and data flow optimization
    - Memory leaks and resource management
    - Data validation and error handling in pipelines

    Args:
        arguments (Dict[str, Any]): Analysis parameters including:
            - file_path or code_content: Code to analyze
            - language: Programming language (optional, auto-detected)

    Returns:
        List[types.TextContent]: Data processing analysis results

    Raises:
        Exception: If analysis fails

    Note:
        Specialized for data engineers and data scientists working with large datasets
    """
    logger.info("Starting data processing pipeline analysis")
    try:
        try:
            code_content, file_path, language = await get_code_info(arguments)
        except FileReadError as e:
            logger.error(f"File read error during data processing analysis: {e}")
            return [
                types.TextContent(
                    type="text",
                    text=f"📊 **Data Processing Analysis Failed**\n\nFile read error: {str(e)}",
                )
            ]

        if not code_content:
            logger.warning("No code content provided for data processing analysis")
            return [
                types.TextContent(
                    type="text",
                    text="📊 **Data Processing Analysis**\n\nError: No code content provided or file not found.",
                )
            ]

        if not language:
            language = detect_language(file_path, code_content)

        # Get patterns related to data processing
        all_patterns = get_compiled_patterns()
        patterns = all_patterns.get(language, [])

        # Filter for data processing specific patterns
        data_patterns = [
            (pattern, severity, message)
            for pattern, severity, message in patterns
            if any(
                keyword in message.lower()
                for keyword in [
                    "dataframe",
                    "pandas",
                    "copy",
                    "astype",
                    "merge",
                    "memory",
                    "json",
                    "to_dict",
                    "fillna",
                    "reset_index",
                    "iterrows",
                    "concat",
                    "append",
                    "vectorized",
                    "chunking",
                ]
            )
        ]

        # Analyze code
        issues = []
        lines = code_content.split("\n")

        for i, line in enumerate(lines, 1):
            for pattern, severity, message in data_patterns:
                if pattern.search(line):
                    # Categorize issues specifically for data processing context
                    if "memory" in message.lower() or "copy" in message.lower():
                        category = "performance"
                        suggestion = "Optimize memory usage by reducing DataFrame copies and consolidating operations"
                    elif "type" in message.lower() or "astype" in message.lower():
                        category = "performance"
                        suggestion = "Optimize data type conversions to reduce processing overhead"
                    elif "merge" in message.lower() or "join" in message.lower():
                        category = "performance"
                        suggestion = "Optimize DataFrame joins and merges for better performance"
                    elif "iterrows" in message.lower() or "vectorized" in message.lower():
                        category = "performance"
                        suggestion = "Use vectorized operations instead of row-by-row processing"
                    else:
                        category = "performance"
                        suggestion = "Review data processing pipeline for optimization opportunities"

                    issues.append(
                        CodeIssue(
                            severity=severity,
                            category=category,
                            message=message,
                            line=i,
                            suggestion=suggestion,
                        )
                    )

        # Additional data processing specific checks
        # Check for potential memory issues
        if "pd.read_csv" in code_content and "chunksize" not in code_content:
            issues.append(
                CodeIssue(
                    severity="medium",
                    category="performance",
                    message="Large file reading without chunking - potential memory issues",
                    suggestion="Consider using chunksize parameter for large CSV files",
                )
            )

        # Check for data validation
        if "input_data[" in code_content and "get(" not in code_content:
            issues.append(
                CodeIssue(
                    severity="medium",
                    category="bug",
                    message="Direct dictionary access without validation",
                    suggestion="Use .get() method or add validation checks for input data",
                )
            )

        if not issues:
            return [
                types.TextContent(
                    type="text",
                    text="✅ No data processing issues detected! Your data pipeline looks optimized.",
                )
            ]

        # Format results specifically for data processing analysis
        result_text = "📊 **Data Processing Pipeline Analysis Results:**\n\n"

        # Group by issue type
        memory_issues = [i for i in issues if "memory" in i.message.lower() or "copy" in i.message.lower()]
        performance_issues = [i for i in issues if i.category == "performance" and i not in memory_issues]
        data_issues = [i for i in issues if i.category == "bug"]

        if memory_issues:
            result_text += "🧠 **Memory & Resource Management:**\n"
            for issue in memory_issues:
                result_text += f"- **{issue.severity.upper()}** (Line {issue.line}): {issue.message}\n"
                result_text += f"  💡 {issue.suggestion}\n\n"

        if performance_issues:
            result_text += "⚡ **Data Processing Performance:**\n"
            for issue in performance_issues:
                result_text += f"- **{issue.severity.upper()}** (Line {issue.line}): {issue.message}\n"
                result_text += f"  💡 {issue.suggestion}\n\n"

        if data_issues:
            result_text += "🔍 **Data Validation & Reliability:**\n"
            for issue in data_issues:
                result_text += f"- **{issue.severity.upper()}** (Line {issue.line}): {issue.message}\n"
                result_text += f"  💡 {issue.suggestion}\n\n"

        # Add data processing specific recommendations
        result_text += "💡 **Data Processing Best Practices Checklist:**\n"
        result_text += "- ✅ Use vectorized operations instead of loops\n"
        result_text += "- ✅ Minimize DataFrame copies and consolidate operations\n"
        result_text += "- ✅ Optimize data types early in the pipeline\n"
        result_text += "- ✅ Use chunking for large datasets\n"
        result_text += "- ✅ Validate input data before processing\n"
        result_text += "- ✅ Monitor memory usage in data pipelines\n"
        result_text += "- ✅ Use efficient join strategies for merges\n"

        return [types.TextContent(type="text", text=result_text)]

    except Exception as e:
        logger.error(f"Unexpected error during data processing analysis: {e}", exc_info=True)
        return [
            types.TextContent(
                type="text",
                text=f"📊 **Data Processing Analysis Error**\n\nAn unexpected error occurred: {str(e)}\n\nPlease try again or contact support.",
            )
        ]


async def main() -> None:
    """Initialize and run the Code Review MCP server.

    Sets up the MCP server with stdio communication channels and runs
    the main server loop. Handles all MCP protocol communication and
    tool invocations.

    Raises:
        Exception: If server initialization or execution fails

    Note:
        This function runs indefinitely until the MCP client disconnects
    """
    logger.info("Starting Code Review MCP Server v0.2.1")
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="code-review-mcp",
                server_version="0.2.1",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
