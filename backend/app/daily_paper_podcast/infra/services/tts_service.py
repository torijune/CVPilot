import logging
import os
from typing import Optional
import uuid
from datetime import datetime
from google.cloud import texttospeech

logger = logging.getLogger(__name__)

class TTSService:
    """Google Cloud TTS 서비스"""
    
    def __init__(self):
        # 정적 파일 서빙을 위한 디렉토리 사용
        import os
        self.temp_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "temp_audio")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Google Cloud TTS 클라이언트 초기화
        try:
            # 서비스 계정 키 경로 설정 (환경 변수에서 가져오거나 기본 경로 사용)
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", 
                                      "/Users/jang-wonjun/Desktop/Dev/CVPilot/cvpilot-467501-80776d682808.json")
            
            if os.path.exists(credentials_path):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
                self.client = texttospeech.TextToSpeechClient()
                logger.info("Google Cloud TTS 클라이언트 초기화 완료")
            else:
                logger.warning(f"Google Cloud 인증 파일을 찾을 수 없음: {credentials_path}")
                self.client = None
                
        except Exception as e:
            logger.error(f"Google Cloud TTS 클라이언트 초기화 실패: {e}")
            self.client = None
    
    async def generate_audio(self, text: str, filename: str = None) -> str:
        """텍스트를 오디오 파일로 변환 (Google Cloud TTS 사용)"""
        try:
            if not filename:
                # 고유한 파일명 생성
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                filename = f"podcast_{timestamp}_{unique_id}.mp3"
            
            file_path = os.path.join(self.temp_dir, filename)
            
            if self.client is None:
                logger.error("Google Cloud TTS 클라이언트가 초기화되지 않았습니다.")
                raise Exception("TTS 클라이언트 초기화 실패")
            
            # Synthesis 입력 값 설정
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # 목소리 및 언어 설정 (한국어)
            voice = texttospeech.VoiceSelectionParams(
                language_code="ko-KR",
                name="ko-KR-Neural2-A",  # 고품질 한국어 음성
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            
            # 오디오 설정 (MP3 출력, 고품질)
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=0.9,  # 약간 빠르게 (0.25 ~ 4.0)
                pitch=0.0,  # 기본 피치
                volume_gain_db=0.0  # 기본 볼륨
            )
            
            # 음성 합성 요청
            response = self.client.synthesize_speech(
                input=synthesis_input, 
                voice=voice, 
                audio_config=audio_config
            )
            
            # 오디오 파일로 저장
            with open(file_path, "wb") as out:
                out.write(response.audio_content)
            
            logger.info(f"Google Cloud TTS 파일 생성 완료: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Google Cloud TTS 파일 생성 실패: {e}")
            raise
    
    async def get_audio_duration(self, file_path: str) -> int:
        """오디오 파일 재생 시간 계산 (초)"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"오디오 파일이 존재하지 않음: {file_path}")
                return 0
            
            # Google Cloud TTS는 더 정확한 파일 크기 기반 추정 가능
            # 고품질 MP3의 경우 대략 1KB당 0.5초 정도
            file_size_kb = os.path.getsize(file_path) / 1024
            estimated_duration = max(1, int(file_size_kb / 2))  # 더 정확한 계산
            
            logger.info(f"오디오 지속 시간 추정: {estimated_duration}초 (file size: {file_size_kb:.1f}KB)")
            return estimated_duration
            
        except Exception as e:
            logger.error(f"오디오 재생 시간 계산 실패: {e}")
            # 텍스트 길이 기반 추정 (대역책)
            return 0 