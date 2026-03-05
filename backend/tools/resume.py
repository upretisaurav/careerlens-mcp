"""
Tool 4: score_resume_fit
Scores a resume against a job description using keyword extraction,
skill matching, and experience analysis. Pure Python — no external API needed.
Returns an ATS-style score with actionable improvement suggestions.
"""

import re
from typing import Optional

# Common tech skills and keywords for detection
SKILL_PATTERNS = [
    # Languages
    r"\bpython\b",
    r"\bjavascript\b",
    r"\btypescript\b",
    r"\bjava\b",
    r"\bc\+\+\b",
    r"\bc#\b",
    r"\bruby\b",
    r"\bgo\b",
    r"\brust\b",
    r"\bkotlin\b",
    r"\bswift\b",
    r"\bscala\b",
    r"\bphp\b",
    # Frontend
    r"\breact\b",
    r"\bvue\b",
    r"\bangular\b",
    r"\bnext\.?js\b",
    r"\bsvelte\b",
    r"\btailwind\b",
    r"\bhtml\b",
    r"\bcss\b",
    r"\bwebpack\b",
    r"\bvite\b",
    # Backend
    r"\bnode\.?js\b",
    r"\bfastapi\b",
    r"\bdjango\b",
    r"\bflask\b",
    r"\bexpress\b",
    r"\bspring\b",
    r"\brails\b",
    r"\blaravel\b",
    r"\bnestjs\b",
    # Data / AI
    r"\bsql\b",
    r"\bpostgres\b",
    r"\bmysql\b",
    r"\bmongodb\b",
    r"\bredis\b",
    r"\bpandas\b",
    r"\bnumpy\b",
    r"\bpytorch\b",
    r"\btensorflow\b",
    r"\bscikit\b",
    r"\bllm\b",
    r"\brag\b",
    r"\bvector\b",
    r"\bembedding\b",
    # DevOps / Cloud
    r"\bdocker\b",
    r"\bkubernetes\b",
    r"\baws\b",
    r"\bgcp\b",
    r"\bazure\b",
    r"\bterraform\b",
    r"\bci/cd\b",
    r"\bgithub actions\b",
    r"\bjenkins\b",
    # Concepts
    r"\brest\b?ful?\b",
    r"\bgraphql\b",
    r"\bmicroservices?\b",
    r"\bagile\b",
    r"\bscrum\b",
    r"\bsystem design\b",
    r"\bapi\b",
    r"\bmcp\b",
]


def _extract_skills(text: str) -> set[str]:
    """Extract technology/skill keywords from text (case-insensitive)."""
    text_lower = text.lower()
    found = set()
    for pattern in SKILL_PATTERNS:
        if re.search(pattern, text_lower):
            # Clean up the skill name
            clean = re.sub(r"\\b|\\.", "", pattern).strip()
            found.add(clean)
    return found


def _extract_years_experience(text: str) -> Optional[int]:
    """Try to pull a years-of-experience number from text."""
    patterns = [
        r"(\d+)\+?\s*years?\s+of\s+experience",
        r"(\d+)\+?\s*years?\s+experience",
        r"minimum\s+(\d+)\s+years?",
        r"at\s+least\s+(\d+)\s+years?",
    ]
    text_lower = text.lower()
    for pat in patterns:
        m = re.search(pat, text_lower)
        if m:
            return int(m.group(1))
    return None


def _extract_education(text: str) -> list[str]:
    """Detect education requirements/mentions."""
    degrees = []
    text_lower = text.lower()
    if re.search(r"\bb\.?s\.?\b|bachelor", text_lower):
        degrees.append("Bachelor's")
    if re.search(r"\bm\.?s\.?\b|master", text_lower):
        degrees.append("Master's")
    if re.search(r"\bph\.?d\b|doctorate", text_lower):
        degrees.append("PhD")
    return degrees


def _count_action_verbs(text: str) -> int:
    """Count strong action verbs — good ATS signal."""
    verbs = [
        "built",
        "developed",
        "designed",
        "led",
        "managed",
        "implemented",
        "created",
        "optimised",
        "optimized",
        "improved",
        "reduced",
        "increased",
        "architected",
        "deployed",
        "shipped",
        "launched",
        "scaled",
        "drove",
        "delivered",
        "collaborated",
        "spearheaded",
        "mentored",
        "automated",
    ]
    text_lower = text.lower()
    return sum(1 for v in verbs if v in text_lower)


