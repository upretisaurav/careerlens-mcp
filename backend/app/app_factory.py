"""FastAPI application factory and route registration."""

import io
from typing import Any

import anthropic
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.chat_service import build_system_prompt, stream_agentic_response
from app.models import (
    ChatRequest,
    JobsRequest,
    LinkedInRequest,
    ReportRequest,
    ResumeRequest,
    SalaryRequest,
    SkillsRequest,
)
from core.config import ANTHROPIC_API_KEY
from tools import (
    analyze_skill_demand,
    find_jobs,
    get_career_report,
    get_salary_benchmark,
    parse_cv,
    parse_linkedin_profile,
    score_resume_fit,
)


def create_app(client: Any | None = None) -> FastAPI:
    """Create and configure the FastAPI app."""
    if client is None:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    app = FastAPI(
        title="CareerLens API",
        description="Career intelligence powered by real-time job market data + Claude AI",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/chat")
    async def chat(request: ChatRequest):
        """Agentic Claude endpoint with SSE streaming events."""
        system = build_system_prompt(request.profile)
        messages = [
            {"role": message.role, "content": message.content} for message in request.messages
        ]

        return StreamingResponse(
            stream_agentic_response(client=client, system=system, messages=messages),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @app.post("/tools/salary")
    async def tool_salary(req: SalaryRequest):
        return await get_salary_benchmark(
            role=req.role,
            location=req.location,
            company=req.company,
            level=req.level,
        )

    @app.post("/tools/jobs")
    async def tool_jobs(req: JobsRequest):
        return await find_jobs(
            role=req.role,
            skills=req.skills,
            location=req.location,
            remote=req.remote,
            max_results=req.max_results,
        )

    @app.post("/tools/skills")
    async def tool_skills(req: SkillsRequest):
        return await analyze_skill_demand(skills=req.skills, location=req.location)

    @app.post("/tools/resume")
    async def tool_resume(req: ResumeRequest):
        return score_resume_fit(
            resume_text=req.resume_text,
            job_description=req.job_description,
        )

    @app.post("/tools/report")
    async def tool_report(req: ReportRequest):
        return await get_career_report(
            role=req.role,
            skills=req.skills,
            location=req.location,
            current_salary=req.current_salary,
            years_of_experience=req.years_of_experience,
            remote=req.remote,
        )

    @app.post("/tools/parse-cv")
    async def parse_cv_endpoint(file: UploadFile = File(...)):
        """
        Accept a PDF resume upload, extract text, and return structured profile data.
        Frontend sends multipart/form-data with a PDF file.
        """
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        try:
            pdf_bytes = await file.read()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")

        # Extract text from PDF using pypdf
        try:
            import pypdf

            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            text_parts = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
            resume_text = "\n".join(text_parts)
        except ImportError:
            raise HTTPException(
                status_code=500, detail="pypdf not installed. Run: pip install pypdf"
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to extract PDF text: {e}")

        if not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract any text from this PDF. It may be image-based. Try copy-pasting your resume text instead.",
            )

        result = await parse_cv(resume_text)
        return result

    @app.post("/tools/parse-linkedin")
    async def parse_linkedin_endpoint(req: LinkedInRequest):
        """
        Accept a LinkedIn profile URL and return structured profile data.
        """
        result = await parse_linkedin_profile(req.url)
        return result

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "service": "CareerLens API",
            "tools": [
                "salary_benchmark",
                "job_search",
                "skill_demand",
                "resume_fit_score",
                "career_report",
                "parse_cv",
                "parse_linkedin_profile",
            ],
        }

    return app


app = create_app()
