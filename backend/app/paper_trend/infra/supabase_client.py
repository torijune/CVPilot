import os
import re
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
    def fetch_top_tier_papers(interest: str, detailed_interests: List[str] = None, limit: int = 10) -> List[Paper]:
        # 기본적으로 해당 분야의 논문들을 가져옴
        query = (
            supabase.table("papers")
            .select("title,abstract,conference,year,url,authors")
            .eq("field", interest)
            .order("year", desc=True)
        )
        
        # 세부 분야가 있으면 더 많은 논문을 가져와서 필터링
        if detailed_interests:
            # 세부 분야가 있을 때는 더 많은 논문을 가져와서 필터링
            data = query.limit(limit * 3).execute()
        else:
            # 세부 분야가 없으면 기본 개수만
            data = query.limit(limit).execute()
        
        papers = []
        for row in data.data:
            paper = Paper(
                title=row["title"],
                abstract=row["abstract"],
                conference=row["conference"],
                year=row["year"],
                url=row.get("url"),
                relevance_score=0.0
            )
            
            # 세부 분야가 있으면 관련성 점수 계산
            if detailed_interests:
                relevance_score = SupabasePaperClient._calculate_relevance_score(
                    paper, detailed_interests
                )
                paper.relevance_score = relevance_score
                papers.append(paper)
            else:
                papers.append(paper)
        
        # 세부 분야가 있으면 관련성 점수로 정렬하고 상위 논문만 선택
        if detailed_interests:
            papers.sort(key=lambda x: x.relevance_score, reverse=True)
            papers = papers[:limit]
        
        return papers
    
    @staticmethod
    def search_papers_by_embedding(query_embedding: List[float], 
                                 field: str = None, 
                                 max_results: int = 10,
                                 similarity_threshold: float = 0.7) -> List[Paper]:
        """
        임베딩 기반 벡터 검색을 수행합니다.
        """
        try:
            # 벡터 검색 함수 호출
            query_params = {
                'query_embedding': f"[{','.join(map(str, query_embedding))}]",
                'similarity_threshold': similarity_threshold,
                'max_results': max_results
            }
            
            # 필드 필터링이 있는 경우
            if field:
                # SQL 쿼리로 직접 실행
                query = f"""
                SELECT 
                    p.id,
                    p.title,
                    p.abstract,
                    p.conference,
                    p.year,
                    p.field,
                    p.url,
                    1 - (p.combined_embedding <=> '{query_params['query_embedding']}'::vector) as similarity_score
                FROM papers p
                WHERE p.combined_embedding IS NOT NULL
                AND p.field = '{field}'
                AND 1 - (p.combined_embedding <=> '{query_params['query_embedding']}'::vector) > {similarity_threshold}
                ORDER BY p.combined_embedding <=> '{query_params['query_embedding']}'::vector
                LIMIT {max_results}
                """
                
                result = supabase.rpc('exec_sql', {'sql': query}).execute()
            else:
                # 기본 검색 함수 사용
                result = supabase.rpc('search_papers_by_similarity', query_params).execute()
            
            papers = []
            for row in result.data:
                paper = Paper(
                    title=row["title"],
                    abstract=row["abstract"],
                    conference=row["conference"],
                    year=row["year"],
                    url=row.get("url"),
                    relevance_score=row.get("similarity_score", 0.0)
                )
                papers.append(paper)
            
            return papers
            
        except Exception as e:
            print(f"벡터 검색 실패: {e}")
            # 폴백: 기존 키워드 검색 사용
            return SupabasePaperClient.fetch_top_tier_papers(
                field or "Natural Language Processing (NLP)", 
                None, 
                max_results
            )
    
    @staticmethod
    def search_top_papers_by_conference_embedding(query_embedding: List[float],
                                                max_papers_per_conference: int = 3) -> List[Paper]:
        """
        학회별로 상위 논문을 임베딩 기반으로 검색합니다.
        """
        try:
            query_params = {
                'query_embedding': f"[{','.join(map(str, query_embedding))}]",
                'max_papers_per_conference': max_papers_per_conference
            }
            
            result = supabase.rpc('search_top_papers_by_conference', query_params).execute()
            
            papers = []
            for row in result.data:
                paper = Paper(
                    title=row["title"],
                    abstract=row["abstract"],
                    conference=row["conference"],
                    year=row["year"],
                    url=row.get("url"),
                    relevance_score=row.get("similarity_score", 0.0)
                )
                papers.append(paper)
            
            return papers
            
        except Exception as e:
            print(f"학회별 벡터 검색 실패: {e}")
            # 폴백: 기본 검색
            return SupabasePaperClient.fetch_top_tier_papers(
                "Natural Language Processing (NLP)", 
                None, 
                max_papers_per_conference * 7  # 7개 학회
            )
    
    @staticmethod
    def _calculate_relevance_score(paper: Paper, detailed_interests: List[str]) -> float:
        """
        논문의 제목과 초록에서 세부 분야 키워드의 출현 빈도를 기반으로 관련성 점수를 계산
        """
        score = 0.0
        text_to_search = f"{paper.title} {paper.abstract}".lower()
        
        for interest in detailed_interests:
            interest_lower = interest.lower().strip()
            
            # 정확한 키워드 매칭 (더 높은 점수)
            if interest_lower in text_to_search:
                score += 3.0
            
            # 부분 매칭 (낮은 점수)
            words = interest_lower.split()
            for word in words:
                if len(word) > 2:  # 2글자 이하는 제외
                    if word in text_to_search:
                        score += 0.5
            
            # 제목에 키워드가 있으면 추가 점수
            if interest_lower in paper.title.lower():
                score += 2.0
        
        # 연도별 가중치 (최신 논문에 더 높은 점수)
        year_weight = min(1.0, (paper.year - 2019) / 5.0)  # 2019년 이후 논문에 가중치
        score *= (1.0 + year_weight * 0.3)
        
        return score
