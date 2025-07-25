from typing import List
from app.paper_trend.infra.supabase_client import SupabasePaperClient
from app.paper_trend.infra.gemini_client import GeminiPaperTrendClient
from app.paper_trend.domain.paper_trend import PaperTrendResult

class PaperTrendService:
    @staticmethod
    async def analyze_trend(interest: str, detailed_interests: List[str] = None, limit: int = 10) -> PaperTrendResult:
        # 세부 분야를 포함하여 논문 가져오기
        papers = SupabasePaperClient.fetch_top_tier_papers(interest, detailed_interests, limit)
        
        # 프롬프트 생성
        if detailed_interests:
            detailed_interests_text = ", ".join(detailed_interests)
            abstracts = "\n\n".join(
                [f"[{p.conference} {p.year}] {p.title}: {p.abstract}" for p in papers]
            )
            prompt = f'''
            아래는 관심 분야({interest})의 세부 분야({detailed_interests_text})와 관련된 최신 논문들의 제목과 초록입니다.
            이 논문들은 세부 분야 키워드를 기반으로 관련성이 높은 순서로 선별되었습니다.

            {abstracts}

            위 논문들을 바탕으로 해당 분야의 최신 연구 트렌드를 500자 이내로 한국어로 요약해주세요.
            특히 세부 분야({detailed_interests_text})와 관련된 연구 동향에 집중해서 설명해주세요.
            '''
        else:
            abstracts = "\n\n".join(
                [f"[{p.conference} {p.year}] {p.title}: {p.abstract}" for p in papers]
            )
            prompt = f'''
            아래는 관심 분야({interest})의 탑티어 학회 최신 논문들의 제목과 초록입니다.

            {abstracts}

            위 논문들을 바탕으로 해당 분야의 최신 연구 트렌드를 500자 이내로 한국어로 요약해주세요.
            '''
        
        trend_summary = await GeminiPaperTrendClient.generate_content(prompt)
        return PaperTrendResult(trend_summary=trend_summary, papers=papers)
