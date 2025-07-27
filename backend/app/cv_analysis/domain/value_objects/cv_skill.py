from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

class SkillLevel(Enum):
    """스킬 레벨"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class SkillCategory(Enum):
    """스킬 카테고리"""
    PROGRAMMING = "programming"
    FRAMEWORK = "framework"
    DATABASE = "database"
    CLOUD = "cloud"
    ML_AI = "ml_ai"
    RESEARCH = "research"
    SOFT_SKILL = "soft_skill"

@dataclass
class CVSkill:
    """CV 스킬 값 객체"""
    name: str
    level: SkillLevel
    category: SkillCategory
    years_experience: float = 0.0
    description: str = ""
    
    def __post_init__(self):
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("스킬 이름은 비어있을 수 없습니다.")
        if self.years_experience < 0:
            raise ValueError("경력 연수는 0 이상이어야 합니다.")
    
    def get_level_score(self) -> float:
        """레벨에 따른 점수 반환"""
        level_scores = {
            SkillLevel.BEGINNER: 0.25,
            SkillLevel.INTERMEDIATE: 0.5,
            SkillLevel.ADVANCED: 0.75,
            SkillLevel.EXPERT: 1.0
        }
        return level_scores.get(self.level, 0.0)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'level': self.level.value,
            'category': self.category.value,
            'years_experience': self.years_experience,
            'description': self.description,
            'level_score': self.get_level_score()
        }

@dataclass
class SkillAssessment:
    """스킬 평가"""
    skill: CVSkill
    market_demand: float  # 0-1
    relevance_score: float  # 0-1
    improvement_needed: bool
    
    def get_overall_score(self) -> float:
        """전체 점수 계산"""
        level_score = self.skill.get_level_score()
        return (level_score + self.market_demand + self.relevance_score) / 3
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'skill': self.skill.to_dict(),
            'market_demand': self.market_demand,
            'relevance_score': self.relevance_score,
            'improvement_needed': self.improvement_needed,
            'overall_score': self.get_overall_score()
        } 