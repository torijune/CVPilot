from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.podcast_analysis import PodcastAnalysis

class PodcastRepository(ABC):
    """팟캐스트 분석 리포지토리 인터페이스"""
    
    @abstractmethod
    async def save_analysis(self, analysis: PodcastAnalysis) -> str:
        """팟캐스트 분석 결과 저장"""
        pass
    
    @abstractmethod
    async def get_analysis_by_id(self, analysis_id: str) -> Optional[PodcastAnalysis]:
        """ID로 팟캐스트 분석 결과 조회"""
        pass
    
    @abstractmethod
    async def get_all_analyses(self, limit: int = 10, offset: int = 0) -> List[PodcastAnalysis]:
        """모든 팟캐스트 분석 결과 조회"""
        pass
    
    @abstractmethod
    async def delete_analysis(self, analysis_id: str) -> bool:
        """팟캐스트 분석 결과 삭제"""
        pass