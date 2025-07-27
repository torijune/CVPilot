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
            
            # 1. 트렌드 분석 결과 조회
            trend_analysis = await self.cv_repository.get_trend_analysis(field)
            
            # 2. 필수 스킬 목록 조회
            required_skills = await self.cv_repository.get_required_skills(field)
            
            # 3. 강점/약점 분석 (LLM이 직접 CV 전체를 분석)
            strengths, weaknesses = await self._analyze_strengths_weaknesses(
                cv_text, field, trend_analysis, required_skills
            )
            
            # 4. 레이더 차트 데이터 생성 (LLM이 직접 CV 전체를 분석)
            radar_chart_data = await self._generate_radar_chart_data(
                cv_text, field, trend_analysis
            )
            
            # 5. 스킬 추출 (LLM이 직접 분석)
            skills = await self._extract_skills_from_cv(cv_text, field)
            
            # 6. 경험 추출 (LLM이 직접 분석)
            experiences = await self._extract_experiences_from_cv(cv_text, field)
            
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
    
    async def _extract_skills_from_cv(self, cv_text: str, field: str) -> List[str]:
        """CV에서 스킬 추출"""
        try:
            # LLM을 사용하여 스킬 추출
            prompt = f"""
            당신은 {field} 분야의 저명한 교수입니다.
            당신의 연구실에 새로운 학생이 지원했습니다. 당신이 생각하기에 {field} 분야의 연구 및 일을 하기 위해 필수적으로 필요한 스킬들을 생각하세요.
            당신이 선택한 스킬들에 대해서 새롭게 지원한 학생의 CV를 분석하여 해당 학생이 {field} 분야에 대한 스킬들을 다뤄본적이 있는지 검토해주세요.
            
            - 학생의 CV
            {cv_text}
            
            {field} 분야에 대해서 연구 및 일을 하기 위해 필요한 스킬 및 프로그래밍 언어, 프레임워크 등을 정하고.
            학생의 CV에 해당 스킬들이 있는지 검토하여 있는 스킬들을 추출해주세요.
            
            학생의 CV에 있는 각 스킬을 쉼표로 구분하여 반환해주세요.
            예시: Python, TypeScript, FastAPI, Next.js, LangChain, LangGraph, ...

            스킬들에 대해서 스킬 단어로만 출력해주세요. 자연어 형식으로 스킬에 대해서 설명하거나 얘기를 하지 말고 스킬에 대해서 단어만 쉼표로 구분하여 출력해주세요.
            """
            
            response = await openai_client._call_chat_completion(prompt)
            
            # 응답을 파싱하여 스킬 리스트 생성
            skills = [skill.strip() for skill in response.split(',') if skill.strip()]
            
            # 중복 제거
            skills = list(set(skills))
            
            return skills
            
        except Exception as e:
            logger.error(f"스킬 추출 실패: {e}")
            return []
    
    async def _extract_experiences_from_cv(self, cv_text: str, field: str) -> List[Dict[str, Any]]:
        """CV에서 경험 추출"""
        try:
            # LLM을 사용하여 경험 추출
            prompt = f"""
            당신은 {field} 분야의 저명한 교수입니다.
            당신의 연구실에 새로운 학생이 지원했습니다. 
            지원한 학생의 CV를 통해 {field} 분야에 대해서 학생이 얼마나 다양하고 깊은 경험을 했는지 추출해주세요.
            연구실의 학생을 뽑는 것이니, {field} 분야의 연구에 대한 경험이 있는 학생을 뽑는 것이 목적입니다.
            
            - 학생의 CV
            {cv_text}
            
            해당 학생의 CV를 {field} 분야에 관련된 경험들로 분석하여 다음 형식으로 JSON 배열로 반환해주세요.
            반드시 유효한 JSON 형식으로만 응답해주세요.
            
            
                {{
                    "title": "프로젝트/연구 제목",
                    "description": "프로젝트/연구 설명",
                    "duration": "기간",
                    "technologies": ["사용 기술들"],
                    "role": "역할",
                    "achievements": ["주요 성과들"],
                    "relevance": "{field} 분야와의 관련성"
                }}
            ]
            
            모든 프로젝트, 연구, 대회 경험을 포함해주세요.
            """
            
            response = await openai_client._call_chat_completion(prompt)
            
            # JSON 파싱 (더 안정적인 구현)
            import json
            import re
            
            # JSON 부분만 추출
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                try:
                    experiences = json.loads(json_str)
                    if isinstance(experiences, list) and len(experiences) > 0:
                        logger.info(f"경험 추출 성공: {len(experiences)}개 경험")
                        return experiences
                except json.JSONDecodeError as e:
                    logger.error(f"JSON 파싱 실패: {e}")
            
            # JSON 파싱에 실패한 경우 기본 구조 반환
            logger.warning("JSON 파싱 실패, 기본 경험 구조 생성")
            return [
                {
                    "title": "CV 분석 결과",
                    "description": f"{field} 분야 관련 경험들이 CV에서 확인됨",
                    "duration": "Various",
                    "technologies": ["LLM", "NLP", "AI/ML"],
                    "role": "연구자/개발자",
                    "achievements": ["다양한 프로젝트 경험 확인"],
                    "relevance": f"{field} 분야 연구 및 개발 경험"
                }
            ]
            
        except Exception as e:
            logger.error(f"경험 추출 실패: {e}")
            # 오류 발생 시에도 기본 구조 반환
            return [
                {
                    "title": "CV 분석 결과",
                    "description": f"{field} 분야 관련 경험들이 CV에서 확인됨",
                    "duration": "Various",
                    "technologies": ["LLM", "NLP", "AI/ML"],
                    "role": "연구자/개발자",
                    "achievements": ["다양한 프로젝트 경험 확인"],
                    "relevance": f"{field} 분야 연구 및 개발 경험"
                }
            ]
    
    async def _analyze_strengths_weaknesses(self, cv_text: str, field: str, 
                                          trend_analysis: Optional[Dict[str, Any]], 
                                          required_skills: List[str]) -> tuple[List[str], List[str]]:
        """강점/약점 분석"""
        try:
            # LLM을 사용하여 강점/약점 분석
            prompt = f"""
            당신은 {field} 분야의 저명한 교수입니다.
            당신의 연구실에 새로운 학생이 지원했습니다.
            
            지원자의 CV를 분석하여 강점과 약점을 평가해주세요.
            
            - 지원자 CV 내용:
            {cv_text}
            
            분석 기준:
            1. {field} 분야에서의 연구/개발 능력
            2. 기술적 스킬과 경험의 깊이
            3. 실제 프로젝트 성과와 성취
            4. 학술적 배경과 연구 경험
            5. 최신 기술 트렌드 적응도
            6. 팀워크 및 리더십 경험
            
            강점과 약점을 각각 3-5개씩 한국어로 작성해주세요.
            강점은 구체적인 성과와 기술을 포함해주세요.
            약점은 개선 가능한 영역을 구체적으로 제시해주세요.
            
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
            
            # 최소한의 기본 강점/약점 보장
            if not strengths:
                strengths = [f"{field} 분야에서 다양한 프로젝트 경험 보유", "LLM 및 AI 기술에 대한 깊은 이해", "실제 서비스 개발 및 배포 경험"]
            if not weaknesses:
                weaknesses = ["더 많은 학술 논문 발표 경험 필요", "특정 분야에서의 전문성 심화 필요", "국제적인 연구 협력 경험 확대 필요"]
            
            return strengths, weaknesses
            
        except Exception as e:
            logger.error(f"강점/약점 분석 실패: {e}")
            # 기본값 반환
            return [
                f"{field} 분야에서 다양한 프로젝트 경험 보유",
                "LLM 및 AI 기술에 대한 깊은 이해",
                "실제 서비스 개발 및 배포 경험"
            ], [
                "더 많은 학술 논문 발표 경험 필요",
                "특정 분야에서의 전문성 심화 필요",
                "국제적인 연구 협력 경험 확대 필요"
            ]
    
    async def _generate_radar_chart_data(self, cv_text: str, field: str, 
                                        trend_analysis: Optional[Dict[str, Any]]) -> CVRadarChartData:
        """레이더 차트 데이터 생성"""
        try:
            # LLM을 사용하여 각 영역별 점수 계산
            research_ability = await self._calculate_research_score_llm(cv_text, field)
            development_skill = await self._calculate_development_score_llm(cv_text, field)
            awards_achievements = await self._calculate_awards_score_llm(cv_text, field)
            latest_tech_trend = await self._calculate_trend_score_llm(cv_text, field, trend_analysis)
            academic_background = await self._calculate_academic_score_llm(cv_text, field)
            project_experience = await self._calculate_project_score_llm(cv_text, field)
            
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
    
    async def _calculate_research_score_llm(self, cv_text: str, field: str) -> float:
        """연구 능력 점수 계산 (LLM 사용)"""
        try:
            prompt = f"""
            당신은 {field} 분야의 저명한 교수입니다.
            연구실 학생 선발을 위해 지원자의 연구 능력을 평가하고 있습니다.
            
            지원자의 CV를 분석하여 연구 능력을 0.0~1.0 사이의 점수로 평가해주세요.
            
            - 지원자 CV:
            {cv_text}
            
            연구 능력 평가 기준:
            - 논문 발표 경험 (arXiv, 학회 논문)
            - 연구 프로젝트 참여 및 성과
            - 학술적 배경 (전공, GPA, 연구 관련 수업)
            - 연구 관련 스킬 (LLM, RAG, Fine-tuning 등)
            - 학회 참여 및 발표 경험
            - 연구 주제의 깊이와 혁신성
            
            점수만 숫자로 반환해주세요 (예: 0.75)
            """
            
            response = await openai_client._call_chat_completion(prompt)
            
            # 숫자 추출
            import re
            score_match = re.search(r'0\.\d+', response)
            if score_match:
                return float(score_match.group())
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"연구 능력 점수 계산 실패: {e}")
            return 0.5
    
    async def _calculate_development_score_llm(self, cv_text: str, field: str) -> float:
        """개발 스킬 점수 계산 (LLM 사용)"""
        try:
            prompt = f"""
            당신은 {field} 분야의 저명한 교수입니다.
            연구실 학생 선발을 위해 지원자의 개발 스킬을 평가하고 있습니다.
            
            지원자의 CV를 분석하여 개발 스킬을 0.0~1.0 사이의 점수로 평가해주세요.
            
            - 지원자 CV:
            {cv_text}
            
            개발 스킬 평가 기준:
            - 프로그래밍 언어 숙련도 (Python, TypeScript, JavaScript 등)
            - 프레임워크/라이브러리 활용 (FastAPI, Next.js, Streamlit, LangChain 등)
            - 개발 도구 사용 경험 (Docker, AWS, Vercel 등)
            - 실제 프로젝트 구현 능력
            - 클린 아키텍처 적용 경험
            - 풀스택 개발 경험
            - 코드 품질과 시스템 설계 능력
            
            점수만 숫자로 반환해주세요 (예: 0.8)
            """
            
            response = await openai_client._call_chat_completion(prompt)
            
            import re
            score_match = re.search(r'0\.\d+', response)
            if score_match:
                return float(score_match.group())
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"개발 스킬 점수 계산 실패: {e}")
            return 0.5
    
    async def _calculate_awards_score_llm(self, cv_text: str, field: str) -> float:
        """수상/성과 점수 계산 (LLM 사용)"""
        try:
            prompt = f"""
            당신은 {field} 분야의 저명한 교수입니다.
            연구실 학생 선발을 위해 지원자의 수상/성과를 평가하고 있습니다.
            
            지원자의 CV를 분석하여 수상/성과를 0.0~1.0 사이의 점수로 평가해주세요.
            
            - 지원자 CV:
            {cv_text}
            
            수상/성과 평가 기준:
            - 대회 수상 경험 (Dacon, 공모전 등)
            - 논문 발표/인용 (arXiv, 학회 논문)
            - 특허 출원
            - 기타 성과/인증 (AWS 인증, 장학금 등)
            - 대회 참여 및 순위
            - 성과의 질과 영향력
            
            점수만 숫자로 반환해주세요 (예: 0.6)
            """
            
            response = await openai_client._call_chat_completion(prompt)
            
            import re
            score_match = re.search(r'0\.\d+', response)
            if score_match:
                return float(score_match.group())
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"수상/성과 점수 계산 실패: {e}")
            return 0.5
    
    async def _calculate_trend_score_llm(self, cv_text: str, field: str, trend_analysis: Optional[Dict[str, Any]]) -> float:
        """최신 기술 트렌드 점수 계산 (LLM 사용)"""
        try:
            prompt = f"""
            당신은 {field} 분야의 저명한 교수입니다.
            연구실 학생 선발을 위해 지원자의 최신 기술 트렌드 적응도를 평가하고 있습니다.
            
            지원자의 CV를 분석하여 최신 기술 트렌드 적응도를 0.0~1.0 사이의 점수로 평가해주세요.
            
            - 지원자 CV:
            {cv_text}
            
            - 현재 트렌드 정보:
            {trend_analysis.get('trend_summary', 'N/A') if trend_analysis else 'N/A'}
            
            최신 기술 트렌드 평가 기준:
            - AI/ML 관련 스킬 (LLM, RAG, Fine-tuning 등)
            - 최신 프레임워크 활용 (LangChain, LangGraph 등)
            - 트렌드에 맞는 기술 스택
            - 혁신적 기술 경험 (멀티 에이전트, 통계 분석 등)
            - 최신 모델 활용 (GPT-4, LLaMA, Gemini 등)
            - 기술 트렌드에 대한 이해도
            
            점수만 숫자로 반환해주세요 (예: 0.7)
            """
            
            response = await openai_client._call_chat_completion(prompt)
            
            import re
            score_match = re.search(r'0\.\d+', response)
            if score_match:
                return float(score_match.group())
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"최신 기술 트렌드 점수 계산 실패: {e}")
            return 0.5
    
    async def _calculate_academic_score_llm(self, cv_text: str, field: str) -> float:
        """학술 배경 점수 계산 (LLM 사용)"""
        try:
            prompt = f"""
            당신은 {field} 분야의 저명한 교수입니다.
            연구실 학생 선발을 위해 지원자의 학술 배경을 평가하고 있습니다.
            
            지원자의 CV를 분석하여 학술 배경을 0.0~1.0 사이의 점수로 평가해주세요.
            
            - 지원자 CV:
            {cv_text}
            
            학술 배경 평가 기준:
            - 학위 수준 (학사, 석사, 박사)
            - 연구 경험 (논문 발표, 연구 프로젝트)
            - 학술 활동 (학회 참여, 컨퍼런스 발표)
            - 교육 배경 (전공, GPA, 복수전공)
            - 학술적 성과 (논문, 특허, 연구 보고서)
            - 학술 커뮤니티 참여도
            
            점수만 숫자로 반환해주세요 (예: 0.65)
            """
            
            response = await openai_client._call_chat_completion(prompt)
            
            import re
            score_match = re.search(r'0\.\d+', response)
            if score_match:
                return float(score_match.group())
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"학술 배경 점수 계산 실패: {e}")
            return 0.5
    
    async def _calculate_project_score_llm(self, cv_text: str, field: str) -> float:
        """프로젝트 경험 점수 계산 (LLM 사용)"""
        try:
            prompt = f"""
            당신은 {field} 분야의 저명한 교수입니다.
            연구실 학생 선발을 위해 지원자의 프로젝트 경험을 평가하고 있습니다.
            
            지원자의 CV를 분석하여 프로젝트 경험을 0.0~1.0 사이의 점수로 평가해주세요.
            
            - 지원자 CV:
            {cv_text}
            
            프로젝트 경험 평가 기준:
            - 프로젝트 규모와 복잡도
            - 역할과 책임 (개발자, 팀 리더, PM 등)
            - 기술적 난이도
            - 성과와 결과 (수상, 논문 발표, 실제 서비스 등)
            - 프로젝트 다양성 (웹 개발, AI/ML, 데이터 분석 등)
            - 팀 협업 경험
            - 프로젝트의 혁신성과 영향력
            
            점수만 숫자로 반환해주세요 (예: 0.8)
            """
            
            response = await openai_client._call_chat_completion(prompt)
            
            import re
            score_match = re.search(r'0\.\d+', response)
            if score_match:
                return float(score_match.group())
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"프로젝트 경험 점수 계산 실패: {e}")
            return 0.5
    
    async def get_cv_analysis(self, analysis_id: str) -> Optional[CVAnalysis]:
        """CV 분석 결과 조회"""
        return await self.cv_repository.get_cv_analysis(analysis_id) 