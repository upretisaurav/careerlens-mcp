"""
Tool 2: find_jobs
Searches live job listings across LinkedIn, Indeed, Glassdoor, and Google Jobs
via JSearch API. Returns enriched job cards with salary, skills, and apply links.
"""

from typing import Optional

import httpx

from core.config import JSEARCH_BASE_URL, JSEARCH_HEADERS


def _build_query(role: str, skills: list[str], remote: bool) -> str:
    """Build a smart JSearch query string."""
    parts = [role]
    if skills:
        # Include top 3 skills in the query for relevance
        parts.extend(skills[:3])
    if remote:
        parts.append("remote")
    return " ".join(parts)


def _format_job(job: dict) -> dict:
    """Extract and clean up relevant fields from a raw JSearch job object."""
    # Salary
    lo = job.get("job_min_salary")
    hi = job.get("job_max_salary")
    period = job.get("job_salary_period")
    if lo and hi:
        if period == "HOUR":
            salary_str = f"${lo:.0f}–${hi:.0f}/hr"
        elif period == "MONTH":
            salary_str = f"${lo:,.0f}–${hi:,.0f}/mo"
        else:
            salary_str = f"${lo:,.0f}–${hi:,.0f}/yr"
    else:
        salary_str = "Not disclosed"

    # Location
    city = job.get("job_city", "")
    state = job.get("job_state", "")
    country = job.get("job_country", "")
    is_remote = job.get("job_is_remote", False)
    if is_remote:
        location = "Remote"
    elif city and state:
        location = f"{city}, {state}"
    elif city:
        location = f"{city}, {country}"
    else:
        location = country or "Location not specified"

    # Posted date
    posted = job.get("job_posted_at_datetime_utc", "")
    posted_display = posted[:10] if posted else "Unknown"

    # Required qualifications snippet
    desc = job.get("job_description", "")
    desc_snippet = (desc[:250] + "…") if len(desc) > 250 else desc

    return {
        "title": job.get("job_title", "N/A"),
        "company": job.get("employer_name", "N/A"),
        "location": location,
        "remote": is_remote,
        "salary": salary_str,
        "employment_type": job.get("job_employment_type", "FULLTIME"),
        "posted_date": posted_display,
        "description_snippet": desc_snippet,
        "required_experience": job.get("job_required_experience", {}).get(
            "required_experience_in_months"
        ),
        "apply_url": job.get("job_apply_link") or job.get("job_google_link"),
        "company_logo": job.get("employer_logo"),
    }


async def find_jobs(
    role: str,
    skills: Optional[list[str]] = None,
    location: str = "United States",
    remote: bool = False,
    max_results: int = 10,
) -> dict:
    """
    Search for live job openings matching a role and skill set.

    Pulls real-time listings from LinkedIn, Indeed, Glassdoor, and Google Jobs.

    Args:
        role:        Job title to search for (e.g. "Backend Engineer").
        skills:      List of skills to include in the search (e.g. ["Python", "FastAPI"]).
        location:    City, state, or country to search in (default "United States").
        remote:      If True, filter for remote jobs only.
        max_results: Number of listings to return (max 10, default 10).

    Returns:
        Dictionary with matching job listings and metadata.
    """
    skills = skills or []
    query = _build_query(role, skills, remote)

    params = {
        "query": query,
        "location": location,
        "num_pages": "2",
        "employment_types": "FULLTIME",
    }
    if remote:
        params["remote_jobs_only"] = "true"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{JSEARCH_BASE_URL}/search",
                headers=JSEARCH_HEADERS,
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        return {
            "error": f"JSearch API error: {e.response.status_code}",
            "hint": "Check your JSEARCH_API_KEY in .env",
        }
    except Exception as e:
        return {"error": str(e)}

    jobs = data.get("data", [])
    total_found = len(jobs)

    formatted = [_format_job(j) for j in jobs[:max_results]]

    # Count how many have salary disclosed
    with_salary = sum(1 for j in formatted if j["salary"] != "Not disclosed")

    return {
        "query": query,
        "location": location,
        "remote_only": remote,
        "total_found": total_found,
        "showing": len(formatted),
        "salary_disclosed_count": with_salary,
        "jobs": formatted,
        "data_source": "LinkedIn, Indeed, Glassdoor, Google Jobs via JSearch",
    }
