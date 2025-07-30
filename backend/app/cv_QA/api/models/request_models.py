from pydantic import BaseModel
from typing import Optional, Literal

class CVUploadRequest(BaseModel):
    """CV 업로드 요청 모델"""
    pass  # 파일 업로드는 multipart/form-data로 처리

class QASessionRequest(BaseModel):
    """QA 세션 생성 요청 모델"""
    analysis_id: str
    mode: Literal["interview", "practice"]  # A: interview, B: practice

class QAMessageRequest(BaseModel):
    """QA 메시지 전송 요청 모델"""
    message: str

class InterviewQuestionSelectRequest(BaseModel):
    """면접 질문 선택 요청 모델 (A 기능용)"""
    selected_question: Optional[str] = None
    custom_question: Optional[str] = None

class AskQuestionRequest(BaseModel):
    """선택된 질문을 AI가 물어보기 요청 모델"""
    question: str

class NewQuestionRequest(BaseModel):
    """새로운 질문 요청 모델 (A 기능용)"""
    request_new: bool = True 