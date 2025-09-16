# Distribution Strategy for Code Review MCP Server

## 1. PyPI Distribution (Recommended)

### Setup PyPI Account
1. Create account at https://pypi.org/
2. Set up API token for GitHub Actions
3. Add token as GitHub secret: `PYPI_API_TOKEN`

### Automatic Publishing
- Already configured in `.github/workflows/publish.yml`
- Publishes automatically when you create a release/tag
- Users can install with: `pip install code-review-mcp`

### Create a Release
```bash
git tag v0.1.0
git push origin v0.1.0
```

## 2. GitHub Distribution (Current)

### Direct Installation
```bash
pip install git+https://github.com/bobbymuls/code-review-mcp.git
```

### Manual Installation
```bash
git clone https://github.com/bobbymuls/code-review-mcp.git
cd code-review-mcp
pip install -e .
```

## 3. Smithery AI Registry

### Submission Process
1. Visit https://smithery.ai/
2. Submit your GitHub repository
3. Include description and usage instructions
4. Benefits: Discoverability in MCP community

## 4. Community Sharing

### MCP Servers Repository
- Consider submitting to: https://github.com/modelcontextprotocol/servers
- Official community registry
- High visibility for MCP developers

## Usage in Cursor

### Configuration
Add to Cursor settings:
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

### Requirements
- Python 3.8+
- Virtual environment recommended
- MCP server runs locally alongside Cursor
