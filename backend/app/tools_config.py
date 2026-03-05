"""Tool metadata and system prompt for Claude interactions."""

CLAUDE_TOOLS = [
    {
        "name": "salary_benchmark",
        "description": "Get real-time salary benchmarks for a job role from live job listings (LinkedIn, Indeed, Glassdoor). Returns median, p25, p75 salaries.",
        "input_schema": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "description": "Job title (e.g. 'Software Engineer')"},
                "location": {
                    "type": "string",
                    "description": "City, state, or country",
                    "default": "United States",
                },
                "company": {
                    "type": "string",
                    "description": "Optional: narrow to a specific company",
                },
                "level": {
                    "type": "string",
                    "description": "Optional: seniority level (e.g. 'Senior', 'L5')",
                },
            },
            "required": ["role"],
        },
    },
    {
        "name": "job_search",
        "description": "Search for live job openings across LinkedIn, Indeed, Glassdoor, and Google Jobs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "description": "Job title to search for"},
                "skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Skills to match",
                },
                "location": {
                    "type": "string",
                    "description": "Target location",
                    "default": "United States",
                },
                "remote": {
                    "type": "boolean",
                    "description": "Remote-only results",
                    "default": False,
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results (1-10)",
                    "default": 10,
                },
            },
            "required": ["role"],
        },
    },
    {
        "name": "skill_demand",
        "description": "Measure job-market demand for a list of skills. Returns demand scores and trend labels.",
        "input_schema": {
            "type": "object",
            "properties": {
                "skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Skills to analyse",
                },
                "location": {
                    "type": "string",
                    "description": "Market to query",
                    "default": "United States",
                },
            },
            "required": ["skills"],
        },
    },
    {
        "name": "resume_fit_score",
        "description": "Score a resume against a job description. Returns ATS score (0-100) and improvement tips.",
        "input_schema": {
            "type": "object",
            "properties": {
                "resume_text": {"type": "string", "description": "Resume content as plain text"},
                "job_description": {"type": "string", "description": "Target job description"},
            },
            "required": ["resume_text", "job_description"],
        },
    },
    {
        "name": "career_report",
        "description": "Full career intelligence report. Combines salary benchmarks, live job matches, and skill demand in one call.",
        "input_schema": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "description": "Current or target job title"},
                "skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Your tech skills",
                },
                "location": {
                    "type": "string",
                    "description": "Target market",
                    "default": "United States",
                },
                "current_salary": {"type": "number", "description": "Current annual salary in USD"},
                "years_of_experience": {
                    "type": "integer",
                    "description": "Total years of experience",
                },
                "remote": {
                    "type": "boolean",
                    "description": "Include remote jobs",
                    "default": False,
                },
            },
            "required": ["role", "skills"],
        },
    },
]

SYSTEM_PROMPT = """You are CareerLens, a sharp career intelligence assistant powered by real-time job market data.

You have 5 tools:
- salary_benchmark: Live salary data for any role/location
- job_search: Real job listings right now
- skill_demand: Which technologies are actually in demand
- resume_fit_score: ATS scoring for resume vs job description
- career_report: Full career report (calls salary + jobs + skills in one shot)

Be concise, data-driven, and actionable. Always use tools to ground your answers.
When presenting data, highlight the most important insight first.
Format numbers clearly. Do not use any emojis in your text responses. Keep all output clean plain text with Markdown formatting only."""
