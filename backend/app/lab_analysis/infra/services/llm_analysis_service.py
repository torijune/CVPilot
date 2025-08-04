import logging
from typing import List, Dict, Any
from app.shared.infra.external.openai_client import OpenAIClient

logger = logging.getLogger(__name__)

class LLMAnalysisService:
    """LLM 분석 서비스"""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
    
    async def analyze_lab_research(
        self, 
        professor_name: str, 
        university_name: str, 
        field: str, 
        publications: List[str]
    ) -> Dict[str, Any]:
        """연구실 연구 내용 분석"""
        try:
            logger.info(f"LLM 분석 시작: {professor_name} ({university_name})")
            
            # 각 섹션별로 별도 LLM 호출
            research_direction = await self._analyze_research_direction(
                professor_name, university_name, field, publications
            )
            
            research_trends = await self._analyze_research_trends(
                professor_name, university_name, field, publications
            )
            
            research_strategy = await self._analyze_research_strategy(
                professor_name, university_name, field, publications
            )
            
            analysis_result = {
                "research_direction": research_direction,
                "research_trends": research_trends,
                "research_strategy": research_strategy
            }
            
            logger.info(f"LLM 분석 완료: {professor_name}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"LLM 분석 실패: {e}")
            return {
                "research_direction": "분석 중 오류가 발생했습니다.",
                "research_trends": "분석 중 오류가 발생했습니다.",
                "research_strategy": "분석 중 오류가 발생했습니다."
            }
    
    async def _analyze_research_direction(
        self, 
        professor_name: str, 
        university_name: str, 
        field: str, 
        publications: List[str]
    ) -> str:
        """연구 방향 및 특징 분석"""
        try:
            publications_text = "\n\n".join([
                f"논문 {i+1}: {pub}" for i, pub in enumerate(publications)
            ])
            
            prompt = f"""
            다음은 {university_name}의 {professor_name} 교수님의 최신 연구 논문들의 초록들입니다.
            이 논문들을 분석하여 연구실의 전체적인 연구 방향과 특징을 분석해주세요.

            연구 분야: {field}

            최신 논문들의 초록:
            {publications_text}

            ## 연구실 전체적인 연구 방향과 특징

            다음 사항들을 자연스럽게 포함하여 분석해주세요:
            - 연구실의 전반적인 연구 철학과 접근 방식
            - 연구실이 중점을 두는 핵심 연구 영역
            - 연구실의 독특한 특징이나 강점
            - 학부생이 이해하기 쉽게 설명

            분석은 한국어로 작성해주시고, 마크다운 형식으로 구조화하여 작성해주세요.
            구체적이고 실용적인 내용으로 작성해주세요.
            """
            
            response = await self.openai_client._call_chat_completion(prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"연구 방향 분석 실패: {e}")
            return "연구 방향 분석 중 오류가 발생했습니다."
    
    async def _analyze_research_trends(
        self, 
        professor_name: str, 
        university_name: str, 
        field: str, 
        publications: List[str]
    ) -> str:
        """연구 트렌드 분석"""
        try:
            publications_text = "\n\n".join([
                f"논문 {i+1}: {pub}" for i, pub in enumerate(publications)
            ])
            
            prompt = f"""
            다음은 {university_name}의 {professor_name} 교수님의 최신 연구 논문들입니다.
            이 논문들을 분석하여 연구실의 최신 연구 트렌드를 분석해주세요.

            연구 분야: {field}

            최신 논문들:
            {publications_text}

            ## 연구실의 최신 연구 트렌드

            다음 사항들을 포함하여 분석해주세요:
            - 연구실에서 최근에 집중하고 있는 연구 주제들
            - 각 논문이 반영하는 연구 동향
            - 연구실의 발전 방향과 추세
            - 학계 전반의 트렌드와의 연관성

            분석은 한국어로 작성해주시고, 마크다운 형식으로 구조화하여 작성해주세요.
            각 트렌드를 명확하게 구분하여 작성해주세요.
            """
            
            response = await self.openai_client._call_chat_completion(prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"연구 트렌드 분석 실패: {e}")
            return "연구 트렌드 분석 중 오류가 발생했습니다."
    
    async def _analyze_research_strategy(
        self, 
        professor_name: str, 
        university_name: str, 
        field: str, 
        publications: List[str]
    ) -> str:
        """학부생을 위한 연구 계획 및 전략 분석"""
        try:
            publications_text = "\n\n".join([
                f"논문 {i+1}: {pub}" for i, pub in enumerate(publications)
            ])
            
            prompt = f"""
            다음은 {university_name}의 {professor_name} 교수님의 최신 연구 논문들입니다.
            이 논문들을 분석하여 학부생이 해당 연구실에 지원하기 위한 연구 계획 및 전략을 제시해주세요.

            연구 분야: {field}

            최신 논문들:
            {publications_text}

            ## 학부생을 위한 연구 계획 및 전략

            다음 사항들을 포함하여 분석해주세요:
            - 학부생이 해당 연구실에 지원하기 위한 구체적인 연구 계획
            - 연구실의 연구 방향에 맞는 개인 연구 주제 제안
            - 연구실에서 기대하는 역량과 준비사항
            - 학부생이 연구실에 기여할 수 있는 방안
            - 지원 전 준비해야 할 기술적/학술적 역량

            분석은 한국어로 작성해주시고, 마크다운 형식으로 구조화하여 작성해주세요.
            실용적이고 구체적인 조언을 제공해주세요.
            """
            
            response = await self.openai_client._call_chat_completion(prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"연구 전략 분석 실패: {e}")
            return "연구 전략 분석 중 오류가 발생했습니다."
    
 