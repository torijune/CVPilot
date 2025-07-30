from typing import List, Optional, Dict, Any
import logging
import uuid
from datetime import datetime

from ...domain.entities.qa_session import QASession, QAMessage
from ...domain.repositories.qa_repository import QARepository

logger = logging.getLogger(__name__)

class CVRepositoryImpl(QARepository):
    """CV QA 리포지토리 구현체 (메모리 기반)"""
    
    def __init__(self):
        self.sessions: Dict[str, QASession] = {}
        self.cv_analyses: Dict[str, Dict[str, Any]] = {}
    
    async def save_session(self, session: QASession) -> bool:
        """QA 세션 저장"""
        try:
            self.sessions[session.session_id] = session
            logger.info(f"QA 세션 저장 완료: {session.session_id}")
            logger.info(f"현재 저장된 세션 수: {len(self.sessions)}")
            logger.info(f"저장된 세션 키들: {list(self.sessions.keys())}")
            return True
        except Exception as e:
            logger.error(f"QA 세션 저장 실패: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[QASession]:
        """QA 세션 조회"""
        try:
            logger.info(f"QA 세션 조회 시도: {session_id}")
            logger.info(f"현재 저장된 세션 수: {len(self.sessions)}")
            logger.info(f"저장된 세션 키들: {list(self.sessions.keys())}")
            result = self.sessions.get(session_id)
            logger.info(f"조회 결과: {result is not None}")
            return result
        except Exception as e:
            logger.error(f"QA 세션 조회 실패: {e}")
            return None
    
    async def update_session(self, session: QASession) -> bool:
        """QA 세션 업데이트"""
        try:
            if session.session_id in self.sessions:
                self.sessions[session.session_id] = session
                logger.info(f"QA 세션 업데이트 완료: {session.session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"QA 세션 업데이트 실패: {e}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """QA 세션 삭제"""
        try:
            if session_id in self.sessions:
                del self.sessions[session_id]
                logger.info(f"QA 세션 삭제 완료: {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"QA 세션 삭제 실패: {e}")
            return False
    
    async def get_sessions(self, limit: int = 10, offset: int = 0) -> List[QASession]:
        """QA 세션 목록 조회"""
        try:
            sessions = list(self.sessions.values())
            # 생성일 기준 내림차순 정렬
            sessions.sort(key=lambda x: x.created_at, reverse=True)
            return sessions[offset:offset + limit]
        except Exception as e:
            logger.error(f"QA 세션 목록 조회 실패: {e}")
            return []
    
    async def save_cv_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """CV 분석 결과 저장"""
        try:
            # 이미 analysis_id가 있으면 사용, 없으면 새로 생성
            analysis_id = analysis_data.get('analysis_id', str(uuid.uuid4()))
            if 'analysis_id' not in analysis_data:
                analysis_data['analysis_id'] = analysis_id
            analysis_data['created_at'] = datetime.now().isoformat()
            
            self.cv_analyses[analysis_id] = analysis_data
            logger.info(f"CV 분석 결과 저장 완료: {analysis_id}")
            return analysis_id
        except Exception as e:
            logger.error(f"CV 분석 결과 저장 실패: {e}")
            raise
    
    async def get_cv_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """CV 분석 결과 조회"""
        try:
            logger.info(f"CV 분석 결과 조회 시도: {analysis_id}")
            logger.info(f"저장된 분석 결과 키들: {list(self.cv_analyses.keys())}")
            result = self.cv_analyses.get(analysis_id)
            logger.info(f"조회 결과: {result is not None}")
            return result
        except Exception as e:
            logger.error(f"CV 분석 결과 조회 실패: {e}")
            return None 