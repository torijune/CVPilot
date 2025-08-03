from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.lab_analysis import LabAnalysis, LabAnalysisResult, Professor

class LabAnalysisRepository(ABC):
    """연구실 분석 리포지토리 인터페이스"""
    
    @abstractmethod
    async def save_analysis(self, analysis: LabAnalysis) -> LabAnalysis:
        """분석 결과 저장"""
        pass
    
    @abstractmethod
    async def get_analysis(self, analysis_id: str) -> Optional[LabAnalysis]:
        """분석 결과 조회"""
        pass
    
    @abstractmethod
    async def save_analysis_result(self, result: LabAnalysisResult) -> LabAnalysisResult:
        """분석 결과 저장"""
        pass
    
    @abstractmethod
    async def get_analysis_result(self, result_id: str) -> Optional[LabAnalysisResult]:
        """분석 결과 조회"""
        pass
    
    @abstractmethod
    async def get_professors_by_field(self, field: str) -> List[Professor]:
        """분야별 교수 목록 조회"""
        pass 