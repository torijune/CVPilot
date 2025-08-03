import logging
from typing import List, Optional
from app.lab_analysis.domain.entities.lab_analysis import LabAnalysis, LabAnalysisResult, Professor
from app.lab_analysis.domain.repositories.lab_analysis_repository import LabAnalysisRepository
from app.shared.application.services.lab_search_service import LabSearchService

logger = logging.getLogger(__name__)

class LabAnalysisRepositoryImpl(LabAnalysisRepository):
    """연구실 분석 리포지토리 구현체"""
    
    def __init__(self):
        self.lab_search_service = LabSearchService()
        self._analysis_cache = {}
        self._result_cache = {}
    
    async def save_analysis(self, analysis: LabAnalysis) -> LabAnalysis:
        """분석 결과 저장 (메모리 캐시)"""
        try:
            self._analysis_cache[analysis.id] = analysis
            logger.info(f"분석 결과 저장: {analysis.id}")
            return analysis
        except Exception as e:
            logger.error(f"분석 결과 저장 실패: {e}")
            raise
    
    async def get_analysis(self, analysis_id: str) -> Optional[LabAnalysis]:
        """분석 결과 조회"""
        try:
            return self._analysis_cache.get(analysis_id)
        except Exception as e:
            logger.error(f"분석 결과 조회 실패: {e}")
            return None
    
    async def save_analysis_result(self, result: LabAnalysisResult) -> LabAnalysisResult:
        """분석 결과 저장 (메모리 캐시)"""
        try:
            self._result_cache[result.id] = result
            logger.info(f"분석 결과 저장: {result.id}")
            return result
        except Exception as e:
            logger.error(f"분석 결과 저장 실패: {e}")
            raise
    
    async def get_analysis_result(self, result_id: str) -> Optional[LabAnalysisResult]:
        """분석 결과 조회"""
        try:
            return self._result_cache.get(result_id)
        except Exception as e:
            logger.error(f"분석 결과 조회 실패: {e}")
            return None
    
    async def get_professors_by_field(self, field: str) -> List[Professor]:
        """분야별 교수 목록 조회"""
        try:
            logger.info(f"분야별 교수 조회: {field}")
            
            # lab_search_service를 통해 교수 정보 조회
            labs = self.lab_search_service.search_labs_by_category(field, min_score=0.3)
            
            professors = []
            for lab in labs:
                # Professor 엔티티로 변환
                professor = Professor(
                    name=lab.get("professor", ""),
                    university=lab.get("university", ""),
                    research_areas=lab.get("research_areas", []),
                    publications=lab.get("publications", []),
                    category_scores=lab.get("category_scores", {}),
                    primary_category=lab.get("primary_category", ""),
                    url=lab.get("url", "")
                )
                professors.append(professor)
            
            logger.info(f"교수 조회 완료: {len(professors)}명")
            return professors
            
        except Exception as e:
            logger.error(f"교수 조회 실패: {e}")
            return [] 