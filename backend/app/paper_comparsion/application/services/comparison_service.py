from typing import List, Dict, Any, Optional
import logging
from ...domain.repositories.comparison_repository import ComparisonRepository
from ...domain.entities.comparison_analysis import ComparisonAnalysis
from ...domain.value_objects.comparison_score import ComparisonScore, ComparisonType, ComparisonResult
from app.shared.infra.external.openai_client import openai_client

logger = logging.getLogger(__name__)

class ComparisonService:
    """비교 분석 서비스"""
    
    def __init__(self, comparison_repository: ComparisonRepository):
        self.comparison_repository = comparison_repository
    
    async def compare_methods(self, user_idea: str, field: str, 
                            limit: int = 10, similarity_threshold: float = 0.7) -> ComparisonAnalysis:
        """방법론 비교 분석 수행"""
        try:
            logger.info(f"방법론 비교 분석 시작: {field}, 아이디어: {user_idea[:50]}...")
            
            # 1. 사용자 아이디어 임베딩 생성
            user_idea_embedding = await openai_client.generate_embedding(user_idea)
            
            # 2. 관련 논문 검색
            similar_papers = await self.comparison_repository.search_similar_papers(
                query_embedding=user_idea_embedding,
                field=field,
                limit=limit,
                threshold=similarity_threshold
            )
            
            if not similar_papers:
                raise ValueError(f"{field} 분야에서 유사한 논문을 찾을 수 없습니다.")
            
            # 3. LLM으로 비교 분석 수행
            comparison_result = await self._perform_comparison_analysis(user_idea, similar_papers)
            
            # 4. 결과 생성
            comparison_analysis = ComparisonAnalysis.create(
                user_idea=user_idea,
                field=field,
                similar_papers=similar_papers,
                comparison_analysis=comparison_result.comparison_analysis,
                differentiation_strategy=comparison_result.differentiation_strategy,
                reviewer_feedback=comparison_result.reviewer_feedback
            )
            
            # 5. 결과 저장
            await self.comparison_repository.save_comparison_analysis(comparison_analysis)
            
            logger.info(f"방법론 비교 분석 완료: {len(similar_papers)}개 논문과 비교")
            return comparison_analysis
            
        except Exception as e:
            logger.error(f"방법론 비교 분석 실패: {e}")
            raise
    
    async def _perform_comparison_analysis(self, user_idea: str, 
                                         similar_papers: List[Dict[str, Any]]) -> ComparisonResult:
        """LLM을 사용한 비교 분석 수행"""
        try:
            # OpenAI API를 사용하여 비교 분석
            analysis_result = await openai_client.compare_methods(user_idea, similar_papers)
            
            # 점수 계산 (간단한 구현)
            scores = self._calculate_comparison_scores(analysis_result)
            
            return ComparisonResult(
                user_idea=user_idea,
                similar_papers=similar_papers,
                comparison_analysis=analysis_result.get('comparison_analysis', ''),
                differentiation_strategy=analysis_result.get('differentiation_strategy', ''),
                reviewer_feedback=analysis_result.get('reviewer_feedback', ''),
                scores=scores
            )
            
        except Exception as e:
            logger.error(f"비교 분석 수행 실패: {e}")
            raise
    
    def _calculate_comparison_scores(self, analysis_result: Dict[str, str]) -> Dict[ComparisonType, ComparisonScore]:
        """비교 점수 계산"""
        scores = {}
        
        # 간단한 점수 계산 로직 (실제로는 더 정교한 방법 사용)
        if analysis_result.get('comparison_analysis'):
            methodology_score = 0.7  # 예시 점수
            scores[ComparisonType.METHODOLOGY] = ComparisonScore(
                score=methodology_score,
                comparison_type=ComparisonType.METHODOLOGY,
                description="방법론 비교 분석 완료"
            )
        
        if analysis_result.get('differentiation_strategy'):
            differentiation_score = 0.8  # 예시 점수
            scores[ComparisonType.DIFFERENTIATION] = ComparisonScore(
                score=differentiation_score,
                comparison_type=ComparisonType.DIFFERENTIATION,
                description="차별화 전략 분석 완료"
            )
        
        if analysis_result.get('reviewer_feedback'):
            reviewer_score = 0.6  # 예시 점수
            scores[ComparisonType.REVIEWER_FEEDBACK] = ComparisonScore(
                score=reviewer_score,
                comparison_type=ComparisonType.REVIEWER_FEEDBACK,
                description="리뷰어 피드백 분석 완료"
            )
        
        return scores
    
    async def get_available_fields(self) -> List[str]:
        """사용 가능한 분야 목록 조회"""
        return await self.comparison_repository.get_available_fields()
    
    async def get_comparison_analysis(self, analysis_id: str) -> Optional[ComparisonAnalysis]:
        """비교 분석 결과 조회"""
        return await self.comparison_repository.get_comparison_analysis(analysis_id) 