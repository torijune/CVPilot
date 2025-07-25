from fastapi import APIRouter, Query
from typing import List
from app.paper_trend.application.paper_trend_service import PaperTrendService

router = APIRouter()

@router.get("/paper-trend")
async def get_paper_trend(
    interest: str = Query(..., description="관심 분야 (예: Natural Language Processing (NLP))"),
    detailed_interests: str = Query("", description="세부 분야 (쉼표로 구분, 예: Transformer,GAN,Reinforcement Learning)"),
    limit: int = Query(10, description="최신 논문 개수")
):
    # 세부 분야를 리스트로 변환
    detailed_interest_list = []
    if detailed_interests.strip():
        detailed_interest_list = [interest.strip() for interest in detailed_interests.split(",") if interest.strip()]
    
    result = await PaperTrendService.analyze_trend(interest, detailed_interest_list, limit)
    return {
        "trend_summary": result.trend_summary,
        "papers": [
            {
                "title": p.title,
                "abstract": p.abstract,
                "conference": p.conference,
                "year": p.year,
                "url": p.url,
                "relevance_score": p.relevance_score
            } for p in result.papers
        ]
    }
