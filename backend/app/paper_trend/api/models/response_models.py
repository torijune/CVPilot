from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TrendAnalysisResponse(BaseModel):
    """트렌드 분석 응답 모델"""
    id: str
    field: str
    keywords: List[str]
    top_papers: List[Dict[str, Any]]
    wordcloud_data: Dict[str, int]
    trend_summary: str
    created_at: str

class FieldStatisticsResponse(BaseModel):
    """분야 통계 응답 모델"""
    total_papers: int
    field_papers: int
    year_distribution: Dict[str, int]
    conference_distribution: Dict[str, int]

class PopularKeywordsResponse(BaseModel):
    """인기 키워드 응답 모델"""
    keywords: Dict[str, int]

class AvailableFieldsResponse(BaseModel):
    """사용 가능한 분야 응답 모델"""
    fields: List[str]

class HealthCheckResponse(BaseModel):
    """헬스체크 응답 모델"""
    status: str
    service: str 