import json
import os
from typing import List, Dict, Optional
from ...domain.value_objects.research_area_mapper import ResearchAreaMapper
from ...infra.external.supabase_client import supabase_client

class LabSearchService:
    """연구실 검색 및 필터링 서비스"""
    
    def __init__(self, config_file_path: str = None):
        """
        초기화
        
        Args:
            config_file_path: 연구실 데이터 파일 경로 (더 이상 사용하지 않음)
        """
        self.supabase_client = supabase_client
        self.labs_data = []  # 초기화 시에는 빈 리스트, 필요할 때 로드
    
    async def _load_labs_data(self) -> List[Dict]:
        """Supabase에서 연구실 데이터 로드"""
        try:
            if not self.supabase_client.client:
                print("⚠️ Supabase 연결이 없습니다.")
                return []
            
            # professors 테이블에서 모든 데이터 가져오기
            result = self.supabase_client.client.table("professors").select("*").execute()
            professors = result.data
            
            # 데이터 형식 변환
            all_labs = []
            for prof in professors:
                # 연구 분야를 리스트로 변환
                research_areas = []
                if prof.get('field'):
                    research_areas = [area.strip() for area in prof['field'].split(',') if area.strip()]
                
                # 논문을 리스트로 변환
                publications = []
                if prof.get('publications'):
                    publications = [pub.strip() for pub in prof['publications'].split(';') if pub.strip()]
                
                lab_data = {
                    "professor": prof.get('name', ''),
                    "university": prof.get('university', ''),
                    "url": prof.get('lab', ''),
                    "research_areas": research_areas,
                    "publications": publications
                }
                all_labs.append(lab_data)
            
            print(f"✅ Supabase에서 {len(all_labs)}명의 교수 데이터 로드 완료")
            return all_labs
            
        except Exception as e:
            print(f"❌ 연구실 데이터 로드 실패: {e}")
            return []
    
    async def search_labs_by_category(self, category: str, min_score: float = 0.3) -> List[Dict]:
        """
        카테고리별 연구실 검색
        
        Args:
            category: 검색할 카테고리
            min_score: 최소 매칭 점수
            
        Returns:
            필터링된 연구실 리스트
        """
        # 데이터가 없으면 먼저 로드
        if not self.labs_data:
            self.labs_data = await self._load_labs_data()
        
        return ResearchAreaMapper.filter_labs_by_category(
            self.labs_data, category, min_score
        )
    
    async def search_labs_by_keyword(self, keyword: str) -> List[Dict]:
        """
        키워드로 연구실 검색
        
        Args:
            keyword: 검색 키워드
            
        Returns:
            검색 결과 리스트
        """
        # 데이터가 없으면 먼저 로드
        if not self.labs_data:
            self.labs_data = await self._load_labs_data()
        
        results = []
        keyword_lower = keyword.lower()
        
        for lab in self.labs_data:
            # 교수명 검색
            if keyword_lower in lab.get("professor", "").lower():
                results.append(lab)
                continue
            
            # 대학명 검색
            if keyword_lower in lab.get("university", "").lower():
                results.append(lab)
                continue
            
            # 연구 분야 검색
            for area in lab.get("research_areas", []):
                if keyword_lower in area.lower():
                    results.append(lab)
                    break
            
            # 논문 제목 검색
            for paper in lab.get("publications", []):
                if keyword_lower in paper.lower():
                    results.append(lab)
                    break
        
        return results
    
    async def get_labs_by_university(self, university_name: str) -> List[Dict]:
        """
        대학별 연구실 조회
        
        Args:
            university_name: 대학명
            
        Returns:
            해당 대학의 연구실 리스트
        """
        # 데이터가 없으면 먼저 로드
        if not self.labs_data:
            self.labs_data = await self._load_labs_data()
        
        return [
            lab for lab in self.labs_data 
            if lab.get("university", "").lower() == university_name.lower()
        ]
    
    async def get_category_statistics(self) -> Dict[str, int]:
        """
        카테고리별 통계 조회
        
        Returns:
            카테고리별 연구실 수
        """
        # 데이터가 없으면 먼저 로드
        if not self.labs_data:
            self.labs_data = await self._load_labs_data()
        
        return ResearchAreaMapper.get_category_statistics(self.labs_data)
    
    async def get_lab_details(self, professor_name: str, university_name: str = None) -> Optional[Dict]:
        """
        특정 연구실 상세 정보 조회
        
        Args:
            professor_name: 교수명
            university_name: 대학명 (선택사항)
            
        Returns:
            연구실 상세 정보
        """
        # 데이터가 없으면 먼저 로드
        if not self.labs_data:
            self.labs_data = await self._load_labs_data()
        
        for lab in self.labs_data:
            if lab.get("professor") == professor_name:
                if university_name is None or lab.get("university") == university_name:
                    # 카테고리 점수 추가
                    if "research_areas" in lab:
                        category_scores = ResearchAreaMapper.map_research_areas_to_categories(
                            lab["research_areas"]
                        )
                        lab_with_scores = lab.copy()
                        lab_with_scores["category_scores"] = category_scores
                        lab_with_scores["primary_category"] = ResearchAreaMapper.get_primary_category(
                            lab["research_areas"]
                        )
                        return lab_with_scores
                    return lab
        
        return None
    
    async def get_recommended_labs(self, target_category: str, limit: int = 10) -> List[Dict]:
        """
        특정 카테고리의 추천 연구실 조회
        
        Args:
            target_category: 타겟 카테고리
            limit: 조회할 연구실 수
            
        Returns:
            추천 연구실 리스트
        """
        filtered_labs = await self.search_labs_by_category(target_category, min_score=0.5)
        return filtered_labs[:limit]
    
    async def get_all_universities(self) -> List[str]:
        """
        모든 대학 목록 조회
        
        Returns:
            대학명 리스트
        """
        # 데이터가 없으면 먼저 로드
        if not self.labs_data:
            self.labs_data = await self._load_labs_data()
        
        universities = set()
        for lab in self.labs_data:
            if lab.get("university"):
                universities.add(lab["university"])
        
        return sorted(list(universities)) 