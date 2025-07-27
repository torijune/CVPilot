from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class WordcloudData:
    """워드클라우드 데이터 값 객체"""
    word_frequencies: Dict[str, int]
    max_frequency: int = 0
    min_frequency: int = 0
    
    def __post_init__(self):
        if self.word_frequencies:
            self.max_frequency = max(self.word_frequencies.values())
            self.min_frequency = min(self.word_frequencies.values())
    
    def get_top_words(self, limit: int = 50) -> List[Tuple[str, int]]:
        """상위 단어 반환"""
        sorted_words = sorted(self.word_frequencies.items(), key=lambda x: x[1], reverse=True)
        return sorted_words[:limit]
    
    def get_normalized_frequencies(self) -> Dict[str, float]:
        """정규화된 빈도 반환 (0-1 범위)"""
        if self.max_frequency == 0:
            return {}
        
        return {
            word: freq / self.max_frequency 
            for word, freq in self.word_frequencies.items()
        }
    
    def filter_by_minimum_frequency(self, min_freq: int) -> 'WordcloudData':
        """최소 빈도로 필터링"""
        filtered_freqs = {
            word: freq for word, freq in self.word_frequencies.items()
            if freq >= min_freq
        }
        return WordcloudData(filtered_freqs)
    
    def to_dict(self) -> Dict[str, int]:
        """딕셔너리로 변환"""
        return self.word_frequencies.copy() 