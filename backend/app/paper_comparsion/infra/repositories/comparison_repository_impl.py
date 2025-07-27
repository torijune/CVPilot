from typing import List, Dict, Any, Optional
import logging
from ...domain.repositories.comparison_repository import ComparisonRepository
from ...domain.entities.comparison_analysis import ComparisonAnalysis
from app.shared.infra.external.supabase_client import supabase_client

logger = logging.getLogger(__name__)

class ComparisonRepositoryImpl(ComparisonRepository):
    """비교 분석 저장소 구현체"""
    
    def __init__(self):
        self.supabase_client = supabase_client
    
    async def save_comparison_analysis(self, comparison_analysis: ComparisonAnalysis) -> bool:
        """비교 분석 결과 저장"""
        try:
            # Supabase에 저장 (실제로는 comparison_analyses 테이블이 필요)
            # 현재는 로깅만 수행
            logger.info(f"비교 분석 결과 저장: {comparison_analysis.id}")
            return True
        except Exception as e:
            logger.error(f"비교 분석 결과 저장 실패: {e}")
            return False
    
    async def get_comparison_analysis(self, analysis_id: str) -> Optional[ComparisonAnalysis]:
        """비교 분석 결과 조회"""
        try:
            # Supabase에서 조회 (실제로는 comparison_analyses 테이블이 필요)
            logger.info(f"비교 분석 결과 조회: {analysis_id}")
            return None
        except Exception as e:
            logger.error(f"비교 분석 결과 조회 실패: {e}")
            return None
    
    async def get_papers_by_field(self, field: str, limit: int = 100) -> List[Dict[str, Any]]:
        """분야별 논문 조회"""
        try:
            return await self.supabase_client.get_papers_by_field(field, limit)
        except Exception as e:
            logger.error(f"분야별 논문 조회 실패: {e}")
            raise
    
    async def search_similar_papers(self, query_embedding: List[float], 
                                  field: str, limit: int = 10, 
                                  threshold: float = 0.7) -> List[Dict[str, Any]]:
        """유사한 논문 검색"""
        try:
            return await self.supabase_client.search_papers_by_vector(
                query_embedding=query_embedding,
                field=field,
                limit=limit,
                threshold=threshold
            )
        except Exception as e:
            logger.error(f"유사한 논문 검색 실패: {e}")
            raise
    
    async def get_available_fields(self) -> List[str]:
        """사용 가능한 분야 목록 조회"""
        try:
            return await self.supabase_client.get_available_fields()
        except Exception as e:
            logger.error(f"분야 목록 조회 실패: {e}")
            raise 