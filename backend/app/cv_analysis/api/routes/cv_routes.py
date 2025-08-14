from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Header
import logging
from ..models.request_models import CVAnalysisRequest, CVAnalysisHistoryRequest
from ..models.response_models import CVAnalysisResponse, RadarChartResponse, HealthCheckResponse, AvailableFieldsResponse
from ...application.services.cv_analysis_service import CVAnalysisService
from ...infra.repositories.cv_repository_impl import CVRepositoryImpl
from ...infra.services.file_processor import FileProcessor

logger = logging.getLogger(__name__)

router = APIRouter()

# 의존성 주입
def get_cv_service(api_key: str = None) -> CVAnalysisService:
    repository = CVRepositoryImpl()
    return CVAnalysisService(repository, api_key=api_key)

@router.get("/fields", response_model=AvailableFieldsResponse)
async def get_available_fields(
    cv_service: CVAnalysisService = Depends(get_cv_service)
):
    """사용 가능한 분야 목록 조회"""
    try:
        fields = await cv_service.get_available_fields()
        return AvailableFieldsResponse(fields=fields)
    except Exception as e:
        logger.error(f"분야 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="분야 목록 조회 중 오류가 발생했습니다.")

@router.post("/analyze", response_model=CVAnalysisResponse)
async def analyze_cv(
    request: CVAnalysisRequest,
    x_api_key: str = Header(None, alias="X-API-Key")
):
    """CV 분석 수행 (텍스트 입력)"""
    try:
        logger.info(f"CV 분석 요청: {request.field} 분야")
        
        # API Key 검증
        if not x_api_key:
            raise HTTPException(
                status_code=401, 
                detail="API Key가 필요합니다. X-API-Key 헤더를 추가해주세요."
            )
        
        # CV 분석 서비스 생성
        cv_service = get_cv_service(x_api_key)
        
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

@router.post("/analyze/upload", response_model=CVAnalysisResponse)
async def analyze_cv_from_file(
    file: UploadFile = File(..., description="CV 파일 (PDF, DOCX)"),
    field: str = Form("Machine Learning / Deep Learning (ML/DL)", description="분석할 분야"),
    x_api_key: str = Header(None, alias="X-API-Key")
):
    """CV 분석 수행 (파일 업로드)"""
    try:
        logger.info(f"CV 파일 분석 요청: {file.filename}, {field} 분야")
        
        # API Key 검증
        if not x_api_key:
            raise HTTPException(
                status_code=401, 
                detail="API Key가 필요합니다. X-API-Key 헤더를 추가해주세요."
            )
        
        # 파일 유효성 검사
        if not FileProcessor.validate_file(file):
            raise HTTPException(
                status_code=400,
                detail="유효하지 않은 파일입니다. PDF 또는 DOCX 파일 (최대 10MB)을 업로드해주세요."
            )
        
        # 파일에서 텍스트 추출
        cv_text = await FileProcessor.extract_text_from_file(file)
        
        if not cv_text.strip():
            raise HTTPException(
                status_code=400,
                detail="파일에서 텍스트를 추출할 수 없습니다."
            )
        
        # CV 분석 서비스 생성
        cv_service = get_cv_service(x_api_key)
        
        # CV 분석 수행
        result = await cv_service.analyze_cv(
            cv_text=cv_text,
            field=field
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
        
        logger.info(f"CV 파일 분석 완료: {result.id}")
        return response
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"CV 분석 검증 실패: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"CV 파일 분석 실패: {e}")
        raise HTTPException(status_code=500, detail="CV 파일 분석 중 오류가 발생했습니다.")

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