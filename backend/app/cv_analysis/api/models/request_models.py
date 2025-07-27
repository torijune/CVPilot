from pydantic import BaseModel, Field
from typing import Optional

class CVAnalysisRequest(BaseModel):
    """CV 분석 요청 모델"""
    cv_text: str = Field(..., description="CV 텍스트")
    field: str = Field("Machine Learning / Deep Learning (ML/DL)", description="분석할 분야")

class CVAnalysisHistoryRequest(BaseModel):
    """CV 분석 히스토리 요청 모델"""
    analysis_id: str = Field(..., description="분석 ID") 