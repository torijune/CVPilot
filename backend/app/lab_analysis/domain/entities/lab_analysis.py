from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Professor:
    """교수 엔티티"""
    name: str
    university: str
    research_areas: List[str]
    publications: List[str]
    category_scores: Dict[str, float]
    primary_category: str
    url: Optional[str] = None

@dataclass
class LabAnalysis:
    """연구실 분석 엔티티"""
    id: str
    field: str
    professors: List[Professor]
    selected_professor: Optional[Professor] = None
    analysis_result: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class LabAnalysisResult:
    """연구실 분석 결과 엔티티"""
    id: str
    professor_name: str
    university_name: str
    field: str
    recent_publications: List[Dict[str, str]]
    analysis_summary: str
    research_trends: str
    key_insights: str
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now() 