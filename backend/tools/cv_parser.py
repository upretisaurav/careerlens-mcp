"""
Tool 6: parse_cv
Extracts structured profile data from resume text using Claude.
Identifies name, role, skills, experience, education, and contact info.
"""

import anthropic

from core.config import ANTHROPIC_API_KEY


async def parse_cv(resume_text: str) -> dict:
    """
    Parse resume text and extract structured profile information.

    Uses Claude to intelligently extract:
    - Name
    - Current/target role
    - Skills (categorized)
    - Years of experience
    - Education
    - Contact information
    - Work history summary

    Args:
        resume_text: Raw text extracted from a PDF or pasted resume.

    Returns:
        Structured dictionary with parsed profile data.
    """
    if not resume_text.strip():
        return {"error": "Resume text is empty"}

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""Parse this resume and extract structured information in JSON format.

Resume text:
{resume_text}

Extract and return a JSON object with this exact structure:
{{
  "name": "Full name if found, or null",
  "email": "Email address if found, or null",
  "phone": "Phone number if found, or null",
  "location": "City/state/country if mentioned, or null",
  "current_role": "Most recent or current job title",
  "target_role": "If they mention a desired role, otherwise use current_role",
  "skills": ["List of technical skills, tools, frameworks, languages"],
  "years_of_experience": "Total years as integer if calculable, or null",
  "education": [
    {{"degree": "Degree name", "institution": "School name", "year": "Year or null"}}
  ],
  "experience": [
    {{
      "title": "Job title",
      "company": "Company name",
      "duration": "e.g. '2 years' or '2020-2022'",
      "highlights": ["Key achievement or responsibility"]
    }}
  ],
  "summary": "Brief 1-2 sentence professional summary"
}}

Important:
- Return ONLY the JSON object, no other text
- Use null for missing fields
- Extract as many skills as you can find
- Be thorough but accurate"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.content[0].text.strip()

        # Claude sometimes wraps in markdown code blocks
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        import json

        parsed_data = json.loads(content)

        return {
            "success": True,
            "profile": parsed_data,
            "raw_text_length": len(resume_text),
        }

    except anthropic.APIError as e:
        return {
            "error": f"Claude API error: {str(e)}",
            "hint": "Check your ANTHROPIC_API_KEY in .env",
        }
    except json.JSONDecodeError as e:
        return {
            "error": f"Failed to parse Claude response as JSON: {str(e)}",
            "raw_response": content[:500],
        }
    except Exception as e:
        return {"error": f"CV parsing failed: {str(e)}"}
