from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
import uuid

class QAMessage:
    """QA 메시지 엔티티"""
    
    def __init__(self, content: str, role: str, message_id: Optional[str] = None, timestamp: Optional[str] = None, 
                 feedback: Optional[str] = None, follow_up_question: Optional[str] = None):
        self.message_id = message_id or str(uuid.uuid4())
        self.content = content
        self.role = role  # 'user' 또는 'assistant'
        self.timestamp = timestamp or datetime.now().isoformat()
        self.feedback = feedback  # interview 모드에서 사용자 답변에 대한 피드백
        self.follow_up_question = follow_up_question  # interview 모드에서 꼬리 질문
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'message_id': self.message_id,
            'content': self.content,
            'role': self.role,
            'timestamp': self.timestamp
        }
        if self.feedback:
            result['feedback'] = self.feedback
        if self.follow_up_question:
            result['follow_up_question'] = self.follow_up_question
        return result
    
    @classmethod
    def create(cls, content: str, role: str, message_id: Optional[str] = None, 
              feedback: Optional[str] = None, follow_up_question: Optional[str] = None) -> 'QAMessage':
        return cls(content, role, message_id, feedback=feedback, follow_up_question=follow_up_question)

class QASession:
    """QA 세션 엔티티"""
    
    def __init__(self, analysis_id: str, mode: Literal["interview", "practice"], 
                 session_id: Optional[str] = None, messages: Optional[List[QAMessage]] = None, 
                 created_at: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.analysis_id = analysis_id
        self.mode = mode  # "interview" (A 기능) 또는 "practice" (B 기능)
        self.messages = messages or []
        self.created_at = created_at or datetime.now().isoformat()
    
    def add_message(self, message: QAMessage):
        """메시지 추가"""
        self.messages.append(message)
    
    def get_messages(self) -> List[QAMessage]:
        """메시지 목록 반환"""
        return self.messages
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_id': self.session_id,
            'analysis_id': self.analysis_id,
            'mode': self.mode,
            'messages': [msg.to_dict() for msg in self.messages],
            'created_at': self.created_at
        }
    
    @classmethod
    def create(cls, analysis_id: str, mode: Literal["interview", "practice"], session_id: Optional[str] = None) -> 'QASession':
        return cls(analysis_id, mode, session_id) 