def score_resume_fit(
    resume_text: str,
    job_description: str,
) -> dict:
    """
    Score how well a resume matches a specific job description.

    Performs keyword analysis, skill matching, experience gap detection,
    and ATS compatibility checks. Returns a score with specific suggestions.

    Args:
        resume_text:     Plain text content of the resume (paste it in).
        job_description: Full job description text to match against.

    Returns:
        ATS fit score (0-100), matched/missing skills, and improvement tips.
    """
    if not resume_text.strip() or not job_description.strip():
        return {"error": "Both resume_text and job_description are required."}

    # --- Skill analysis ---
    jd_skills = _extract_skills(job_description)
    resume_skills = _extract_skills(resume_text)

    matched_skills = jd_skills & resume_skills
    missing_skills = jd_skills - resume_skills
    extra_skills = resume_skills - jd_skills  # skills on resume not in JD

    skill_match_pct = (len(matched_skills) / len(jd_skills) * 100) if jd_skills else 100

    # --- Experience analysis ---
    jd_years_required = _extract_years_experience(job_description)
    resume_years = _extract_years_experience(resume_text)
    experience_gap = None
    if jd_years_required and resume_years:
        experience_gap = resume_years - jd_years_required

    # --- Education ---
    jd_education = _extract_education(job_description)
    resume_education = _extract_education(resume_text)

    # --- ATS readability signals ---
    action_verb_count = _count_action_verbs(resume_text)
    word_count = len(resume_text.split())
    has_bullet_indicators = bool(re.search(r"[•\-\*]", resume_text))
    has_quantified_impact = bool(
        re.search(
            r"\d+%|\$\d+|\d+x\b|\d+\s*(users|customers|engineers|services)", resume_text.lower()
        )
    )

    # --- Scoring ---
    # Skill match: 50 points
    skill_score = min(50, skill_match_pct * 0.5)

    # Action verbs: 15 points
    verb_score = min(15, action_verb_count * 1.5)

    # Quantified impact: 15 points
    impact_score = 15 if has_quantified_impact else 0

    # Word count (ideal 400-800): 10 points
    if 400 <= word_count <= 800:
        length_score = 10
    elif 300 <= word_count <= 1000:
        length_score = 6
    else:
        length_score = 2

    # Experience match: 10 points
    if experience_gap is None:
        exp_score = 5  # can't assess
    elif experience_gap >= 0:
        exp_score = 10
    else:
        exp_score = max(0, 10 + experience_gap * 2)

    ats_score = round(skill_score + verb_score + impact_score + length_score + exp_score)
    ats_score = max(0, min(100, ats_score))

    # --- Grade label ---
    if ats_score >= 85:
        grade = "Excellent"
        summary = "Strong match. This resume is well-optimised for this role."
    elif ats_score >= 70:
        grade = "Good"
        summary = "Decent match with a few gaps. A few tweaks could push this to excellent."
    elif ats_score >= 50:
        grade = "Fair"
        summary = "Moderate match. Several important skills or signals are missing."
    else:
        grade = "Weak"
        summary = "Low match. Resume needs significant tailoring for this role."

    # --- Improvement suggestions ---
    suggestions = []

    if missing_skills:
        top_missing = sorted(missing_skills)[:5]
        suggestions.append(
            f"Add these skills from the JD that are missing from your resume: {', '.join(top_missing)}."
        )

    if not has_quantified_impact:
        suggestions.append(
            "Add quantified achievements (e.g. 'reduced latency by 40%', 'scaled to 1M users') — "
            "ATS systems and hiring managers weight these heavily."
        )

    if action_verb_count < 5:
        suggestions.append(
            "Use stronger action verbs (built, designed, led, shipped, optimised) to open bullet points."
        )

    if word_count < 400:
        suggestions.append(
            f"Resume is quite short ({word_count} words). Consider expanding project descriptions and impact."
        )
    elif word_count > 900:
        suggestions.append(
            f"Resume is long ({word_count} words). Trim to 1-2 pages focusing on the most relevant experience."
        )

    if jd_education and not resume_education:
        suggestions.append(
            f"Job requires: {', '.join(jd_education)}. Make sure your education section is clearly visible."
        )

    if experience_gap is not None and experience_gap < 0:
        suggestions.append(
            f"Job asks for {jd_years_required}+ years; your resume signals ~{resume_years} years. "
            "Highlight scope and impact of your experience to compensate."
        )

    if not suggestions:
        suggestions.append(
            "Resume looks strong for this role. Focus on tailoring the summary/objective section."
        )

    return {
        "ats_score": ats_score,
        "grade": grade,
        "summary": summary,
        "skill_analysis": {
            "jd_skills_detected": sorted(jd_skills),
            "matched_skills": sorted(matched_skills),
            "missing_skills": sorted(missing_skills),
            "bonus_skills_on_resume": sorted(extra_skills),
            "skill_match_percentage": f"{skill_match_pct:.0f}%",
        },
        "experience": {
            "required_years": jd_years_required,
            "resume_signals_years": resume_years,
            "gap": experience_gap,
        },
        "ats_signals": {
            "action_verb_count": action_verb_count,
            "has_quantified_impact": has_quantified_impact,
            "word_count": word_count,
            "has_bullet_formatting": has_bullet_indicators,
        },
        "suggestions": suggestions,
        "score_breakdown": {
            "skill_match": f"{skill_score:.0f}/50",
            "action_verbs": f"{verb_score:.0f}/15",
            "quantified_impact": f"{impact_score}/15",
            "length": f"{length_score}/10",
            "experience": f"{exp_score:.0f}/10",
        },
    }
