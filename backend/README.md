# CareerLens MCP — Backend

Real-time career intelligence as an MCP server. Salary benchmarks, live job search, skill demand analysis, resume scoring — all callable by Claude.

---

## Quick Start

### 1. Install dependencies
```bash
cd server
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env and add your keys:
#   JSEARCH_API_KEY  → https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch (free tier)
#   ANTHROPIC_API_KEY → https://console.anthropic.com
```

### 3a. Run the API server (for the React frontend)
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```
Test it: http://localhost:8000/health

### 3b. Run the MCP server (for Claude Desktop)
```bash
python mcp_server.py
```

---

## Claude Desktop Setup

Add to `~/.config/claude/claude_desktop_config.json` (macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "careerlens": {
      "command": "python",
      "args": ["/absolute/path/to/careerlens-mcp/server/mcp_server.py"],
      "env": {
        "JSEARCH_API_KEY": "your_jsearch_key",
        "ANTHROPIC_API_KEY": "your_anthropic_key"
      }
    }
  }
}
```

Restart Claude Desktop. You'll see the CareerLens tools appear in the toolbar.

---

## The 5 Tools

| Tool | What it does | Data source |
|---|---|---|
| `salary_benchmark` | Median + p25/p75 for any role/location | Live job listings |
| `job_search` | Real job listings matching role + skills | LinkedIn, Indeed, Glassdoor |
| `skill_demand` | Demand score + trend per skill | Live job listing volume |
| `resume_fit_score` | ATS score (0-100) + improvement tips | Algorithmic (no API needed) |
| `career_report` | Full briefing: salary gap + jobs + skills | All of the above |

---

## REST API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/chat` | Agentic Claude chat with tool-use (SSE streaming) |
| `POST` | `/tools/salary` | Direct salary benchmark call |
| `POST` | `/tools/jobs` | Direct job search call |
| `POST` | `/tools/skills` | Direct skill demand call |
| `POST` | `/tools/resume` | Direct resume scoring call |
| `POST` | `/tools/report` | Direct career report call |
| `GET`  | `/health` | Health check |

Interactive API docs: http://localhost:8000/docs

---

## Architecture

```
React Frontend
      │
      │  POST /chat (SSE stream)
      ▼
FastAPI (api_server.py)
      │
      ├── Anthropic SDK (Claude claude-sonnet-4-20250514)
      │         │  tool_use
      │         ▼
      └── Tools (tools/*.py) ──► JSearch API (salary, jobs, skills)
                               ──► Pure Python (resume scoring)

Claude Desktop
      │
      │  stdio / SSE
      ▼
FastMCP (mcp_server.py) ──► same tools/*.py
```

The MCP server and the API server share the **same tool implementations** in `tools/`. Zero duplication.
