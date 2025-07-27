from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import uuid

@dataclass
class FeedbackAnalysis:
    """피드백 분석 엔티티"""
    id: str
    cv_analysis_id: str
    improvement_projects: List[Dict[str, Any]]
    skill_recommendations: List[str]
    career_path_suggestions: List[str]
    created_at: datetime
    
    @classmethod
    def create(cls, cv_analysis_id: str, improvement_projects: List[Dict[str, Any]], 
               skill_recommendations: List[str], career_path_suggestions: List[str]) -> 'FeedbackAnalysis':
        """피드백 분석 엔티티 생성"""
        return cls(
            id=str(uuid.uuid4()),
            cv_analysis_id=cv_analysis_id,
            improvement_projects=improvement_projects,
            skill_recommendations=skill_recommendations,
            career_path_suggestions=career_path_suggestions,
            created_at=datetime.now()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'cv_analysis_id': self.cv_analysis_id,
            'improvement_projects': self.improvement_projects,
            'skill_recommendations': self.skill_recommendations,
            'career_path_suggestions': self.career_path_suggestions,
            'created_at': self.created_at.isoformat()
        } 