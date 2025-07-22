from fastapi import APIRouter, UploadFile, File, Form
from app.cv_loader.application.cv_service import CVService

router = APIRouter()

@router.post("/cv")
async def upload_cv(
    cv: UploadFile = File(...),
    interests: str = Form(...)
):
    result = await CVService.process_cv(cv, interests)
    return {
        "summary": result.summary,
        "strengths": result.strengths,
        "weaknesses": result.weaknesses,
        "suggestions": result.suggestions,
        "projects": result.projects,
    }
