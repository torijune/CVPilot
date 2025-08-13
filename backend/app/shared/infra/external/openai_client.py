import os
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class OpenAIClient:
    """OpenAI API 클라이언트"""
    
    def __init__(self, api_key: Optional[str] = None):
        # 클라이언트에서 제공한 API key를 우선 사용, 없으면 환경변수 사용
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        self.model_name = "gpt-4o-mini"
        self.embedding_model = "text-embedding-3-small"
        
        if not self.api_key:
            raise ValueError("API Key가 제공되지 않았습니다. 클라이언트에서 API Key를 전송하거나 OPENAI_API_KEY 환경변수를 설정해주세요.")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """텍스트 임베딩 생성"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "input": text,
            "model": self.embedding_model
        }
        
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(
                f"{self.base_url}/embeddings",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["data"][0]["embedding"]
                else:
                    error_text = await response.text()
                    logger.error(f"OpenAI API 오류: {response.status} - {error_text}")
                    raise Exception(f"API 오류: {response.status}")
    
    async def analyze_trends(self, abstracts: List[str], field: str, keywords: List[str]) -> str:
        """트렌드 분석"""
        prompt = f"""
        다음은 {field} 분야의 논문 초록들입니다. 키워드: {', '.join(keywords)}
        
        논문 초록들:
        {chr(10).join([f"{i+1}. {abstract}" for i, abstract in enumerate(abstracts[:20])])}
        
        이 논문들을 분석하여 다음을 포함한 트렌드 요약을 작성해주세요:
        1. 주요 연구 동향
        2. 핵심 기술 및 방법론
        3. 최신 발전 방향
        4. 향후 전망
        
        한국어로 작성해주세요.
        """
        
        return await self._call_chat_completion(prompt)
    

    
    async def analyze_paper_abstract(self, abstract: str, title: str) -> Dict[str, str]:
        """논문 초록 분석"""
        prompt = f"""
        논문 제목: {title}
        논문 초록: {abstract}
        
        다음 5개 항목으로 분석해주세요:
        
        1. 문제 정의: 이 논문이 해결하려는 문제와 기존 한계점
        2. 제안 방법: 새로운 방법이나 접근법
        3. 실험 방법: 사용된 데이터셋, 환경, 방법
        4. 주요 결과: 핵심 성과와 성능
        5. 연구 의의: 학문적/산업적 의미
        
        각 항목을 명확히 구분하여 한국어로 작성해주세요.
        """
        
        result = await self._call_chat_completion(prompt)
        
        # 결과를 섹션별로 분리
        sections = result.split('\n\n')
        return {
            'problem_definition': sections[0] if len(sections) > 0 else result,
            'proposed_method': sections[1] if len(sections) > 1 else '',
            'experimental_setup': sections[2] if len(sections) > 2 else '',
            'key_results': sections[3] if len(sections) > 3 else '',
            'research_significance': sections[4] if len(sections) > 4 else ''
        }
    
    async def _call_chat_completion(self, prompt: str) -> str:
        """ChatGPT API 호출"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "당신은 AI/ML 분야의 전문 연구자입니다."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    logger.error(f"OpenAI API 오류: {response.status} - {error_text}")
                    raise Exception(f"API 오류: {response.status}")

# 팩토리 함수 - API key에 따라 클라이언트 인스턴스 생성
def get_openai_client(api_key: Optional[str] = None) -> OpenAIClient:
    """OpenAI 클라이언트 인스턴스를 반환합니다."""
    return OpenAIClient(api_key=api_key) 