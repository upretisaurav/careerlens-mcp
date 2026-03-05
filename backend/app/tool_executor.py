"""Tool execution dispatch for CareerLens tools."""

import json
from typing import Any

from tools import (
    analyze_skill_demand,
    find_jobs,
    get_career_report,
    get_salary_benchmark,
    score_resume_fit,
)


async def execute_tool(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Route a tool call to the correct implementation and return JSON string."""
    try:
        if tool_name == "salary_benchmark":
            result = await get_salary_benchmark(**tool_input)
        elif tool_name == "job_search":
            result = await find_jobs(**tool_input)
        elif tool_name == "skill_demand":
            result = await analyze_skill_demand(**tool_input)
        elif tool_name == "resume_fit_score":
            result = score_resume_fit(**tool_input)
        elif tool_name == "career_report":
            result = await get_career_report(**tool_input)
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
    except Exception as exc:
        result = {"error": f"Tool execution failed: {str(exc)}"}

    return json.dumps(result, indent=2)
