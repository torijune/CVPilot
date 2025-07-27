from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class Paper:
    """공통 논문 엔티티"""
    id: int
    title: str
    abstract: str
    authors: List[str]
    conference: str
    year: int
    field: str
    url: Optional[str] = None
    title_embedding: Optional[List[float]] = None
    abstract_embedding: Optional[List[float]] = None
    combined_embedding: Optional[List[float]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'title': self.title,
            'abstract': self.abstract,
            'authors': self.authors,
            'conference': self.conference,
            'year': self.year,
            'field': self.field,
            'url': self.url,
            'title_embedding': self.title_embedding,
            'abstract_embedding': self.abstract_embedding,
            'combined_embedding': self.combined_embedding,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Paper':
        """딕셔너리에서 엔티티 생성"""
        return cls(
            id=data['id'],
            title=data['title'],
            abstract=data['abstract'],
            authors=data.get('authors', []),
            conference=data['conference'],
            year=data['year'],
            field=data['field'],
            url=data.get('url'),
            title_embedding=data.get('title_embedding'),
            abstract_embedding=data.get('abstract_embedding'),
            combined_embedding=data.get('combined_embedding'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        ) 