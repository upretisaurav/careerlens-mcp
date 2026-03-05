"""
CareerLens MCP Server
─────────────────────
Exposes 5 career intelligence tools via the Model Context Protocol.

Usage (stdio — Claude Desktop):
  python mcp_server.py

Usage (SSE — remote / web clients):
  fastmcp run mcp_server.py --transport sse --port 8001 --host 0.0.0.0

Claude Desktop config (~/.config/claude/claude_desktop_config.json):
  {
    "mcpServers": {
      "careerlens": {
        "command": "python",
        "args": ["/absolute/path/to/server/mcp_server.py"],
        "env": {
          "JSEARCH_API_KEY": "your_key_here",
          "ANTHROPIC_API_KEY": "your_key_here"
        }
      }
    }
  }
"""

from fastmcp import FastMCP

from tools import (
    analyze_skill_demand,
    find_jobs,
    get_career_report,
    get_salary_benchmark,
    score_resume_fit,
)

# ── Create the MCP server ──────────────────────────────────────────────────────
mcp = FastMCP(
    name="CareerLens",
    instructions="""
You are CareerLens, a career intelligence assistant backed by real-time job market data.

You have access to 5 tools:
1. get_salary_benchmark  — Market salary data for any role/location
2. find_jobs             — Live job listings matching a role and skill set
3. analyze_skill_demand  — Relative demand ranking of technologies/skills
4. score_resume_fit      — ATS compatibility score for a resume vs job description
5. get_career_report     — Full career intelligence report (orchestrates tools 1-3)

Always use tools to back up your answers with real data. Be direct and actionable.
When a user asks a career question, pick the most relevant tool(s) and provide
clear, data-driven insights.
""",
)


# ── Register tools ─────────────────────────────────────────────────────────────


@mcp.tool()
async def salary_benchmark(
    role: str,
    location: str = "United States",
    company: str = None,
    level: str = None,
) -> dict:
    """
    Get real-time salary benchmarks for a job role.

    Pulls data from live job listings (LinkedIn, Indeed, Glassdoor) and
    computes median, 25th, and 75th percentile salaries.

    Args:
        role:     Job title (e.g. "Software Engineer", "Product Manager").
        location: City, state, or country (default: "United States").
        company:  Optional — narrow to a specific company.
        level:    Optional — seniority level (e.g. "Senior", "Staff", "L5").
    """
    return await get_salary_benchmark(role=role, location=location, company=company, level=level)


@mcp.tool()
async def job_search(
    role: str,
    skills: list[str] = None,
    location: str = "United States",
    remote: bool = False,
    max_results: int = 10,
) -> dict:
    """
    Search for live job openings that match a role and skill set.

    Queries LinkedIn, Indeed, Glassdoor, and Google Jobs in real time.

    Args:
        role:        Job title to search (e.g. "Backend Engineer").
        skills:      Skills to filter by (e.g. ["Python", "FastAPI", "Docker"]).
        location:    Target location (default: "United States").
        remote:      Set to true for remote-only results.
        max_results: Number of jobs to return (1-10).
    """
    return await find_jobs(
        role=role, skills=skills or [], location=location, remote=remote, max_results=max_results
    )


@mcp.tool()
async def skill_demand(
    skills: list[str],
    location: str = "United States",
) -> dict:
    """
    Analyse the job-market demand for a list of skills or technologies.

    Runs parallel market queries and returns a demand score + trend label
    for each skill (Hot / Growing / Stable / Declining).

    Args:
        skills:   Technologies or skills to compare (e.g. ["React", "Vue", "Angular"]).
        location: Market to query (default: "United States").
    """
    return await analyze_skill_demand(skills=skills, location=location)


@mcp.tool()
def resume_fit_score(
    resume_text: str,
    job_description: str,
) -> dict:
    """
    Score how well a resume matches a job description (ATS compatibility check).

    Performs keyword analysis, skill gap detection, and readability scoring.
    Returns a 0-100 ATS score with specific improvement suggestions.

    Args:
        resume_text:     Paste your resume as plain text.
        job_description: Paste the target job description.
    """
    return score_resume_fit(resume_text=resume_text, job_description=job_description)


@mcp.tool()
async def career_report(
    role: str,
    skills: list[str],
    location: str = "United States",
    current_salary: float = None,
    years_of_experience: int = None,
    remote: bool = False,
) -> dict:
    """
    Generate a full career intelligence report in one call.

    Combines salary benchmarks, live job matches, and skill demand analysis
    into an actionable briefing. Answers: Am I underpaid? What's hiring?
    Which of my skills matter most right now?

    Args:
        role:                 Your current or target job title.
        skills:               Your tech skills (e.g. ["Python", "React", "AWS"]).
        location:             Your target market (default: "United States").
        current_salary:       Your current annual salary in USD (for gap analysis).
        years_of_experience:  Total years of professional experience.
        remote:               Include remote jobs (default: False).
    """
    return await get_career_report(
        role=role,
        skills=skills,
        location=location,
        current_salary=current_salary,
        years_of_experience=years_of_experience,
        remote=remote,
    )


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Default: stdio transport (for Claude Desktop)
    mcp.run()
