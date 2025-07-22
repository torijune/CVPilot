from app.cv_loader.infra.parser import CVParser
from app.cv_loader.infra.gemini_client import GeminiAnalyzer
from app.cv_loader.domain.cv import CV, CVAnalysisResult

class CVService:
    @staticmethod
    async def process_cv(file, interests: str):
        text = await CVParser.parse(file)
        cv = CV(file.filename, text)
        analysis_text = await GeminiAnalyzer.analyze(cv.text, interests)
        # 분석 결과를 단순 분리(실제 LLM 프롬프트에 맞게 파싱 필요)
        # 예시: 각 항목을 줄바꿈 기준으로 분리
        parts = analysis_text.split('\n')
        return CVAnalysisResult(
            summary=parts[0] if len(parts) > 0 else "",
            strengths=parts[1] if len(parts) > 1 else "",
            weaknesses=parts[2] if len(parts) > 2 else "",
            suggestions=parts[3] if len(parts) > 3 else "",
            projects=parts[4] if len(parts) > 4 else "",
        )
