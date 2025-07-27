from pydantic import BaseModel, Field
from typing import List, Optional

class TrendAnalysisRequest(BaseModel):
    """트렌드 분석 요청 모델"""
    field: str = Field(..., description="분석할 분야")
    keywords: List[str] = Field(..., description="키워드 목록")
    limit: int = Field(50, ge=1, le=100, description="분석할 논문 수")
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0, description="유사도 임계값")

class FieldStatisticsRequest(BaseModel):
    """분야 통계 요청 모델"""
    field: str = Field(..., description="통계를 조회할 분야")

class PopularKeywordsRequest(BaseModel):
    """인기 키워드 요청 모델"""
    field: str = Field(..., description="키워드를 조회할 분야")
    limit: int = Field(20, ge=1, le=100, description="반환할 키워드 수") 