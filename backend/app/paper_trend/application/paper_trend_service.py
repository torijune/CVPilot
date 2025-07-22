from app.paper_trend.infra.supabase_client import SupabasePaperClient
from app.paper_trend.infra.gemini_client import GeminiPaperTrendClient
from app.paper_trend.domain.paper_trend import PaperTrendResult

class PaperTrendService:
    @staticmethod
    async def analyze_trend(interest: str, limit: int = 10) -> PaperTrendResult:
        papers = SupabasePaperClient.fetch_top_tier_papers(interest, limit)
        # 프롬프트 생성 및 LLM 호출
        abstracts = "\n\n".join(
            [f"[{p.conference} {p.year}] {p.title}: {p.abstract}" for p in papers]
        )
        prompt = f'''
        아래는 관심 분야({interest})의 탑티어 학회 최신 논문들의 제목과 초록입니다.

        {abstracts}

        위 논문들을 바탕으로 해당 분야의 최신 연구 트렌드를 500자 이내로 한국어로 요약해줘.
        '''
        trend_summary = await GeminiPaperTrendClient.generate_content(prompt)
        return PaperTrendResult(trend_summary=trend_summary, papers=papers)
