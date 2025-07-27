from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..entities.cv_analysis import CVAnalysis

class CVRepository(ABC):
    """CV 분석 저장소 인터페이스"""
    
    @abstractmethod
    async def save_cv_analysis(self, cv_analysis: CVAnalysis) -> bool:
        """CV 분석 결과 저장"""
        pass
    
    @abstractmethod
    async def get_cv_analysis(self, analysis_id: str) -> Optional[CVAnalysis]:
        """CV 분석 결과 조회"""
        pass
    
    @abstractmethod
    async def get_trend_analysis(self, field: str) -> Optional[Dict[str, Any]]:
        """트렌드 분석 결과 조회 (Paper Trend에서)"""
        pass
    
    @abstractmethod
    async def get_required_skills(self, field: str) -> List[str]:
        """필수 스킬 목록 조회"""
        pass 