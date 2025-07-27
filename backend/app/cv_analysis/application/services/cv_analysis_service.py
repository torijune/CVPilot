from typing import List, Dict, Any, Optional
import logging
import re
from ...domain.repositories.cv_repository import CVRepository
from ...domain.entities.cv_analysis import CVAnalysis
from ...domain.value_objects.cv_skill import CVSkill, SkillLevel, SkillCategory, SkillAssessment
from ...domain.value_objects.radar_chart_data import CVRadarChartData
from app.shared.infra.external.openai_client import openai_client

logger = logging.getLogger(__name__)

class CVAnalysisService:
    """CV 분석 서비스"""
    
    def __init__(self, cv_repository: CVRepository):
        self.cv_repository = cv_repository
    
    async def analyze_cv(self, cv_text: str, field: str = "Machine Learning / Deep Learning (ML/DL)") -> CVAnalysis:
        """CV 분석 수행"""
        try:
            logger.info(f"CV 분석 시작: {field} 분야")
            
            # 1. CV 텍스트에서 스킬 추출
            skills = await self._extract_skills_from_cv(cv_text)
            
            # 2. 경험 추출
            experiences = await self._extract_experiences_from_cv(cv_text)
            
            # 3. 트렌드 분석 결과 조회
            trend_analysis = await self.cv_repository.get_trend_analysis(field)
            
            # 4. 필수 스킬 목록 조회
            required_skills = await self.cv_repository.get_required_skills(field)
            
            # 5. 강점/약점 분석
            strengths, weaknesses = await self._analyze_strengths_weaknesses(
                skills, experiences, trend_analysis, required_skills
            )
            
            # 6. 레이더 차트 데이터 생성
            radar_chart_data = await self._generate_radar_chart_data(
                skills, experiences, trend_analysis
            )
            
            # 7. 결과 생성
            cv_analysis = CVAnalysis.create(
                cv_text=cv_text,
                skills=skills,
                experiences=experiences,
                strengths=strengths,
                weaknesses=weaknesses,
                radar_chart_data=radar_chart_data.to_dict()
            )
            
            # 8. 결과 저장
            await self.cv_repository.save_cv_analysis(cv_analysis)
            
            logger.info(f"CV 분석 완료: {len(skills)}개 스킬, {len(experiences)}개 경험")
            return cv_analysis
            
        except Exception as e:
            logger.error(f"CV 분석 실패: {e}")
            raise
    
    async def _extract_skills_from_cv(self, cv_text: str) -> List[str]:
        """CV에서 스킬 추출"""
        try:
            # LLM을 사용하여 스킬 추출
            prompt = f"""
            다음 CV 텍스트에서 기술 스킬들을 추출해주세요:
            
            {cv_text[:2000]}...
            
            프로그래밍 언어, 프레임워크, 도구, 기술 등을 추출하여 쉼표로 구분된 리스트로 반환해주세요.
            예시: Python, TensorFlow, PyTorch, Docker, AWS, Git
            """
            
            response = await openai_client._call_chat_completion(prompt)
            
            # 응답을 파싱하여 스킬 리스트 생성
            skills = [skill.strip() for skill in response.split(',') if skill.strip()]
            
            return skills
            
        except Exception as e:
            logger.error(f"스킬 추출 실패: {e}")
            return []
    
    async def _extract_experiences_from_cv(self, cv_text: str) -> List[Dict[str, Any]]:
        """CV에서 경험 추출"""
        try:
            # LLM을 사용하여 경험 추출
            prompt = f"""
            다음 CV 텍스트에서 프로젝트 경험들을 추출해주세요:
            
            {cv_text[:2000]}...
            
            각 경험에 대해 다음 형식으로 JSON 배열로 반환해주세요:
            [
                {{
                    "title": "프로젝트 제목",
                    "description": "프로젝트 설명",
                    "duration": "기간",
                    "technologies": ["사용 기술들"],
                    "role": "역할"
                }}
            ]
            """
            
            response = await openai_client._call_chat_completion(prompt)
            
            # JSON 파싱 (간단한 구현)
            import json
            try:
                experiences = json.loads(response)
                return experiences if isinstance(experiences, list) else []
            except:
                return []
            
        except Exception as e:
            logger.error(f"경험 추출 실패: {e}")
            return []
    
    async def _analyze_strengths_weaknesses(self, skills: List[str], 
                                          experiences: List[Dict[str, Any]], 
                                          trend_analysis: Optional[Dict[str, Any]], 
                                          required_skills: List[str]) -> tuple[List[str], List[str]]:
        """강점/약점 분석"""
        try:
            # LLM을 사용하여 강점/약점 분석
            prompt = f"""
            다음 정보를 바탕으로 CV의 강점과 약점을 분석해주세요:
            
            스킬: {', '.join(skills)}
            경험: {len(experiences)}개 프로젝트
            필수 스킬: {', '.join(required_skills)}
            트렌드: {trend_analysis.get('trend_summary', '') if trend_analysis else 'N/A'}
            
            강점과 약점을 각각 3-5개씩 한국어로 작성해주세요.
            형식:
            강점:
            1. ...
            2. ...
            
            약점:
            1. ...
            2. ...
            """
            
            response = await openai_client._call_chat_completion(prompt)
            
            # 응답을 강점과 약점으로 분리
            strengths = []
            weaknesses = []
            
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if '강점:' in line:
                    current_section = 'strengths'
                elif '약점:' in line:
                    current_section = 'weaknesses'
                elif line.startswith(('1.', '2.', '3.', '4.', '5.')) and current_section:
                    content = line.split('.', 1)[1].strip()
                    if current_section == 'strengths':
                        strengths.append(content)
                    else:
                        weaknesses.append(content)
            
            return strengths, weaknesses
            
        except Exception as e:
            logger.error(f"강점/약점 분석 실패: {e}")
            return [], []
    
    async def _generate_radar_chart_data(self, skills: List[str], 
                                        experiences: List[Dict[str, Any]], 
                                        trend_analysis: Optional[Dict[str, Any]]) -> CVRadarChartData:
        """레이더 차트 데이터 생성"""
        try:
            # 간단한 점수 계산 로직
            research_ability = self._calculate_research_score(skills, experiences)
            development_skill = self._calculate_development_score(skills, experiences)
            awards_achievements = self._calculate_awards_score(experiences)
            latest_tech_trend = self._calculate_trend_score(skills, trend_analysis)
            academic_background = self._calculate_academic_score(experiences)
            project_experience = self._calculate_project_score(experiences)
            
            return CVRadarChartData(
                research_ability=research_ability,
                development_skill=development_skill,
                awards_achievements=awards_achievements,
                latest_tech_trend=latest_tech_trend,
                academic_background=academic_background,
                project_experience=project_experience
            )
            
        except Exception as e:
            logger.error(f"레이더 차트 데이터 생성 실패: {e}")
            # 기본값 반환
            return CVRadarChartData(
                research_ability=0.5,
                development_skill=0.5,
                awards_achievements=0.5,
                latest_tech_trend=0.5,
                academic_background=0.5,
                project_experience=0.5
            )
    
    def _calculate_research_score(self, skills: List[str], experiences: List[Dict[str, Any]]) -> float:
        """연구 능력 점수 계산"""
        research_keywords = ['research', 'paper', '논문', '연구', 'publication', 'conference']
        score = 0.0
        
        for skill in skills:
            if any(keyword in skill.lower() for keyword in research_keywords):
                score += 0.2
        
        for exp in experiences:
            if any(keyword in exp.get('description', '').lower() for keyword in research_keywords):
                score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_development_score(self, skills: List[str], experiences: List[Dict[str, Any]]) -> float:
        """개발 스킬 점수 계산"""
        dev_keywords = ['python', 'java', 'javascript', 'c++', 'tensorflow', 'pytorch', 'docker', 'aws']
        score = 0.0
        
        for skill in skills:
            if any(keyword in skill.lower() for keyword in dev_keywords):
                score += 0.15
        
        score += len(experiences) * 0.1
        
        return min(score, 1.0)
    
    def _calculate_awards_score(self, experiences: List[Dict[str, Any]]) -> float:
        """수상/성과 점수 계산"""
        award_keywords = ['award', 'prize', '수상', '상', 'competition', '대회']
        score = 0.0
        
        for exp in experiences:
            if any(keyword in exp.get('description', '').lower() for keyword in award_keywords):
                score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_trend_score(self, skills: List[str], trend_analysis: Optional[Dict[str, Any]]) -> float:
        """최신 기술 트렌드 점수 계산"""
        trend_keywords = ['ai', 'ml', 'deep learning', 'transformer', 'gpt', 'llm', 'vision', 'nlp']
        score = 0.0
        
        for skill in skills:
            if any(keyword in skill.lower() for keyword in trend_keywords):
                score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_academic_score(self, experiences: List[Dict[str, Any]]) -> float:
        """학술 배경 점수 계산"""
        academic_keywords = ['university', '대학', '학과', '학부', '대학원', 'phd', 'master']
        score = 0.0
        
        for exp in experiences:
            if any(keyword in exp.get('description', '').lower() for keyword in academic_keywords):
                score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_project_score(self, experiences: List[Dict[str, Any]]) -> float:
        """프로젝트 경험 점수 계산"""
        score = len(experiences) * 0.2
        return min(score, 1.0)
    
    async def get_cv_analysis(self, analysis_id: str) -> Optional[CVAnalysis]:
        """CV 분석 결과 조회"""
        return await self.cv_repository.get_cv_analysis(analysis_id) 