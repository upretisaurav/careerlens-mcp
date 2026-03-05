"""
Tool 5: get_career_report
Orchestrates salary benchmark + job search + skill demand into one
comprehensive career intelligence report. The flagship tool.
"""

import asyncio
from typing import Optional

from tools.jobs import find_jobs
from tools.salary import get_salary_benchmark
from tools.skills import analyze_skill_demand


def _salary_gap_analysis(current_salary: Optional[float], market_median: Optional[int]) -> dict:
    """Compute how current salary compares to market median."""
    if not current_salary or not market_median:
        return {"available": False}

    gap = market_median - current_salary
    gap_pct = (gap / market_median) * 100

    if gap_pct > 15:
        verdict = "⬇️ Underpaid"
        message = (
            f"You appear to be underpaid by ~${abs(gap):,.0f}/yr ({abs(gap_pct):.0f}%). "
            "Market data suggests strong grounds for a salary negotiation."
        )
    elif gap_pct < -15:
        verdict = "⬆️ Above Market"
        message = (
            f"You're earning ~${abs(gap):,.0f}/yr ({abs(gap_pct):.0f}%) above the market median. "
            "Focus on growing scope and title rather than chasing a salary bump elsewhere."
        )
    else:
        verdict = "At Market Rate"
        message = (
            f"Your salary is within ±15% of the market median (${market_median:,}). "
            "You're fairly compensated. Use skill demand data to plan your next level-up."
        )

    return {
        "available": True,
        "verdict": verdict,
        "message": message,
        "your_salary": f"${current_salary:,.0f}",
        "market_median": f"${market_median:,}",
        "gap_amount": f"${abs(gap):,.0f}",
        "gap_percentage": f"{abs(gap_pct):.0f}%",
        "direction": "above" if gap < 0 else "below",
    }


async def get_career_report(
    role: str,
    skills: list[str],
    location: str = "United States",
    current_salary: Optional[float] = None,
    years_of_experience: Optional[int] = None,
    remote: bool = False,
) -> dict:
    """
    Generate a comprehensive career intelligence report.

    Combines real-time salary benchmarks, live job market data, and
    skill demand analysis into one actionable career briefing.
    Answers: Am I underpaid? What's hiring? Which of my skills matter most?

    Args:
        role:                 Your current or target job title.
        skills:               Your tech skills (e.g. ["Python", "React", "AWS"]).
        location:             Your target job market (default "United States").
        current_salary:       Your current annual salary in USD (optional, for gap analysis).
        years_of_experience:  Years of total professional experience (optional).
        remote:               Whether to include remote jobs (default False).

    Returns:
        Full career intelligence report with salary gap, top jobs, skill rankings,
        and a personalised action plan.
    """

    # Run salary, jobs, and skill demand in parallel for speed
    salary_task = get_salary_benchmark(role=role, location=location)
    jobs_task = find_jobs(role=role, skills=skills, location=location, remote=remote, max_results=5)
    skills_task = analyze_skill_demand(skills=skills, location=location)

    salary_data, jobs_data, skills_data = await asyncio.gather(salary_task, jobs_task, skills_task)

    # Salary gap analysis
    market_median = salary_data.get("raw_median") if "error" not in salary_data else None
    gap_analysis = _salary_gap_analysis(current_salary, market_median)

    # Top 3 jobs
    top_jobs = jobs_data.get("jobs", [])[:3] if "error" not in jobs_data else []

    # Skill ranking
    skill_ranking = skills_data.get("ranking", []) if "error" not in skills_data else []
    hot_skills = [
        s for s in skill_ranking if "Hot" in s.get("trend", "") or "Growing" in s.get("trend", "")
    ]
    weak_skills = [s for s in skill_ranking if "Declining" in s.get("trend", "")]

    # Build action plan
    actions = []

    if gap_analysis.get("available") and gap_analysis.get("direction") == "below":
        actions.append(
            f"[MONEY] Negotiate or explore — {gap_analysis['verdict']}: {gap_analysis['message']}"
        )

    if hot_skills:
        top_hot = hot_skills[0]["skill"]
        actions.append(
            f"[FIRE] Double down on {top_hot} — it's your highest-demand skill right now. "
            "Lead with it in your resume and interviews."
        )

    if weak_skills:
        weak_names = [s["skill"] for s in weak_skills[:2]]
        actions.append(
            f"[WARNING] Low demand detected for: {', '.join(weak_names)}. "
            "Consider pairing these with higher-demand technologies in your projects."
        )

    if top_jobs:
        actions.append(
            f"[JOBS] {len(top_jobs)} strong job matches found. Review them below and apply to the best fit."
        )

    if (
        years_of_experience
        and years_of_experience >= 5
        and not any("senior" in role.lower() for role in [role])
    ):
        actions.append(
            "🎯 With your experience level, consider targeting Senior or Staff-level titles "
            "which typically come with 20-40% higher compensation."
        )

    return {
        "report_for": {
            "role": role,
            "location": location,
            "years_of_experience": years_of_experience,
            "skills": skills,
        },
        "salary_intelligence": {
            **salary_data.get("salary_stats", {}),
            "sample_size": salary_data.get("sample_size", 0),
        }
        if "error" not in salary_data
        else {"error": salary_data["error"]},
        "salary_gap_analysis": gap_analysis,
        "top_job_matches": top_jobs,
        "skill_demand_ranking": skill_ranking,
        "skill_insights": skills_data.get("insights", {}),
        "action_plan": actions
        if actions
        else [
            "Your career metrics look healthy! Focus on building in public and raising your visibility."
        ],
        "data_freshness": "Real-time (pulled just now from live job boards)",
    }
