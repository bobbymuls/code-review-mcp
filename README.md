# 🔍 Code Review MCP Server v0.2.1

**Automatically catch bugs, security issues, and performance problems while you code!**

An intelligent Model Context Protocol (MCP) server that provides real-time code analysis directly in Cursor IDE. Now with **specialized analysis tools** for data science, AI development, and API integration. Get instant feedback on code quality without leaving your editor.

## 🆕 **What's New in v0.2.1**

### 🎯 **New Specialized Analysis Tool**
- **📊 `analyze_data_processing`** - Specialized analysis for data processing pipelines, pandas operations, and memory optimization

### 🔧 **Enhanced Detection Patterns**
- **Enhanced Security Patterns** - Better detection of configuration-based secrets and credentials
- **Enhanced Performance Patterns** - Advanced pandas-specific optimizations and data processing improvements
- **Enhanced API Patterns** - Improved pagination, rate limiting, and service-specific API analysis
- **30+ new analysis patterns** specifically for data engineering and processing workflows

### 🏗️ **Previous Features (v0.2.0)**
- **🤖 `analyze_llm_invoke`** - Critique LLM integration, prompt engineering, and model parameters
- **🌐 `analyze_api_handling`** - Analyze API calls, error handling, timeouts, and retry strategies  
- **📈 Enhanced `check_performance`** - DataFrame operations and data science optimizations
- **50+ analysis patterns** for data science and AI workflows
- **Precompiled regex patterns** for 3x faster analysis

---

## ⚡ Quick Start (3 Minutes Setup)

