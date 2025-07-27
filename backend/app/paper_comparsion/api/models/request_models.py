from pydantic import BaseModel, Field
from typing import List, Optional

class ComparisonRequest(BaseModel):
    """방법론 비교 분석 요청 모델"""
    user_idea: str = Field(..., description="사용자의 연구 아이디어")
    field: str = Field(..., description="관련 분야")
    limit: int = Field(10, ge=1, le=50, description="비교할 논문 수")
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0, description="유사도 임계값")

class ComparisonHistoryRequest(BaseModel):
    """비교 분석 히스토리 요청 모델"""
    analysis_id: str = Field(..., description="분석 ID") 