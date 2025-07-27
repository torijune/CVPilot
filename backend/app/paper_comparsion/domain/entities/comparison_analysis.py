from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import uuid

@dataclass
class ComparisonAnalysis:
    """방법론 비교 분석 엔티티"""
    id: str
    user_idea: str
    field: str
    similar_papers: List[Dict[str, Any]]
    comparison_analysis: str
    differentiation_strategy: str
    reviewer_feedback: str
    created_at: datetime
    
    @classmethod
    def create(cls, user_idea: str, field: str, similar_papers: List[Dict[str, Any]], 
               comparison_analysis: str, differentiation_strategy: str, 
               reviewer_feedback: str) -> 'ComparisonAnalysis':
        """비교 분석 엔티티 생성"""
        return cls(
            id=str(uuid.uuid4()),
            user_idea=user_idea,
            field=field,
            similar_papers=similar_papers,
            comparison_analysis=comparison_analysis,
            differentiation_strategy=differentiation_strategy,
            reviewer_feedback=reviewer_feedback,
            created_at=datetime.now()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'user_idea': self.user_idea,
            'field': self.field,
            'similar_papers': self.similar_papers,
            'comparison_analysis': self.comparison_analysis,
            'differentiation_strategy': self.differentiation_strategy,
            'reviewer_feedback': self.reviewer_feedback,
            'created_at': self.created_at.isoformat()
        } 