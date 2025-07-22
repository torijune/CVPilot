import os
from supabase import create_client, Client
from typing import List
from app.paper_trend.domain.paper_trend import Paper
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabasePaperClient:
    @staticmethod
    def fetch_top_tier_papers(interest: str, limit: int = 10) -> List[Paper]:
        # 'url' 컬럼도 함께 가져옴
        data = (
            supabase.table("papers")
            .select("title,abstract,conference,year,url")
            .eq("field", interest)
            .order("year", desc=True)
            .limit(limit)
            .execute()
        )
        papers = []
        for row in data.data:
            papers.append(Paper(
                title=row["title"],
                abstract=row["abstract"],
                conference=row["conference"],
                year=row["year"],
                url=row.get("url")
            ))
        return papers
