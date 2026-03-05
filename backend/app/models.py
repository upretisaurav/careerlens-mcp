"""
CareerLens API Data Models
──────────────────────────
Pydantic models for request/response validation.
"""

from typing import Optional

from pydantic import BaseModel


class Message(BaseModel):
    """A single message in the conversation."""

    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request body for the /chat endpoint."""

    messages: list[Message]
    profile: Optional[dict] = (
        None  # { role, location, skills, current_salary, years_of_experience }
    )


class SalaryRequest(BaseModel):
    """Request body for the /tools/salary endpoint."""

    role: str
    location: str = "United States"
    company: Optional[str] = None
    level: Optional[str] = None


class JobsRequest(BaseModel):
    """Request body for the /tools/jobs endpoint."""

    role: str
    skills: list[str] = []
    location: str = "United States"
    remote: bool = False
    max_results: int = 10


class SkillsRequest(BaseModel):
    """Request body for the /tools/skills endpoint."""

    skills: list[str]
    location: str = "United States"


class ResumeRequest(BaseModel):
    """Request body for the /tools/resume endpoint."""

    resume_text: str
    job_description: str


class ReportRequest(BaseModel):
    """Request body for the /tools/report endpoint."""

    role: str
    skills: list[str]
    location: str = "United States"
    current_salary: Optional[float] = None
    years_of_experience: Optional[int] = None
    remote: bool = False


class LinkedInRequest(BaseModel):
    """Request body for the /tools/parse-linkedin endpoint."""

    url: str
