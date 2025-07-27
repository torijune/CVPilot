from typing import List, Dict, Any
import logging
from app.paper_trend.domain.repositories.trend_repository import TrendRepository
from app.paper_trend.domain.entities.trend_analysis import TrendAnalysis
from app.shared.infra.external.openai_client import openai_client

logger = logging.getLogger(__name__)

class TrendAnalysisService:
    """트렌드 분석 서비스"""
    
    def __init__(self, trend_repository: TrendRepository):
        self.trend_repository = trend_repository
    
    async def analyze_trends(self, field: str, keywords: List[str], 
                           limit: int = 50, similarity_threshold: float = 0.7) -> TrendAnalysis:
        """트렌드 분석 수행"""
        try:
            logger.info(f"트렌드 분석 시작: {field}, 키워드: {keywords}")
            
            # 1. 학회별로 Top-3 논문 선택 (각 학회에서 3개씩)
            top_papers = await self._get_top_papers_by_conference(field, keywords, top_per_conference=3)
            
            if not top_papers:
                # 논문이 없어도 기본 분석 결과 생성
                logger.warning(f"{field} 분야에서 키워드와 관련된 논문을 찾을 수 없습니다. 기본 분석을 수행합니다.")
                return self._create_default_analysis(field, keywords)
            
            # 2. LLM으로 트렌드 분석
            trend_summary = await self._analyze_trends_with_llm(top_papers, field, keywords)
            
            # 3. 결과 생성
            trend_analysis = TrendAnalysis.create(
                field=field,
                keywords=keywords,
                top_papers=top_papers,
                wordcloud_data={},  # 워드클라우드 제거
                trend_summary=trend_summary
            )
            
            # 6. 결과 저장
            await self.trend_repository.save_trend_analysis(trend_analysis)
            
            logger.info(f"트렌드 분석 완료: {len(top_papers)}개 논문 분석")
            return trend_analysis
            
        except Exception as e:
            logger.error(f"트렌드 분석 실패: {e}")
            # 에러 발생 시 기본 분석 결과 반환
            return self._create_default_analysis(field, keywords)
    
    async def _get_top_papers_by_keywords(self, field: str, keywords: List[str], top_k: int = 7) -> List[Dict[str, Any]]:
        """키워드 기반으로 Top-K 논문 선택 (전체에서 선택)"""
        try:
            logger.info(f"키워드 기반 Top-{top_k} 논문 선택: {field}, 키워드: {keywords}")
            
            # Supabase 클라이언트를 통해 Top-K 논문 선택
            from app.shared.infra.external.supabase_client import supabase_client
            top_papers = await supabase_client.get_top_papers_by_keywords(field, keywords, top_k)
            
            logger.info(f"Top-{top_k} 논문 선택 완료: {len(top_papers)}개 논문")
            return top_papers
            
        except Exception as e:
            logger.error(f"Top-K 논문 선택 실패: {e}")
            return []
    
    async def _get_top_papers_by_conference(self, field: str, keywords: List[str], top_per_conference: int = 3) -> List[Dict[str, Any]]:
        """학회별로 Top-K 논문 선택"""
        try:
            logger.info(f"학회별 Top-{top_per_conference} 논문 선택: {field}, 키워드: {keywords}")
            
            # Supabase 클라이언트를 통해 학회별 Top-K 논문 선택
            from app.shared.infra.external.supabase_client import supabase_client
            top_papers = await supabase_client.get_top_papers_by_conference(field, keywords, top_per_conference)
            
            logger.info(f"학회별 Top-{top_per_conference} 논문 선택 완료: {len(top_papers)}개 논문")
            return top_papers
            
        except Exception as e:
            logger.error(f"학회별 Top-K 논문 선택 실패: {e}")
            return []
    
    def _create_default_analysis(self, field: str, keywords: List[str]) -> TrendAnalysis:
        """기본 분석 결과 생성"""
        return TrendAnalysis.create(
            field=field,
            keywords=keywords,
            top_papers=[],
            wordcloud_data={},
            trend_summary=f"{field} 분야의 {', '.join(keywords)} 관련 연구 동향을 분석할 수 있는 충분한 데이터가 없습니다. 더 많은 논문 데이터가 필요합니다."
        )
    
    async def _find_relevant_papers(self, papers: List[Dict[str, Any]], 
                                  keywords: List[str], threshold: float) -> List[Dict[str, Any]]:
        """키워드 기반으로 관련 논문 찾기"""
        try:
            # 키워드를 결합하여 쿼리 생성
            query = " ".join(keywords)
            logger.info(f"쿼리 생성: {query}")
            query_embedding = await openai_client.generate_embedding(query)
            logger.info(f"쿼리 임베딩 생성 완료: {len(query_embedding)} 차원")
            
            # 유사도 검색
            relevant_papers = await self.trend_repository.search_similar_papers(
                query_embedding=query_embedding,
                field=papers[0]['field'] if papers else None,
                limit=50,
                threshold=threshold
            )
            
            logger.info(f"유사도 검색 결과: {len(relevant_papers)}개 논문 발견")
            
            # 검색 결과가 없으면 원본 논문들 사용
            if not relevant_papers:
                logger.warning("유사도 검색 결과가 없어 원본 논문들을 사용합니다.")
                return papers[:20]  # 최대 20개만 사용
            
            return relevant_papers
            
        except Exception as e:
            logger.error(f"관련 논문 검색 실패: {e}")
            # 에러 발생 시 원본 논문들 사용
            return papers[:20]  # 최대 20개만 사용
    
    # 클러스터링과 워드클라우드 기능은 제거됨 (사용하지 않음)
    # async def _perform_clustering(self, papers: List[Dict[str, Any]]) -> List[Cluster]:
    #     """논문 클러스터링 수행 (제거됨)"""
    #     pass

    # async def _analyze_cluster(self, papers: List[Dict[str, Any]]) -> str:
    #     """클러스터 분석 (제거됨)"""
    #     pass

    # def _extract_cluster_keywords(self, papers: List[Dict[str, Any]]) -> List[str]:
    #     """클러스터 키워드 추출 (제거됨)"""
    #     pass

    # def _generate_wordcloud_data(self, papers: List[Dict[str, Any]]) -> Dict[str, int]:
    #     """워드클라우드 데이터 생성 (제거됨)"""
    #     pass
            text = (paper.get('title', '') + ' ' + paper.get('abstract', '')).lower()
            words = re.findall(r'\b\w+\b', text)
            for word in words:
                if len(word) <= 2:
                    continue
                if word in stopwords or word in custom_stopwords:
                    continue
                word_counter[word] += 1
        return dict(word_counter.most_common(50))
    
    async def _analyze_trends_with_llm(self, papers: List[Dict[str, Any]], 
                                     field: str, keywords: List[str]) -> str:
        """LLM으로 트렌드 분석"""
        abstracts = [paper.get('abstract', '') for paper in papers[:20]]
        
        return await openai_client.analyze_trends(abstracts, field, keywords)
    
    async def get_available_fields(self) -> List[str]:
        """사용 가능한 분야 목록 조회"""
        return await self.trend_repository.get_available_fields()
    
    async def get_field_statistics(self, field: str) -> Dict[str, Any]:
        """분야별 통계 조회"""
        return await self.trend_repository.get_field_statistics(field) 