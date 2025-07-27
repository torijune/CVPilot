from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import uuid

@dataclass
class QAMessage:
    """QA 메시지"""
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    
    @classmethod
    def create(cls, role: str, content: str) -> 'QAMessage':
        return cls(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            timestamp=datetime.now()
        )

@dataclass
class QASession:
    """QA 세션 엔티티"""
    id: str
    cv_analysis_id: str
    messages: List[QAMessage]
    created_at: datetime
    
    @classmethod
    def create(cls, cv_analysis_id: str) -> 'QASession':
        """QA 세션 엔티티 생성"""
        return cls(
            id=str(uuid.uuid4()),
            cv_analysis_id=cv_analysis_id,
            messages=[],
            created_at=datetime.now()
        )
    
    def add_message(self, role: str, content: str):
        """메시지 추가"""
        message = QAMessage.create(role, content)
        self.messages.append(message)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """대화 히스토리 반환"""
        return [
            {
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in self.messages
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'cv_analysis_id': self.cv_analysis_id,
            'messages': self.get_conversation_history(),
            'created_at': self.created_at.isoformat()
        } 