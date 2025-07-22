from app.cv_analysis.infra.gemini_client import GeminiClient
from app.cv_analysis.domain.cv_analysis import CVAnalysisResult

class CVAnalysisService:
    @staticmethod
    async def analyze(cv_text: str, interests: str) -> CVAnalysisResult:
        prompt = f'''
        아래는 사용자의 이력서(CV)입니다.

        [CV]
        {cv_text}

        사용자의 관심 분야: {interests}

        아래 항목별로 각각 300자 이내로 한국어로 답변해줘. (각 항목은 반드시 \n\n으로 구분)
        1. 관심 분야의 최신 논문 트렌드 요약
        2. 관심 분야의 국내외 교수/대학원 및 연구실 추천
        3. CV에 기반한 강점/약점 및 피드백
        4. 진학/연구 준비를 위한 개선 방향
        5. 추천 연구/프로젝트 가이드
        '''
        response = await GeminiClient.generate_content(prompt)
        parts = response.split("\n\n")
        return CVAnalysisResult(
            trend=parts[0] if len(parts) > 0 else "",
            professors=parts[1] if len(parts) > 1 else "",
            feedback=parts[2] if len(parts) > 2 else "",
            improvement=parts[3] if len(parts) > 3 else "",
            project=parts[4] if len(parts) > 4 else "",
        )