> **🔄 Fast-changing project?** This MCP server updates frequently! Consider using [Method 2: Editable Install](#-method-2-editable-install-developers--testers) for instant updates.

### Step 1: Install Python Package
```bash
pip install git+https://github.com/bobbymuls/code-review-mcp.git
```

### Step 2: Configure Cursor IDE

1. **Open Cursor Settings** (Ctrl+, or Cmd+,)
2. **Navigate to**: `MCP & Integrations` → `New MCP Server`
3. **Find your Python path in cmd**:
   ```bash
   # Find where Python is installed
   which python   # macOS/Linux
   where python   # Windows
   ```

4. **Add this configuration** (using your Python path):

```json
{
  "code-review-mcp": {
    "command": "/full/path/to/your/python",
    "args": ["-m", "code_review_mcp.server"],
    "env": {}
  }
}
```

**Example paths**:
- **Windows**: `"C:\\Python311\\python.exe"` or `"C:\\Users\\YourName\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"`
- **macOS**: `"/usr/local/bin/python3"` or `"/opt/homebrew/bin/python3"`
- **Linux**: `"/usr/bin/python3"` or `"/home/username/.local/bin/python"`

### Step 3: Restart Cursor & Start Coding!

✅ You should see **6 tools enabled** under `code-review-mcp` in MCP settings  
✅ Now you can ask: *"Review this code for security issues"* and get instant analysis!

---

## 🎯 What It Does

### 🔒 **Security Analysis**
- Detects code injection vulnerabilities (`eval`, `exec`)
- Finds hardcoded passwords and API keys  
- Identifies XSS and SQL injection risks
- Spots unsafe deserialization patterns
- **NEW**: Command injection and crypto weaknesses

### 🤖 **LLM Integration Analysis**
- **NEW**: Prompt injection detection and prevention
- **NEW**: Cost optimization (token usage monitoring)
- **NEW**: Model parameter recommendations
- **NEW**: Prompt engineering best practices

### 🌐 **API Handling Analysis**
- **NEW**: Error handling and status code checking
- **NEW**: Timeout configuration validation
- **NEW**: Retry strategy optimization
- **NEW**: JSON parsing safety

### 📊 **Data Processing & Performance Optimization**
- **NEW**: Specialized data processing pipeline analysis
- **NEW**: DataFrame operation optimization (pandas)
- **NEW**: Memory usage and efficiency improvements
- **NEW**: Data type optimization recommendations
- **NEW**: Vectorization and performance suggestions
- Suggests more efficient algorithms
- Identifies slow list operations
- Recommends better data structures

### 🐛 **Bug Detection**
- Catches syntax errors before runtime
- Identifies potential logic errors
- Finds missing error handling
- Detects unreachable code

### 📝 **Code Quality**
- Enforces consistent styling
- Suggests better naming conventions
- Identifies overly complex functions
- Recommends adding documentation

---

## 🗣️ How to Use in Cursor

Once installed, simply chat with Cursor using these prompts:

### 🔍 **General Code Review**
```
"Please review this code for any issues"
"Review the file src/components/Button.tsx"
```

### 🔒 **Security-Focused Analysis**  
```
"Check this code for security vulnerabilities"
"Analyze security issues in src/auth/login.py"
```

### 🤖 **NEW: LLM Integration Analysis**
```
"Use analyze_llm_invoke to review my OpenAI integration"
"Check my prompt engineering for security issues"
"Analyze this LLM code for cost optimization"
```

### 🌐 **NEW: API Handling Analysis**
```
"Use analyze_api_handling to review my REST API code"
"Check my API error handling and timeouts"
"Analyze this fetch code for best practices"
```

### 📈 **Enhanced Performance Analysis**
```
"Use check_performance to analyze my pandas DataFrame code"
"Check this data processing code for optimization"
"Analyze performance of utils/data-processing.js"
```

### 📊 **NEW: Data Processing Analysis**
```
"Use analyze_data_processing to review my data pipeline"
"Check my pandas operations for memory efficiency"
"Analyze this ETL code for optimization opportunities"
```

---

## 🌍 Language Support

| Language | Security | Performance | Style | Syntax |
|----------|----------|-------------|-------|--------|
| **Python** | ✅ | ✅ | ✅ | ✅ |
| **JavaScript** | ✅ | ✅ | ✅ | ⚠️ |
| **TypeScript** | ✅ | ✅ | ✅ | ⚠️ |
| **Java** | ✅ | ⚠️ | ✅ | ⚠️ |
| **C/C++** | ⚠️ | ⚠️ | ✅ | ⚠️ |
| **Go, Rust, PHP, Ruby** | ⚠️ | ⚠️ | ✅ | ⚠️ |

✅ = Full support | ⚠️ = Basic support

---

## 🛠️ Installation & Configuration Options

> **💡 Choose your installation method based on your needs:**

### 📦 **Method 1: Regular Install (Most Users)**
**Use this if:** You want stable, easy setup and don't plan to modify the code.

```bash
# Install from GitHub
pip install git+https://github.com/bobbymuls/code-review-mcp.git

# Find your Python path
where python    # Windows
which python    # macOS/Linux
```

**✅ Pros:** Simple, works everywhere  
**❌ Cons:** Must reinstall to get updates (`pip uninstall code-review-mcp && pip install git+https://github.com/bobbymuls/code-review-mcp.git`)

---

### 🔧 **Method 2: Editable Install (Developers & Testers)**
**Use this if:** You want instant updates, plan to test changes, or contribute to development.

```bash
# Clone and install in development mode
git clone https://github.com/bobbymuls/code-review-mcp.git
cd code-review-mcp
pip install -e .
```

**✅ Pros:** Changes take effect immediately after Cursor restart  
**✅ Pros:** Perfect for testing latest features  
**❌ Cons:** Requires local repository

**🚀 For Rapid Development:**
- Edit `src/code_review_mcp/server.py` 
- Restart Cursor
- Changes are live instantly!

**⚡ Perfect for fast-changing MCP servers:** Since this server updates frequently with new features and bug fixes, editable install lets you pull updates with `git pull` and test them immediately.

---

### 🐍 **Method 3: Virtual Environment (Isolation)**
**Use this if:** You want to isolate dependencies or use multiple Python projects.

```bash
git clone https://github.com/bobbymuls/code-review-mcp.git
cd code-review-mcp
python -m venv venv

# Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# Choose regular or editable install
pip install -e .               # For development (recommended)
# OR
pip install git+https://github.com/bobbymuls/code-review-mcp.git  # For stable use
```

**For virtual environment, use the venv Python path in Cursor**:
- **Windows**: `"C:\\path\\to\\project\\venv\\Scripts\\python.exe"`
- **macOS/Linux**: `"/path/to/project/venv/bin/python"`

---

### 🔄 **Method 4: Conda Environment**
```bash
conda create -n code-review python=3.11
conda activate code-review
pip install git+https://github.com/bobbymuls/code-review-mcp.git

# Find conda Python path
conda info --envs
```

---

## 🚀 **Quick Setup Comparison**

| Installation Method | Commands | Update Process | Best For |
|-------------------|----------|----------------|----------|
| **Regular Install** | `pip install git+...` | Reinstall command | Regular users |
| **Editable Install** | `git clone` + `pip install -e .` | `git pull` + restart Cursor | Developers & testers |
| **Virtual Environment** | `python -m venv` + install | Depends on install method | Project isolation |
| **Conda** | `conda create` + install | Reinstall in conda env | Conda users |

---

## 🔧 Cursor Configuration Guide

### Method 1: Via Settings UI
1. Open Cursor Settings (⚙️ icon)
2. Go to `MCP & Integrations`
3. Click `+ New MCP Server`
4. Name: `code-review-mcp`
5. Command: `/full/path/to/your/python` (see examples below)
6. Args: `["-m", "code_review_mcp.server"]`

### Method 2: Direct Config File
**Windows**: `%APPDATA%\Cursor\User\globalStorage\cursor-mcp\mcp.json`  
**macOS**: `~/Library/Application Support/Cursor/User/globalStorage/cursor-mcp/mcp.json`  
**Linux**: `~/.config/Cursor/User/globalStorage/cursor-mcp/mcp.json`

```json
{
  "mcpServers": {
    "code-review-mcp": {
      "command": "/full/path/to/your/python",
      "args": ["-m", "code_review_mcp.server"],
      "env": {}
    }
  }
}
```

### Method 3: Custom Python Path
If you have multiple Python versions or virtual environments:

```json
{
  "mcpServers": {
    "code-review-mcp": {
      "command": "/full/path/to/your/python",
      "args": ["-m", "code_review_mcp.server"],
      "env": {}
    }
  }
}
```

---

## 🧪 Test Your Installation

### Quick Test
Ask Cursor: 
> "Use the review_code tool to analyze this Python code: `def test(): password='admin123'; eval('print(password)')`"

**Expected Result**: Should detect critical security issues (hardcoded password + code injection)

### File Path Test
Test relative path support:
> "Review the file src/code_review_mcp/server.py"

**Expected Result**: Should successfully analyze the server file using relative path from workspace root

### Verify Tools Available
Check Cursor's MCP settings - you should see:
- ✅ `review_code` - Complete code analysis
- ✅ `analyze_security` - Security-focused scanning
- ✅ `analyze_llm_invoke` - LLM integration critique
- ✅ `analyze_api_handling` - API calls and error handling  
- ✅ `check_performance` - Enhanced performance optimization with DataFrame analysis
- ✅ `analyze_data_processing` - **NEW**: Specialized data processing pipeline analysis

---

## 🎯 Example Use Cases

The Code Review MCP Server provides **6 specialized analysis tools**, each designed for specific code review needs:

- **`review_code`** - Comprehensive analysis combining all checks
- **`analyze_security`** - Focused security vulnerability assessment  
- **`analyze_llm_invoke`** - LLM integration and prompt engineering critique
- **`analyze_api_handling`** - API calls, timeouts, and retry strategy analysis
- **`check_performance`** - Performance bottlenecks and DataFrame optimization
- **`analyze_data_processing`** - **NEW**: Specialized data processing pipeline analysis

> 💡 **Pro Tip**: Use the specialized tools when you want focused analysis, or `review_code` for comprehensive assessment!

### 🔒 **Security Analysis** (`analyze_security`)
```python
# Before (vulnerable)
import os
import pickle

api_key = "sk-1234567890abcdef"  # ❌ Hardcoded API key detected
password = "admin123"           # ❌ Hardcoded password detected

def execute_command(user_input):
    os.system(f"ls {user_input}")  # ❌ Command injection vulnerability
    return True

def load_data(data):
    return pickle.loads(data)  # ❌ Pickle deserialization can be unsafe

# After (secure)
import os
import json
import subprocess

api_key = os.getenv("API_KEY")  # ✅ Environment variable
password = os.getenv("PASSWORD")  # ✅ Environment variable

def execute_command(user_input):
    # ✅ Safe subprocess with shell=False
    result = subprocess.run(["ls", user_input], capture_output=True, text=True)
    return result.stdout

def load_data(data):
    return json.loads(data)  # ✅ Safe JSON deserialization
```

### ⚡ **Performance Optimization** (`check_performance`)
```python
# Before (slow DataFrame operations)
import pandas as pd

# ❌ Very slow iterrows() usage
total = 0
for index, row in df.iterrows():
    total += row['value']

# ❌ Inefficient DataFrame.append() in loop
result_df = pd.DataFrame()
for item in data:
    new_row = pd.DataFrame([item])
    result_df = result_df.append(new_row)

# ❌ List concatenation with +=
items = []
for i in range(1000):
    items += [i]  # O(n²) complexity!

# After (fast)
import pandas as pd

# ✅ Vectorized operation
total = df['value'].sum()

# ✅ Collect data first, then create DataFrame
result_df = pd.DataFrame(data)

# ✅ List comprehension or extend()
items = [i for i in range(1000)]  # O(n) complexity
# or use extend(): items.extend(range(1000))
```

### 🌐 **API Handling Analysis** (`analyze_api_handling`)
```python
# Before (unreliable API calls)
import requests

def fetch_data(url):
    # ❌ No timeout - potential hanging requests
    # ❌ No status code checking
    # ❌ No error handling
    response = requests.get(url)
    return response.json()

def retry_request(url):
    while True:  # ❌ Potential infinite retry loop
        try:
            return requests.get(url).json()
        except:
            time.sleep(5)  # ❌ Fixed sleep - no exponential backoff

# After (robust API calls)
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def fetch_data(url, timeout=30):
    try:
        # ✅ Proper timeout and status checking
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # ✅ Check status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

def retry_request(url, max_retries=3):
    session = requests.Session()
    # ✅ Exponential backoff retry strategy
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed after {max_retries} retries: {e}")
        return None
```

### 🤖 **LLM Integration Analysis** (`analyze_llm_invoke`)
```python
# Before (unsafe LLM usage)
import openai

def chat_with_ai(user_input):
    # ❌ User input directly in prompt - prompt injection risk
    prompt = f"Answer this question: {user_input}"
    
    # ❌ Very high max_tokens - cost implications
    # ❌ No system message for guidance
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=8000,
        temperature=0.7
    )
    
    # ❌ No response validation or stripping
    return response.choices[0].message.content

# After (secure LLM usage)
import openai
import re

def sanitize_input(user_input):
    # ✅ Input validation and sanitization
    cleaned = re.sub(r'[^\w\s\-\.\?\!]', '', user_input)
    return cleaned[:500]  # Limit length

def chat_with_ai(user_input):
    # ✅ Sanitize user input
    safe_input = sanitize_input(user_input)
    
    # ✅ Use system message for better guidance
    # ✅ Reasonable token limits
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Answer questions concisely and safely."},
            {"role": "user", "content": f"Please answer: {safe_input}"}
        ],
        max_tokens=1000,  # ✅ Reasonable limit
        temperature=0.7
    )
    
    # ✅ Validate and strip response
    result = response.choices[0].message.content.strip()
    return result if result else "Sorry, I couldn't generate a proper response."
```

---

## 📊 Project Stats

- **🔧 Languages**: 8+ programming languages supported (Primary focus on Python)
- **🔍 Detection Rules**: 110+ built-in analysis patterns (30+ new in v0.2.1, 50+ new in v0.2.0)
- **⚡ Performance**: Analyzes 1000+ lines of code in <2 seconds (3x faster with precompiled patterns)
- **🛠️ Tools**: 6 specialized analysis tools (1 new in v0.2.1, 3 new in v0.2.0)

---

## 📋 How to Use This MCP Tool - Template Prompt

To get the most comprehensive and effective code reviews using this MCP tool, we recommend using this **hybrid methodology** that combines automated MCP tools with manual critical analysis:

### 🎯 **Optimal Hybrid Code Review Prompt Template**

```
Please conduct a comprehensive code review of [filename] using both automated MCP tools and manual critical analysis. Structure your review using this hybrid methodology:

**PHASE 1: Automated Comprehensive Scanning**
- Run MCP general code review for syntax, style, and basic patterns (use full file path like "C:\\Users\\..." for file_path parameter)
- Execute MCP security analysis for vulnerability detection (use full file path like "C:\\Users\\..." for file_path parameter)
- Perform MCP performance analysis for optimization opportunities (use full file path like "C:\\Users\\..." for file_path parameter)
- Conduct MCP API handling analysis for integration best practices (use full file path like "C:\\Users\\..." for file_path parameter)
- [Add data processing analysis if applicable for data-heavy scripts] (use full file path like "C:\\Users\\..." for file_path parameter)

**PHASE 2: Manual Critical Analysis**
- Architecture review: Design patterns, coupling, global state, code organization
- Security deep-dive: Hardcoded credentials, input validation, data exposure risks
- Business logic validation: Domain rules, calculations, data flow correctness
- Error handling strategy: Exception types, propagation, recovery patterns
- Maintainability assessment: Code complexity, testability, documentation

**PHASE 3: Synthesis & Cross-Validation**
- Compare automated vs manual findings
- Identify issues caught by only one method
- Validate and prioritize by severity and business impact
- Note any false positives or tool limitations

**PHASE 4: Actionable Recommendations**
- Immediate fixes: Specific line-level changes
- Strategic improvements: Architecture and design enhancements  
- Implementation priority: Critical → High → Medium → Low
- Provide code examples for key improvements

Please ensure you leverage the complementary strengths of both approaches: automated tools for comprehensive coverage and precise identification, manual analysis for context, domain understanding, and critical security/architecture issues that tools typically miss.
```

### 🎯 **Context-Specific Variations**

**For Data Processing Scripts:**
```
"Please conduct a comprehensive code review of [filename] using both automated MCP tools and manual critical analysis. This is a data processing script that handles API calls, performs [specific domain] calculations, and processes [type] metrics. Pay special attention to data validation, API security, performance with large datasets, and business logic correctness for [domain-specific] calculations."
```

**For Web Applications:**
```
"Please conduct a comprehensive code review of [filename] using both automated MCP tools and manual critical analysis. This is a web application component that handles [functionality]. Focus particularly on security vulnerabilities, input validation, authentication/authorization, and web-specific performance concerns."
```

**For API Integration Code:**
```
"Please conduct a comprehensive code review of [filename] using both automated MCP tools and manual critical analysis. This code integrates with external APIs for [purpose]. Emphasize API security, error handling, retry logic, rate limiting, and data transformation accuracy."
```

### 🏆 **Why This Hybrid Approach Works**

| Aspect | Automated Tools | Manual Analysis | Combined Benefit |
|--------|----------------|-----------------|------------------|
| **Coverage** | Comprehensive scanning | Deep, contextual | Complete assessment |
| **Precision** | Exact line numbers | Strategic insights | Actionable specificity |
| **Speed** | Instant analysis | Thoughtful review | Efficient thoroughness |
| **Expertise** | Consistent rules | Domain knowledge | Balanced perspective |

### 📝 **Best Practices**

1. **Always specify the code type/domain** in your prompt for better context
2. **Request both immediate fixes and strategic improvements**
3. **Ask for cross-validation** between automated and manual findings
4. **Emphasize areas of particular concern** based on the code's purpose
5. **Request code examples** for recommended improvements

---

## 🤝 Contributing

We love contributions! Here's how to get started:

1. **🍴 Fork** the repository to your GitHub account
2. **📥 Clone** your fork: `git clone https://github.com/YOUR_USERNAME/code-review-mcp.git`
3. **🌿 Create** a feature branch: `git checkout -b my-feature`
4. **✨ Make** your changes and add tests
5. **✅ Test**: `pytest tests/`
6. **📝 Commit**: `git commit -am 'Add amazing feature'`
7. **🚀 Push** to your fork: `git push origin my-feature`
8. **🎯 Create** a Pull Request from your fork to the main repository

**Areas we need help with:**
- Adding support for more programming languages
- Improving detection accuracy
- Adding new analysis rules
- Writing documentation
- Creating examples

---

## 📝 Changelog

### v0.2.1 (2025-09-18) - Enhanced Analysis Patterns
#### 🎯 **New Analysis Tool**
- **📊 `analyze_data_processing`** - Specialized analysis for data processing pipelines, pandas operations, and memory optimization

#### 🔧 **Enhanced Detection Patterns**
- **Enhanced Security Patterns** - Better detection of configuration-based secrets, hardcoded credentials, and internal service URLs
- **Enhanced Performance Patterns** - Advanced pandas-specific optimizations including chained operations, DataFrame copies, and memory usage
- **Enhanced API Patterns** - Improved detection of pagination issues, rate limiting problems, and service-specific API calls
- **30+ new analysis patterns** specifically targeting data engineering and processing workflows

#### 🐛 **Bug Fixes & Improvements**
- Fixed security pattern matching for configuration objects and API keys
- Improved DataFrame operation detection for complex data processing pipelines
- Enhanced error handling for API client operations
- Better detection of input validation issues

### v0.2.0 (2025-09-17) - Major Feature Release
#### 🎯 **New Specialized Analysis Tools**
- **🤖 `analyze_llm_invoke`** - LLM integration critique with prompt security and cost optimization
- **🌐 `analyze_api_handling`** - API calls analysis with error handling and timeout validation
- **📈 Enhanced `check_performance`** - Now includes DataFrame operations and data science optimizations

#### 🔧 **Technical Improvements**
- **50+ new analysis patterns** for data science workflows
- **Precompiled regex patterns** for 3x performance improvement
- **Pydantic v2 compatibility** with modern field validators
- **Comprehensive error handling** with custom exception classes
- **Full type annotations** throughout the codebase
- **Enhanced logging** with structured error reporting

#### 🏗️ **Architecture Changes**
- Modular tool design replacing generic `analyze_data_science`
- Optimized pattern matching with `@lru_cache` decorators
- Improved workspace detection and file path resolution
- Better categorization of issues by domain expertise

### v0.1.0 (2025-09-16) - Initial Release
- Basic code review functionality
- Security, performance, and style analysis
- Support for Python and JavaScript
- MCP protocol integration

---

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.
