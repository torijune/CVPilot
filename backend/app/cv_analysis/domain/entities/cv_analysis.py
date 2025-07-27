from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import uuid

@dataclass
class CVAnalysis:
    """CV 분석 엔티티"""
    id: str
    cv_text: str
    skills: List[str]
    experiences: List[Dict[str, Any]]
    strengths: List[str]
    weaknesses: List[str]
    radar_chart_data: Dict[str, float]
    created_at: datetime
    
    @classmethod
    def create(cls, cv_text: str, skills: List[str], experiences: List[Dict[str, Any]], 
               strengths: List[str], weaknesses: List[str], 
               radar_chart_data: Dict[str, float]) -> 'CVAnalysis':
        """CV 분석 엔티티 생성"""
        return cls(
            id=str(uuid.uuid4()),
            cv_text=cv_text,
            skills=skills,
            experiences=experiences,
            strengths=strengths,
            weaknesses=weaknesses,
            radar_chart_data=radar_chart_data,
            created_at=datetime.now()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'cv_text': self.cv_text,
            'skills': self.skills,
            'experiences': self.experiences,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'radar_chart_data': self.radar_chart_data,
            'created_at': self.created_at.isoformat()
        } 