from typing import List, Dict, Any, Optional
import logging
from ...domain.entities.qa_session import QASession, QAMessage
from app.shared.infra.external.openai_client import openai_client

logger = logging.getLogger(__name__)

class QAService:
    """CV QA 서비스"""
    
    def __init__(self):
        self.sessions: Dict[str, QASession] = {}
    
    async def create_session(self, cv_analysis_id: str) -> QASession:
        """QA 세션 생성"""
        try:
            session = QASession.create(cv_analysis_id)
            self.sessions[session.id] = session
            
            # 초기 인사 메시지 추가
            welcome_message = "안녕하세요! CV 기반 면접 질의응답을 도와드리겠습니다. 어떤 질문이든 편하게 해주세요."
            session.add_message("assistant", welcome_message)
            
            logger.info(f"QA 세션 생성: {session.id}")
            return session
            
        except Exception as e:
            logger.error(f"QA 세션 생성 실패: {e}")
            raise
    
    async def send_message(self, session_id: str, user_message: str, cv_analysis_data: Dict[str, Any]) -> str:
        """메시지 전송 및 응답"""
        try:
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError("세션을 찾을 수 없습니다.")
            
            # 사용자 메시지 추가
            session.add_message("user", user_message)
            
            # AI 응답 생성
            ai_response = await self._generate_response(user_message, cv_analysis_data, session)
            
            # AI 응답 추가
            session.add_message("assistant", ai_response)
            
            logger.info(f"메시지 처리 완료: {session_id}")
            return ai_response
            
        except Exception as e:
            logger.error(f"메시지 처리 실패: {e}")
            raise
    
    async def _generate_response(self, user_message: str, cv_analysis_data: Dict[str, Any], session: QASession) -> str:
        """AI 응답 생성"""
        try:
            # 대화 히스토리 생성
            conversation_history = session.get_conversation_history()
            
            # CV 정보 추출
            skills = cv_analysis_data.get('skills', [])
            experiences = cv_analysis_data.get('experiences', [])
            strengths = cv_analysis_data.get('strengths', [])
            weaknesses = cv_analysis_data.get('weaknesses', [])
            
            # 프롬프트 생성
            prompt = f"""
            당신은 CV 기반 면접관입니다. 다음 정보를 바탕으로 사용자의 질문에 답변해주세요:
            
            CV 정보:
            - 스킬: {', '.join(skills)}
            - 경험: {len(experiences)}개 프로젝트
            - 강점: {', '.join(strengths)}
            - 약점: {', '.join(weaknesses)}
            
            대화 히스토리:
            {chr(10).join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-5:]])}
            
            사용자 질문: {user_message}
            
            면접관 관점에서 자연스럽고 도움이 되는 답변을 한국어로 작성해주세요.
            """
            
            response = await openai_client._call_chat_completion(prompt)
            return response
            
        except Exception as e:
            logger.error(f"AI 응답 생성 실패: {e}")
            return "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."
    
    async def get_session(self, session_id: str) -> Optional[QASession]:
        """세션 조회"""
        return self.sessions.get(session_id)
    
    async def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """대화 히스토리 조회"""
        session = self.sessions.get(session_id)
        if not session:
            return []
        
        return session.get_conversation_history() 