from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class PodcastGenerationRequest(BaseModel):
    """팟캐스트 생성 요청 모델"""
    field: str
    papers: Optional[List[Dict[str, Any]]] = None
    analysis_type: str = "comprehensive"  # comprehensive, summary, detailed

class PodcastAnalysisRequest(BaseModel):
    """팟캐스트 분석 결과 조회 요청 모델"""
    analysis_id: str

class PodcastListRequest(BaseModel):
    """팟캐스트 목록 조회 요청 모델"""
    field: Optional[str] = None
    limit: int = 10
    offset: int = 0 