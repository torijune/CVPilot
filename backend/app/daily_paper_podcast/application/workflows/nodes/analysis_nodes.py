from typing import List, Dict, Any
import logging
from app.shared.infra.external.openai_client import openai_client

logger = logging.getLogger(__name__)

class ProblemDefinitionNode:
    """문제 정의 분석 노드"""
    
    @staticmethod
    async def analyze(papers: List[Dict[str, Any]], field: str) -> str:
        """문제 정의 분석"""
        try:
            abstracts = [paper['abstract'] for paper in papers]
            combined_abstracts = "\n\n".join(abstracts)
            
            prompt = f"""
다음은 {field} 분야의 최신 논문들의 초록입니다.
이 논문들이 해결하려는 핵심 문제들을 분석해주세요.

논문 초록들:
{combined_abstracts}

위의 논문들을 종합적으로 분석하여 다음을 작성해주세요:

1. 해당 분야에서 현재 직면하고 있는 주요 문제들
2. 기존 방법론의 한계점들
3. 해결이 필요한 핵심 과제들
4. 연구 커뮤니티가 집중하고 있는 방향성

분석 결과를 2-3문단으로 요약해주세요.
"""

            response = await openai_client._call_chat_completion(prompt)
            return response
            
        except Exception as e:
            logger.error(f"문제 정의 분석 실패: {e}")
            return "문제 정의 분석 중 오류가 발생했습니다."

class ProposedMethodNode:
    """제안 방법 분석 노드"""
    
    @staticmethod
    async def analyze(papers: List[Dict[str, Any]], field: str) -> str:
        """제안 방법 분석"""
        try:
            abstracts = [paper['abstract'] for paper in papers]
            combined_abstracts = "\n\n".join(abstracts)
            
            prompt = f"""
다음은 {field} 분야의 최신 논문들의 초록입니다.
이 논문들이 제안하는 혁신적인 방법론들을 분석해주세요.

논문 초록들:
{combined_abstracts}

위의 논문들을 종합적으로 분석하여 다음을 작성해주세요:

1. 제안된 주요 방법론들
2. 기존 방법론과의 차별점
3. 혁신적인 접근 방식들
4. 방법론의 핵심 아이디어

분석 결과를 2-3문단으로 요약해주세요.
"""

            response = await openai_client._call_chat_completion(prompt)
            return response
            
        except Exception as e:
            logger.error(f"제안 방법 분석 실패: {e}")
            return "제안 방법 분석 중 오류가 발생했습니다."

class ExperimentMethodNode:
    """실험 방법 분석 노드"""
    
    @staticmethod
    async def analyze(papers: List[Dict[str, Any]], field: str) -> str:
        """실험 방법 분석"""
        try:
            abstracts = [paper['abstract'] for paper in papers]
            combined_abstracts = "\n\n".join(abstracts)
            
            prompt = f"""
다음은 {field} 분야의 최신 논문들의 초록입니다.
이 논문들의 실험 방법과 평가 방식을 분석해주세요.

논문 초록들:
{combined_abstracts}

위의 논문들을 종합적으로 분석하여 다음을 작성해주세요:

1. 사용된 주요 데이터셋들
2. 실험 설계 방법
3. 평가 지표와 기준
4. 비교 실험 방법
5. 재현성과 검증 방법

분석 결과를 2-3문단으로 요약해주세요.
"""

            response = await openai_client._call_chat_completion(prompt)
            return response
            
        except Exception as e:
            logger.error(f"실험 방법 분석 실패: {e}")
            return "실험 방법 분석 중 오류가 발생했습니다."

class KeyResultsNode:
    """주요 결과 분석 노드"""
    
    @staticmethod
    async def analyze(papers: List[Dict[str, Any]], field: str) -> str:
        """주요 결과 분석"""
        try:
            abstracts = [paper['abstract'] for paper in papers]
            combined_abstracts = "\n\n".join(abstracts)
            
            prompt = f"""
다음은 {field} 분야의 최신 논문들의 초록입니다.
이 논문들의 주요 실험 결과와 성과를 분석해주세요.

논문 초록들:
{combined_abstracts}

위의 논문들을 종합적으로 분석하여 다음을 작성해주세요:

1. 달성된 주요 성과들
2. 기존 방법론 대비 개선점
3. 핵심 성능 지표
4. 실용적 의미와 영향
5. 예상치 못한 발견이나 인사이트

분석 결과를 2-3문단으로 요약해주세요.
"""

            response = await openai_client._call_chat_completion(prompt)
            return response
            
        except Exception as e:
            logger.error(f"주요 결과 분석 실패: {e}")
            return "주요 결과 분석 중 오류가 발생했습니다."

class ResearchSignificanceNode:
    """연구 의의 분석 노드"""
    
    @staticmethod
    async def analyze(papers: List[Dict[str, Any]], field: str) -> str:
        """연구 의의 분석"""
        try:
            abstracts = [paper['abstract'] for paper in papers]
            combined_abstracts = "\n\n".join(abstracts)
            
            prompt = f"""
다음은 {field} 분야의 최신 논문들의 초록입니다.
이 논문들의 연구 의의와 미래 전망을 분석해주세요.

논문 초록들:
{combined_abstracts}

위의 논문들을 종합적으로 분석하여 다음을 작성해주세요:

1. 학술적 의의와 기여도
2. 산업계에 미치는 영향
3. 향후 연구 방향성
4. 기술 발전에 미치는 영향
5. 사회적 가치와 의미

분석 결과를 2-3문단으로 요약해주세요.
"""

            response = await openai_client._call_chat_completion(prompt)
            return response
            
        except Exception as e:
            logger.error(f"연구 의의 분석 실패: {e}")
            return "연구 의의 분석 중 오류가 발생했습니다." 