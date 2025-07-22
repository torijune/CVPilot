from app.profess_analysis.infra.supabase_client import SupabaseProfessorClient
from app.profess_analysis.infra.gemini_client import GeminiProfessAnalysisClient
from app.profess_analysis.domain.profess_analysis import ProfessAnalysisResult

class ProfessAnalysisService:
    @staticmethod
    async def analyze(field: str, limit: int = 10) -> ProfessAnalysisResult:
        professors = SupabaseProfessorClient.fetch_professors(field, limit)
        # 프롬프트 생성
        prof_texts = "\n\n".join(
            [f"{p.name} ({p.university}) - {p.lab or ''}\n프로필: {p.profile}\n주요 논문: {p.publications}\n홈페이지: {p.homepage}" for p in professors]
        )
        prompt = f'''
        아래는 관심 분야({field})의 국내외 교수 및 연구실 정보입니다.

        {prof_texts}

        위 정보를 바탕으로 해당 분야의 교수/연구실 연구 트렌드와 특징을 500자 이내로 한국어로 요약해줘.
        '''
        summary = await GeminiProfessAnalysisClient.generate_content(prompt)
        return ProfessAnalysisResult(summary=summary, professors=professors)
