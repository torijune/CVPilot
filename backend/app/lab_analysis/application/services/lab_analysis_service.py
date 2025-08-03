import logging
import uuid
from typing import List, Optional
from app.lab_analysis.domain.entities.lab_analysis import LabAnalysis, LabAnalysisResult, Professor
from app.lab_analysis.domain.repositories.lab_analysis_repository import LabAnalysisRepository
from app.lab_analysis.infra.services.arxiv_service import ArxivService
from app.lab_analysis.infra.services.llm_analysis_service import LLMAnalysisService

logger = logging.getLogger(__name__)

class LabAnalysisService:
    """연구실 분석 서비스"""
    
    def __init__(self, repository: LabAnalysisRepository):
        self.repository = repository
        self.arxiv_service = ArxivService()
        self.llm_service = LLMAnalysisService()
    
    async def get_professors_by_field(self, field: str) -> List[Professor]:
        """분야별 교수 목록 조회"""
        try:
            logger.info(f"분야별 교수 조회: {field}")
            professors = await self.repository.get_professors_by_field(field)
            logger.info(f"교수 조회 완료: {len(professors)}명")
            return professors
        except Exception as e:
            logger.error(f"교수 조회 실패: {e}")
            raise
    
    async def analyze_lab(self, professor_name: str, university_name: str, field: str) -> LabAnalysisResult:
        """연구실 분석 수행"""
        try:
            logger.info(f"연구실 분석 시작: {professor_name} ({university_name})")
            
            # 1. 교수 정보 조회
            professors = await self.repository.get_professors_by_field(field)
            professor = next((p for p in professors if p.name == professor_name and p.university == university_name), None)
            
            if not professor:
                raise ValueError(f"교수를 찾을 수 없습니다: {professor_name} ({university_name})")
            
            # 2. 교수의 publications에서 논문 제목들을 사용하여 초록 수집
            if professor.publications:
                recent_publications = await self.arxiv_service.get_publications_from_titles(
                    professor.publications, limit=10
                )
            else:
                # publications가 없는 경우 교수명으로 검색
                recent_publications = await self.arxiv_service.get_recent_publications(
                    professor_name, university_name, limit=10
                )
            
            if not recent_publications:
                raise ValueError("최신 논문을 찾을 수 없습니다.")
            
            # 3. LLM을 통한 분석
            analysis_result = await self.llm_service.analyze_lab_research(
                professor_name=professor_name,
                university_name=university_name,
                field=field,
                publications=recent_publications
            )
            
            # 4. 결과 저장
            result = LabAnalysisResult(
                id=str(uuid.uuid4()),
                professor_name=professor_name,
                university_name=university_name,
                field=field,
                recent_publications=recent_publications,
                analysis_summary=analysis_result.get("research_direction", ""),
                research_trends=analysis_result.get("research_trends", ""),
                key_insights=analysis_result.get("research_strategy", "")
            )
            
            saved_result = await self.repository.save_analysis_result(result)
            logger.info(f"연구실 분석 완료: {result.id}")
            
            return saved_result
            
        except Exception as e:
            logger.error(f"연구실 분석 실패: {e}")
            raise
    
    async def get_analysis_result(self, result_id: str) -> Optional[LabAnalysisResult]:
        """분석 결과 조회"""
        try:
            return await self.repository.get_analysis_result(result_id)
        except Exception as e:
            logger.error(f"분석 결과 조회 실패: {e}")
            raise 