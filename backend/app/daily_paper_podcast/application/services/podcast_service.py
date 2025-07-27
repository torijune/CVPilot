from typing import List, Dict, Any, Optional
import logging
from ...domain.entities.podcast_analysis import PodcastAnalysis
from app.shared.infra.external.openai_client import openai_client

logger = logging.getLogger(__name__)

class PodcastService:
    """팟캐스트 서비스"""
    
    def __init__(self):
        pass
    
    async def generate_podcast(self, field: str, papers: List[Dict[str, Any]]) -> PodcastAnalysis:
        """팟캐스트 생성"""
        try:
            logger.info(f"팟캐스트 생성 시작: {field} 분야")
            
            # 1. 논문 분석 텍스트 생성
            analysis_text = await self._generate_analysis_text(field, papers)
            
            # 2. 오디오 파일 생성 (실제로는 TTS 서비스 사용)
            audio_file_path = await self._generate_audio_file(analysis_text)
            
            # 3. 결과 생성
            podcast_analysis = PodcastAnalysis.create(
                field=field,
                papers=papers,
                analysis_text=analysis_text,
                audio_file_path=audio_file_path,
                duration_seconds=len(analysis_text.split()) // 3  # 대략적인 계산
            )
            
            logger.info(f"팟캐스트 생성 완료: {len(papers)}개 논문 분석")
            return podcast_analysis
            
        except Exception as e:
            logger.error(f"팟캐스트 생성 실패: {e}")
            raise
    
    async def _generate_analysis_text(self, field: str, papers: List[Dict[str, Any]]) -> str:
        """분석 텍스트 생성"""
        try:
            # 논문 정보 추출
            paper_summaries = []
            for i, paper in enumerate(papers[:10]):  # 최대 10개 논문
                title = paper.get('title', '')
                abstract = paper.get('abstract', '')
                paper_summaries.append(f"논문 {i+1}: {title}\n{abstract[:200]}...")
            
            prompt = f"""
            다음 {field} 분야의 논문들을 분석하여 팟캐스트 스크립트를 작성해주세요:
            
            논문들:
            {chr(10).join(paper_summaries)}
            
            다음 5개 항목을 포함하여 자연스러운 한국어로 작성해주세요:
            1. 오늘의 주제 소개
            2. 주요 연구 동향
            3. 핵심 기술 및 방법론
            4. 실험 결과 및 성과
            5. 향후 전망 및 시사점
            
            팟캐스트 듣기 좋게 자연스럽고 흥미롭게 작성해주세요.
            """
            
            response = await openai_client._call_chat_completion(prompt)
            return response
            
        except Exception as e:
            logger.error(f"분석 텍스트 생성 실패: {e}")
            return f"{field} 분야의 최신 논문들을 분석한 결과입니다."
    
    async def _generate_audio_file(self, text: str) -> str:
        """오디오 파일 생성"""
        try:
            # 실제로는 TTS 서비스를 사용하여 오디오 파일 생성
            # 현재는 파일 경로만 반환
            import uuid
            file_id = str(uuid.uuid4())
            audio_path = f"/audio/podcast_{file_id}.mp3"
            
            logger.info(f"오디오 파일 생성: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"오디오 파일 생성 실패: {e}")
            return ""
    
    async def get_podcast_analysis(self, analysis_id: str) -> Optional[PodcastAnalysis]:
        """팟캐스트 분석 결과 조회"""
        try:
            # 실제로는 데이터베이스에서 조회
            logger.info(f"팟캐스트 분석 결과 조회: {analysis_id}")
            return None
        except Exception as e:
            logger.error(f"팟캐스트 분석 결과 조회 실패: {e}")
            return None 