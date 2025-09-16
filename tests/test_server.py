"""Tests for the MCP server functionality."""

import pytest
from code_review_mcp.server import (
    CodeIssue, 
    detect_language, 
    analyze_syntax, 
    analyze_security_issues,
    analyze_performance_issues,
    calculate_metrics,
    get_code_info
)


class TestCodeReviewServer:
    """Test cases for code review functionality."""

    def test_detect_language_python(self):
        """Test Python language detection."""
        # Test by file extension
        language = detect_language("test.py", "")
        assert language == "python"
        
        # Test by content
        python_code = "import os\ndef hello():\n    print('Hello, world!')"
        language = detect_language(None, python_code)
        assert language == "python"

    def test_detect_language_javascript(self):
        """Test JavaScript language detection."""
        # Test by file extension
        language = detect_language("test.js", "")
        assert language == "javascript"
        
        # Test by content
        js_code = "function hello() { console.log('Hello'); }"
        language = detect_language(None, js_code)
        assert language == "javascript"

    @pytest.mark.asyncio
    async def test_analyze_syntax_valid_python(self):
        """Test syntax analysis with valid Python code."""
        code = "def hello():\n    return 'Hello, world!'"
        issues = await analyze_syntax(code, "python")
        assert len(issues) == 0

    @pytest.mark.asyncio
    async def test_analyze_syntax_invalid_python(self):
        """Test syntax analysis with invalid Python code."""
        code = "def hello(\n    return 'Hello, world!'"  # Missing closing parenthesis
        issues = await analyze_syntax(code, "python")
        assert len(issues) > 0
        assert issues[0].severity == "critical"
        assert issues[0].category == "bug"

    @pytest.mark.asyncio
    async def test_analyze_security_python(self):
        """Test security analysis for Python code."""
        code = """
def dangerous_function():
    eval("print('This is dangerous')")
    password = "hardcoded_password"
    return True
"""
        issues = await analyze_security_issues(code, "python")
        
        # Should find eval() and hardcoded password issues
        assert len(issues) >= 2
        
        # Check for eval issue
        eval_issues = [issue for issue in issues if "eval" in issue.message.lower()]
        assert len(eval_issues) > 0
        assert eval_issues[0].severity == "high"
        
        # Check for password issue
        password_issues = [issue for issue in issues if "password" in issue.message.lower()]
        assert len(password_issues) > 0
        assert password_issues[0].severity == "critical"

    @pytest.mark.asyncio
    async def test_analyze_performance_python(self):
        """Test performance analysis for Python code."""
        code = """
def inefficient_function():
    items = []
    for i in range(100):
        if i % 2 == 0:
            items += [i]  # Inefficient list concatenation
    return items
"""
        issues = await analyze_performance_issues(code, "python")
        
        # Should find the inefficient list concatenation
        concat_issues = [issue for issue in issues if "concatenation" in issue.message.lower()]
        assert len(concat_issues) > 0
        assert concat_issues[0].category == "performance"

    def test_calculate_metrics_python(self):
        """Test code metrics calculation for Python."""
        code = """# This is a comment
class TestClass:
    def method1(self):
        pass
    
    def method2(self):
        return True

def function1():
    pass
"""
        metrics = calculate_metrics(code, "python")
        
        assert metrics["total_lines"] == 10
        assert metrics["comment_lines"] == 1
        assert metrics["function_count"] == 3  # 2 methods + 1 function
        assert metrics["class_count"] == 1

    def test_code_issue_model(self):
        """Test CodeIssue model."""
        issue = CodeIssue(
            severity="high",
            category="security",
            message="Test security issue",
            line=42,
            suggestion="Fix this issue"
        )
        
        assert issue.severity == "high"
        assert issue.category == "security"
        assert issue.message == "Test security issue"
        assert issue.line == 42
        assert issue.suggestion == "Fix this issue"

    @pytest.mark.asyncio
    async def test_get_code_info_with_content(self):
        """Test get_code_info with direct code content."""
        arguments = {
            "code_content": "print('Hello')",
            "language": "python"
        }
        
        code_content, file_path, language = await get_code_info(arguments)
        
        assert code_content == "print('Hello')"
        assert file_path is None
        assert language == "python"

    @pytest.mark.asyncio
    async def test_get_code_info_with_file_path(self):
        """Test get_code_info with file path."""
        arguments = {
            "file_path": "nonexistent.py",
            "language": "python"
        }
        
        code_content, file_path, language = await get_code_info(arguments)
        
        assert code_content == ""  # File doesn't exist
        assert file_path == "nonexistent.py"
        assert language == "python"
