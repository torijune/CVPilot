import logging
import os
from typing import Optional
from gtts import gTTS
import tempfile
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class TTSService:
    """TTS 서비스"""
    
    def __init__(self):
        # 정적 파일 서빙을 위한 디렉토리 사용
        import os
        self.temp_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "temp_audio")
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def generate_audio(self, text: str, filename: str = None) -> str:
        """텍스트를 오디오 파일로 변환"""
        try:
            if not filename:
                # 고유한 파일명 생성
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                filename = f"podcast_{timestamp}_{unique_id}.mp3"
            
            file_path = os.path.join(self.temp_dir, filename)
            
            # gTTS를 사용하여 한국어 TTS 생성
            tts = gTTS(text=text, lang='ko', slow=False)
            tts.save(file_path)
            
            logger.info(f"TTS 파일 생성 완료: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"TTS 파일 생성 실패: {e}")
            raise
    
    async def get_audio_duration(self, file_path: str) -> int:
        """오디오 파일 재생 시간 계산 (초)"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"오디오 파일이 존재하지 않음: {file_path}")
                return 0
            
            # 파일 크기 기반 추정 (간단한 방법)
            # gTTS로 생성된 MP3 파일의 경우 대략 1KB당 1초 정도
            file_size_kb = os.path.getsize(file_path) / 1024
            estimated_duration = max(1, int(file_size_kb / 4))  # 대략적인 계산
            
            logger.info(f"오디오 지속 시간 추정: {estimated_duration}초 (file size: {file_size_kb:.1f}KB)")
            return estimated_duration
            
        except Exception as e:
            logger.error(f"오디오 재생 시간 계산 실패: {e}")
            # 텍스트 길이 기반 추정 (대역책)
            return 0 