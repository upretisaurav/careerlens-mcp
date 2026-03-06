# ⚡ CareerLens MCP

> Real-time career intelligence as an MCP server. Ask Claude if you're underpaid, find live job listings, benchmark your skills, and score your resume — all in one chat.

## **[Live Demo →](https://careerlens-mcp.vercel.app/)** &nbsp;|&nbsp; **[Backend API Docs →](https://backend-production-17b1d.up.railway.app/docs)**

## What It Does

CareerLens exposes 5 career intelligence tools via the **Model Context Protocol (MCP)**. Claude decides which tools to call based on your question — you just chat.

| Tool               | What it answers                                        |
| ------------------ | ------------------------------------------------------ |
| `salary_benchmark` | What should I be earning for this role?                |
| `job_search`       | What's actually hiring for my skills right now?        |
| `skill_demand`     | Is my tech stack trending up or dying?                 |
| `resume_fit_score` | How well does my resume match this job?                |
| `career_report`    | Full briefing: salary gap + live jobs + skill rankings |

**Bonus features:**

- 📄 Upload your CV (PDF) → auto-extracts your profile
- 🔗 Paste your LinkedIn URL → auto-fills your profile

---

## Architecture

```
React Frontend (Vercel)
        │
        │  POST /chat — SSE streaming
        ▼
FastAPI Bridge Server (Railway)
        │
        ├── Anthropic SDK (Claude Sonnet)
        │         │  tool_use (agentic loop)
        │         ▼
        └── tools/*.py ──► JSearch API (LinkedIn, Indeed, Glassdoor)
                         ──► Pure Python (resume ATS scoring)

Claude Desktop (optional)
        │  stdio / MCP protocol
        ▼
FastMCP Server ──► same tools/*.py
```

The MCP server and the API server **share the same tool implementations** in `server/tools/`. Zero duplication.

---

## Tech Stack

| Layer           | Tech                                      |
| --------------- | ----------------------------------------- |
| MCP Server      | Python + FastMCP                          |
| API Server      | Python + FastAPI + SSE streaming          |
| Job/Salary Data | JSearch API (LinkedIn, Indeed, Glassdoor) |
| AI              | Claude Sonnet via Anthropic SDK           |
| Frontend        | React + Tailwind CSS                      |
| Backend Deploy  | Railway                                   |
| Frontend Deploy | Vercel                                    |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- [JSearch API key](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) (free tier)
- [Anthropic API key](https://console.anthropic.com)

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/careerlens-mcp.git
cd careerlens-mcp
```

### 2. Backend setup

```bash
cd server
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your API keys
uvicorn api_server:app --reload --port 8000
```

### 3. Frontend setup

```bash
cd client
npm install
cp .env.example .env.local
# .env.local already points to localhost:8000
npm start
```

Open **http://localhost:3000** — fill in your profile and start chatting.

### 4. Claude Desktop setup (optional)

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "careerlens": {
      "command": "python",
      "args": ["/absolute/path/to/careerlens-mcp/server/mcp_server.py"],
      "env": {
        "JSEARCH_API_KEY": "your_key",
        "ANTHROPIC_API_KEY": "your_key"
      }
    }
  }
}
```

---

## Deploy Your Own

### Backend → Railway

1. Create new project on [railway.app](https://railway.app)
2. Connect your GitHub repo, set **Root Directory** to `server`
3. Add environment variables: `JSEARCH_API_KEY`, `ANTHROPIC_API_KEY`
4. Railway auto-deploys from `Procfile`

### Frontend → Vercel

1. Import repo on [vercel.com](https://vercel.com)
2. Set **Root Directory** to `client`
3. Add environment variable: `REACT_APP_API_URL=https://your-app.railway.app`
4. Deploy

---

## Project Structure

```
careerlens-mcp/
├── server/
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── salary.py          # Tool 1: Salary benchmarks
│   │   ├── jobs.py            # Tool 2: Live job search
│   │   ├── skills.py          # Tool 3: Skill demand analysis
│   │   ├── resume.py          # Tool 4: ATS resume scoring
│   │   ├── report.py          # Tool 5: Full career report
│   │   ├── cv_parser.py       # CV PDF parsing
│   │   └── linkedin_parser.py # LinkedIn profile scraping
│   ├── api_server.py          # FastAPI + SSE bridge for frontend
│   ├── mcp_server.py          # FastMCP server for Claude Desktop
│   ├── config.py
│   ├── requirements.txt
│   ├── Procfile
│   └── railway.toml
├── client/
│   ├── src/
│   │   ├── App.js             # Full chat UI + result cards
│   │   └── App.css            # Dark bold theme
│   ├── vercel.json
│   └── package.json
├── .gitignore
└── README.md
```

---

## Built With

Built in a weekend as a demonstration of the **Model Context Protocol (MCP)** — the open standard for connecting AI models to external tools and data sources.

---

## License

MIT — do whatever you want with it.
