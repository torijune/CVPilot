from pydantic import BaseModel, Field
from typing import Optional, List

class LabAnalysisRequest(BaseModel):
    """연구실 분석 요청 모델"""
    field: str = Field(..., description="분석할 연구 분야")
    professor_name: Optional[str] = Field(None, description="특정 교수명 (선택사항)")
    university_name: Optional[str] = Field(None, description="특정 대학명 (선택사항)")

class ProfessorSelectionRequest(BaseModel):
    """교수 선택 요청 모델"""
    professor_name: str = Field(..., description="선택된 교수명")
    university_name: str = Field(..., description="대학명")
    field: str = Field(..., description="분석 분야")

class LabAnalysisHistoryRequest(BaseModel):
    """연구실 분석 히스토리 요청 모델"""
    analysis_id: str = Field(..., description="분석 ID") 