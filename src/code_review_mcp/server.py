#!/usr/bin/env python3
"""
Code Review MCP Server

An MCP server that analyzes code for potential bugs, security issues,
performance problems, and code quality improvements.
"""

import asyncio
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from pydantic import BaseModel, Field


class CodeIssue(BaseModel):
    """Represents a code issue found during review."""
    
    severity: str = Field(description="Severity level: critical, high, medium, low")
    category: str = Field(description="Issue category: bug, security, performance, style")
    message: str = Field(description="Description of the issue")
    line: Optional[int] = Field(default=None, description="Line number where issue occurs")
    column: Optional[int] = Field(default=None, description="Column number where issue occurs")
    suggestion: Optional[str] = Field(default=None, description="Suggested fix")


class CodeReviewResult(BaseModel):
    """Result of code review analysis."""
    
    file_path: str = Field(description="Path to the analyzed file")
    language: str = Field(description="Programming language detected")
    issues: List[CodeIssue] = Field(description="List of issues found")
    metrics: Dict[str, Any] = Field(description="Code metrics and statistics")


class CodeReviewServer:
    """Main server class for code review MCP server."""
    
    def __init__(self):
        self.server = Server("code-review-mcp")
        self.setup_handlers()
    
    def setup_handlers(self):
        """Set up MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="review_code",
                    description="Analyze code for potential bugs, security issues, and improvements",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the code file to review"
                            },
                            "code_content": {
                                "type": "string",
                                "description": "Code content to review (alternative to file_path)"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language (auto-detected if not provided)"
                            },
                            "severity_filter": {
                                "type": "string",
                                "enum": ["all", "critical", "high", "medium", "low"],
                                "description": "Minimum severity level to include in results",
                                "default": "all"
                            }
                        },
                        "required": [],
                        "additionalProperties": False
                    }
                ),
                types.Tool(
                    name="analyze_security",
                    description="Perform focused security analysis on code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the code file to analyze"
                            },
                            "code_content": {
                                "type": "string",
                                "description": "Code content to analyze (alternative to file_path)"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language"
                            }
                        },
                        "required": [],
                        "additionalProperties": False
                    }
                ),
                types.Tool(
                    name="check_performance",
                    description="Analyze code for performance issues and optimization opportunities",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the code file to analyze"
                            },
                            "code_content": {
                                "type": "string",
                                "description": "Code content to analyze (alternative to file_path)"
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language"
                            }
                        },
                        "required": [],
                        "additionalProperties": False
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict | None
        ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool calls."""
            
            if arguments is None:
                arguments = {}
            
            if name == "review_code":
                return await self.review_code(arguments)
            elif name == "analyze_security":
                return await self.analyze_security(arguments)
            elif name == "check_performance":
                return await self.check_performance(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def review_code(self, arguments: dict) -> list[types.TextContent]:
        """Perform comprehensive code review."""
        try:
            code_content, file_path, language = await self._get_code_info(arguments)
            
            if not code_content:
                return [types.TextContent(
                    type="text",
                    text="Error: No code content provided or file not found."
                )]
            
            # Detect language if not provided
            if not language:
                language = self._detect_language(file_path, code_content)
            
            # Perform analysis
            issues = []
            issues.extend(await self._analyze_syntax(code_content, language))
            issues.extend(await self._analyze_security(code_content, language))
            issues.extend(await self._analyze_performance(code_content, language))
            issues.extend(await self._analyze_style(code_content, language))
            
            # Filter by severity if requested
            severity_filter = arguments.get("severity_filter", "all")
            if severity_filter != "all":
                severity_levels = {"critical": 4, "high": 3, "medium": 2, "low": 1}
                min_level = severity_levels.get(severity_filter, 0)
                issues = [issue for issue in issues 
                         if severity_levels.get(issue.severity, 0) >= min_level]
            
            # Calculate metrics
            metrics = self._calculate_metrics(code_content, language)
            
            # Create result
            result = CodeReviewResult(
                file_path=file_path or "inline_code",
                language=language,
                issues=issues,
                metrics=metrics
            )
            
            return [types.TextContent(
                type="text",
                text=self._format_review_result(result)
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error during code review: {str(e)}"
            )]
    
    async def analyze_security(self, arguments: dict) -> list[types.TextContent]:
        """Perform focused security analysis."""
        try:
            code_content, file_path, language = await self._get_code_info(arguments)
            
            if not code_content:
                return [types.TextContent(
                    type="text",
                    text="Error: No code content provided or file not found."
                )]
            
            if not language:
                language = self._detect_language(file_path, code_content)
            
            issues = await self._analyze_security(code_content, language)
            
            # Filter only security issues
            security_issues = [issue for issue in issues if issue.category == "security"]
            
            if not security_issues:
                return [types.TextContent(
                    type="text",
                    text="No security issues detected in the provided code."
                )]
            
            result_text = "🔒 Security Analysis Results:\\n\\n"
            for issue in security_issues:
                result_text += f"**{issue.severity.upper()}** - {issue.message}\\n"
                if issue.line:
                    result_text += f"   📍 Line {issue.line}\\n"
                if issue.suggestion:
                    result_text += f"   💡 Suggestion: {issue.suggestion}\\n"
                result_text += "\\n"
            
            return [types.TextContent(type="text", text=result_text)]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error during security analysis: {str(e)}"
            )]
    
    async def check_performance(self, arguments: dict) -> list[types.TextContent]:
        """Analyze code for performance issues."""
        try:
            code_content, file_path, language = await self._get_code_info(arguments)
            
            if not code_content:
                return [types.TextContent(
                    type="text",
                    text="Error: No code content provided or file not found."
                )]
            
            if not language:
                language = self._detect_language(file_path, code_content)
            
            issues = await self._analyze_performance(code_content, language)
            
            # Filter only performance issues
            perf_issues = [issue for issue in issues if issue.category == "performance"]
            
            if not perf_issues:
                return [types.TextContent(
                    type="text",
                    text="No performance issues detected in the provided code."
                )]
            
            result_text = "⚡ Performance Analysis Results:\\n\\n"
            for issue in perf_issues:
                result_text += f"**{issue.severity.upper()}** - {issue.message}\\n"
                if issue.line:
                    result_text += f"   📍 Line {issue.line}\\n"
                if issue.suggestion:
                    result_text += f"   💡 Suggestion: {issue.suggestion}\\n"
                result_text += "\\n"
            
            return [types.TextContent(type="text", text=result_text)]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error during performance analysis: {str(e)}"
            )]
    
    async def _get_code_info(self, arguments: dict) -> tuple[str, Optional[str], Optional[str]]:
        """Extract code content and metadata from arguments."""
        code_content = arguments.get("code_content", "")
        file_path = arguments.get("file_path")
        language = arguments.get("language")
        
        # If file_path is provided but no code_content, try to read the file
        if file_path and not code_content:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code_content = f.read()
            except Exception:
                # File might not exist or not readable
                pass
        
        return code_content, file_path, language
    
    def _detect_language(self, file_path: Optional[str], code_content: str) -> str:
        """Detect programming language from file extension or content."""
        if file_path:
            ext = Path(file_path).suffix.lower()
            lang_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.java': 'java',
                '.cpp': 'cpp',
                '.c': 'c',
                '.cs': 'csharp',
                '.go': 'go',
                '.rs': 'rust',
                '.php': 'php',
                '.rb': 'ruby',
                '.swift': 'swift',
                '.kt': 'kotlin',
                '.scala': 'scala',
                '.html': 'html',
                '.css': 'css',
                '.sql': 'sql',
                '.sh': 'bash',
                '.ps1': 'powershell'
            }
            if ext in lang_map:
                return lang_map[ext]
        
        # Basic content-based detection
        if 'def ' in code_content and 'import ' in code_content:
            return 'python'
        elif 'function ' in code_content and ('var ' in code_content or 'let ' in code_content):
            return 'javascript'
        elif 'public class ' in code_content:
            return 'java'
        
        return 'unknown'
    
    async def _analyze_syntax(self, code_content: str, language: str) -> List[CodeIssue]:
        """Analyze code for syntax and basic structural issues."""
        issues = []
        
        if language == 'python':
            try:
                ast.parse(code_content)
            except SyntaxError as e:
                issues.append(CodeIssue(
                    severity="critical",
                    category="bug",
                    message=f"Syntax error: {e.msg}",
                    line=e.lineno,
                    column=e.offset,
                    suggestion="Fix the syntax error to make the code runnable"
                ))
        
        return issues
    
    async def _analyze_security(self, code_content: str, language: str) -> List[CodeIssue]:
        """Analyze code for security vulnerabilities."""
        issues = []
        lines = code_content.split('\\n')
        
        # Common security patterns to check
        security_patterns = {
            'python': [
                (r'eval\\(', 'high', 'Use of eval() can lead to code injection'),
                (r'exec\\(', 'high', 'Use of exec() can lead to code injection'),
                (r'pickle\\.loads?\\(', 'medium', 'Pickle deserialization can be unsafe'),
                (r'subprocess\\.call\\([^)]*shell=True', 'medium', 'Shell injection risk'),
                (r'os\\.system\\(', 'high', 'Command injection vulnerability'),
                (r'password\\s*=\\s*["\'][^"\']*["\']', 'critical', 'Hardcoded password detected'),
                (r'api_key\\s*=\\s*["\'][^"\']*["\']', 'high', 'Hardcoded API key detected'),
            ],
            'javascript': [
                (r'eval\\(', 'high', 'Use of eval() can lead to code injection'),
                (r'innerHTML\\s*=', 'medium', 'Potential XSS vulnerability'),
                (r'document\\.write\\(', 'medium', 'Potential XSS vulnerability'),
                (r'password\\s*[=:]\\s*["\'][^"\']*["\']', 'critical', 'Hardcoded password detected'),
                (r'api_key\\s*[=:]\\s*["\'][^"\']*["\']', 'high', 'Hardcoded API key detected'),
            ]
        }
        
        patterns = security_patterns.get(language, [])
        
        for i, line in enumerate(lines, 1):
            for pattern, severity, message in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        severity=severity,
                        category="security",
                        message=message,
                        line=i,
                        suggestion="Review this line for security implications"
                    ))
        
        return issues
    
    async def _analyze_performance(self, code_content: str, language: str) -> List[CodeIssue]:
        """Analyze code for performance issues."""
        issues = []
        lines = code_content.split('\\n')
        
        # Performance patterns to check
        performance_patterns = {
            'python': [
                (r'for .+ in .+\\:\\s*if .+\\:\\s*break', 'medium', 'Consider using next() or any() instead of loop with break'),
                (r'\\.append\\(.+\\)\\s*$', 'low', 'Consider list comprehension for better performance'),
                (r'\\+= \\[.+\\]', 'medium', 'Use extend() instead of += for list concatenation'),
                (r'len\\(.+\\) == 0', 'low', 'Use "not sequence" instead of "len(sequence) == 0"'),
            ],
            'javascript': [
                (r'for\\s*\\(.+\\s+in\\s+.+\\)', 'medium', 'Consider for...of or forEach for arrays'),
                (r'\\$\\(.+\\)\\.each', 'medium', 'Consider native forEach instead of jQuery each'),
                (r'document\\.getElementById', 'low', 'Consider caching DOM queries'),
            ]
        }
        
        patterns = performance_patterns.get(language, [])
        
        for i, line in enumerate(lines, 1):
            for pattern, severity, message in patterns:
                if re.search(pattern, line):
                    issues.append(CodeIssue(
                        severity=severity,
                        category="performance",
                        message=message,
                        line=i,
                        suggestion="Consider optimization for better performance"
                    ))
        
        return issues
    
    async def _analyze_style(self, code_content: str, language: str) -> List[CodeIssue]:
        """Analyze code for style and maintainability issues."""
        issues = []
        lines = code_content.split('\\n')
        
        # Check line length
        max_line_length = 100
        for i, line in enumerate(lines, 1):
            if len(line) > max_line_length:
                issues.append(CodeIssue(
                    severity="low",
                    category="style",
                    message=f"Line too long ({len(line)} characters)",
                    line=i,
                    suggestion=f"Keep lines under {max_line_length} characters"
                ))
        
        # Language-specific style checks
        if language == 'python':
            for i, line in enumerate(lines, 1):
                # Check for missing docstrings in functions/classes
                if re.match(r'^\\s*(def|class)\\s+', line) and i < len(lines):
                    next_line = lines[i] if i < len(lines) else ""
                    if not re.match(r'^\\s*["\']', next_line.strip()):
                        issues.append(CodeIssue(
                            severity="low",
                            category="style",
                            message="Missing docstring",
                            line=i,
                            suggestion="Add docstring to describe the function/class"
                        ))
        
        return issues
    
    def _calculate_metrics(self, code_content: str, language: str) -> Dict[str, Any]:
        """Calculate basic code metrics."""
        lines = code_content.split('\\n')
        
        metrics = {
            "total_lines": len(lines),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "comment_lines": 0,
            "function_count": 0,
            "class_count": 0,
        }
        
        if language == 'python':
            metrics["comment_lines"] = len([line for line in lines if line.strip().startswith('#')])
            metrics["function_count"] = len(re.findall(r'^\\s*def\\s+', code_content, re.MULTILINE))
            metrics["class_count"] = len(re.findall(r'^\\s*class\\s+', code_content, re.MULTILINE))
        elif language == 'javascript':
            metrics["comment_lines"] = len([line for line in lines if line.strip().startswith('//')])
            metrics["function_count"] = len(re.findall(r'function\\s+\\w+|\\w+\\s*=>|\\w+:\\s*function', code_content))
            metrics["class_count"] = len(re.findall(r'class\\s+\\w+', code_content))
        
        return metrics
    
    def _format_review_result(self, result: CodeReviewResult) -> str:
        """Format the review result for display."""
        output = f"🔍 **Code Review Results for {result.file_path}**\\n\\n"
        output += f"**Language:** {result.language}\\n\\n"
        
        # Metrics
        output += "📊 **Code Metrics:**\\n"
        for key, value in result.metrics.items():
            output += f"  - {key.replace('_', ' ').title()}: {value}\\n"
        output += "\\n"
        
        # Issues summary
        if result.issues:
            severity_counts = {}
            category_counts = {}
            
            for issue in result.issues:
                severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
                category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
            
            output += "⚠️ **Issues Summary:**\\n"
            for severity, count in severity_counts.items():
                output += f"  - {severity.title()}: {count}\\n"
            output += "\\n"
            
            output += "📋 **Issues by Category:**\\n"
            for category, count in category_counts.items():
                output += f"  - {category.title()}: {count}\\n"
            output += "\\n"
            
            # Detailed issues
            output += "🔍 **Detailed Issues:**\\n\\n"
            for i, issue in enumerate(result.issues, 1):
                output += f"**{i}. {issue.severity.upper()} - {issue.category.upper()}**\\n"
                output += f"   {issue.message}\\n"
                if issue.line:
                    output += f"   📍 Line {issue.line}\\n"
                if issue.suggestion:
                    output += f"   💡 {issue.suggestion}\\n"
                output += "\\n"
        else:
            output += "✅ **No issues detected!** Your code looks good.\\n"
        
        return output
    
    async def run(self):
        """Run the MCP server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="code-review-mcp",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


def main():
    """Main entry point for the server."""
    server = CodeReviewServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
