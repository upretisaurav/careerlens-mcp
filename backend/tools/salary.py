"""
Tool 1: get_salary_benchmark
Pulls real salary ranges for a given role/location by querying live job listings
via JSearch (LinkedIn, Indeed, Glassdoor data) and computing statistical benchmarks.
"""

import statistics
from typing import Optional

import httpx

from core.config import JSEARCH_BASE_URL, JSEARCH_HEADERS


def _extract_salary_numbers(min_salary, max_salary, period) -> Optional[tuple[float, float]]:
    """Normalise raw salary fields to annual USD figures."""
    if min_salary is None or max_salary is None:
        return None

    try:
        lo = float(min_salary)
        hi = float(max_salary)
    except (TypeError, ValueError):
        return None

    # Normalise to yearly
    if period == "HOUR":
        lo, hi = lo * 2080, hi * 2080  # 40 hrs × 52 weeks
    elif period == "MONTH":
        lo, hi = lo * 12, hi * 12
    elif period == "WEEK":
        lo, hi = lo * 52, hi * 52

    # Sanity-check: ignore obviously bad values
    if lo < 20_000 or hi > 1_500_000:
        return None

    return lo, hi


async def get_salary_benchmark(
    role: str,
    location: str = "United States",
    company: Optional[str] = None,
    level: Optional[str] = None,
) -> dict:
    """
    Fetch real-time salary benchmarks for a given role and location.

    Queries live job listings (LinkedIn, Indeed, Glassdoor) to compute
    salary statistics: median, 25th percentile, 75th percentile, and range.

    Args:
        role:     Job title to look up (e.g. "Software Engineer", "Data Scientist").
        location: City, state, or country (default "United States").
        company:  Optional — narrow results to a specific company.
        level:    Optional — seniority hint (e.g. "Senior", "L5", "Staff").

    Returns:
        Dictionary with salary statistics and source job sample.
    """
    query = role
    if level:
        query = f"{level} {query}"
    if company:
        query = f"{query} at {company}"

    params = {
        "query": query,
        "location": location,
        "num_pages": "3",  # 30 listings total
        "employment_types": "FULLTIME",
    }

    salaries: list[float] = []
    sample_jobs: list[dict] = []

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{JSEARCH_BASE_URL}/search",
                headers=JSEARCH_HEADERS,
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

        jobs = data.get("data", [])

        for job in jobs:
            pair = _extract_salary_numbers(
                job.get("job_min_salary"),
                job.get("job_max_salary"),
                job.get("job_salary_period"),
            )
            if pair:
                lo, hi = pair
                mid = (lo + hi) / 2
                salaries.append(mid)

                if len(sample_jobs) < 5:
                    sample_jobs.append(
                        {
                            "title": job.get("job_title"),
                            "company": job.get("employer_name"),
                            "location": job.get("job_city") or job.get("job_country"),
                            "salary_range": f"${lo:,.0f} – ${hi:,.0f}",
                            "url": job.get("job_apply_link") or job.get("job_google_link"),
                        }
                    )

    except httpx.HTTPStatusError as e:
        return {
            "error": f"JSearch API error: {e.response.status_code}",
            "hint": "Check your JSEARCH_API_KEY in .env",
        }
    except Exception as e:
        return {"error": str(e)}

    if not salaries:
        return {
            "role": role,
            "location": location,
            "message": "No salary data found for this query. Try a broader role title or location.",
            "tip": "Example: role='Software Engineer', location='United States'",
        }

    salaries_sorted = sorted(salaries)
    n = len(salaries_sorted)
    p25 = salaries_sorted[n // 4]
    p75 = salaries_sorted[(3 * n) // 4]
    median = statistics.median(salaries_sorted)
    mean = statistics.mean(salaries_sorted)

    return {
        "role": role,
        "location": location,
        "company": company,
        "level": level,
        "sample_size": n,
        "salary_stats": {
            "median": f"${median:,.0f}",
            "mean": f"${mean:,.0f}",
            "p25_low_end": f"${p25:,.0f}",
            "p75_high_end": f"${p75:,.0f}",
            "range": f"${min(salaries_sorted):,.0f} – ${max(salaries_sorted):,.0f}",
        },
        "raw_median": round(median),
        "sample_jobs": sample_jobs,
        "data_source": "Live job listings (LinkedIn, Indeed, Glassdoor via JSearch)",
    }
