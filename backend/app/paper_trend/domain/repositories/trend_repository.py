from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..entities.trend_analysis import TrendAnalysis
from ..entities.cluster import Cluster

class TrendRepository(ABC):
    """트렌드 저장소 인터페이스"""
    
    @abstractmethod
    async def save_trend_analysis(self, trend_analysis: TrendAnalysis) -> bool:
        """트렌드 분석 결과 저장"""
        pass
    
    @abstractmethod
    async def get_trend_analysis(self, analysis_id: str) -> Optional[TrendAnalysis]:
        """트렌드 분석 결과 조회"""
        pass
    
    @abstractmethod
    async def get_papers_by_field(self, field: str, limit: int = 100) -> List[Dict[str, Any]]:
        """분야별 논문 조회"""
        pass
    
    @abstractmethod
    async def search_similar_papers(self, query_embedding: List[float], 
                                  field: str, limit: int = 10, 
                                  threshold: float = 0.7) -> List[Dict[str, Any]]:
        """유사한 논문 검색"""
        pass
    
    @abstractmethod
    async def get_available_fields(self) -> List[str]:
        """사용 가능한 분야 목록 조회"""
        pass
    
    @abstractmethod
    async def get_field_statistics(self, field: str) -> Dict[str, Any]:
        """분야별 통계 조회"""
        pass 