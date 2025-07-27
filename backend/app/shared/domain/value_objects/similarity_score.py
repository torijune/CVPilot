from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass(frozen=True)
class SimilarityScore:
    """유사도 점수 값 객체"""
    score: float
    paper_id: int
    paper_title: str
    
    def __post_init__(self):
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("Similarity score must be between 0.0 and 1.0")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'score': self.score,
            'paper_id': self.paper_id,
            'paper_title': self.paper_title
        }

@dataclass
class SimilarityResult:
    """유사도 검색 결과"""
    query: str
    results: List[SimilarityScore]
    total_count: int
    
    def get_top_k(self, k: int) -> List[SimilarityScore]:
        """상위 k개 결과 반환"""
        return sorted(self.results, key=lambda x: x.score, reverse=True)[:k]
    
    def filter_by_threshold(self, threshold: float) -> List[SimilarityScore]:
        """임계값 이상의 결과만 필터링"""
        return [result for result in self.results if result.score >= threshold] 