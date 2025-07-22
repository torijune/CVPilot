import os
from supabase import create_client, Client
from typing import List
from app.profess_analysis.domain.profess_analysis import Professor
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabaseProfessorClient:
    @staticmethod
    def fetch_professors(field: str, limit: int = 10) -> List[Professor]:
        data = (
            supabase.table("professors")
            .select("name,university,lab,field,homepage,profile,publications")
            .eq("field", field)
            .limit(limit)
            .execute()
        )
        professors = []
        for row in data.data:
            professors.append(Professor(
                name=row["name"],
                university=row["university"],
                lab=row.get("lab"),
                field=row["field"],
                homepage=row.get("homepage"),
                profile=row.get("profile"),
                publications=row.get("publications")
            ))
        return professors
