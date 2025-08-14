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
    
    async def get_professors_by_field(self, field: str, university: Optional[str] = None) -> List[Professor]:
        """분야별 교수 목록 조회 (학교 필터링 지원)"""
        try:
            logger.info(f"분야별 교수 조회: {field}, 학교: {university}")
            
            # lab_search_service를 통해 교수 정보 조회 (async 호출)
            labs = await self.lab_search_service.search_labs_by_category(field, min_score=0.3)
            
            # 학교 필터링 적용
            if university:
                labs = [lab for lab in labs if lab.get("university", "").lower() == university.lower()]
                logger.info(f"학교 필터링 적용: {university}, 필터링 후 {len(labs)}명")
            
            professors = []
            for lab in labs:
                # category_scores와 primary_category 계산
                from app.shared.domain.value_objects.research_area_mapper import ResearchAreaMapper
                
                research_areas = lab.get("research_areas", [])
                category_scores = ResearchAreaMapper.map_research_areas_to_categories(research_areas)
                primary_category = ResearchAreaMapper.get_primary_category(research_areas)
                
                # Professor 엔티티로 변환
                professor = Professor(
                    name=lab.get("professor", ""),
                    university=lab.get("university", ""),
                    research_areas=research_areas,
                    publications=lab.get("publications", []),
                    category_scores=category_scores,
                    primary_category=primary_category,
                    url=lab.get("url", "")
                )
                professors.append(professor)
            
            logger.info(f"교수 조회 완료: {len(professors)}명")
            return professors
            
        except Exception as e:
            logger.error(f"교수 조회 실패: {e}")
            return []
    
    async def get_available_fields(self) -> List[str]:
        """사용 가능한 분야 목록 조회"""
        try:
            # Supabase에서 사용 가능한 분야 목록 조회
            from app.shared.infra.external.supabase_client import SupabaseClient
            supabase_client = SupabaseClient()
            return await supabase_client.get_available_fields()
        except Exception as e:
            logger.error(f"분야 목록 조회 실패: {e}")
            # 기본 분야 목록 반환
            return [
                "Machine Learning / Deep Learning (ML/DL)",
                "Natural Language Processing (NLP)",
                "Computer Vision (CV)",
                "Multimodal"
            ] 