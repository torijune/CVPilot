from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class RadarChartData:
    """레이더 차트 데이터 값 객체"""
    categories: List[str]
    scores: Dict[str, float]
    max_score: float = 1.0
    
    def __post_init__(self):
        if not self.categories:
            raise ValueError("카테고리는 비어있을 수 없습니다.")
        if not self.scores:
            raise ValueError("점수는 비어있을 수 없습니다.")
        if self.max_score <= 0:
            raise ValueError("최대 점수는 0보다 커야 합니다.")
    
    def get_normalized_scores(self) -> Dict[str, float]:
        """정규화된 점수 반환 (0-1 범위)"""
        return {
            category: min(score / self.max_score, 1.0)
            for category, score in self.scores.items()
        }
    
    def get_average_score(self) -> float:
        """평균 점수 계산"""
        if not self.scores:
            return 0.0
        return sum(self.scores.values()) / len(self.scores)
    
    def get_top_categories(self, limit: int = 5) -> List[tuple]:
        """상위 카테고리 반환"""
        sorted_categories = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_categories[:limit]
    
    def get_bottom_categories(self, limit: int = 5) -> List[tuple]:
        """하위 카테고리 반환"""
        sorted_categories = sorted(self.scores.items(), key=lambda x: x[1])
        return sorted_categories[:limit]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'categories': self.categories,
            'scores': self.scores,
            'normalized_scores': self.get_normalized_scores(),
            'average_score': self.get_average_score(),
            'top_categories': self.get_top_categories(),
            'bottom_categories': self.get_bottom_categories()
        }

@dataclass
class CVRadarChartData:
    """CV 레이더 차트 데이터"""
    research_ability: float
    development_skill: float
    awards_achievements: float
    latest_tech_trend: float
    academic_background: float
    project_experience: float
    
    def __post_init__(self):
        # 모든 점수가 0-1 범위인지 확인
        scores = [
            self.research_ability, self.development_skill, self.awards_achievements,
            self.latest_tech_trend, self.academic_background, self.project_experience
        ]
        for score in scores:
            if not 0.0 <= score <= 1.0:
                raise ValueError("모든 점수는 0.0과 1.0 사이여야 합니다.")
    
    def to_radar_chart_data(self) -> RadarChartData:
        """RadarChartData로 변환"""
        categories = [
            "연구 능력", "개발 스킬", "수상/성과", 
            "최신 기술 트렌드", "학술 배경", "프로젝트 경험"
        ]
        scores = {
            "연구 능력": self.research_ability,
            "개발 스킬": self.development_skill,
            "수상/성과": self.awards_achievements,
            "최신 기술 트렌드": self.latest_tech_trend,
            "학술 배경": self.academic_background,
            "프로젝트 경험": self.project_experience
        }
        return RadarChartData(categories=categories, scores=scores)
    
    def get_overall_score(self) -> float:
        """전체 점수 계산"""
        scores = [
            self.research_ability, self.development_skill, self.awards_achievements,
            self.latest_tech_trend, self.academic_background, self.project_experience
        ]
        return sum(scores) / len(scores)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'research_ability': self.research_ability,
            'development_skill': self.development_skill,
            'awards_achievements': self.awards_achievements,
            'latest_tech_trend': self.latest_tech_trend,
            'academic_background': self.academic_background,
            'project_experience': self.project_experience,
            'overall_score': self.get_overall_score(),
            'radar_chart_data': self.to_radar_chart_data().to_dict()
        } 