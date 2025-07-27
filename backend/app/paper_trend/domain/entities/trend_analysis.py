from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

@dataclass
class TrendAnalysis:
    """트렌드 분석 엔티티"""
    id: str
    field: str
    keywords: List[str]
    top_papers: List[Dict[str, Any]]
    wordcloud_data: Dict[str, int]
    trend_summary: str
    created_at: datetime
    
    @classmethod
    def create(cls, field: str, keywords: List[str], top_papers: List[Dict[str, Any]], 
               wordcloud_data: Dict[str, int], trend_summary: str) -> 'TrendAnalysis':
        """트렌드 분석 엔티티 생성"""
        return cls(
            id=str(uuid.uuid4()),
            field=field,
            keywords=keywords,
            top_papers=top_papers,
            wordcloud_data=wordcloud_data,
            trend_summary=trend_summary,
            created_at=datetime.now()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'field': self.field,
            'keywords': self.keywords,
            'top_papers': self.top_papers,
            'wordcloud_data': self.wordcloud_data,
            'trend_summary': self.trend_summary,
            'created_at': self.created_at.isoformat()
        } 