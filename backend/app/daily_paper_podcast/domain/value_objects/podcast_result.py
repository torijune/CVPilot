from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class PodcastResult:
    """팟캐스트 결과 값 객체"""
    field: str
    papers: List[Dict[str, Any]]
    analysis_text: str
    audio_file_path: str
    duration_seconds: int
    created_at: datetime
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "field": self.field,
            "papers": self.papers,
            "analysis_text": self.analysis_text,
            "audio_file_path": self.audio_file_path,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat()
        } 