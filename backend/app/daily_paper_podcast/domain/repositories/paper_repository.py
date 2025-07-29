from abc import ABC, abstractmethod
from typing import List, Optional
from app.daily_paper_podcast.domain.entities.paper import Paper

class PaperRepository(ABC):
    """논문 리포지토리 인터페이스"""
    
    @abstractmethod
    async def get_papers_by_field(self, field: str, limit: int = 5) -> List[Paper]:
        """분야별 논문 조회"""
        pass
    
    @abstractmethod
    async def get_random_papers_by_field(self, field: str, limit: int = 5) -> List[Paper]:
        """분야별 랜덤 논문 조회"""
        pass
    
    @abstractmethod
    async def get_all_fields(self) -> List[str]:
        """모든 분야 조회"""
        pass
    
    @abstractmethod
    async def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """ID로 논문 조회"""
        pass 