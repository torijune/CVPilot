from fastapi import APIRouter, Query
from app.profess_analysis.application.profess_analysis_service import ProfessAnalysisService

router = APIRouter()

@router.get("/profess-analysis")
async def get_profess_analysis(
    field: str = Query(..., description="관심 분야"),
    limit: int = Query(10, description="교수/연구실 개수")
):
    result = await ProfessAnalysisService.analyze(field, limit)
    return {
        "summary": result.summary,
        "professors": [
            {
                "name": p.name,
                "university": p.university,
                "lab": p.lab,
                "field": p.field,
                "homepage": p.homepage,
                "profile": p.profile,
                "publications": p.publications
            } for p in result.professors
        ]
    }
