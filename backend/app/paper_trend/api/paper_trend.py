from fastapi import APIRouter, Query
from app.paper_trend.application.paper_trend_service import PaperTrendService

router = APIRouter()

@router.get("/paper-trend")
async def get_paper_trend(
    interest: str = Query(..., description="관심 분야"),
    limit: int = Query(10, description="최신 논문 개수")
):
    result = await PaperTrendService.analyze_trend(interest, limit)
    return {
        "trend_summary": result.trend_summary,
        "papers": [
            {
                "title": p.title,
                "abstract": p.abstract,
                "conference": p.conference,
                "year": p.year
            } for p in result.papers
        ]
    }
