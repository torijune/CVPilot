import json
import os
from typing import List, Dict, Optional
from ...domain.value_objects.research_area_mapper import ResearchAreaMapper

class LabSearchService:
    """연구실 검색 및 필터링 서비스"""
    
    def __init__(self, config_file_path: str = None):
        """
        초기화
        
        Args:
            config_file_path: 연구실 데이터 파일 경로
        """
        if config_file_path is None:
            # 기본 경로 설정
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            config_file_path = os.path.join(current_dir, "utils", "crawl", "school_crawl", "simple_lab_config.json")
            
            # 경로가 존재하지 않으면 상대 경로로 시도
            if not os.path.exists(config_file_path):
                config_file_path = os.path.join(current_dir, "..", "utils", "crawl", "school_crawl", "simple_lab_config.json")
            
            # 여전히 존재하지 않으면 절대 경로로 시도
            if not os.path.exists(config_file_path):
                config_file_path = os.path.join(os.path.dirname(current_dir), "utils", "crawl", "school_crawl", "simple_lab_config.json")
            
            # 마지막 시도: 현재 작업 디렉토리 기준
            if not os.path.exists(config_file_path):
                config_file_path = os.path.join(os.getcwd(), "..", "utils", "crawl", "school_crawl", "simple_lab_config.json")
        
        self.config_file_path = config_file_path
        self.labs_data = self._load_labs_data()
    
    def _load_labs_data(self) -> List[Dict]:
        """연구실 데이터 로드"""
        try:
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 모든 연구실 데이터를 평면화
            all_labs = []
            for university in data.get("universities", []):
                university_name = university.get("name", "")
                for lab in university.get("labs", []):
                    lab_with_university = lab.copy()
                    lab_with_university["university"] = university_name
                    all_labs.append(lab_with_university)
            
            return all_labs
        except Exception as e:
            print(f"연구실 데이터 로드 실패: {e}")
            return []
    
    def search_labs_by_category(self, category: str, min_score: float = 0.3) -> List[Dict]:
        """
        카테고리별 연구실 검색
        
        Args:
            category: 검색할 카테고리
            min_score: 최소 매칭 점수
            
        Returns:
            필터링된 연구실 리스트
        """
        return ResearchAreaMapper.filter_labs_by_category(
            self.labs_data, category, min_score
        )
    
    def search_labs_by_keyword(self, keyword: str) -> List[Dict]:
        """
        키워드로 연구실 검색
        
        Args:
            keyword: 검색 키워드
            
        Returns:
            검색 결과 리스트
        """
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
    
    def get_labs_by_university(self, university_name: str) -> List[Dict]:
        """
        대학별 연구실 조회
        
        Args:
            university_name: 대학명
            
        Returns:
            해당 대학의 연구실 리스트
        """
        return [
            lab for lab in self.labs_data 
            if lab.get("university", "").lower() == university_name.lower()
        ]
    
    def get_category_statistics(self) -> Dict[str, int]:
        """
        카테고리별 통계 조회
        
        Returns:
            카테고리별 연구실 수
        """
        return ResearchAreaMapper.get_category_statistics(self.labs_data)
    
    def get_lab_details(self, professor_name: str, university_name: str = None) -> Optional[Dict]:
        """
        특정 연구실 상세 정보 조회
        
        Args:
            professor_name: 교수명
            university_name: 대학명 (선택사항)
            
        Returns:
            연구실 상세 정보
        """
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
    
    def get_recommended_labs(self, target_category: str, limit: int = 10) -> List[Dict]:
        """
        특정 카테고리의 추천 연구실 조회
        
        Args:
            target_category: 타겟 카테고리
            limit: 조회할 연구실 수
            
        Returns:
            추천 연구실 리스트
        """
        filtered_labs = self.search_labs_by_category(target_category, min_score=0.5)
        return filtered_labs[:limit]
    
    def get_all_universities(self) -> List[str]:
        """
        모든 대학 목록 조회
        
        Returns:
            대학명 리스트
        """
        universities = set()
        for lab in self.labs_data:
            if lab.get("university"):
                universities.add(lab["university"])
        
        return sorted(list(universities)) 