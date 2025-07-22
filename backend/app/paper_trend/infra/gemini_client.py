import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class GeminiPaperTrendClient:
    MODEL = "gemini-2.5-flash-lite-preview-06-17"

    @staticmethod
    async def generate_content(prompt: str) -> str:
        model = genai.GenerativeModel(GeminiPaperTrendClient.MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
