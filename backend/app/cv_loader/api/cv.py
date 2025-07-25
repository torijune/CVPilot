from fastapi import APIRouter, UploadFile, File, Form
from app.cv_loader.application.cv_service import CVService
from app.cv_loader.infra.parser import extract_text_from_file

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

@router.post("/extract-text")
async def extract_text(
    file: UploadFile = File(...)
):
    """파일에서 텍스트 추출"""
    try:
        text = await extract_text_from_file(file)
        return {"text": text}
    except Exception as e:
        return {"error": str(e)}, 400
