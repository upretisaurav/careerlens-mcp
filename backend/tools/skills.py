"""
Tool 3: analyze_skill_demand
Runs parallel job-market queries for each skill to measure relative demand.
Returns a ranked list with demand scores, trend labels, and average salary signal.
"""

import asyncio

import httpx

from core.config import JSEARCH_BASE_URL, JSEARCH_HEADERS

TREND_THRESHOLDS = {
    "Hot": 80,  # top 20%
    "Growing": 55,  # above average
    "Stable": 30,  # average
    "Declining": 0,  # bottom tier
}


def _score_to_trend(score: float) -> str:
    for label, threshold in TREND_THRESHOLDS.items():
        if score >= threshold:
            return label
    return "Declining"


async def _query_skill(client: httpx.AsyncClient, skill: str, location: str) -> dict:
    """Run a single skill query and return result count + avg salary signal."""
    params = {
        "query": f"{skill} developer engineer",
        "location": location,
        "num_pages": "1",
        "employment_types": "FULLTIME",
    }
    try:
        resp = await client.get(
            f"{JSEARCH_BASE_URL}/search",
            headers=JSEARCH_HEADERS,
            params=params,
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()
        jobs = data.get("data", [])

        # Count jobs and extract salary signals
        count = len(jobs)
        salaries = []
        for job in jobs:
            lo = job.get("job_min_salary")
            hi = job.get("job_max_salary")
            period = job.get("job_salary_period")
            if lo and hi:
                try:
                    mid = (float(lo) + float(hi)) / 2
                    if period == "HOUR":
                        mid *= 2080
                    elif period == "MONTH":
                        mid *= 12
                    if 25_000 < mid < 1_000_000:
                        salaries.append(mid)
                except (TypeError, ValueError):
                    pass

        avg_salary = int(sum(salaries) / len(salaries)) if salaries else None
        return {"skill": skill, "job_count": count, "avg_salary": avg_salary}

    except Exception:
        return {"skill": skill, "job_count": 0, "avg_salary": None}


async def analyze_skill_demand(
    skills: list[str],
    location: str = "United States",
) -> dict:
    """
    Measure the current job-market demand for a list of skills.

    Runs parallel searches for each skill and computes a relative demand index.
    Useful for comparing technologies (e.g. React vs Vue vs Angular) or
    checking if your current stack is trending up or cooling down.

    Args:
        skills:   List of skills/technologies to analyse (e.g. ["React", "Vue", "Svelte"]).
        location: Market to query (default "United States").

    Returns:
        Ranked list of skills with demand scores, trend labels, and salary signals.
    """
    if not skills:
        return {"error": "Please provide at least one skill to analyse."}

    # Cap at 10 skills to stay within free-tier rate limits
    skills = skills[:10]

    async with httpx.AsyncClient() as client:
        tasks = [_query_skill(client, skill, location) for skill in skills]
        results = await asyncio.gather(*tasks)

    # Normalise job counts to a 0-100 demand score
    counts = [r["job_count"] for r in results]
    max_count = max(counts) if counts else 1

    ranked = []
    for r in results:
        raw_score = (r["job_count"] / max_count) * 100 if max_count else 0
        score = round(raw_score, 1)
        ranked.append(
            {
                "skill": r["skill"],
                "demand_score": score,  # 0-100 relative index
                "job_listings_found": r["job_count"],
                "avg_salary": f"${r['avg_salary']:,}" if r["avg_salary"] else "N/A",
                "trend": _score_to_trend(score),
            }
        )

    # Sort by demand score descending
    ranked.sort(key=lambda x: x["demand_score"], reverse=True)

    # Summary insights
    hot_skills = [s["skill"] for s in ranked if "Hot" in s["trend"] or "Growing" in s["trend"]]
    declining = [s["skill"] for s in ranked if "Declining" in s["trend"]]

    return {
        "location": location,
        "skills_analysed": len(ranked),
        "ranking": ranked,
        "insights": {
            "highest_demand": ranked[0]["skill"] if ranked else None,
            "lowest_demand": ranked[-1]["skill"] if ranked else None,
            "hot_or_growing": hot_skills,
            "potentially_declining": declining,
        },
        "data_source": "Live job listings via JSearch (LinkedIn, Indeed, Glassdoor)",
        "note": "Demand score is relative within your queried skill set, not an absolute market index.",
    }
