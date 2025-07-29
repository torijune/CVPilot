from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Optional
import logging

from ..models.request_models import (
    PodcastGenerationRequest,
    PodcastAnalysisRequest,
    PodcastListRequest
)
from ..models.response_models import (
    PodcastAnalysisResponse,
    PodcastListResponse,
    PodcastGenerationResponse,
    AvailableFieldsResponse
)
from ...application.services.podcast_service import PodcastService
from ...infra.repositories.paper_repository_impl import PaperRepositoryImpl
from ...infra.repositories.podcast_repository_impl import PodcastRepositoryImpl

logger = logging.getLogger(__name__)

router = APIRouter()

# 의존성 주입
def get_podcast_service() -> PodcastService:
    paper_repository = PaperRepositoryImpl()
    podcast_repository = PodcastRepositoryImpl()
    return PodcastService(paper_repository, podcast_repository)

@router.get("/health")
async def health_check():
    """팟캐스트 서비스 헬스체크"""
    return {"status": "healthy", "service": "podcast"}

@router.get("/fields", response_model=AvailableFieldsResponse)
async def get_available_fields(
    podcast_service: PodcastService = Depends(get_podcast_service)
):
    """사용 가능한 분야 목록 조회"""
    try:
        # 4개 분야로 제한
        fields = [
            "Natural Language Processing (NLP)",
            "Computer Vision (CV)",
            "Multimodal",
            "Machine Learning / Deep Learning (ML/DL)"
        ]
        return AvailableFieldsResponse(fields=fields)
    except Exception as e:
        logger.error(f"분야 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="분야 목록 조회 중 오류가 발생했습니다.")

@router.get("/papers/random/{field}")
async def get_random_paper(
    field: str,
    podcast_service: PodcastService = Depends(get_podcast_service)
):
    """분야별 랜덤 논문 단일 조회 (팟캐스트용)"""
    try:
        papers = await podcast_service.get_random_papers_for_field(field, limit=1)
        if not papers:
            raise HTTPException(status_code=404, detail=f"{field} 분야에서 논문을 찾을 수 없습니다.")
        return {"paper": papers[0]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"랜덤 논문 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=PodcastGenerationResponse)
async def analyze_paper(
    request: PodcastGenerationRequest,
    podcast_service: PodcastService = Depends(get_podcast_service)
):
    """논문 분석만 수행"""
    try:
        logger.info(f"논문 분석 요청: {request.field} 분야")
        
        # 논문 분석만 수행 (TTS 생성 제외)
        analysis_result = await podcast_service.analyze_paper_only(
            request.field,
            request.papers if request.papers else None
        )
        
        return PodcastGenerationResponse(
            success=True,
            analysis_id=analysis_result.id,
            message="논문 분석이 완료되었습니다.",
            estimated_duration=0
        )
        
    except Exception as e:
        logger.error(f"논문 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-tts/{analysis_id}", response_model=PodcastGenerationResponse)
async def generate_tts(
    analysis_id: str,
    podcast_service: PodcastService = Depends(get_podcast_service)
):
    """TTS 대본 및 오디오 생성"""
    try:
        logger.info(f"TTS 생성 요청: {analysis_id}")
        
        # 기존 분석 결과를 바탕으로 TTS 생성
        podcast_analysis = await podcast_service.generate_tts_from_analysis(analysis_id)
        
        return PodcastGenerationResponse(
            success=True,
            analysis_id=podcast_analysis.id,
            message="TTS 생성이 완료되었습니다.",
            estimated_duration=podcast_analysis.duration_seconds
        )
        
    except Exception as e:
        logger.error(f"TTS 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate", response_model=PodcastGenerationResponse)
async def generate_podcast(
    request: PodcastGenerationRequest,
    background_tasks: BackgroundTasks,
    podcast_service: PodcastService = Depends(get_podcast_service)
):
    """팟캐스트 생성 (전체 과정)"""
    try:
        logger.info(f"팟캐스트 생성 요청: {request.field} 분야")
        
        # 실시간으로 팟캐스트 생성 (단일 논문 분석이므로 빠름)
        # papers가 없으면 DB에서 랜덤으로 단일 논문 가져옴
        podcast_analysis = await podcast_service.generate_podcast(
            request.field,
            request.papers if request.papers else None
        )
        
        return PodcastGenerationResponse(
            success=True,
            analysis_id=podcast_analysis.id,
            message="팟캐스트 생성이 완료되었습니다.",
            estimated_duration=podcast_analysis.duration_seconds
        )
        
    except Exception as e:
        logger.error(f"팟캐스트 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{analysis_id}", response_model=PodcastAnalysisResponse)
async def get_podcast_analysis(
    analysis_id: str,
    podcast_service: PodcastService = Depends(get_podcast_service)
):
    """팟캐스트 분석 결과 조회"""
    try:
        analysis = await podcast_service.get_podcast_analysis(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
        
        return PodcastAnalysisResponse(
            id=analysis.id,
            field=analysis.field,
            papers=analysis.papers,
            analysis_text=analysis.analysis_text,
            audio_file_path=analysis.audio_file_path,
            duration_seconds=analysis.duration_seconds,
            created_at=analysis.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팟캐스트 분석 결과 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=PodcastListResponse)
async def get_podcast_list(
    limit: int = 10,
    offset: int = 0,
    podcast_service: PodcastService = Depends(get_podcast_service)
):
    """팟캐스트 목록 조회"""
    try:
        # 데이터베이스에서 실제 목록 조회
        analyses = await podcast_service.get_all_podcast_analyses(limit, offset)
        
        # PodcastAnalysisResponse 형태로 변환
        podcast_responses = []
        for analysis in analyses:
            # papers 데이터를 PaperInfo 형태로 변환
            paper_infos = []
            for paper_dict in analysis.papers:
                from ..models.response_models import PaperInfo
                paper_info = PaperInfo(
                    id=paper_dict.get('id', ''),
                    title=paper_dict.get('title', ''),
                    abstract=paper_dict.get('abstract', ''),
                    authors=paper_dict.get('authors', []),
                    conference=paper_dict.get('conference'),
                    year=paper_dict.get('year'),
                    field=paper_dict.get('field', ''),
                    url=paper_dict.get('url')
                )
                paper_infos.append(paper_info)
            
            from ..models.response_models import PodcastAnalysisResponse
            podcast_response = PodcastAnalysisResponse(
                id=analysis.id,
                field=analysis.field,
                papers=paper_infos,
                analysis_text=analysis.analysis_text,
                audio_file_path=analysis.audio_file_path,
                duration_seconds=analysis.duration_seconds,
                created_at=analysis.created_at
            )
            podcast_responses.append(podcast_response)
        
        return PodcastListResponse(
            podcasts=podcast_responses,
            total_count=len(podcast_responses),
            has_more=len(podcast_responses) == limit  # limit와 같으면 더 있을 가능성
        )
        
    except Exception as e:
        logger.error(f"팟캐스트 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/analysis/{analysis_id}")
async def delete_podcast_analysis(
    analysis_id: str,
    podcast_service: PodcastService = Depends(get_podcast_service)
):
    """팟캐스트 분석 결과 삭제"""
    try:
        success = await podcast_service.delete_podcast_analysis(analysis_id)
        
        if success:
            logger.info(f"팟캐스트 분석 결과 삭제 완료: {analysis_id}")
            return {"message": "삭제되었습니다."}
        else:
            raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"팟캐스트 분석 결과 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 