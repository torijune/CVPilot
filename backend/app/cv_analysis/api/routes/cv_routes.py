from fastapi import APIRouter, HTTPException, Depends
import logging
from ..models.request_models import CVAnalysisRequest, CVAnalysisHistoryRequest
from ..models.response_models import CVAnalysisResponse, RadarChartResponse, HealthCheckResponse
from ...application.services.cv_analysis_service import CVAnalysisService
from ...infra.repositories.cv_repository_impl import CVRepositoryImpl

logger = logging.getLogger(__name__)

router = APIRouter()

# 의존성 주입
def get_cv_service() -> CVAnalysisService:
    repository = CVRepositoryImpl()
    return CVAnalysisService(repository)

@router.post("/analyze", response_model=CVAnalysisResponse)
async def analyze_cv(
    request: CVAnalysisRequest,
    cv_service: CVAnalysisService = Depends(get_cv_service)
):
    """CV 분석 수행"""
    try:
        logger.info(f"CV 분석 요청: {request.field} 분야")
        
        # CV 분석 수행
        result = await cv_service.analyze_cv(
            cv_text=request.cv_text,
            field=request.field
        )
        
        # 응답 모델로 변환
        response = CVAnalysisResponse(
            id=result.id,
            cv_text=result.cv_text,
            skills=result.skills,
            experiences=result.experiences,
            strengths=result.strengths,
            weaknesses=result.weaknesses,
            radar_chart_data=result.radar_chart_data,
            created_at=result.created_at.isoformat()
        )
        
        logger.info(f"CV 분석 완료: {result.id}")
        return response
        
    except ValueError as e:
        logger.error(f"CV 분석 검증 실패: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"CV 분석 실패: {e}")
        raise HTTPException(status_code=500, detail="CV 분석 중 오류가 발생했습니다.")

@router.get("/analysis/{analysis_id}", response_model=CVAnalysisResponse)
async def get_cv_analysis(
    analysis_id: str,
    cv_service: CVAnalysisService = Depends(get_cv_service)
):
    """CV 분석 결과 조회"""
    try:
        result = await cv_service.get_cv_analysis(analysis_id)
        if not result:
            raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
        
        response = CVAnalysisResponse(
            id=result.id,
            cv_text=result.cv_text,
            skills=result.skills,
            experiences=result.experiences,
            strengths=result.strengths,
            weaknesses=result.weaknesses,
            radar_chart_data=result.radar_chart_data,
            created_at=result.created_at.isoformat()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"CV 분석 결과 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="CV 분석 결과 조회 중 오류가 발생했습니다.")

@router.get("/radar-chart/{analysis_id}", response_model=RadarChartResponse)
async def get_radar_chart_data(
    analysis_id: str,
    cv_service: CVAnalysisService = Depends(get_cv_service)
):
    """레이더 차트 데이터 조회"""
    try:
        result = await cv_service.get_cv_analysis(analysis_id)
        if not result:
            raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
        
        radar_data = result.radar_chart_data
        return RadarChartResponse(
            categories=radar_data.get('categories', []),
            scores=radar_data.get('scores', {}),
            average_score=radar_data.get('average_score', 0.0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"레이더 차트 데이터 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="레이더 차트 데이터 조회 중 오류가 발생했습니다.")

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """CV 분석 서비스 헬스체크"""
    return HealthCheckResponse(status="healthy", service="cv_analysis") 