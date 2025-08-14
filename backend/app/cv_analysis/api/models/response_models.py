from pydantic import BaseModel
from typing import List, Dict, Any

class CVAnalysisResponse(BaseModel):
    """CV 분석 응답 모델"""
    id: str
    cv_text: str
    skills: List[str]
    experiences: List[Dict[str, Any]]
    strengths: List[str]
    weaknesses: List[str]
    radar_chart_data: Dict[str, Any]
    created_at: str

class RadarChartResponse(BaseModel):
    """레이더 차트 응답 모델"""
    categories: List[str]
    scores: Dict[str, float]
    average_score: float

class AvailableFieldsResponse(BaseModel):
    """사용 가능한 분야 응답 모델"""
    fields: List[str]

class HealthCheckResponse(BaseModel):
    """헬스체크 응답 모델"""
    status: str
    service: str 