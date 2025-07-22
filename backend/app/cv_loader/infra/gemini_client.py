import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class GeminiAnalyzer:
    @staticmethod
    async def analyze(cv_text: str, interests: str):
        prompt = f'''
        아래는 사용자의 이력서(CV)입니다.

        [CV]
        {cv_text}

        사용자의 관심 분야: {interests}

        1. 이력서의 주요 경력/학업/스킬을 요약해줘.
        2. 관심 분야와 관련된 강점과 약점을 분석해줘.
        3. 대학원 진학/연구 준비에 부족한 점과 보완할 점을 제안해줘.
        4. 추가로 추천할 연구 주제나 프로젝트가 있다면 알려줘.
        '''
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text