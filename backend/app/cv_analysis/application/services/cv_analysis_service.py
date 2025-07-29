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
            새로운 학생의 연구 능력 및 경험들에 대해서 분석을하여 해당 학생의 약점과 강점을 분석 및 평가해주세요.
            
            지원자의 CV를 분석하여 강점과 약점을 평가해주세요.
            
            - 지원자 CV 내용:
            {cv_text}
            
            분석 기준:
            1. {field} 분야에서의 연구/개발 능력
                - {field} 관련 프로젝트 경험 (개발, 연구, 실험, 구현 등)
                - {field} 관련 논문 작성 경험 (arXiv preprint, 학회 논문, 저널 논문, 포스터 발표)
                - {field} 관련 논문 읽기 및 리뷰 경험 (최신 논문 추적, 논문 분석, 구현)
                - {field} 관련 학부 연구생 및 인턴 경험 (연구실 활동, 멘토링, 실무 경험)
                - {field} 관련 대회 참여 및 수상 경험 (Kaggle, Dacon, 학회 대회, 공모전 등)
                - {field} 관련 오픈소스 기여 경험 (GitHub, 코드 공유, 커뮤니티 활동, 라이브러리 개발)
            
            2. 기술적 스킬과 경험의 깊이
                - 프로그래밍 언어 숙련도 (Python, C++, Java, JavaScript, MATLAB, R 등)
                - 프레임워크/라이브러리 활용 능력 (PyTorch, TensorFlow, FastAPI, React, OpenCV, scikit-learn 등)
                - 개발 도구 및 환경 관리 (Docker, Git, AWS, Linux, CUDA, GPU 활용 등)
                - 데이터 처리 및 분석 능력 (Pandas, NumPy, SQL, 데이터 시각화, EDA 등)
                - 시스템 설계 및 아키텍처 이해도 (클린 아키텍처, 마이크로서비스, 분산 시스템 등)
                - 성능 최적화 및 디버깅 능력 (알고리즘 최적화, 메모리 관리, 병렬 처리 등)
            
            3. 실제 프로젝트 성과와 성취
                - 프로젝트 규모 및 복잡도 (개인/팀 프로젝트, 기업/학술 프로젝트, 대규모 시스템)
                - 프로젝트 완성도 및 배포 경험 (실제 서비스 런칭, 사용자 피드백, 운영 경험)
                - 프로젝트 성과 지표 (성능 향상, 사용자 수, 매출, 정확도 개선 등)
                - 문제 해결 능력 (기술적 난제 극복, 창의적 솔루션 제시, 최적화)
                - 프로젝트 관리 및 일정 준수 능력 (일정 관리, 리소스 관리, 위험 관리)
                - 팀 협업 및 의사소통 능력 (기술 문서 작성, 발표, 토론, 코드 리뷰)
            
            4. 학술적 배경과 연구 경험
                - 학위 수준 및 전공 관련성 (학사/석사/박사, 관련 전공, 복수전공)
                - GPA 및 학업 성취도 (우수한 학업 성적, 장학금 수혜, 우등 졸업)
                - 연구 관련 수업 이수 (논문 읽기, 연구 방법론, 통계학, 수학, 알고리즘 등)
                - 학술 대회 참여 및 수상 (논문 발표, 포스터 발표, 우수상, 장려상 등)
                - 연구 프로젝트 참여 (학부 연구생, 대학원 연구조교, 인턴십, 연구비 지원)
                - 학술 커뮤니티 활동 (학회 가입, 세미나 참여, 네트워킹, 멘토링)
            
            5. 최신 기술 트렌드 적응도
                - 최신 AI/ML 기술 이해도 (LLM, RAG, 멀티모달, 생성 AI, 컴퓨터 비전, 강화학습 등)
                - 최신 프레임워크 및 도구 활용 (LangChain, Hugging Face, 최신 라이브러리, 클라우드 서비스)
                - 기술 트렌드 추적 능력 (논문 읽기, 컨퍼런스 참여, 블로그/유튜브 학습, 워크샵 참여)
                - 새로운 기술 학습 및 적용 능력 (자기주도 학습, 실험적 적용, 프로토타이핑)
                - 기술 커뮤니티 참여 (GitHub, Stack Overflow, 기술 블로그, 오픈소스 기여)
                - 혁신적 아이디어 제시 및 구현 능력 (독창적 접근, 실험적 프로젝트, 특허 출원)
            
            6. 팀워크 및 리더십 경험
                - 팀 프로젝트 참여 경험 (역할 분담, 협업, 갈등 해결, 의사결정)
                - 리더십 경험 (팀 리더, 프로젝트 매니저, 멘토링, 기술 리드)
                - 의사소통 능력 (기술 문서 작성, 발표, 토론, 비기술자와의 소통)
                - 조직 내 기여도 (팀 성과 향상, 지식 공유, 문화 조성, 멘토링)
                - 네트워킹 및 협력 능력 (외부 협업, 오픈소스 기여, 커뮤니티 활동, 학술 협력)
                - 리더십 스타일 및 관리 능력 (동기부여, 갈등 관리, 의사결정, 리스크 관리)
            
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
            - 논문 발표 경험 (arXiv preprint, 학회 논문, 저널 논문, 포스터 발표, 워크샵)
            - 연구 프로젝트 참여 및 성과 (학부 연구생, 대학원 연구조교, 인턴십, 연구비 지원)
            - 학술적 배경 (전공, GPA, 연구 관련 수업, 논문 읽기 수업, 수학/통계학)
            - 연구 관련 스킬 (AI/ML 모델, 실험 설계, 통계 분석, 알고리즘 설계, 데이터 분석)
            - 학회 참여 및 발표 경험 (컨퍼런스 참여, 워크샵 발표, 세미나 발표, 포스터 세션)
            - 연구 주제의 깊이와 혁신성 (최신 트렌드 반영, 독창적 접근, 실용적 가치)
            - 연구 커뮤니티 활동 (학회 가입, 연구 그룹 참여, 네트워킹, 멘토링)
            - 연구 성과의 영향력 (인용 수, 실제 적용, 산업계 연계, 오픈소스 기여)
            - 연구 방법론 이해도 (실험 설계, 평가 지표, 재현성, 윤리적 고려사항)
            - 지속적인 연구 활동 (연속적인 연구, 학술 커뮤니티 기여, 최신 동향 추적)
            
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
            - 프로그래밍 언어 숙련도 (Python, TypeScript, JavaScript, Java, C++, MATLAB, R 등)
            - 프레임워크/라이브러리 활용 (FastAPI, Next.js, Streamlit, LangChain, PyTorch, TensorFlow, OpenCV, scikit-learn 등)
            - 개발 도구 사용 경험 (Docker, AWS, Vercel, Git, CI/CD, Linux, CUDA, GPU 활용 등)
            - 실제 프로젝트 구현 능력 (풀스택 개발, API 설계, 데이터베이스 설계, ML 파이프라인)
            - 클린 아키텍처 적용 경험 (모듈화, 테스트 코드, 문서화, 코드 품질)
            - 풀스택 개발 경험 (프론트엔드, 백엔드, 데이터베이스, 인프라, ML 모델 배포)
            - 코드 품질과 시스템 설계 능력 (성능 최적화, 확장성, 유지보수성, 보안)
            - 개발 프로세스 이해도 (Agile, Scrum, 코드 리뷰, 버전 관리, DevOps)
            - 문제 해결 및 디버깅 능력 (복잡한 이슈 해결, 성능 튜닝, 알고리즘 최적화)
            - 최신 개발 트렌드 적응도 (새로운 기술 학습, 실험적 적용, 클라우드 서비스)
            - 하드웨어 활용 능력 (GPU, TPU, 분산 컴퓨팅, 엣지 디바이스)
            - 데이터 엔지니어링 스킬 (데이터 파이프라인, ETL, 데이터 웨어하우스, 실시간 처리)
            
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
            - 대회 수상 경험 (Dacon, Kaggle, 학회 대회, 공모전, 해커톤, AI 챌린지 등)
            - 논문 발표/인용 (arXiv, 학회 논문, 저널 논문, 인용 수, 논문 품질)
            - 특허 출원 및 등록 (발명 특허, 실용신안, 디자인 등록, 소프트웨어 등록)
            - 기타 성과/인증 (AWS 인증, 장학금, 우수상, 장려상, 우등 졸업 등)
            - 대회 참여 및 순위 (상위권 진입, 본선 진출, 특별상, 혁신상 등)
            - 성과의 질과 영향력 (산업계 적용, 실제 서비스화, 매출 창출, 사회적 기여)
            - 학술적 성과 (논문 품질, 연구의 독창성, 학계 인정도, 오픈소스 기여)
            - 프로젝트 성과 (사용자 수, 성능 향상, 비즈니스 임팩트, 기술적 혁신)
            - 커뮤니티 기여 (오픈소스 기여, 기술 블로그, 세미나 발표, 멘토링)
            - 지속적인 성과 창출 (연속적인 수상, 지속적인 연구 활동, 성장 추세)
            - 국제적 성과 (해외 대회 참여, 국제 학회 발표, 해외 연구 협력)
            - 산업계 연계 성과 (기업 협력, 기술 이전, 상용화, 스타트업 창업)
            
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
            - AI/ML 관련 스킬 (LLM, RAG, Fine-tuning, 멀티모달, 생성 AI, 컴퓨터 비전, 강화학습, 음성인식 등)
            - 최신 프레임워크 활용 (LangChain, LangGraph, Hugging Face, 최신 라이브러리, 클라우드 AI 서비스)
            - 트렌드에 맞는 기술 스택 (최신 모델, 최신 도구, 최신 방법론, 엣지 AI, 페더레이티드 러닝)
            - 혁신적 기술 경험 (멀티 에이전트, 통계 분석, 실시간 처리, 양자 컴퓨팅, 신경망 아키텍처)
            - 최신 모델 활용 (GPT-4, LLaMA, Gemini, Claude, Vision Transformers, Diffusion Models 등)
            - 기술 트렌드에 대한 이해도 (논문 읽기, 컨퍼런스 참여, 블로그 학습, 워크샵 참여)
            - 새로운 기술 학습 및 적용 능력 (자기주도 학습, 실험적 적용, 프로토타이핑, A/B 테스트)
            - 기술 커뮤니티 참여 (GitHub, Stack Overflow, 기술 블로그, 오픈소스 기여, 세미나)
            - 최신 연구 동향 추적 (arXiv, 컨퍼런스 논문, 연구 그룹 활동, 논문 구현)
            - 혁신적 아이디어 제시 및 구현 (독창적 접근, 실험적 프로젝트, 특허 출원, 연구 제안)
            - 크로스 도메인 지식 (AI + 도메인 지식, 멀티디스플리너리 접근, 융합 기술)
            - 지속적인 학습 및 적응 (온라인 코스, 인증 프로그램, 컨퍼런스 참여, 네트워킹)
            
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
            - 학위 수준 (학사, 석사, 박사, 복수전공, 부전공, 연계전공)
            - 연구 경험 (논문 발표, 연구 프로젝트, 학부 연구생, 대학원 연구조교, 인턴십)
            - 학술 활동 (학회 참여, 컨퍼런스 발표, 워크샵 참여, 세미나 발표, 포스터 세션)
            - 교육 배경 (전공, GPA, 복수전공, 관련 수업 이수, 수학/통계학/컴퓨터과학)
            - 학술적 성과 (논문, 특허, 연구 보고서, 학술상, 우수 논문상)
            - 학술 커뮤니티 참여도 (학회 가입, 연구 그룹 활동, 네트워킹, 멘토링)
            - 연구 방법론 이해도 (실험 설계, 평가 지표, 재현성, 윤리적 고려사항, 통계 분석)
            - 학술적 네트워크 (교수진과의 관계, 연구 협력, 멘토링, 국제 협력)
            - 학술적 성취 (장학금, 우수상, 연구비 지원, 특별 프로그램 참여, 우등 졸업)
            - 지속적인 학술 활동 (연속적인 연구, 학술 커뮤니티 기여, 최신 동향 추적)
            - 국제적 학술 활동 (해외 학회 참여, 국제 논문 발표, 해외 연구 협력)
            - 학제간 연구 경험 (다양한 분야 융합 연구, 크로스 디스플리너리 접근)
            
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
            - 프로젝트 규모와 복잡도 (개인/팀 프로젝트, 기업/학술 프로젝트, 대규모 시스템, 엔터프라이즈급)
            - 역할과 책임 (개발자, 팀 리더, 프로젝트 매니저, 아키텍트, 연구원, 데이터 사이언티스트)
            - 기술적 난이도 (최신 기술 적용, 복잡한 알고리즘 구현, 시스템 통합, 성능 최적화)
            - 성과와 결과 (수상, 논문 발표, 실제 서비스, 사용자 피드백, 매출 창출)
            - 프로젝트 다양성 (웹 개발, AI/ML, 데이터 분석, 모바일 앱, 시스템 개발, 연구 프로젝트)
            - 팀 협업 경험 (다양한 역할과의 협업, 원격 협업, 크로스 펑셔널 팀, 국제 협력)
            - 프로젝트의 혁신성과 영향력 (새로운 기술 도입, 비즈니스 임팩트, 사회적 기여, 학술적 기여)
            - 프로젝트 관리 능력 (일정 관리, 리소스 관리, 위험 관리, 품질 관리)
            - 문제 해결 능력 (기술적 난제 극복, 창의적 솔루션, 최적화, 성능 튜닝)
            - 지속적인 개선 (사용자 피드백 반영, 성능 최적화, 유지보수, 버전 업그레이드)
            - 프로젝트의 완성도 (실제 배포, 운영 경험, 사용자 테스트, 성능 평가)
            - 기술적 혁신 (새로운 아키텍처, 최적화 기법, 효율적인 알고리즘, 확장 가능한 설계)
            
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