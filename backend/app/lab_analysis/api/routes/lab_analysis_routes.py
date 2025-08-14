from fastapi import APIRouter, HTTPException, Depends
import logging
from typing import Optional
from app.lab_analysis.api.models.request_models import LabAnalysisRequest, ProfessorSelectionRequest
from app.lab_analysis.api.models.response_models import LabAnalysisResponse, ProfessorListResponse, LabAnalysisResultResponse, HealthCheckResponse, AvailableFieldsResponse
from app.lab_analysis.application.services.lab_analysis_service import LabAnalysisService
from app.lab_analysis.infra.repositories.lab_analysis_repository_impl import LabAnalysisRepositoryImpl

logger = logging.getLogger(__name__)

router = APIRouter()

# 의존성 주입
def get_lab_analysis_service() -> LabAnalysisService:
    repository = LabAnalysisRepositoryImpl()
    return LabAnalysisService(repository)

@router.get("/test")
async def test_endpoint():
    """테스트 엔드포인트"""
    return {"message": "lab_analysis router is working"}

@router.get("/fields", response_model=AvailableFieldsResponse)
async def get_available_fields(
    lab_service: LabAnalysisService = Depends(get_lab_analysis_service)
):
    """사용 가능한 분야 목록 조회"""
    try:
        fields = await lab_service.get_available_fields()
        return AvailableFieldsResponse(fields=fields)
    except Exception as e:
        logger.error(f"분야 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="분야 목록 조회 중 오류가 발생했습니다.")

@router.get("/professors", response_model=ProfessorListResponse)
async def get_professors_by_field(
    field: str,
    university: Optional[str] = None,
    lab_service: LabAnalysisService = Depends(get_lab_analysis_service)
):
    # URL 디코딩 처리
    import urllib.parse
    original_field = field
    field = urllib.parse.unquote(field)
    logger.info(f"교수 목록 조회 엔드포인트 호출됨")
    logger.info(f"원본 field: {original_field}")
    logger.info(f"디코딩된 field: {field}")
    """분야별 교수 목록 조회 (학교 필터링 지원)"""
    try:
        logger.info(f"교수 목록 조회 요청: {field}, 학교: {university}")
        
        professors = await lab_service.get_professors_by_field(field, university)
        
        # 응답 모델로 변환
        professor_infos = []
        for prof in professors:
            professor_info = {
                "professor_name": prof.name,
                "university_name": prof.university,
                "research_areas": prof.research_areas,
                "publications": prof.publications,
                "category_scores": prof.category_scores,
                "primary_category": prof.primary_category,
                "url": prof.url
            }
            professor_infos.append(professor_info)
        
        response = ProfessorListResponse(
            field=field,
            professors=professor_infos,
            total_count=len(professor_infos)
        )
        
        logger.info(f"교수 목록 조회 완료: {len(professor_infos)}명")
        return response
        
    except Exception as e:
        logger.error(f"교수 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="교수 목록 조회 중 오류가 발생했습니다.")

@router.post("/analyze", response_model=LabAnalysisResultResponse)
async def analyze_lab(
    request: ProfessorSelectionRequest,
    lab_service: LabAnalysisService = Depends(get_lab_analysis_service)
):
    """연구실 분석 수행"""
    try:
        logger.info(f"연구실 분석 요청: {request.professor_name} ({request.university_name})")
        
        # 연구실 분석 수행
        result = await lab_service.analyze_lab(
            professor_name=request.professor_name,
            university_name=request.university_name,
            field=request.field
        )
        
        # 응답 모델로 변환
        response = LabAnalysisResultResponse(
            id=result.id,
            professor_name=result.professor_name,
            university_name=result.university_name,
            field=result.field,
            recent_publications=result.recent_publications,
            analysis_summary=result.analysis_summary,
            research_trends=result.research_trends,
            key_insights=result.key_insights,
            created_at=result.created_at.isoformat()
        )
        
        logger.info(f"연구실 분석 완료: {result.id}")
        return response
        
    except ValueError as e:
        logger.error(f"연구실 분석 검증 실패: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"연구실 분석 실패: {e}")
        raise HTTPException(status_code=500, detail="연구실 분석 중 오류가 발생했습니다.")

@router.get("/result/{result_id}", response_model=LabAnalysisResultResponse)
async def get_analysis_result(
    result_id: str,
    lab_service: LabAnalysisService = Depends(get_lab_analysis_service)
):
    """분석 결과 조회"""
    try:
        result = await lab_service.get_analysis_result(result_id)
        if not result:
            raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
        
        response = LabAnalysisResultResponse(
            id=result.id,
            professor_name=result.professor_name,
            university_name=result.university_name,
            field=result.field,
            recent_publications=result.recent_publications,
            analysis_summary=result.analysis_summary,
            research_trends=result.research_trends,
            key_insights=result.key_insights,
            created_at=result.created_at.isoformat()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"분석 결과 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="분석 결과 조회 중 오류가 발생했습니다.")

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """연구실 분석 서비스 헬스체크"""
    return HealthCheckResponse(status="healthy", service="lab_analysis") 