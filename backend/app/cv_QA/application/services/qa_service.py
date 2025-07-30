from typing import List, Dict, Any, Optional
import logging
from fastapi import UploadFile
import uuid
from datetime import datetime
import io
import PyPDF2
from docx import Document

from ...domain.entities.qa_session import QASession, QAMessage
from ...domain.repositories.qa_repository import QARepository
from app.shared.infra.external.openai_client import openai_client

logger = logging.getLogger(__name__)

class QAService:
    """CV QA 서비스"""
    
    def __init__(self, qa_repository: QARepository):
        self.qa_repository = qa_repository
    
    async def analyze_cv(self, file: UploadFile) -> Dict[str, Any]:
        """CV 파일 분석"""
        try:
            logger.info(f"CV 분석 시작: {file.filename}")
            
            # 파일 내용 읽기
            content = await file.read()
            file_content = self._extract_text_from_file(content, file.filename)
            
            # CV 분석 수행
            analysis_result = await self._analyze_cv_content(file_content)
            
            # 분석 결과 저장
            analysis_id = str(uuid.uuid4())
            await self.qa_repository.save_cv_analysis({**analysis_result, 'analysis_id': analysis_id})
            
            logger.info(f"CV 분석 완료: {analysis_id}")
            return {
                'analysis_id': analysis_id,
                'analysis_result': analysis_result
            }
            
        except Exception as e:
            logger.error(f"CV 분석 실패: {e}")
            raise
    
    async def create_qa_session(self, analysis_id: str, mode: str) -> Dict[str, Any]:
        """QA 세션 생성"""
        try:
            logger.info(f"QA 세션 생성: {analysis_id}, 모드: {mode}")
            
            # CV 분석 결과 조회
            cv_analysis = await self.qa_repository.get_cv_analysis(analysis_id)
            if not cv_analysis:
                logger.error(f"CV 분석 결과를 찾을 수 없습니다. analysis_id: {analysis_id}")
                raise Exception("CV 분석 결과를 찾을 수 없습니다.")
            
            # QA 세션 생성
            session = QASession.create(analysis_id, mode)
            
            # 모드에 따른 초기 메시지 설정
            if mode == "interview":
                # A 기능: 면접관 모드
                interview_questions = await self._generate_interview_questions(cv_analysis)
                welcome_message = QAMessage.create(
                    content="안녕하세요! 저는 대학원 면접관입니다. CV를 바탕으로 면접을 진행해보겠습니다. 아래 추천 질문 중 하나를 선택하거나 직접 질문을 입력해주세요.",
                    role="assistant"
                )
                session.add_message(welcome_message)
                
                # 초기 추천 질문들을 세션에 저장
                session.interview_questions = interview_questions
            else:
                # B 기능: 연습 모드
                welcome_message = QAMessage.create(
                    content="안녕하세요! CV 기반 면접 연습을 도와드리겠습니다. 면접에서 받을 수 있는 질문을 자유롭게 해주시면, CV를 바탕으로 답변 예시와 피드백을 제공해드리겠습니다.",
                    role="assistant"
                )
                session.add_message(welcome_message)
                interview_questions = []
            
            # 세션 저장
            await self.qa_repository.save_session(session)
            
            logger.info(f"QA 세션 생성 완료: {session.session_id}")
            return {
                'session_id': session.session_id,
                'analysis_id': analysis_id,
                'mode': mode,
                'interview_questions': interview_questions if mode == "interview" else None
            }
            
        except Exception as e:
            logger.error(f"QA 세션 생성 실패: {e}")
            raise
    
    async def send_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """메시지 전송 및 AI 응답"""
        try:
            logger.info(f"메시지 전송: {session_id}")
            
            # 세션 조회
            session = await self.qa_repository.get_session(session_id)
            if not session:
                raise Exception("QA 세션을 찾을 수 없습니다.")
            
            # 사용자 메시지 추가
            user_message = QAMessage.create(message, "user")
            session.add_message(user_message)
            
            # CV 분석 결과 조회
            cv_analysis = await self.qa_repository.get_cv_analysis(session.analysis_id)
            if not cv_analysis:
                raise Exception("CV 분석 결과를 찾을 수 없습니다.")
            
            # 모드에 따른 AI 응답 생성
            if session.mode == "interview":
                # A 기능: 면접관 모드 - 피드백과 꼬리 질문 생성
                ai_response_data = await self._generate_interview_response(session, cv_analysis, message)
                
                ai_message = QAMessage.create(
                    content=ai_response_data['content'], 
                    role="assistant",
                    feedback=ai_response_data.get('feedback'),
                    follow_up_question=ai_response_data.get('follow_up_question')
                )
            else:
                # B 기능: 연습 모드 - 모범 답변과 조언 제공
                ai_response_data = await self._generate_practice_response(session, cv_analysis, message)
                
                ai_message = QAMessage.create(
                    content=ai_response_data['content'], 
                    role="assistant"
                )
            
            session.add_message(ai_message)
            
            # 세션 업데이트
            await self.qa_repository.update_session(session)
            
            logger.info(f"메시지 전송 완료: {session_id}")
            result = {
                'message_id': ai_message.message_id,
                'content': ai_message.content,
                'timestamp': ai_message.timestamp
            }
            
            if ai_message.feedback:
                result['feedback'] = ai_message.feedback
            if ai_message.follow_up_question:
                result['follow_up_question'] = ai_message.follow_up_question
                
            return result
            
        except Exception as e:
            logger.error(f"메시지 전송 실패: {e}")
            raise
    
    async def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """세션 메시지 목록 조회"""
        try:
            session = await self.qa_repository.get_session(session_id)
            if not session:
                raise Exception("QA 세션을 찾을 수 없습니다.")
            
            return [msg.to_dict() for msg in session.get_messages()]
            
        except Exception as e:
            logger.error(f"메시지 목록 조회 실패: {e}")
            raise
    
    async def get_qa_sessions(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """QA 세션 목록 조회"""
        try:
            sessions = await self.qa_repository.get_sessions(limit, offset)
            return [session.to_dict() for session in sessions]
            
        except Exception as e:
            logger.error(f"QA 세션 목록 조회 실패: {e}")
            raise
    
    async def delete_qa_session(self, session_id: str) -> bool:
        """QA 세션 삭제"""
        try:
            return await self.qa_repository.delete_session(session_id)
            
        except Exception as e:
            logger.error(f"QA 세션 삭제 실패: {e}")
            raise
    
    def _extract_text_from_file(self, content: bytes, filename: str) -> str:
        """파일에서 텍스트 추출"""
        try:
            file_extension = filename.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                # PDF 파일 처리
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
                
            elif file_extension == 'docx':
                # DOCX 파일 처리
                doc = Document(io.BytesIO(content))
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
                
            elif file_extension == 'txt':
                # TXT 파일 처리
                return content.decode('utf-8')
                
            else:
                raise Exception(f"지원하지 않는 파일 형식: {file_extension}")
                
        except Exception as e:
            logger.error(f"파일 텍스트 추출 실패: {e}")
            raise Exception(f"파일을 읽을 수 없습니다: {str(e)}")

    async def _analyze_cv_content(self, content: str) -> Dict[str, Any]:
        """CV 내용 분석"""
        try:
            prompt = f"""
다음 CV 내용을 분석하여 구조화된 정보를 추출해주세요.

CV 내용:
{content}

다음 형식으로 분석 결과를 제공해주세요:

1. 기본 정보 (이름, 연락처, 학력 등)
2. 기술 스킬 (프로그래밍 언어, 프레임워크, 도구 등)
3. 프로젝트 경험 (프로젝트명, 역할, 기술스택, 성과 등)
4. 연구 경험 (논문, 연구과제, 학회발표 등)
5. 업무 경험 (회사명, 직책, 기간, 주요 업무 등)
6. 수상 경험 (상명, 수상일, 주관기관 등)
7. 자격증 및 교육 (자격증명, 취득일, 교육과정 등)

각 항목은 JSON 형태로 구조화하여 제공해주세요.
"""

            response = await openai_client._call_chat_completion(prompt)
            
            # 분석 결과 구조화
            analysis_result = {
                'original_content': content,
                'cv_content': content,  # 원본 CV 내용 추가
                'structured_analysis': response,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"CV 내용 분석 실패: {e}")
            raise
    
    async def _generate_interview_questions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """면접 질문 생성 - CV 맞춤형 질문"""
        try:
            cv_info = analysis_result.get('structured_analysis', '')
            cv_content = analysis_result.get('cv_content', '')
            
            prompt = f"""
당신은 대학원 교수이자 면접관입니다. 지원자의 CV를 깊이 분석하여 개인 맞춤형 면접 질문을 생성해주세요.

CV 분석 정보:
{cv_info}

CV 원본 내용:
{cv_content}

다음 가이드라인에 따라 5개의 맞춤형 면접 질문을 생성해주세요:

**질문 생성 원칙:**
1. **구체성**: CV에 언급된 특정 프로젝트, 기술, 경험을 직접 언급
2. **개인화**: 지원자만의 고유한 경험과 배경을 반영
3. **심화성**: 표면적이 아닌 깊이 있는 기술적/학술적 질문
4. **연결성**: 지원자의 경험들을 연결하여 종합적 사고력 평가
5. **미래지향성**: 대학원 진학 후의 연구 계획과 연결

**질문 유형별 가이드라인:**

**기술/연구 관련:**
- CV에 언급된 특정 기술/도구의 구체적 활용 경험
- 연구 과정에서 마주한 기술적 도전과 해결 방법
- 특정 프로젝트의 기술적 의사결정 과정

**학술/연구 관련:**
- 특정 논문이나 연구의 핵심 기여도와 의미
- 연구 분야에서의 독창적 접근법이나 관점
- 학회 발표나 논문 작성 과정에서의 경험

**개인적 성장 관련:**
- CV에 나타난 학습 곡선과 발전 과정
- 실패 경험에서 배운 교훈과 성장
- 지원자의 고유한 강점과 약점

**미래 계획 관련:**
- 대학원에서의 구체적 연구 목표와 계획
- 현재 경험을 바탕으로 한 향후 발전 방향
- 학술 커뮤니티에 기여할 수 있는 방안

**질문 작성 요구사항:**
- CV의 구체적 내용을 직접 언급 (예: "CV에 언급된 [특정 프로젝트]에서...")
- 지원자의 배경과 경험을 고려한 개인화된 질문
- 대학원 수준의 심화된 사고를 요구하는 질문
- 자연스러운 대화체로 작성

JSON 배열 형태로 5개의 질문만 반환해주세요:
["질문1", "질문2", "질문3", "질문4", "질문5"]
"""

            response = await openai_client._call_chat_completion(prompt)
            
            # JSON 파싱 시도
            try:
                import json
                questions = json.loads(response)
                if isinstance(questions, list) and len(questions) > 0:
                    return questions[:5]  # 최대 5개만 반환
                else:
                    raise ValueError("올바른 형식이 아닙니다")
            except:
                # JSON 파싱 실패 시 기본 질문 반환
                return [
                    "CV에 있는 주요 연구 경험에 대해 구체적으로 설명해주세요.",
                    "가장 도전적이었던 프로젝트는 무엇이고, 어떻게 해결하셨나요?",
                    "대학원에서 연구하고 싶은 분야와 그 이유는 무엇인가요?",
                    "기술적으로 가장 자신 있는 부분과 부족한 부분은 무엇인가요?",
                    "앞으로의 연구 계획과 목표는 무엇인가요?"
                ]
            
        except Exception as e:
            logger.error(f"면접 질문 생성 실패: {e}")
            return [
                "CV에 있는 주요 연구 경험에 대해 구체적으로 설명해주세요.",
                "가장 도전적이었던 프로젝트는 무엇이고, 어떻게 해결하셨나요?",
                "대학원에서 연구하고 싶은 분야와 그 이유는 무엇인가요?",
                "기술적으로 가장 자신 있는 부분과 부족한 부분은 무엇인가요?",
                "앞으로의 연구 계획과 목표는 무엇인가요?"
            ]

    async def _generate_interview_response(self, session: QASession, cv_analysis: Dict[str, Any], user_message: str) -> Dict[str, Any]:
        """A 기능: 면접관 모드 응답 생성 (피드백 + 꼬리 질문)"""
        try:
            # 대화 히스토리 구성 - 전체 대화 히스토리 사용
            conversation_history = []
            for msg in session.get_messages():
                conversation_history.append({
                    'role': msg.role,
                    'content': msg.content
                })
            
            # CV 분석 정보 추출
            cv_info = cv_analysis.get('structured_analysis', '')
            
            prompt = f"""
당신은 대학원 교수이자 면접관입니다. 지원자가 답변한 내용을 평가하고 피드백을 제공해주세요.

CV 분석 정보:
{cv_info}

대화 히스토리:
{conversation_history}

지원자의 최근 답변: "{user_message}"

다음 형식으로 JSON 응답을 생성해주세요:
{{
    "content": "지원자에게 하는 말 (피드백과 격려)",
    "feedback": "답변에 대한 구체적인 평가와 개선점",
    "follow_up_question": "CV를 바탕으로 한 자연스러운 꼬리 질문 (선택적)"
}}

가이드라인:
1. **긍정적 피드백**: 좋은 점을 먼저 언급하고 격려
2. **구체적 평가**: CV와 연결해서 답변을 분석
3. **건설적 조언**: 부족한 부분에 대한 개선 제안
4. **꼬리 질문**: CV 내용과 관련된 자연스러운 추가 질문
5. **교수 톤**: 전문적이지만 친근하고 격려하는 분위기

JSON 형식으로만 응답해주세요.
"""

            response = await openai_client._call_chat_completion(prompt)
            
            # JSON 파싱 시도
            try:
                import json
                response_data = json.loads(response)
                return response_data
            except:
                # JSON 파싱 실패 시 기본 응답
                return {
                    "content": "좋은 답변이네요. CV를 보니 다양한 경험을 하셨군요.",
                    "feedback": "답변이 구체적이고 좋습니다. 더 자세한 설명을 들어보고 싶네요.",
                    "follow_up_question": "그 경험에서 가장 어려웠던 점은 무엇이었나요?"
                }
            
        except Exception as e:
            logger.error(f"면접 응답 생성 실패: {e}")
            return {
                "content": "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다.",
                "feedback": "시스템 오류가 발생했습니다.",
                "follow_up_question": None
            }
    
    async def _generate_practice_response(self, session: QASession, cv_analysis: Dict[str, Any], user_question: str) -> Dict[str, Any]:
        """B 기능: 연습 모드 응답 생성 (모범 답변 + 조언)"""
        try:
            # 대화 히스토리 구성 - 전체 대화 히스토리 사용
            conversation_history = []
            for msg in session.get_messages():
                conversation_history.append({
                    'role': msg.role,
                    'content': msg.content
                })
            
            # CV 분석 정보 추출
            cv_info = cv_analysis.get('structured_analysis', '')
            
            prompt = f"""
당신은 면접 코치입니다. 지원자가 받을 수 있는 질문에 대해 CV를 바탕으로 모범 답변과 조언을 제공해주세요.

CV 분석 정보:
{cv_info}

대화 히스토리:
{conversation_history}

지원자의 질문: "{user_question}"

다음 가이드라인에 따라 응답해주세요:

1. **모범 답변 제시**: CV 내용을 바탕으로 한 구체적이고 효과적인 답변 예시
2. **답변 전략**: 이 질문에 어떻게 접근하면 좋을지 설명
3. **CV 연결**: 본인의 CV에서 어떤 부분을 강조하면 좋을지 조언
4. **주의사항**: 답변할 때 피해야 할 점들
5. **실전 팁**: 면접에서 이 질문에 답할 때의 실용적인 조언
6. **대화 연속성**: 이전 대화 내용을 참고하여 일관성 있는 조언 제공

친근하고 도움이 되는 톤으로 답변해주세요. 마치 선배가 후배에게 조언하는 느낌으로 작성해주세요.
"""

            response = await openai_client._call_chat_completion(prompt)
            
            return {
                "content": response
            }
            
        except Exception as e:
            logger.error(f"연습 응답 생성 실패: {e}")
            return {
                "content": "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다. 다시 질문해주세요."
            }

    async def get_new_interview_questions(self, session_id: str) -> List[str]:
        """A 기능: 새로운 면접 질문 생성"""
        try:
            # 세션 조회
            session = await self.qa_repository.get_session(session_id)
            if not session:
                raise Exception("QA 세션을 찾을 수 없습니다.")
            
            # CV 분석 결과 조회
            cv_analysis = await self.qa_repository.get_cv_analysis(session.analysis_id)
            if not cv_analysis:
                raise Exception("CV 분석 결과를 찾을 수 없습니다.")
            
            # 이전 대화 히스토리를 고려한 새로운 질문 생성
            conversation_history = []
            for msg in session.get_messages()[-20:]:  # 최근 20개 메시지
                conversation_history.append({
                    'role': msg.role,
                    'content': msg.content
                })
            
            return await self._generate_new_interview_questions(cv_analysis, conversation_history)
            
        except Exception as e:
            logger.error(f"새로운 면접 질문 생성 실패: {e}")
            raise

    async def ask_selected_question(self, session_id: str, question: str) -> Dict[str, Any]:
        """선택된 질문을 AI가 사용자에게 물어보기"""
        try:
            # 세션 조회
            session = await self.qa_repository.get_session(session_id)
            if not session:
                raise Exception("QA 세션을 찾을 수 없습니다.")
            
            # AI가 질문하는 메시지 생성
            ai_message = QAMessage.create(
                content=question,
                role="assistant"
            )
            
            # 세션에 메시지 추가
            session.add_message(ai_message)
            
            # 세션 저장
            await self.qa_repository.save_session(session)
            
            logger.info(f"선택된 질문 처리 완료: {session_id}")
            return {
                'message_id': ai_message.message_id,
                'content': ai_message.content,
                'timestamp': ai_message.timestamp
            }
            
        except Exception as e:
            logger.error(f"선택된 질문 처리 실패: {e}")
            raise

    async def _generate_new_interview_questions(self, cv_analysis: Dict[str, Any], conversation_history: List[Dict]) -> List[str]:
        """새로운 면접 질문 생성 (이전 대화 고려) - CV 맞춤형"""
        try:
            cv_info = cv_analysis.get('structured_analysis', '')
            cv_content = cv_analysis.get('cv_content', '')
            
            prompt = f"""
당신은 대학원 교수이자 면접관입니다. 지원자의 CV와 이전 대화를 깊이 분석하여 새로운 맞춤형 면접 질문 5개를 생성해주세요.

CV 분석 정보:
{cv_info}

CV 원본 내용:
{cv_content}

이전 대화 히스토리:
{conversation_history}

**새로운 질문 생성 전략:**

1. **이전 대화 분석**: 이미 다룬 주제와 아직 탐구하지 않은 CV 영역 파악
2. **심화 질문**: 이전 답변을 바탕으로 더 깊이 있는 후속 질문
3. **연결 질문**: 이전 대화와 CV의 다른 부분을 연결하는 질문
4. **미탐구 영역**: 아직 언급되지 않은 CV의 중요한 부분에 대한 질문
5. **종합 평가**: 지원자의 전체 역량을 종합적으로 평가하는 질문

**질문 생성 원칙:**
- **구체성**: CV에 언급된 특정 내용을 직접 참조
- **개인화**: 지원자의 고유한 경험과 배경 반영
- **심화성**: 이전 대화보다 더 깊이 있는 기술적/학술적 질문
- **연결성**: 이전 답변과 CV의 다른 부분을 연결
- **미래지향성**: 대학원 진학 후의 연구 계획과 연결

**질문 유형별 가이드라인:**

**기술/연구 심화:**
- 이전에 언급된 기술/도구의 더 구체적 활용 사례
- 연구 과정에서의 기술적 의사결정과 그 근거
- 특정 프로젝트의 기술적 한계와 극복 방법

**학술/연구 심화:**
- 이전 연구의 학술적 기여도와 영향력
- 연구 분야에서의 독창적 방법론이나 접근법
- 학회 활동이나 논문 작성의 구체적 경험

**개인적 성장 심화:**
- 이전 답변에서 드러난 학습 패턴과 성장 과정
- 실패 경험의 구체적 교훈과 적용 사례
- 지원자의 고유한 강점과 약점의 균형

**미래 계획 심화:**
- 현재 경험을 바탕으로 한 구체적 연구 로드맵
- 학술 커뮤니티 기여 방안과 계획
- 장기적 연구 비전과 목표

**질문 작성 요구사항:**
- CV의 구체적 내용을 직접 언급
- 이전 대화 내용을 참조하여 연속성 확보
- 지원자의 배경과 경험을 고려한 개인화된 질문
- 대학원 수준의 심화된 사고를 요구하는 질문
- 자연스러운 대화체로 작성

JSON 배열 형태로 5개의 질문만 반환해주세요:
["질문1", "질문2", "질문3", "질문4", "질문5"]
"""

            response = await openai_client._call_chat_completion(prompt)
            
            # JSON 파싱 시도
            try:
                import json
                questions = json.loads(response)
                if isinstance(questions, list) and len(questions) > 0:
                    return questions[:5]  # 최대 5개만 반환
                else:
                    raise ValueError("올바른 형식이 아닙니다")
            except:
                # JSON 파싱 실패 시 기본 질문 반환
                return [
                    "지금까지의 연구 경험 중 가장 의미 있었던 성과는 무엇인가요?",
                    "연구를 진행하면서 마주한 가장 큰 도전은 무엇이었고, 어떻게 해결했나요?",
                    "본인만의 독특한 관점이나 접근 방식이 있다면 소개해주세요.",
                    "대학원에서 이루고 싶은 구체적인 연구 목표가 있나요?",
                    "10년 후 본인의 모습을 어떻게 그리고 계신가요?"
                ]
            
        except Exception as e:
            logger.error(f"새로운 면접 질문 생성 실패: {e}")
            return [
                "지금까지의 연구 경험 중 가장 의미 있었던 성과는 무엇인가요?",
                "연구를 진행하면서 마주한 가장 큰 도전은 무엇이었고, 어떻게 해결했나요?",
                "본인만의 독특한 관점이나 접근 방식이 있다면 소개해주세요.",
                "대학원에서 이루고 싶은 구체적인 연구 목표가 있나요?",
                "10년 후 본인의 모습을 어떻게 그리고 계신가요?"
            ] 