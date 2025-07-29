from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import uuid

@dataclass
class Paper:
    """논문 엔티티"""
    id: str
    title: str
    abstract: str
    authors: List[str]
    conference: Optional[str]
    year: Optional[int]
    field: str
    url: Optional[str]
    created_at: datetime
    
    @classmethod
    def create(cls, title: str, abstract: str, authors: List[str], 
               conference: Optional[str] = None, year: Optional[int] = None,
               field: str = "", url: Optional[str] = None) -> 'Paper':
        """Paper 엔티티 생성"""
        return cls(
            id=str(uuid.uuid4()),
            title=title,
            abstract=abstract,
            authors=authors,
            conference=conference,
            year=year,
            field=field,
            url=url,
            created_at=datetime.now()
        )
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "title": self.title,
            "abstract": self.abstract,
            "authors": self.authors,
            "conference": self.conference,
            "year": self.year,
            "field": self.field,
            "url": self.url,
            "created_at": self.created_at.isoformat()
        } 