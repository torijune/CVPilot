from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Body
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from ..models.request_models import (
    CVUploadRequest,
    QASessionRequest,
    QAMessageRequest,
    InterviewQuestionSelectRequest,
    NewQuestionRequest,
    AskQuestionRequest
)
from ..models.response_models import (
    CVUploadResponse,
    QASessionResponse,
    QAMessageResponse,
    InterviewQuestionsResponse,
    QASessionListResponse
)
from ...application.services.qa_service import QAService
from ...infra.repositories.cv_repository_impl import CVRepositoryImpl

logger = logging.getLogger(__name__)

router = APIRouter()

# 싱글톤 저장소 인스턴스
_cv_repository = CVRepositoryImpl()

# 의존성 주입
def get_qa_service() -> QAService:
    return QAService(_cv_repository)

@router.get("/health")
async def health_check():
    """CV QA 서비스 헬스체크"""
    return {"status": "healthy", "service": "cv_qa"}

@router.post("/upload", response_model=CVUploadResponse)
async def upload_cv(
    file: UploadFile = File(...),
    qa_service: QAService = Depends(get_qa_service)
):
    """CV 파일 업로드 및 분석"""
    try:
        logger.info(f"CV 업로드 요청: {file.filename}")
        
        # 파일 유효성 검사
        if not file.filename or not file.filename.lower().endswith(('.pdf', '.docx', '.txt')):
            raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다. PDF, DOCX, TXT 파일만 업로드 가능합니다.")
        
        # CV 분석 수행
        analysis_result = await qa_service.analyze_cv(file)
        
        return CVUploadResponse(
            success=True,
            analysis_id=analysis_result['analysis_id'],
            message="CV 분석이 완료되었습니다. 원하는 모드를 선택해서 QA 세션을 시작하세요."
        )
        
    except Exception as e:
        logger.error(f"CV 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions", response_model=QASessionResponse)
async def create_qa_session(
    request: QASessionRequest,
    qa_service: QAService = Depends(get_qa_service)
):
    """QA 세션 생성"""
    try:
        logger.info(f"QA 세션 생성 요청: {request.analysis_id}, 모드: {request.mode}")
        
        session_result = await qa_service.create_qa_session(request.analysis_id, request.mode)
        
        return QASessionResponse(
            success=True,
            session_id=session_result['session_id'],
            mode=session_result['mode'],
            interview_questions=session_result.get('interview_questions'),
            message=f"{'면접관 모드' if request.mode == 'interview' else '연습 모드'} QA 세션이 시작되었습니다."
        )
        
    except Exception as e:
        logger.error(f"QA 세션 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/sessions/{session_id}/messages", response_model=QAMessageResponse)
async def send_message(
    session_id: str,
    request: QAMessageRequest,
    qa_service: QAService = Depends(get_qa_service)
):
    """QA 세션에 메시지 전송"""
    try:
        logger.info(f"메시지 전송 요청: {session_id}")
        
        response = await qa_service.send_message(session_id, request.message)
        
        return QAMessageResponse(
            success=True,
            message_id=response['message_id'],
            content=response['content'],
            timestamp=response['timestamp'],
            feedback=response.get('feedback'),
            follow_up_question=response.get('follow_up_question')
        )
        
    except Exception as e:
        logger.error(f"메시지 전송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/new-questions", response_model=InterviewQuestionsResponse)
async def get_new_interview_questions(
    session_id: str,
    request: NewQuestionRequest,
    qa_service: QAService = Depends(get_qa_service)
):
    """A 기능: 새로운 면접 질문 생성"""
    try:
        logger.info(f"새로운 면접 질문 요청: {session_id}")
        
        questions = await qa_service.get_new_interview_questions(session_id)
        
        return InterviewQuestionsResponse(
            success=True,
            questions=questions,
            message="새로운 면접 질문이 생성되었습니다. 질문을 선택하거나 직접 입력해주세요."
        )
        
    except Exception as e:
        logger.error(f"새로운 면접 질문 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/ask-question", response_model=QAMessageResponse)
async def ask_selected_question(
    session_id: str,
    request: AskQuestionRequest,
    qa_service: QAService = Depends(get_qa_service)
):
    """선택된 면접 질문을 AI가 사용자에게 물어보기"""
    try:
        logger.info(f"선택된 질문 요청: {session_id}, 질문: {request.question}")
        
        response = await qa_service.ask_selected_question(session_id, request.question)
        
        return QAMessageResponse(
            success=True,
            message_id=response['message_id'],
            content=response['content'],
            timestamp=response['timestamp']
        )
        
    except Exception as e:
        logger.error(f"선택된 질문 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/messages", response_model=List[QAMessageResponse])
async def get_session_messages(
    session_id: str,
    qa_service: QAService = Depends(get_qa_service)
):
    """QA 세션의 메시지 목록 조회"""
    try:
        logger.info(f"메시지 목록 조회 요청: {session_id}")
        
        messages = await qa_service.get_session_messages(session_id)
        
        return [
            QAMessageResponse(
                success=True,
                message_id=msg['message_id'],
                content=msg['content'],
                role=msg['role'],
                timestamp=msg['timestamp']
            )
            for msg in messages
        ]
        
    except Exception as e:
        logger.error(f"메시지 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", response_model=QASessionListResponse)
async def get_qa_sessions(
    limit: int = 10,
    offset: int = 0,
    qa_service: QAService = Depends(get_qa_service)
):
    """QA 세션 목록 조회"""
    try:
        logger.info(f"QA 세션 목록 조회 요청")
        
        sessions = await qa_service.get_qa_sessions(limit, offset)
        
        return QASessionListResponse(
            success=True,
            sessions=sessions,
            total=len(sessions)
        )
        
    except Exception as e:
        logger.error(f"QA 세션 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_qa_session(
    session_id: str,
    qa_service: QAService = Depends(get_qa_service)
):
    """QA 세션 삭제"""
    try:
        logger.info(f"QA 세션 삭제 요청: {session_id}")
        
        success = await qa_service.delete_qa_session(session_id)
        
        if success:
            return {"success": True, "message": "QA 세션이 삭제되었습니다."}
        else:
            raise HTTPException(status_code=404, detail="QA 세션을 찾을 수 없습니다.")
        
    except Exception as e:
        logger.error(f"QA 세션 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 