from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class PaperInfo(BaseModel):
    """논문 정보 응답 모델"""
    id: str
    title: str
    abstract: str
    authors: List[str]
    conference: Optional[str]
    year: Optional[int]
    field: str
    url: Optional[str]

class PodcastAnalysisResponse(BaseModel):
    """팟캐스트 분석 결과 응답 모델"""
    id: str
    field: str
    papers: List[PaperInfo]
    analysis_text: str
    audio_file_path: str
    duration_seconds: int
    created_at: datetime

class PodcastListResponse(BaseModel):
    """팟캐스트 목록 응답 모델"""
    podcasts: List[PodcastAnalysisResponse]
    total_count: int
    has_more: bool

class PodcastGenerationResponse(BaseModel):
    """팟캐스트 생성 응답 모델"""
    success: bool
    analysis_id: str
    message: str
    estimated_duration: int  # 예상 소요 시간 (초)

class AvailableFieldsResponse(BaseModel):
    """사용 가능한 분야 응답 모델"""
    fields: List[str]

class ConferenceInfo(BaseModel):
    """학회 정보 모델"""
    name: str
    paper_count: int
    latest_year: int
    year_range: str

class ConferencesResponse(BaseModel):
    """분야별 학회 목록 응답 모델"""
    field: str
    conferences: List[ConferenceInfo]
    total_conferences: int

class PaperPreviewInfo(BaseModel):
    """논문 미리보기 정보 모델"""
    id: str
    title: str
    abstract: str
    authors: List[str]
    conference: Optional[str]
    year: Optional[int]
    field: str
    url: Optional[str]

class PaperPreviewResponse(BaseModel):
    """논문 미리보기 응답 모델"""
    paper: PaperPreviewInfo
    field: str
    conference: str
    can_reselect: bool
    total_papers_in_conference: int 