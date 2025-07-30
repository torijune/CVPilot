from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..entities.qa_session import QASession, QAMessage

class QARepository(ABC):
    """QA 리포지토리 인터페이스"""
    
    @abstractmethod
    async def save_session(self, session: QASession) -> bool:
        """QA 세션 저장"""
        pass
    
    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[QASession]:
        """QA 세션 조회"""
        pass
    
    @abstractmethod
    async def update_session(self, session: QASession) -> bool:
        """QA 세션 업데이트"""
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """QA 세션 삭제"""
        pass
    
    @abstractmethod
    async def get_sessions(self, limit: int = 10, offset: int = 0) -> List[QASession]:
        """QA 세션 목록 조회"""
        pass
    
    @abstractmethod
    async def save_cv_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """CV 분석 결과 저장"""
        pass
    
    @abstractmethod
    async def get_cv_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """CV 분석 결과 조회"""
        pass 