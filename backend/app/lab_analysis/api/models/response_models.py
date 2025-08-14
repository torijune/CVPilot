from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ProfessorInfo(BaseModel):
    """교수 정보 모델"""
    professor_name: str
    university_name: str
    research_areas: List[str]
    publications: List[str]
    category_scores: Dict[str, float]
    primary_category: str
    url: Optional[str] = None

class LabAnalysisResponse(BaseModel):
    """연구실 분석 응답 모델"""
    id: str
    field: str
    professors: List[ProfessorInfo]
    selected_professor: Optional[ProfessorInfo] = None
    analysis_result: Optional[Dict[str, Any]] = None
    created_at: str

class ProfessorListResponse(BaseModel):
    """교수 목록 응답 모델"""
    field: str
    professors: List[ProfessorInfo]
    total_count: int

class LabAnalysisResultResponse(BaseModel):
    """연구실 분석 결과 응답 모델"""
    id: str
    professor_name: str
    university_name: str
    field: str
    recent_publications: List[Dict[str, str]]
    analysis_summary: str
    research_trends: str
    key_insights: str
    created_at: str

class AvailableFieldsResponse(BaseModel):
    """사용 가능한 분야 응답 모델"""
    fields: List[str]

class HealthCheckResponse(BaseModel):
    """헬스체크 응답 모델"""
    status: str
    service: str 