from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List
import logging
from ..models.request_models import TrendAnalysisRequest, FieldStatisticsRequest, PopularKeywordsRequest
from ..models.response_models import (
    TrendAnalysisResponse, FieldStatisticsResponse, 
    PopularKeywordsResponse, AvailableFieldsResponse, HealthCheckResponse
)
from ...application.services.trend_analysis_service import TrendAnalysisService
from ...infra.repositories.trend_repository_impl import TrendRepositoryImpl

logger = logging.getLogger(__name__)

router = APIRouter()

# 의존성 주입
def get_trend_service() -> TrendAnalysisService:
    repository = TrendRepositoryImpl()
    return TrendAnalysisService(repository)

@router.post("/analyze", response_model=TrendAnalysisResponse)
async def analyze_trends(
    request: TrendAnalysisRequest,
    trend_service: TrendAnalysisService = Depends(get_trend_service)
):
    """트렌드 분석 수행"""
    try:
        logger.info(f"트렌드 분석 요청: {request.field}, 키워드: {request.keywords}")
        
        # 트렌드 분석 수행
        result = await trend_service.analyze_trends(
            field=request.field,
            keywords=request.keywords,
            limit=request.limit,
            similarity_threshold=request.similarity_threshold
        )
        
        # 응답 모델로 변환
        response = TrendAnalysisResponse(
            id=result.id,
            field=result.field,
            keywords=result.keywords,
            top_papers=result.top_papers,
            wordcloud_data=result.wordcloud_data,
            trend_summary=result.trend_summary,
            created_at=result.created_at.isoformat()
        )
        
        logger.info(f"트렌드 분석 완료: {result.id}")
        return response
        
    except ValueError as e:
        logger.error(f"트렌드 분석 검증 실패: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"트렌드 분석 실패: {e}")
        raise HTTPException(status_code=500, detail="트렌드 분석 중 오류가 발생했습니다.")

@router.get("/fields", response_model=AvailableFieldsResponse)
async def get_available_fields(
    trend_service: TrendAnalysisService = Depends(get_trend_service)
):
    """사용 가능한 분야 목록 조회"""
    try:
        fields = await trend_service.get_available_fields()
        return AvailableFieldsResponse(fields=fields)
    except Exception as e:
        logger.error(f"분야 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="분야 목록 조회 중 오류가 발생했습니다.")

@router.get("/fields/{field}/statistics", response_model=FieldStatisticsResponse)
async def get_field_statistics(
    field: str,
    trend_service: TrendAnalysisService = Depends(get_trend_service)
):
    """특정 분야의 통계 정보 조회"""
    try:
        statistics = await trend_service.get_field_statistics(field)
        return FieldStatisticsResponse(**statistics)
    except Exception as e:
        logger.error(f"분야 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="분야 통계 조회 중 오류가 발생했습니다.")

@router.get("/fields/{field}/keywords", response_model=PopularKeywordsResponse)
async def get_popular_keywords(
    field: str,
    limit: int = Query(20, ge=1, le=100, description="반환할 키워드 수"),
    trend_service: TrendAnalysisService = Depends(get_trend_service)
):
    """특정 분야의 인기 키워드 조회"""
    try:
        # 간단한 키워드 추출 구현
        papers = await trend_service.trend_repository.get_papers_by_field(field, limit=100)
        
        # 워드클라우드 서비스를 사용하여 키워드 추출
        from ...infra.services.wordcloud_service import WordcloudService
        wordcloud_service = WordcloudService()
        wordcloud_data = wordcloud_service.generate_wordcloud_data(papers, max_words=limit)
        
        return PopularKeywordsResponse(keywords=wordcloud_data.word_frequencies)
    except Exception as e:
        logger.error(f"인기 키워드 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="인기 키워드 조회 중 오류가 발생했습니다.")

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """트렌드 분석 서비스 헬스체크"""
    return HealthCheckResponse(status="healthy", service="trend_analysis") 