# Code Review MCP Server

An advanced Model Context Protocol (MCP) server that provides automated code review and bug detection capabilities for various programming languages. This server integrates seamlessly with Cursor IDE and other MCP-compatible applications to enhance your development workflow.

## Features

🔍 **Comprehensive Code Analysis**
- Syntax error detection
- Security vulnerability scanning
- Performance optimization suggestions
- Code style and maintainability checks

🚀 **Multi-Language Support**
- Python
- JavaScript/TypeScript
- Java
- C/C++
- Go, Rust, PHP, Ruby, and more

⚡ **Real-time Analysis**
- Instant feedback on code quality
- Configurable severity filtering
- Detailed suggestions for improvements

🛡️ **Security Focus**
- Detects common security vulnerabilities
- Identifies hardcoded credentials
- Checks for injection risks

## Installation

### Prerequisites

- Python 3.8 or higher
- Git

### Option 1: Install from PyPI (Recommended)

```bash
pip install code-review-mcp
```

### Option 2: Install from Source

1. Clone the repository:
```bash
git clone https://github.com/bobbymuls/code-review-mcp.git
cd code-review-mcp
```

2. Create and activate a virtual environment:
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package:
```bash
pip install -e .
```

## Configuration

### For Cursor IDE

Add the following configuration to your Cursor settings:

```json
{
  "mcpServers": {
    "code-review-mcp": {
      "command": "python",
      "args": ["-m", "code_review_mcp.server"],
      "env": {}
    }
  }
}
```

### For Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "code-review-mcp": {
      "command": "code-review-mcp",
      "args": []
    }
  }
}
```

## Usage

Once configured, the MCP server provides three main tools:

### 1. `review_code`
Comprehensive code analysis including syntax, security, performance, and style checks.

**Parameters:**
- `file_path` (optional): Path to the code file
- `code_content` (optional): Direct code content to analyze
- `language` (optional): Programming language (auto-detected if not provided)
- `severity_filter` (optional): Filter by minimum severity level

**Example:**
```python
# Analyze a Python file
review_code(file_path="my_script.py")

# Analyze code content directly
review_code(code_content="def hello(): print('world')", language="python")

# Filter only critical and high severity issues
review_code(file_path="app.py", severity_filter="high")
```

### 2. `analyze_security`
Focused security vulnerability analysis.

**Parameters:**
- `file_path` (optional): Path to the code file
- `code_content` (optional): Direct code content to analyze
- `language` (optional): Programming language

### 3. `check_performance`
Performance analysis and optimization suggestions.

**Parameters:**
- `file_path` (optional): Path to the code file
- `code_content` (optional): Direct code content to analyze
- `language` (optional): Programming language

## Detection Capabilities

### Security Issues
- Code injection vulnerabilities (eval, exec)
- SQL injection risks
- XSS vulnerabilities
- Hardcoded credentials
- Unsafe deserialization
- Command injection

### Performance Issues
- Inefficient loops and iterations
- Unnecessary list concatenations
- Inefficient DOM queries
- Suboptimal data structures

### Code Quality
- Missing documentation
- Overly long lines
- Complex functions
- Code duplication patterns

### Syntax Issues
- Parse errors
- Invalid syntax
- Missing imports

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/code_review_mcp --cov-report=html
```

### Code Quality

```bash
# Format code
black src/code_review_mcp tests/

# Sort imports
isort src/code_review_mcp tests/

# Lint code
flake8 src/code_review_mcp

# Type checking
mypy src/code_review_mcp
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Ensure all tests pass: `pytest`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

- 📚 [Documentation](https://github.com/bobbymuls/code-review-mcp/wiki)
- 🐛 [Issue Tracker](https://github.com/bobbymuls/code-review-mcp/issues)
- 💬 [Discussions](https://github.com/bobbymuls/code-review-mcp/discussions)

## Roadmap

- [ ] Support for more programming languages
- [ ] Integration with popular linters (ESLint, Pylint, etc.)
- [ ] Custom rule configuration
- [ ] Code complexity metrics
- [ ] Integration with CI/CD pipelines
- [ ] VS Code extension

---

Made with ❤️ for the developer community
