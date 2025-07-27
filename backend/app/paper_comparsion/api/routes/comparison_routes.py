from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging
from ..models.request_models import ComparisonRequest, ComparisonHistoryRequest
from ..models.response_models import (
    ComparisonResponse, ComparisonScoreResponse, 
    AvailableFieldsResponse, HealthCheckResponse
)
from ...application.services.comparison_service import ComparisonService
from ...infra.repositories.comparison_repository_impl import ComparisonRepositoryImpl

logger = logging.getLogger(__name__)

router = APIRouter()

# 의존성 주입
def get_comparison_service() -> ComparisonService:
    repository = ComparisonRepositoryImpl()
    return ComparisonService(repository)

@router.post("/compare", response_model=ComparisonResponse)
async def compare_methods(
    request: ComparisonRequest,
    comparison_service: ComparisonService = Depends(get_comparison_service)
):
    """방법론 비교 분석 수행"""
    try:
        logger.info(f"방법론 비교 분석 요청: {request.field}, 아이디어: {request.user_idea[:50]}...")
        
        # 비교 분석 수행
        result = await comparison_service.compare_methods(
            user_idea=request.user_idea,
            field=request.field,
            limit=request.limit,
            similarity_threshold=request.similarity_threshold
        )
        
        # 응답 모델로 변환
        response = ComparisonResponse(
            id=result.id,
            user_idea=result.user_idea,
            field=result.field,
            similar_papers=result.similar_papers,
            comparison_analysis=result.comparison_analysis,
            differentiation_strategy=result.differentiation_strategy,
            reviewer_feedback=result.reviewer_feedback,
            created_at=result.created_at.isoformat()
        )
        
        logger.info(f"방법론 비교 분석 완료: {result.id}")
        return response
        
    except ValueError as e:
        logger.error(f"방법론 비교 분석 검증 실패: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"방법론 비교 분석 실패: {e}")
        raise HTTPException(status_code=500, detail="방법론 비교 분석 중 오류가 발생했습니다.")

@router.get("/fields", response_model=AvailableFieldsResponse)
async def get_available_fields(
    comparison_service: ComparisonService = Depends(get_comparison_service)
):
    """사용 가능한 분야 목록 조회"""
    try:
        fields = await comparison_service.get_available_fields()
        return AvailableFieldsResponse(fields=fields)
    except Exception as e:
        logger.error(f"분야 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="분야 목록 조회 중 오류가 발생했습니다.")

@router.get("/analysis/{analysis_id}", response_model=ComparisonResponse)
async def get_comparison_analysis(
    analysis_id: str,
    comparison_service: ComparisonService = Depends(get_comparison_service)
):
    """비교 분석 결과 조회"""
    try:
        result = await comparison_service.get_comparison_analysis(analysis_id)
        if not result:
            raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
        
        response = ComparisonResponse(
            id=result.id,
            user_idea=result.user_idea,
            field=result.field,
            similar_papers=result.similar_papers,
            comparison_analysis=result.comparison_analysis,
            differentiation_strategy=result.differentiation_strategy,
            reviewer_feedback=result.reviewer_feedback,
            created_at=result.created_at.isoformat()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"비교 분석 결과 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="비교 분석 결과 조회 중 오류가 발생했습니다.")

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """비교 분석 서비스 헬스체크"""
    return HealthCheckResponse(status="healthy", service="comparison_analysis") 