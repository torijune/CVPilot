import os
import logging
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Supabase 클라이언트"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase 환경변수가 설정되지 않았습니다.")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    async def get_papers_by_field(self, field: str, limit: int = 100) -> List[Dict[str, Any]]:
        """분야별 논문 조회"""
        try:
            result = self.client.table("papers").select("*").eq("field", field).limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"분야별 논문 조회 실패: {e}")
            raise
    
    async def search_papers_by_vector(self, query_embedding: List[float], 
                                    field: str = None, limit: int = 10, 
                                    threshold: float = 0.7) -> List[Dict[str, Any]]:
        """벡터 유사도 검색"""
        try:
            # 임베딩이 있는 논문만 필터링 (페이지네이션 적용)
            query = self.client.table("papers").select("*").not_.is_("combined_embedding", "null")
            
            if field:
                query = query.eq("field", field)
            
            # 페이지네이션으로 데이터 가져오기
            page_size = 50  # 한 번에 가져올 데이터 수 제한
            all_papers = []
            page = 0
            
            while True:
                try:
                    result = query.range(page * page_size, (page + 1) * page_size - 1).execute()
                    papers = result.data
                    
                    if not papers:
                        break
                    
                    all_papers.extend(papers)
                    
                    # 충분한 데이터를 가져왔거나 타임아웃 방지를 위해 중단
                    if len(all_papers) >= 200:  # 최대 200개 논문까지만 처리
                        break
                    
                    page += 1
                    
                except Exception as e:
                    logger.warning(f"페이지 {page} 로드 실패: {e}")
                    break
            
            # 유사도 계산 및 필터링
            similar_papers = []
            logger.info(f"총 {len(all_papers)}개 논문에서 유사도 계산 시작")
            
            for i, paper in enumerate(all_papers):
                embedding = paper.get('combined_embedding')
                if embedding:
                    try:
                        # 임베딩 데이터 검증
                        if isinstance(embedding, str):
                            import json
                            embedding = json.loads(embedding)
                        
                        if not isinstance(embedding, list) or len(embedding) == 0:
                            logger.warning(f"논문 {paper.get('id')}: 유효하지 않은 임베딩 형식")
                            continue
                        
                        similarity = self._calculate_cosine_similarity(
                            query_embedding, embedding
                        )
                        
                        if similarity >= threshold:
                            paper['similarity_score'] = similarity
                            similar_papers.append(paper)
                            logger.info(f"유사한 논문 발견: ID {paper.get('id')}, 유사도: {similarity:.3f}")
                        
                    except Exception as e:
                        logger.warning(f"유사도 계산 실패 (논문 ID: {paper.get('id', 'unknown')}): {e}")
                        continue
            
            logger.info(f"유사도 계산 완료: {len(similar_papers)}개 논문 발견 (임계값: {threshold})")
            
            # 유사도 순으로 정렬
            similar_papers.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similar_papers[:limit]
            
        except Exception as e:
            logger.error(f"벡터 검색 실패: {e}")
            # 에러 발생 시 빈 리스트 반환
            return []
    
    async def get_random_paper(self, field: str = None) -> Optional[Dict[str, Any]]:
        """랜덤 논문 조회"""
        try:
            query = self.client.table("papers").select("*")
            if field:
                query = query.eq("field", field)
            
            result = query.execute()
            papers = result.data
            
            if papers:
                import random
                return random.choice(papers)
            return None
            
        except Exception as e:
            logger.error(f"랜덤 논문 조회 실패: {e}")
            raise
    
    async def get_paper_by_id(self, paper_id: int) -> Optional[Dict[str, Any]]:
        """ID로 논문 조회"""
        try:
            result = self.client.table("papers").select("*").eq("id", paper_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"논문 조회 실패: {e}")
            raise
    
    async def get_available_fields(self) -> List[str]:
        """사용 가능한 분야 목록 조회"""
        try:
            result = self.client.table("papers").select("field").execute()
            fields = list(set([paper['field'] for paper in result.data if paper.get('field')]))
            return sorted(fields)
        except Exception as e:
            logger.error(f"분야 목록 조회 실패: {e}")
            raise
    
    async def get_field_statistics(self, field: str) -> Dict[str, Any]:
        """분야별 통계 조회"""
        try:
            # 전체 논문 수
            total_result = self.client.table("papers").select("id", count="exact").execute()
            total_papers = total_result.count if total_result.count is not None else 0
            
            # 해당 분야 논문 수
            field_result = self.client.table("papers").select("id", count="exact").eq("field", field).execute()
            field_papers = field_result.count if field_result.count is not None else 0
            
            # 연도별 분포
            year_result = self.client.table("papers").select("year").eq("field", field).execute()
            year_distribution = {}
            for paper in year_result.data:
                year = paper.get('year')
                if year:
                    year_distribution[str(year)] = year_distribution.get(str(year), 0) + 1
            
            # 컨퍼런스별 분포
            conference_result = self.client.table("papers").select("conference").eq("field", field).execute()
            conference_distribution = {}
            for paper in conference_result.data:
                conference = paper.get('conference')
                if conference:
                    conference_distribution[conference] = conference_distribution.get(conference, 0) + 1
            
            return {
                "total_papers": total_papers,
                "field_papers": field_papers,
                "year_distribution": year_distribution,
                "conference_distribution": conference_distribution
            }
            
        except Exception as e:
            logger.error(f"분야 통계 조회 실패: {e}")
            raise
    
    async def get_top_papers_by_keywords(self, field: str, keywords: List[str], top_k: int = 7) -> List[Dict[str, Any]]:
        """키워드 기반으로 Top-K 논문 선택 (전체에서 선택)"""
        try:
            logger.info(f"키워드 기반 Top-{top_k} 논문 검색: {field}, 키워드: {keywords}")
            
            # 1. 해당 분야의 모든 논문 조회 (임베딩이 있는 것만)
            query = self.client.table("papers").select("*").eq("field", field).not_.is_("combined_embedding", "null")
            
            # 페이지네이션으로 데이터 가져오기
            page_size = 100
            all_papers = []
            page = 0
            
            while True:
                try:
                    result = query.range(page * page_size, (page + 1) * page_size - 1).execute()
                    papers = result.data
                    
                    if not papers:
                        break
                    
                    all_papers.extend(papers)
                    
                    # 충분한 데이터를 가져왔거나 타임아웃 방지를 위해 중단
                    if len(all_papers) >= 500:  # 최대 500개 논문까지만 처리
                        break
                    
                    page += 1
                    
                except Exception as e:
                    logger.warning(f"페이지 {page} 로드 실패: {e}")
                    break
            
            if not all_papers:
                logger.warning(f"{field} 분야에서 임베딩이 있는 논문을 찾을 수 없습니다.")
                return []
            
            # 2. 키워드 임베딩 생성
            query_text = " ".join(keywords)
            query_embedding = await self._generate_embedding_for_keywords(query_text)
            
            # 3. 유사도 계산 및 Top-K 선택
            similar_papers = []
            for paper in all_papers:
                embedding = paper.get('combined_embedding')
                if embedding:
                    try:
                        # 임베딩 데이터 검증 및 파싱
                        if isinstance(embedding, str):
                            import json
                            embedding = json.loads(embedding)
                        
                        if not isinstance(embedding, list) or len(embedding) == 0:
                            continue
                        
                        similarity = self._calculate_cosine_similarity(
                            query_embedding, embedding
                        )
                        
                        paper['similarity_score'] = similarity
                        similar_papers.append(paper)
                        
                    except Exception as e:
                        logger.warning(f"유사도 계산 실패 (논문 ID: {paper.get('id', 'unknown')}): {e}")
                        continue
            
            # 4. 유사도 순으로 정렬하고 Top-K 선택
            similar_papers.sort(key=lambda x: x['similarity_score'], reverse=True)
            top_papers = similar_papers[:top_k]
            
            logger.info(f"Top-{top_k} 논문 선택 완료: {len(top_papers)}개 논문")
            for i, paper in enumerate(top_papers):
                logger.info(f"  {i+1}. ID: {paper.get('id')}, 제목: {paper.get('title', 'N/A')[:50]}..., 유사도: {paper.get('similarity_score', 0):.3f}")
            
            return top_papers
            
        except Exception as e:
            logger.error(f"키워드 기반 Top-K 논문 검색 실패: {e}")
            return []
    
    async def get_top_papers_by_conference(self, field: str, keywords: List[str], top_per_conference: int = 3) -> List[Dict[str, Any]]:
        """학회별로 Top-K 논문 선택"""
        try:
            logger.info(f"학회별 Top-{top_per_conference} 논문 검색: {field}, 키워드: {keywords}")
            
            # 1. 해당 분야의 모든 논문 조회 (임베딩이 있는 것만) - 제한 없음
            query = self.client.table("papers").select("*").eq("field", field).not_.is_("combined_embedding", "null")
            
            # 페이지네이션으로 데이터 가져오기 (제한 없음)
            page_size = 100
            all_papers = []
            page = 0
            
            while True:
                try:
                    result = query.range(page * page_size, (page + 1) * page_size - 1).execute()
                    papers = result.data
                    
                    if not papers:
                        break
                    
                    all_papers.extend(papers)
                    page += 1
                    
                    # 진행상황 로깅 (10페이지마다)
                    if page % 10 == 0:
                        logger.info(f"페이지 {page} 완료, 총 {len(all_papers)}개 논문 로드됨")
                    
                except Exception as e:
                    logger.warning(f"페이지 {page} 로드 실패: {e}")
                    break
                    
                except Exception as e:
                    logger.warning(f"페이지 {page} 로드 실패: {e}")
                    break
            
            if not all_papers:
                logger.warning(f"{field} 분야에서 임베딩이 있는 논문을 찾을 수 없습니다.")
                return []
            
            # 2. 키워드 임베딩 생성
            query_text = " ".join(keywords)
            query_embedding = await self._generate_embedding_for_keywords(query_text)
            
            # 3. 학회별로 논문 분류
            conference_papers = {}
            for paper in all_papers:
                conference = paper.get('conference', 'Unknown')
                if conference not in conference_papers:
                    conference_papers[conference] = []
                conference_papers[conference].append(paper)
            
            # 4. 각 학회별로 유사도 계산 및 Top-K 선택
            all_top_papers = []
            for conference, papers in conference_papers.items():
                logger.info(f"학회 '{conference}'에서 {len(papers)}개 논문 처리 중...")
                
                similar_papers = []
                for paper in papers:
                    embedding = paper.get('combined_embedding')
                    if embedding:
                        try:
                            # 임베딩 데이터 검증 및 파싱
                            if isinstance(embedding, str):
                                import json
                                embedding = json.loads(embedding)
                            
                            if not isinstance(embedding, list) or len(embedding) == 0:
                                continue
                            
                            similarity = self._calculate_cosine_similarity(
                                query_embedding, embedding
                            )
                            
                            paper['similarity_score'] = similarity
                            similar_papers.append(paper)
                            
                        except Exception as e:
                            logger.warning(f"유사도 계산 실패 (논문 ID: {paper.get('id', 'unknown')}): {e}")
                            continue
                
                # 유사도 순으로 정렬하고 Top-K 선택
                similar_papers.sort(key=lambda x: x['similarity_score'], reverse=True)
                top_papers = similar_papers[:top_per_conference]
                
                logger.info(f"학회 '{conference}'에서 Top-{len(top_papers)} 논문 선택 완료")
                for i, paper in enumerate(top_papers):
                    logger.info(f"  {i+1}. ID: {paper.get('id')}, 제목: {paper.get('title', 'N/A')[:50]}..., 유사도: {paper.get('similarity_score', 0):.3f}")
                
                all_top_papers.extend(top_papers)
            
            logger.info(f"전체 학회에서 총 {len(all_top_papers)}개 논문 선택 완료")
            return all_top_papers
            
        except Exception as e:
            logger.error(f"학회별 Top-K 논문 검색 실패: {e}")
            return []
    
    async def _generate_embedding_for_keywords(self, keywords: str) -> List[float]:
        """키워드에 대한 임베딩 생성"""
        try:
            from app.shared.infra.external.openai_client import openai_client
            return await openai_client.generate_embedding(keywords)
        except Exception as e:
            logger.error(f"키워드 임베딩 생성 실패: {e}")
            raise
    
    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """코사인 유사도 계산"""
        import numpy as np
        import json
        
        try:
            # vec2가 문자열인 경우 JSON 파싱
            if isinstance(vec2, str):
                vec2 = json.loads(vec2)
            elif isinstance(vec2, list) and len(vec2) > 0 and isinstance(vec2[0], str):
                # 리스트의 첫 번째 요소가 문자열인 경우 (잘못된 형식)
                return 0.0
            
            # vec1도 동일하게 처리
            if isinstance(vec1, str):
                vec1 = json.loads(vec1)
            elif isinstance(vec1, list) and len(vec1) > 0 and isinstance(vec1[0], str):
                return 0.0
            
            # numpy 배열로 변환
            vec1 = np.array(vec1, dtype=float)
            vec2 = np.array(vec2, dtype=float)
            
            # 차원 확인
            if vec1.shape != vec2.shape:
                return 0.0
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
            
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            logger.warning(f"유사도 계산 실패: {e}")
            return 0.0

# 싱글톤 인스턴스
supabase_client = SupabaseClient() 