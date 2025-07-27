from typing import List, Dict, Any
import logging
from ...domain.entities.feedback_analysis import FeedbackAnalysis
from app.shared.infra.external.openai_client import openai_client

logger = logging.getLogger(__name__)

class FeedbackService:
    """CV 피드백 서비스"""
    
    def __init__(self):
        pass
    
    async def generate_feedback(self, cv_analysis_id: str, cv_analysis_data: Dict[str, Any]) -> FeedbackAnalysis:
        """CV 피드백 생성"""
        try:
            logger.info(f"CV 피드백 생성 시작: {cv_analysis_id}")
            
            # 1. 개선 프로젝트 제안
            improvement_projects = await self._generate_improvement_projects(cv_analysis_data)
            
            # 2. 스킬 추천
            skill_recommendations = await self._generate_skill_recommendations(cv_analysis_data)
            
            # 3. 커리어 패스 제안
            career_path_suggestions = await self._generate_career_path_suggestions(cv_analysis_data)
            
            # 4. 결과 생성
            feedback_analysis = FeedbackAnalysis.create(
                cv_analysis_id=cv_analysis_id,
                improvement_projects=improvement_projects,
                skill_recommendations=skill_recommendations,
                career_path_suggestions=career_path_suggestions
            )
            
            logger.info(f"CV 피드백 생성 완료: {len(improvement_projects)}개 프로젝트 제안")
            return feedback_analysis
            
        except Exception as e:
            logger.error(f"CV 피드백 생성 실패: {e}")
            raise
    
    async def _generate_improvement_projects(self, cv_analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """개선 프로젝트 제안 생성"""
        try:
            weaknesses = cv_analysis_data.get('weaknesses', [])
            skills = cv_analysis_data.get('skills', [])
            
            prompt = f"""
            다음 CV의 약점을 보완할 수 있는 프로젝트를 제안해주세요:
            
            현재 스킬: {', '.join(skills)}
            약점: {', '.join(weaknesses)}
            
            각 프로젝트에 대해 다음 형식으로 JSON 배열로 반환해주세요:
            [
                {{
                    "title": "프로젝트 제목",
                    "description": "프로젝트 설명",
                    "technologies": ["사용 기술들"],
                    "duration": "예상 기간",
                    "difficulty": "난이도",
                    "learning_outcomes": ["학습 목표들"]
                }}
            ]
            """
            
            response = await openai_client._call_chat_completion(prompt)
            
            # JSON 파싱 (간단한 구현)
            import json
            try:
                projects = json.loads(response)
                return projects if isinstance(projects, list) else []
            except:
                return []
                
        except Exception as e:
            logger.error(f"개선 프로젝트 생성 실패: {e}")
            return []
    
    async def _generate_skill_recommendations(self, cv_analysis_data: Dict[str, Any]) -> List[str]:
        """스킬 추천 생성"""
        try:
            current_skills = cv_analysis_data.get('skills', [])
            weaknesses = cv_analysis_data.get('weaknesses', [])
            
            prompt = f"""
            다음 CV를 개선하기 위해 추천하는 스킬들을 제안해주세요:
            
            현재 스킬: {', '.join(current_skills)}
            약점: {', '.join(weaknesses)}
            
            쉼표로 구분된 스킬 리스트로 반환해주세요.
            예시: Python, TensorFlow, Docker, AWS
            """
            
            response = await openai_client._call_chat_completion(prompt)
            
            # 응답을 파싱하여 스킬 리스트 생성
            skills = [skill.strip() for skill in response.split(',') if skill.strip()]
            
            return skills
            
        except Exception as e:
            logger.error(f"스킬 추천 생성 실패: {e}")
            return []
    
    async def _generate_career_path_suggestions(self, cv_analysis_data: Dict[str, Any]) -> List[str]:
        """커리어 패스 제안 생성"""
        try:
            strengths = cv_analysis_data.get('strengths', [])
            weaknesses = cv_analysis_data.get('weaknesses', [])
            
            prompt = f"""
            다음 CV를 바탕으로 추천하는 커리어 패스를 제안해주세요:
            
            강점: {', '.join(strengths)}
            약점: {', '.join(weaknesses)}
            
            각 커리어 패스에 대해 번호를 매겨 한국어로 작성해주세요.
            예시:
            1. AI/ML 엔지니어로 발전
            2. 연구원으로 전향
            3. 데이터 사이언티스트로 전환
            """
            
            response = await openai_client._call_chat_completion(prompt)
            
            # 응답을 라인별로 분리
            suggestions = [line.strip() for line in response.split('\n') if line.strip()]
            
            return suggestions
            
        except Exception as e:
            logger.error(f"커리어 패스 제안 생성 실패: {e}")
            return [] 