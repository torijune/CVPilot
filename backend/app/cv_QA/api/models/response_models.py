from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime

class CVUploadResponse(BaseModel):
    """CV 업로드 응답 모델"""
    success: bool
    analysis_id: str
    message: str

class QASessionResponse(BaseModel):
    """QA 세션 생성 응답 모델"""
    success: bool
    session_id: str
    mode: Literal["interview", "practice"]
    interview_questions: Optional[List[str]] = None  # interview 모드일 때만
    message: str

class QAMessageResponse(BaseModel):
    """QA 메시지 응답 모델"""
    success: bool
    message_id: str
    content: str
    role: Optional[str] = None
    timestamp: Optional[str] = None
    feedback: Optional[str] = None  # interview 모드에서 피드백
    follow_up_question: Optional[str] = None  # interview 모드에서 꼬리 질문

class InterviewQuestionsResponse(BaseModel):
    """면접 질문 추천 응답 모델 (A 기능용)"""
    success: bool
    questions: List[str]
    message: str

class QASessionListResponse(BaseModel):
    """QA 세션 목록 응답 모델"""
    success: bool
    sessions: List[Dict[str, Any]]
    total: int 