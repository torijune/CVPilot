from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import uuid

@dataclass
class PodcastAnalysis:
    """팟캐스트 분석 엔티티"""
    id: str
    field: str
    papers: List[Dict[str, Any]]
    analysis_text: str
    audio_file_path: str
    duration_seconds: int
    created_at: datetime
    
    @classmethod
    def create(cls, field: str, papers: List[Dict[str, Any]], 
               analysis_text: str, audio_file_path: str = "", 
               duration_seconds: int = 0) -> 'PodcastAnalysis':
        """팟캐스트 분석 엔티티 생성"""
        return cls(
            id=str(uuid.uuid4()),
            field=field,
            papers=papers,
            analysis_text=analysis_text,
            audio_file_path=audio_file_path,
            duration_seconds=duration_seconds,
            created_at=datetime.now()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'field': self.field,
            'papers': self.papers,
            'analysis_text': self.analysis_text,
            'audio_file_path': self.audio_file_path,
            'duration_seconds': self.duration_seconds,
            'created_at': self.created_at.isoformat()
        } 