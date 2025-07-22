from fastapi import APIRouter, Form
from app.cv_analysis.application.cv_analysis_service import CVAnalysisService

router = APIRouter()

@router.post("/cv-analysis")
async def analyze_cv(
    cv_text: str = Form(...),
    interests: str = Form(...)
):
    result = await CVAnalysisService.analyze(cv_text, interests)
    return {
        "trend": result.trend,
        "professors": result.professors,
        "feedback": result.feedback,
        "improvement": result.improvement,
        "project": result.project,
    }
