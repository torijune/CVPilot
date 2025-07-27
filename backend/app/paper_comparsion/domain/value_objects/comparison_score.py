from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum

class ComparisonType(Enum):
    """비교 유형"""
    METHODOLOGY = "methodology"
    INNOVATION = "innovation"
    DIFFERENTIATION = "differentiation"
    REVIEWER_FEEDBACK = "reviewer_feedback"

@dataclass(frozen=True)
class ComparisonScore:
    """비교 점수 값 객체"""
    score: float
    comparison_type: ComparisonType
    description: str
    
    def __post_init__(self):
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("비교 점수는 0.0과 1.0 사이여야 합니다.")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'score': self.score,
            'comparison_type': self.comparison_type.value,
            'description': self.description
        }

@dataclass
class ComparisonResult:
    """비교 결과"""
    user_idea: str
    similar_papers: List[Dict[str, Any]]
    comparison_analysis: str
    differentiation_strategy: str
    reviewer_feedback: str
    scores: Dict[ComparisonType, ComparisonScore]
    
    def get_overall_score(self) -> float:
        """전체 점수 계산"""
        if not self.scores:
            return 0.0
        
        total_score = sum(score.score for score in self.scores.values())
        return total_score / len(self.scores)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_idea': self.user_idea,
            'similar_papers': self.similar_papers,
            'comparison_analysis': self.comparison_analysis,
            'differentiation_strategy': self.differentiation_strategy,
            'reviewer_feedback': self.reviewer_feedback,
            'scores': {k.value: v.to_dict() for k, v in self.scores.items()},
            'overall_score': self.get_overall_score()
        } 