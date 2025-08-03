import logging
import arxiv
import requests
import feedparser
from typing import List, Optional, Dict
import re

logger = logging.getLogger(__name__)

class ArxivService:
    """Arxiv API 서비스"""
    
    def __init__(self):
        self.client = arxiv.Client()
    
    async def get_recent_publications(self, professor_name: str, university_name: str, limit: int = 10) -> List[Dict[str, str]]:
        """교수의 최신 논문 초록 수집"""
        try:
            logger.info(f"논문 초록 수집 시작: {professor_name} ({university_name})")
            
            # 교수명으로 검색 쿼리 생성
            search_query = f'au:"{professor_name}"'
            
            # 검색 수행
            search = arxiv.Search(
                query=search_query,
                max_results=limit,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            publications = []
            for result in self.client.results(search):
                # 초록에서 불필요한 문자 제거
                abstract = self._clean_abstract(result.summary)
                if abstract:
                    publications.append({
                        "title": result.title,
                        "abstract": abstract
                    })
                
                if len(publications) >= limit:
                    break
            
            logger.info(f"논문 초록 수집 완료: {len(publications)}개")
            return publications
            
        except Exception as e:
            logger.error(f"논문 초록 수집 실패: {e}")
            return []
    
    async def get_publications_from_titles(self, paper_titles: List[str], limit: int = 10) -> List[Dict[str, str]]:
        """논문 제목들로부터 초록 수집"""
        try:
            logger.info(f"논문 제목으로 초록 수집 시작: {len(paper_titles)}개 논문")
            
            publications = []
            
            for title in paper_titles[:limit]:
                try:
                    abstract = self._get_arxiv_abstract(title)
                    if abstract:
                        publications.append({
                            "title": title,
                            "abstract": abstract
                        })
                        logger.info(f"논문 초록 수집 성공: {title[:50]}...")
                    else:
                        logger.warning(f"논문 초록을 찾을 수 없음: {title}")
                except Exception as e:
                    logger.error(f"논문 초록 수집 실패 ({title}): {e}")
                    continue
                
                if len(publications) >= limit:
                    break
            
            logger.info(f"논문 초록 수집 완료: {len(publications)}개")
            return publications
            
        except Exception as e:
            logger.error(f"논문 제목으로 초록 수집 실패: {e}")
            return []
    
    def _get_arxiv_abstract(self, title: str) -> str:
        """논문 제목으로 Arxiv에서 초록 가져오기"""
        try:
            # 제목에서 특수문자 제거 및 정리
            clean_title = self._clean_title(title)
            
            # 1. 정확한 제목으로 검색
            base_url = "http://export.arxiv.org/api/query"
            params = {
                "search_query": f'ti:"{clean_title}"',
                "max_results": 1
            }
            
            response = requests.get(base_url, params=params)
            feed = feedparser.parse(response.text)
            
            if feed.entries:
                abstract = feed.entries[0].summary
                return self._clean_abstract(abstract)
            
            # 2. 제목에서 따옴표 제거하고 검색
            clean_title_no_quotes = clean_title.replace('"', '').replace("'", '')
            params = {
                "search_query": f'ti:"{clean_title_no_quotes}"',
                "max_results": 1
            }
            
            response = requests.get(base_url, params=params)
            feed = feedparser.parse(response.text)
            
            if feed.entries:
                abstract = feed.entries[0].summary
                return self._clean_abstract(abstract)
            
            # 3. 부분 검색 시도
            return self._search_partial_title(clean_title)
                
        except Exception as e:
            logger.error(f"Arxiv 초록 검색 실패 ({title}): {e}")
            return ""
    
    def _search_partial_title(self, title: str) -> str:
        """부분 제목으로 검색 시도"""
        try:
            # 제목의 주요 키워드들만 추출
            keywords = self._extract_keywords(title)
            if not keywords:
                return ""
            
            # 여러 키워드로 검색 시도
            for keyword in keywords[:2]:  # 상위 2개 키워드만 사용
                search_query = f'ti:"{keyword}"'
                
                base_url = "http://export.arxiv.org/api/query"
                params = {
                    "search_query": search_query,
                    "max_results": 10
                }
                
                response = requests.get(base_url, params=params)
                feed = feedparser.parse(response.text)
                
                if feed.entries:
                    # 가장 유사한 제목 찾기
                    best_match = self._find_best_match(title, [entry.title for entry in feed.entries])
                    if best_match:
                        return self._clean_abstract(feed.entries[0].summary)
            
            # 키워드 검색도 실패한 경우, 제목의 첫 부분으로 검색
            first_part = title.split(':')[0].split(' - ')[0].strip()
            if len(first_part) > 10:
                search_query = f'ti:"{first_part}"'
                
                params = {
                    "search_query": search_query,
                    "max_results": 5
                }
                
                response = requests.get(base_url, params=params)
                feed = feedparser.parse(response.text)
                
                if feed.entries:
                    best_match = self._find_best_match(title, [entry.title for entry in feed.entries])
                    if best_match:
                        return self._clean_abstract(feed.entries[0].summary)
            
            return ""
            
        except Exception as e:
            logger.error(f"부분 제목 검색 실패 ({title}): {e}")
            return ""
    
    def _extract_keywords(self, title: str) -> List[str]:
        """제목에서 주요 키워드 추출"""
        # 불용어 제거
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall'}
        
        # 제목을 단어로 분리하고 필터링
        words = re.findall(r'\b\w+\b', title.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:3]  # 상위 3개 키워드만 반환
    
    def _find_best_match(self, original_title: str, candidate_titles: List[str]) -> bool:
        """가장 유사한 제목 찾기"""
        original_lower = original_title.lower()
        
        for candidate in candidate_titles:
            candidate_lower = candidate.lower()
            # 간단한 유사도 계산 (공통 단어 수)
            original_words = set(re.findall(r'\b\w+\b', original_lower))
            candidate_words = set(re.findall(r'\b\w+\b', candidate_lower))
            
            common_words = original_words.intersection(candidate_words)
            if len(common_words) >= 2:  # 최소 2개 이상의 공통 단어가 있으면 매치
                return True
        
        return False
    
    def _clean_title(self, title: str) -> str:
        """논문 제목 정리"""
        if not title:
            return ""
        
        # 특수문자 제거 및 정리
        cleaned = re.sub(r'[^\w\s\.\,\!\?\-\(\)]', '', title.strip())
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned
    
    def _clean_abstract(self, abstract: str) -> str:
        """초록 텍스트 정리"""
        if not abstract:
            return ""
        
        # 불필요한 공백 제거
        cleaned = re.sub(r'\s+', ' ', abstract.strip())
        
        # 특수 문자 정리
        cleaned = re.sub(r'[^\w\s\.\,\!\?\-\(\)]', '', cleaned)
        
        return cleaned
    
    async def search_by_keywords(self, keywords: List[str], limit: int = 10) -> List[Dict[str, str]]:
        """키워드로 논문 검색"""
        try:
            # 키워드를 OR 조건으로 결합
            query = ' OR '.join([f'ti:"{keyword}" OR abs:"{keyword}"' for keyword in keywords])
            
            search = arxiv.Search(
                query=query,
                max_results=limit,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            publications = []
            for result in self.client.results(search):
                abstract = self._clean_abstract(result.summary)
                if abstract:
                    publications.append({
                        "title": result.title,
                        "abstract": abstract
                    })
                
                if len(publications) >= limit:
                    break
            
            return publications
            
        except Exception as e:
            logger.error(f"키워드 검색 실패: {e}")
            return [] 


def get_arxiv_abstract(title: str) -> str:
    import requests
    import feedparser

    title = "Attention Is All You Need"
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": f'ti:"{title}"',
        "max_results": 1
    }
    response = requests.get(base_url, params=params)
    feed = feedparser.parse(response.text)

    if feed.entries:
        abstract = feed.entries[0].summary
        # print(abstract)  # 논문 초록 출력
        return abstract
    else:
        print("논문을 찾을 수 없습니다.")
        return ""
    
 