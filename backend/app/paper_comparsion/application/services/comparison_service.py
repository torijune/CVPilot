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
                            limit: int = 10, similarity_threshold: float = 0.6) -> ComparisonAnalysis:
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
                reviewer_feedback=comparison_result.reviewer_feedback,
                recommendations=comparison_result.recommendations
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
        """3단계 LLM 분석 수행"""
        try:
            logger.info(f"3단계 LLM 분석 시작: {len(similar_papers)}개 논문")
            
            # 1단계: 비교 분석
            comparison_analysis = await self._perform_comparison_analysis_step1(user_idea, similar_papers)
            logger.info(f"1단계 비교 분석 완료: {len(comparison_analysis)}자")
            
            # 2단계: 차별화 전략
            differentiation_strategy = await self._perform_differentiation_strategy_step2(user_idea, comparison_analysis)
            logger.info(f"2단계 차별화 전략 완료: {len(differentiation_strategy)}자")
            
            # 3단계: 리뷰어 피드백
            reviewer_feedback = await self._perform_reviewer_feedback_step3(user_idea, comparison_analysis)
            logger.info(f"3단계 리뷰어 피드백 완료: {len(reviewer_feedback)}자")
            
            # 분석 결과 통합
            analysis_result = {
                'comparison_analysis': comparison_analysis,
                'differentiation_strategy': differentiation_strategy,
                'reviewer_feedback': reviewer_feedback
            }
            
            # 점수 계산
            scores = self._calculate_comparison_scores(analysis_result)
            
            # 추천사항 생성
            recommendations = await self._generate_recommendations(user_idea, analysis_result)
            
            return ComparisonResult(
                user_idea=user_idea,
                similar_papers=similar_papers,
                comparison_analysis=comparison_analysis,
                differentiation_strategy=differentiation_strategy,
                reviewer_feedback=reviewer_feedback,
                recommendations=recommendations,
                scores=scores
            )
            
        except Exception as e:
            logger.error(f"3단계 비교 분석 수행 실패: {e}")
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
    
    async def _perform_comparison_analysis_step1(self, user_idea: str, similar_papers: List[Dict[str, Any]]) -> str:
        """1단계: 사용자 아이디어와 유사 논문들의 비교 분석"""
        try:
            # 논문 정보를 상세하게 포맷팅
            papers_text = "\n\n".join([
                f"논문 {i+1}: {paper.get('title', 'N/A')}\n"
                f"저자: {paper.get('authors', 'N/A')}\n"
                f"학회: {paper.get('conference', 'N/A')} ({paper.get('year', 'N/A')})\n"
                f"초록: {paper.get('abstract', 'N/A')}"
                for i, paper in enumerate(similar_papers[:10])  # 상위 10개 논문만 사용
            ])
            
            prompt = f"""
            당신은 AI 대학원 교수로서, 당신의 제자의 연구 아이디어를 최신 논문들과 비교 분석하여 
            유사점과 차별화 포인트를 명확하게 도출해야 합니다.

            ## 입력 정보
            - 당신의 제자의 연구 아이디어:
            {user_idea}

            - 관련 기존 논문들:
            {papers_text}

            ## 작성 지침
            1. 각 논문의 **제목, 저자, 학회/연도**를 구체적으로 언급하며 비교 분석합니다.
            2. **기술적 관점(모델, 알고리즘, 데이터셋, 실험 방법론)**과 **아이디어적 관점(연구 목표, 접근 전략, 문제 정의)** 모두 고려하여 비교합니다.
            3. 한국어로 간결하고 명확하게 작성합니다.
            4. 아래 마크다운 템플릿을 반드시 따릅니다.

            ## 출력 형식 (마크다운)

            # 유사한 점
            - 당신의 제자의 연구 아이디어와 기존 논문 간 **공통점**을 기술적, 아이디어적 관점으로 구체적으로 나열
                - [논문1: "제목" (저자, 학회/연도)] - 공통점 요약
                - [논문2: "제목" (저자, 학회/연도)] - 공통점 요약
                - ...

            # 참신한 점
            - 당신의 제자의 연구 아이디어가 기존 논문 대비 가지는 **차별화 요소**
                - [논문1: "제목" (저자, 학회/연도)] - 차별화 요소 및 혁신 포인트
                - [논문2: "제목" (저자, 학회/연도)] - 차별화 요소 및 혁신 포인트
                - ...
            - **혁신적인 접근 방법** 및 기존 연구와의 차별성을 강조
            """
            
            result = await openai_client._call_chat_completion(prompt)
            return result
            
        except Exception as e:
            logger.error(f"1단계 비교 분석 실패: {e}")
            return "비교 분석을 수행하는 중 오류가 발생했습니다."
    
    async def _perform_differentiation_strategy_step2(self, user_idea: str, comparison_analysis: str) -> str:
        """2단계: 차별화 전략 제시"""
        try:
            prompt = f"""
        당신은 AI 대학원 교수입니다. 아래의 정보들을 바탕으로 당신의 제자의 연구 아이디어를
        기존 연구들과 비교하여 차별화 전략을 제시하는 것이 목표입니다. 당신의 제자의 연구 아이디어가 기존 연구들과 비교했을 때 돋보일 수 있도록 차별화 전략을 제시해주세요.

        ## 입력 정보
        - 당신의 제자의 연구 아이디어:
        {user_idea}

        - 기존 연구들과의 비교 분석 결과:
        {comparison_analysis}

        ## 작성 지침
        - 당신의 제자의 연구 아이디어가 기존 연구들과 비교했을 때 돋보일 수 있도록 **실현 가능한 전략과 제안**을 작성해주세요.
        - 구체적인 방법론, 실험 설계 아이디어, 평가 지표 확장 및 차별화된 접근 방법을 제시해주세요.
        - 기술적 타당성과 참신성을 동시에 강조하세요.
        - 한국어로 작성하고, 아래 마크다운 템플릿을 따르세요.

        ## 출력 형식 (마크다운)
        # 실험 설계 개선
        - 추가로 고려할 수 있는 실험 설계 요소
        - 데이터셋 구성 방안

        # 성능 평가 방법
        - 평가 지표의 확장 방안
        - 비교 실험 설계

        # 차별화 전략
        - 기존 연구들과의 차별화를 위한 구체적인 방법론
        - 혁신적인 접근 방법

        # 향후 연구 방향
        - 추가 연구가 필요한 부분
        - 확장 가능한 연구 영역
        """
            
            result = await openai_client._call_chat_completion(prompt)
            return result
            
        except Exception as e:
            logger.error(f"2단계 차별화 전략 실패: {e}")
            return "차별화 전략을 제시하는 중 오류가 발생했습니다."
    
    async def _perform_reviewer_feedback_step3(self, user_idea: str, comparison_analysis: str) -> str:
        """3단계: 리뷰어 관점의 비판적 평가"""
        try:
            prompt = f"""
            당신의 제자의 연구 아이디어: {user_idea}
            
            기존 연구들과의 비교 분석 결과:
            {comparison_analysis}
            
            당신은 성격이 아주 냉철하고 비판적인 AI 대학원 교수입니다. 
            위의 비교 분석 결과를 바탕으로 당신의 제자의 연구 아이디어를 객관적이고 비판적인 시각으로 평가해주세요.
            
            다음 형식으로 마크다운을 사용하여 작성해주세요:
            
            # 강점
            - 연구 아이디어의 학술적 가치와 기여도
            - 방법론의 타당성과 실현 가능성
            - 혁신적인 요소들
            
            # 약점
            - 잠재적인 문제점과 한계
            - 실험 설계의 개선 필요 사항
            - 방법론의 취약점
            
            # 개선이 필요한 부분
            - 구체적인 개선 방안
            - 추가 실험이 필요한 부분
            - 논문 제출 시 예상되는 리뷰어 피드백
            
            객관적이고 건설적인 피드백을 제공해주세요.
            한국어로 작성해주세요.
            """
            
            result = await openai_client._call_chat_completion(prompt)
            return result
            
        except Exception as e:
            logger.error(f"3단계 리뷰어 피드백 실패: {e}")
            return "리뷰어 피드백을 생성하는 중 오류가 발생했습니다."
    
    async def _generate_recommendations(self, user_idea: str, analysis_result: Dict[str, str]) -> List[str]:
        """LLM을 사용하여 구체적이고 실용적인 추천사항 생성"""
        try:
            comparison_analysis = analysis_result.get('comparison_analysis', '')
            differentiation_strategy = analysis_result.get('differentiation_strategy', '')
            reviewer_feedback = analysis_result.get('reviewer_feedback', '')
            
            prompt = f"""
            당신은 AI 대학원 교수입니다. 당신의 제자의 연구 아이디어와 관련된 모든 분석 결과를 종합하여 
            구체적이고 실용적인 추천사항을 제시해야 합니다.

            ## 입력 정보
            - 당신의 제자의 연구 아이디어: {user_idea}
            - 비교 분석 결과: {comparison_analysis}
            - 차별화 전략: {differentiation_strategy}
            - 리뷰어 피드백: {reviewer_feedback}

            ## 작성 지침
            1. 위의 모든 정보를 종합하여 **구체적이고 실행 가능한** 추천사항을 작성하세요.
            2. 각 추천사항은 **한 문장으로 명확하게** 작성하세요.
            3. **우선순위가 높은 것부터** 정렬하세요.
            4. **기술적, 방법론적, 실험적** 측면을 모두 고려하세요.
            5. 한국어로 작성하세요.

            ## 출력 형식
            다음 형식으로 6-8개의 추천사항을 작성하세요:
            - 추천사항 1
            - 추천사항 2
            - 추천사항 3
            - ...

            각 추천사항은 구체적이고 실용적이어야 하며, 실제 연구에 적용할 수 있는 내용이어야 합니다.
            """

            response = await self.openai_client._call_chat_completion(prompt)
            
            if response and len(response.strip()) > 0:
                # 응답에서 추천사항 추출
                lines = response.strip().split('\n')
                recommendations = []
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                        # 불릿 포인트 제거하고 텍스트만 추출
                        recommendation = line.lstrip('-•* ').strip()
                        if recommendation and len(recommendation) > 10:
                            recommendations.append(recommendation)
                
                # 최대 8개까지만 반환
                if recommendations:
                    logger.info(f"LLM 추천사항 생성 완료: {len(recommendations)}개")
                    return recommendations[:8]
            
            # LLM 응답이 실패한 경우 기본 추천사항 반환
            logger.warning("LLM 추천사항 생성 실패, 기본 추천사항 사용")
            return self._get_default_recommendations()
            
        except Exception as e:
            logger.error(f"추천사항 생성 중 오류 발생: {e}")
            return self._get_default_recommendations()
    
    def _get_default_recommendations(self) -> List[str]:
        """기본 추천사항 반환"""
        return [
            "유사한 연구들과의 차별화 포인트를 명확히 하세요.",
            "실험 설계의 독창성을 강조하세요.",
            "성능 평가 지표를 다양화하세요.",
            "기존 연구의 한계점을 보완하는 방향으로 접근하세요.",
            "제안된 차별화 전략을 구체적으로 구현해보세요.",
            "리뷰어 피드백을 반영하여 논문의 완성도를 높이세요."
        ]
    
    async def get_available_fields(self) -> List[str]:
        """사용 가능한 분야 목록 조회"""
        return await self.comparison_repository.get_available_fields()
    
    async def get_comparison_analysis(self, analysis_id: str) -> Optional[ComparisonAnalysis]:
        """비교 분석 결과 조회"""
        return await self.comparison_repository.get_comparison_analysis(analysis_id)