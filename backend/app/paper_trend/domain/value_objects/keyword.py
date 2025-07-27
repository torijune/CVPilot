from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Keyword:
    """키워드 값 객체"""
    value: str
    frequency: int = 1
    
    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("키워드는 비어있을 수 없습니다.")
        if self.frequency < 1:
            raise ValueError("빈도는 1 이상이어야 합니다.")
    
    def __str__(self) -> str:
        return self.value
    
    def __hash__(self) -> int:
        return hash(self.value)

@dataclass
class KeywordSet:
    """키워드 집합"""
    keywords: List[Keyword]
    
    def get_top_keywords(self, limit: int = 10) -> List[Keyword]:
        """상위 키워드 반환"""
        sorted_keywords = sorted(self.keywords, key=lambda k: k.frequency, reverse=True)
        return sorted_keywords[:limit]
    
    def get_keyword_strings(self) -> List[str]:
        """키워드 문자열 리스트 반환"""
        return [keyword.value for keyword in self.keywords]
    
    def add_keyword(self, keyword: Keyword):
        """키워드 추가"""
        # 이미 존재하는 키워드인지 확인
        for existing in self.keywords:
            if existing.value == keyword.value:
                # 빈도 증가
                object.__setattr__(existing, 'frequency', existing.frequency + keyword.frequency)
                return
        
        self.keywords.append(keyword) 