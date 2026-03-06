"""
Tool 7: parse_linkedin_profile
Scrapes and parses a LinkedIn profile URL to extract structured profile data.
Uses httpx for fetching and BeautifulSoup for parsing, with Claude as fallback for structured extraction.
"""

import json
import re

import anthropic
import httpx
from bs4 import BeautifulSoup

from core.config import ANTHROPIC_API_KEY


def _extract_linkedin_url(raw_value: str) -> str | None:
    """Extract a clean LinkedIn profile URL from user-provided input."""
    text = (raw_value or "").strip()
    if not text:
        return None

    match = re.search(r"https?://(?:www\.)?linkedin\.com/in/[^\s\"'<>]+", text, re.IGNORECASE)
    if match:
        return match.group(0).rstrip(
            "/)",
        )

    match = re.search(r"(?:www\.)?linkedin\.com/in/[^\s\"'<>]+", text, re.IGNORECASE)
    if match:
        return f"https://{match.group(0).rstrip('/),')}"

    return None


async def parse_linkedin_profile(profile_url: str) -> dict:
    """
    Parse a LinkedIn profile URL and extract structured information.

    Note: LinkedIn has aggressive anti-scraping measures. This tool:
    1. Attempts basic scraping (often blocked)
    2. Falls back to asking the user to paste profile text
    3. Uses Claude to structure whatever data is available

    Args:
        profile_url: LinkedIn profile URL (e.g., linkedin.com/in/username)

    Returns:
        Structured profile data or error with fallback suggestion.
    """
    if not profile_url.strip():
        return {"error": "LinkedIn URL is required"}

    cleaned_url = _extract_linkedin_url(profile_url)
    if not cleaned_url:
        return {
            "error": "Invalid LinkedIn URL format",
            "hint": "URL should be like: https://linkedin.com/in/username",
        }

    profile_url = cleaned_url

    # Validate URL format
    if "linkedin.com/in/" not in profile_url.lower():
        return {
            "error": "Invalid LinkedIn URL format",
            "hint": "URL should be like: https://linkedin.com/in/username",
        }

    # Normalize URL
    if not profile_url.startswith("http"):
        profile_url = "https://" + profile_url

    profile_text = ""

    try:
        # Attempt to fetch the page (likely to be blocked)
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(profile_url, headers=headers, follow_redirects=True)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Try to extract basic info from meta tags (works sometimes)
        title = soup.find("title")
        og_title = soup.find("meta", property="og:title")
        og_description = soup.find("meta", property="og:description")

        if title:
            profile_text += f"Title: {title.get_text(strip=True)}\n"
        if og_title:
            profile_text += f"Name: {og_title.get('content', '')}\n"
        if og_description:
            profile_text += f"Bio: {og_description.get('content', '')}\n"

        # Try to extract visible text (often fails due to JS rendering)
        body_text = soup.get_text(separator="\n", strip=True)
        if len(body_text) > 200:
            profile_text += f"\n{body_text[:2000]}"

        if not profile_text.strip():
            return {
                "error": "LinkedIn blocked automated access",
                "suggestion": "LinkedIn actively prevents scraping. Please either:",
                "options": [
                    "1. Manually copy-paste the profile text into the CV parser",
                    "2. Export your LinkedIn profile as a PDF and upload it",
                    "3. Use LinkedIn's official API (requires OAuth setup)",
                ],
                "url_attempted": profile_url,
            }

        # Use Claude to structure the extracted text
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        prompt = f"""Parse this LinkedIn profile data and extract structured information in JSON format.

Profile data:
{profile_text}

Extract and return a JSON object with this exact structure:
{{
  "name": "Full name if found, or null",
  "headline": "Professional headline/title",
  "location": "City/country if mentioned, or null",
  "current_role": "Most recent job title",
  "current_company": "Current employer, or null",
  "skills": ["List of skills if mentioned"],
  "summary": "Brief professional summary",
  "source": "linkedin"
}}

Return ONLY the JSON object, no other text."""

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.content[0].text.strip()

        # Clean up markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        parsed_data = json.loads(content)

        return {
            "success": True,
            "profile": parsed_data,
            "url": profile_url,
            "note": "Limited data: LinkedIn blocks most scraping. Consider manual profile export.",
        }

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 999:
            return {
                "error": "LinkedIn detected automated access (HTTP 999)",
                "suggestion": "Use manual profile export or copy-paste method instead",
                "url_attempted": profile_url,
            }
        return {
            "error": f"Failed to fetch LinkedIn profile: HTTP {e.response.status_code}",
            "url_attempted": profile_url,
        }
    except httpx.InvalidURL:
        return {
            "error": "Invalid LinkedIn URL",
            "hint": "Please provide a valid LinkedIn profile URL, e.g. https://linkedin.com/in/username",
            "url_attempted": profile_url,
        }
    except anthropic.APIError as e:
        return {
            "error": f"Claude API error: {str(e)}",
            "hint": "Check your ANTHROPIC_API_KEY in .env",
        }
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse structured data from profile",
            "raw_text_sample": profile_text[:300] if profile_text else "No text extracted",
        }
    except Exception as e:
        return {"error": f"LinkedIn parsing failed: {str(e)}"}
