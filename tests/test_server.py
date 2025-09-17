"""Tests for the MCP server functionality."""

import pytest
from code_review_mcp.server import (
    CodeIssue, 
    detect_language, 
    analyze_syntax, 
    analyze_security_issues,
    analyze_performance_issues,
    calculate_metrics,
    get_code_info,
    analyze_llm_invoke,
    analyze_api_handling
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
        
        # Test by content (updated pattern for better detection)
        js_code = "function hello() { var x = 'test'; console.log('Hello'); }"
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
        
        assert metrics["total_lines"] == 11  # Updated to match actual line count
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
        """Test get_code_info with file path that doesn't exist."""
        from code_review_mcp.server import FileReadError
        
        arguments = {
            "file_path": "nonexistent.py",
            "language": "python"
        }
        
        # Should raise FileReadError for nonexistent files
        with pytest.raises(FileReadError):
            await get_code_info(arguments)

    @pytest.mark.asyncio
    async def test_analyze_llm_invoke_patterns(self):
        """Test LLM integration analysis."""
        code = """
import openai

# High token usage
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=5000
)

# User input in prompt
user_input = input("Question: ")
prompt += user_input

# Missing system message
messages = [{"role": "user", "content": "Hello"}]
"""
        result = await analyze_llm_invoke({"code_content": code, "language": "python"})
        
        # Should return formatted text content
        assert len(result) == 1
        assert "LLM Integration Analysis Results" in result[0].text
        assert "Security & Prompt Safety" in result[0].text or "Performance & Cost Optimization" in result[0].text

    @pytest.mark.asyncio
    async def test_analyze_api_handling_patterns(self):
        """Test API handling analysis."""
        code = """
import requests

# API call without status checking
response = requests.get('https://api.example.com/data')
data = response.json()

# API call without timeout
response2 = requests.post('https://api.example.com/submit')

# JSON parsing without exception handling
result = response.json()
"""
        result = await analyze_api_handling({"code_content": code, "language": "python"})
        
        # Should return formatted text content
        assert len(result) == 1
        assert "API Handling Analysis Results" in result[0].text
        assert ("Error Handling & Reliability" in result[0].text or 
                "Performance & Timeouts" in result[0].text)

    @pytest.mark.asyncio
    async def test_dataframe_performance_analysis(self):
        """Test DataFrame performance analysis in check_performance."""
        code = """import pandas as pd

# DataFrame iterrows - very slow
df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
for index, row in df.iterrows():
    print(row['a'])

# Large CSV without chunking
big_df = pd.read_csv('huge_file.csv')

# DataFrame append in loop
new_df = pd.DataFrame()
for i in range(10):
    new_df = new_df.append({'col': i}, ignore_index=True)
"""
        issues = await analyze_performance_issues(code, "python")
        
        # Should find DataFrame performance issues
        df_issues = [issue for issue in issues if any(keyword in issue.message.lower() 
                    for keyword in ['iterrows', 'csv', 'append', 'vectorized'])]
        assert len(df_issues) > 0
        
        # Should find iterrows issue specifically
        iterrows_issues = [issue for issue in issues if "iterrows" in issue.message.lower()]
        assert len(iterrows_issues) > 0
