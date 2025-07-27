from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ComparisonResponse(BaseModel):
    """방법론 비교 분석 응답 모델"""
    id: str
    user_idea: str
    field: str
    similar_papers: List[Dict[str, Any]]
    comparison_analysis: str
    differentiation_strategy: str
    reviewer_feedback: str
    recommendations: Optional[List[str]] = None
    created_at: str

class ComparisonScoreResponse(BaseModel):
    """비교 점수 응답 모델"""
    methodology_score: float
    differentiation_score: float
    reviewer_score: float
    overall_score: float

class AvailableFieldsResponse(BaseModel):
    """사용 가능한 분야 응답 모델"""
    fields: List[str]

class HealthCheckResponse(BaseModel):
    """헬스체크 응답 모델"""
    status: str
    service: str 