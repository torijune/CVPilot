from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Cluster:
    """클러스터 엔티티"""
    id: int
    papers: List[Dict[str, Any]]
    keywords: List[str]
    summary: str
    centroid: List[float]
    
    def get_paper_count(self) -> int:
        """클러스터 내 논문 수 반환"""
        return len(self.papers)
    
    def get_keywords_str(self) -> str:
        """키워드를 문자열로 반환"""
        return ", ".join(self.keywords)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'paper_count': self.get_paper_count(),
            'keywords': self.keywords,
            'summary': self.summary,
            'papers': self.papers
        } 