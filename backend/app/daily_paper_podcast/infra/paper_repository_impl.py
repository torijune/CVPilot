from typing import List, Optional
import logging
import random
from app.daily_paper_podcast.domain.paper_repository import PaperRepository
from app.daily_paper_podcast.domain.paper import Paper
from app.shared.infra.external.supabase_client import supabase_client

logger = logging.getLogger(__name__)

class PaperRepositoryImpl(PaperRepository):
    """논문 리포지토리 구현체"""
    
    def __init__(self):
        self.supabase_client = supabase_client
    
    async def get_papers_by_field(self, field: str, limit: int = 5) -> List[Paper]:
        """분야별 논문 조회"""
        try:
            papers_data = await self.supabase_client.get_papers_by_field(field, limit)
            papers = []
            
            for paper_data in papers_data:
                paper = Paper.create(
                    title=paper_data.get('title', ''),
                    abstract=paper_data.get('abstract', ''),
                    authors=paper_data.get('authors', '').split(', ') if paper_data.get('authors') else [],
                    conference=paper_data.get('conference'),
                    year=paper_data.get('year'),
                    field=paper_data.get('field'),
                    url=paper_data.get('url')
                )
                papers.append(paper)
            
            return papers
            
        except Exception as e:
            logger.error(f"분야별 논문 조회 실패: {e}")
            raise
    
    async def get_random_papers_by_field(self, field: str, limit: int = 5) -> List[Paper]:
        """분야별 랜덤 논문 조회"""
        try:
            # 먼저 해당 분야의 모든 논문을 가져옴
            all_papers_data = await self.supabase_client.get_papers_by_field(field, 1000)  # 충분한 수의 논문
            
            if not all_papers_data:
                logger.warning(f"{field} 분야에서 논문을 찾을 수 없습니다.")
                return []
            
            # 랜덤하게 선택
            selected_papers_data = random.sample(all_papers_data, min(limit, len(all_papers_data)))
            
            papers = []
            for paper_data in selected_papers_data:
                paper = Paper.create(
                    title=paper_data.get('title', ''),
                    abstract=paper_data.get('abstract', ''),
                    authors=paper_data.get('authors', '').split(', ') if paper_data.get('authors') else [],
                    conference=paper_data.get('conference'),
                    year=paper_data.get('year'),
                    field=paper_data.get('field'),
                    url=paper_data.get('url')
                )
                papers.append(paper)
            
            logger.info(f"{field} 분야에서 {len(papers)}개 랜덤 논문 선택 완료")
            return papers
            
        except Exception as e:
            logger.error(f"분야별 랜덤 논문 조회 실패: {e}")
            raise
    
    async def get_all_fields(self) -> List[str]:
        """모든 분야 조회"""
        try:
            return await self.supabase_client.get_available_fields()
        except Exception as e:
            logger.error(f"분야 목록 조회 실패: {e}")
            raise
    
    async def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """ID로 논문 조회"""
        try:
            paper_data = await self.supabase_client.get_paper_by_id(int(paper_id))
            
            if not paper_data:
                return None
            
            paper = Paper.create(
                title=paper_data.get('title', ''),
                abstract=paper_data.get('abstract', ''),
                authors=paper_data.get('authors', '').split(', ') if paper_data.get('authors') else [],
                conference=paper_data.get('conference'),
                year=paper_data.get('year'),
                field=paper_data.get('field'),
                url=paper_data.get('url')
            )
            
            return paper
            
        except Exception as e:
            logger.error(f"논문 조회 실패: {e}")
            raise 