import logging
from typing import Optional, List
from ...domain.repositories.podcast_repository import PodcastRepository
from ...domain.entities.podcast_analysis import PodcastAnalysis
from app.shared.infra.external.supabase_client import supabase_client

logger = logging.getLogger(__name__)

class PodcastRepositoryImpl(PodcastRepository):
    """팟캐스트 분석 리포지토리 구현체"""
    
    def __init__(self):
        self.supabase_client = supabase_client
    
    async def save_analysis(self, analysis: PodcastAnalysis) -> str:
        """팟캐스트 분석 결과 저장"""
        try:
            # Supabase에 저장할 데이터 구성
            data = {
                "id": analysis.id,
                "field": analysis.field,
                "papers": analysis.papers,  # JSON으로 저장
                "analysis_text": analysis.analysis_text,
                "audio_file_path": analysis.audio_file_path,
                "duration_seconds": analysis.duration_seconds,
                "created_at": analysis.created_at.isoformat()
            }
            
            # podcast_analyses 테이블에 저장
            result = self.supabase_client.client.table("podcast_analyses").insert(data).execute()
            
            if result.data:
                logger.info(f"팟캐스트 분석 결과 저장 완료: {analysis.id}")
                return analysis.id
            else:
                raise Exception("데이터 저장 실패")
                
        except Exception as e:
            logger.error(f"팟캐스트 분석 결과 저장 실패: {e}")
            raise
    
    async def get_analysis_by_id(self, analysis_id: str) -> Optional[PodcastAnalysis]:
        """ID로 팟캐스트 분석 결과 조회"""
        try:
            result = self.supabase_client.client.table("podcast_analyses").select("*").eq("id", analysis_id).execute()
            
            if not result.data:
                return None
            
            data = result.data[0]
            
            # PodcastAnalysis 엔티티로 변환
            analysis = PodcastAnalysis.create(
                field=data["field"],
                papers=data["papers"],
                analysis_text=data["analysis_text"],
                audio_file_path=data["audio_file_path"],
                duration_seconds=data["duration_seconds"]
            )
            
            # ID와 created_at 복원
            analysis.id = data["id"]
            from datetime import datetime
            analysis.created_at = datetime.fromisoformat(data["created_at"])
            
            return analysis
            
        except Exception as e:
            logger.error(f"팟캐스트 분석 결과 조회 실패: {e}")
            return None
    
    async def get_all_analyses(self, limit: int = 10, offset: int = 0) -> List[PodcastAnalysis]:
        """모든 팟캐스트 분석 결과 조회"""
        try:
            result = self.supabase_client.client.table("podcast_analyses").select("*").order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            analyses = []
            for data in result.data:
                analysis = PodcastAnalysis.create(
                    field=data["field"],
                    papers=data["papers"],
                    analysis_text=data["analysis_text"],
                    audio_file_path=data["audio_file_path"],
                    duration_seconds=data["duration_seconds"]
                )
                
                # ID와 created_at 복원
                analysis.id = data["id"]
                from datetime import datetime
                analysis.created_at = datetime.fromisoformat(data["created_at"])
                
                analyses.append(analysis)
            
            return analyses
            
        except Exception as e:
            logger.error(f"팟캐스트 분석 목록 조회 실패: {e}")
            return []
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """팟캐스트 분석 결과 삭제"""
        try:
            result = self.supabase_client.client.table("podcast_analyses").delete().eq("id", analysis_id).execute()
            
            if result.data:
                logger.info(f"팟캐스트 분석 결과 삭제 완료: {analysis_id}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"팟캐스트 분석 결과 삭제 실패: {e}")
            return False