from typing import List, Dict, Any, Optional
import logging
from app.daily_paper_podcast.domain.entities.podcast_analysis import PodcastAnalysis
from app.daily_paper_podcast.domain.entities.paper import Paper
from app.daily_paper_podcast.domain.repositories.paper_repository import PaperRepository
from app.daily_paper_podcast.domain.repositories.podcast_repository import PodcastRepository
from app.shared.infra.external.openai_client import get_openai_client
# 기존 분석 노드들은 더 이상 사용하지 않음 (통합 프롬프트로 대체)
from app.daily_paper_podcast.infra.services.tts_service import TTSService

logger = logging.getLogger(__name__)

class PodcastService:
    """팟캐스트 서비스"""
    
    def __init__(self, paper_repository: PaperRepository, podcast_repository: PodcastRepository):
        self.paper_repository = paper_repository
        self.podcast_repository = podcast_repository
        self.tts_service = TTSService()
    
    async def analyze_paper_only(self, field: str, papers: List[Dict[str, Any]] = None) -> PodcastAnalysis:
        """논문 분석만 수행 (TTS 생성 제외)"""
        try:
            logger.info(f"논문 분석 시작: {field} 분야")
            
            # 1. DB에서 랜덤으로 단일 논문 가져오기
            if not papers:
                papers_entities = await self.paper_repository.get_random_papers_by_field(field, limit=1)
                if not papers_entities:
                    raise Exception(f"{field} 분야에서 논문을 찾을 수 없습니다.")
                
                selected_paper = papers_entities[0]
                logger.info(f"선택된 논문: {selected_paper.title}")
            else:
                # papers가 제공된 경우 첫 번째 논문만 사용
                if not papers:
                    raise Exception("논문이 제공되지 않았습니다.")
                
                paper_data = papers[0]
                selected_paper = Paper.create(
                    title=paper_data.get('title', ''),
                    abstract=paper_data.get('abstract', ''),
                    authors=paper_data.get('authors', []),
                    conference=paper_data.get('conference'),
                    year=paper_data.get('year'),
                    field=paper_data.get('field'),
                    url=paper_data.get('url')
                )
                logger.info(f"선택된 논문: {selected_paper.title}")
            
            # 2. 단일 논문에 대한 5단계 분석 수행
            analysis_text = await self._generate_single_paper_analysis(selected_paper)
            
            # 3. 결과 생성 (오디오 파일 없이)
            podcast_analysis = PodcastAnalysis.create(
                field=field,
                papers=[selected_paper.to_dict()],
                analysis_text=analysis_text,
                audio_file_path="",  # 아직 생성되지 않음
                duration_seconds=0
            )
            
            # 4. 데이터베이스에 저장 (임시로 주석 처리)
            try:
                await self.podcast_repository.save_analysis(podcast_analysis)
            except Exception as e:
                logger.warning(f"데이터베이스 저장 실패 (임시): {e}")
                # 임시로 저장 실패해도 계속 진행
            
            logger.info(f"논문 분석 완료: {selected_paper.title} 논문 분석")
            return podcast_analysis
            
        except Exception as e:
            logger.error(f"논문 분석 실패: {e}")
            raise

    async def generate_tts_from_analysis(self, analysis_id: str, tts_settings: dict = None) -> PodcastAnalysis:
        """기존 분석 결과를 바탕으로 TTS 생성"""
        try:
            # 기존 분석 결과 조회
            analysis = await self.get_podcast_analysis(analysis_id)
            if not analysis:
                raise Exception("분석 결과를 찾을 수 없습니다.")
            
            # 논문 정보 추출
            paper_data = analysis.papers[0] if analysis.papers else None
            if not paper_data:
                raise Exception("논문 정보가 없습니다.")
            
            paper = Paper.create(
                title=paper_data.get('title', ''),
                abstract=paper_data.get('abstract', ''),
                authors=paper_data.get('authors', []),
                conference=paper_data.get('conference'),
                year=paper_data.get('year'),
                field=paper_data.get('field'),
                url=paper_data.get('url')
            )
            
            # TTS 대본 생성
            tts_script = await self._generate_tts_script(paper, analysis.analysis_text)
            
            # TTS 설정을 적용하여 오디오 파일 생성
            audio_file_path = await self.tts_service.generate_audio(tts_script, tts_settings)
            duration_seconds = await self.tts_service.get_audio_duration(audio_file_path)
            
            # 오디오 파일 경로를 웹 URL로 변환
            import os
            filename = os.path.basename(audio_file_path)
            audio_url = f"/audio/{filename}"  # 상대 경로 사용
            
            # 분석 결과 업데이트
            analysis.audio_file_path = audio_url
            analysis.duration_seconds = duration_seconds if duration_seconds > 0 else len(tts_script.split()) // 3
            
            # 데이터베이스에 업데이트 (기존 레코드 업데이트)
            try:
                await self.podcast_repository.update_analysis(analysis)
            except Exception as e:
                logger.warning(f"데이터베이스 업데이트 실패 (임시): {e}")
                # 데이터베이스 업데이트 실패해도 메모리상의 결과는 업데이트됨
            
            logger.info(f"TTS 생성 완료: {paper.title}")
            logger.info(f"오디오 파일 경로: {audio_url}")
            return analysis
            
        except Exception as e:
            logger.error(f"TTS 생성 실패: {e}")
            raise

    async def generate_podcast(self, field: str, papers: List[Dict[str, Any]] = None) -> PodcastAnalysis:
        """팟캐스트 생성 - 단일 논문 분석"""
        try:
            logger.info(f"팟캐스트 생성 시작: {field} 분야")
            
            # 1. DB에서 랜덤으로 단일 논문 가져오기
            if not papers:
                papers_entities = await self.paper_repository.get_random_papers_by_field(field, limit=1)
                if not papers_entities:
                    raise Exception(f"{field} 분야에서 논문을 찾을 수 없습니다.")
                
                selected_paper = papers_entities[0]
                logger.info(f"선택된 논문: {selected_paper.title}")
            else:
                # papers가 제공된 경우 첫 번째 논문만 사용
                if not papers:
                    raise Exception("논문이 제공되지 않았습니다.")
                
                paper_data = papers[0]
                selected_paper = Paper.create(
                    title=paper_data.get('title', ''),
                    abstract=paper_data.get('abstract', ''),
                    authors=paper_data.get('authors', []),
                    conference=paper_data.get('conference'),
                    year=paper_data.get('year'),
                    field=paper_data.get('field'),
                    url=paper_data.get('url')
                )
            
            # 2. 단일 논문에 대한 5단계 분석 수행
            analysis_text = await self._generate_single_paper_analysis(selected_paper)
            
            # 3. TTS 대본 생성
            tts_script = await self._generate_tts_script(paper, analysis_text)
            
            # 4. TTS를 통한 오디오 파일 생성
            audio_file_path = await self.tts_service.generate_audio(tts_script)
            duration_seconds = await self.tts_service.get_audio_duration(audio_file_path)
            
            # 5. 오디오 파일 경로를 웹 URL로 변환
            import os
            filename = os.path.basename(audio_file_path)
            audio_url = f"/audio/{filename}"  # 상대 경로 사용
            
            # 6. 결과 생성 (단일 논문 정보로)
            podcast_analysis = PodcastAnalysis.create(
                field=field,
                papers=[selected_paper.to_dict()],
                analysis_text=analysis_text,  # 논문 분석 결과
                audio_file_path=audio_url,  # 웹 URL 사용
                duration_seconds=duration_seconds if duration_seconds > 0 else len(tts_script.split()) // 3
            )
            
            # 5. 데이터베이스에 저장 (임시로 주석 처리)
            try:
                await self.podcast_repository.save_analysis(podcast_analysis)
            except Exception as e:
                logger.warning(f"데이터베이스 저장 실패 (임시): {e}")
                # 임시로 저장 실패해도 계속 진행
            
            logger.info(f"팟캐스트 생성 완료: {selected_paper.title} 논문 분석")
            return podcast_analysis
            
        except Exception as e:
            logger.error(f"팟캐스트 생성 실패: {e}")
            raise
    
    async def get_random_papers_for_field(self, field: str, limit: int = 5) -> List[Dict[str, Any]]:
        """분야별 랜덤 논문 조회"""
        try:
            papers_entities = await self.paper_repository.get_random_papers_by_field(field, limit)
            return [paper.to_dict() for paper in papers_entities]
        except Exception as e:
            logger.error(f"랜덤 논문 조회 실패: {e}")
            raise
    
    async def get_available_fields(self) -> List[str]:
        """사용 가능한 분야 목록 조회"""
        try:
            return await self.paper_repository.get_all_fields()
        except Exception as e:
            logger.error(f"분야 목록 조회 실패: {e}")
            raise
    
    async def get_conferences_for_field(self, field: str) -> List[Dict[str, Any]]:
        """분야별 학회 목록 조회 (통계 포함)"""
        try:
            logger.info(f"분야별 학회 목록 조회: {field}")
            
            # Supabase 클라이언트를 통해 학회 목록 조회
            from app.shared.infra.external.supabase_client import supabase_client
            conferences = await supabase_client.get_conferences_by_field(field)
            
            logger.info(f"{field} 분야에서 {len(conferences)}개 학회 발견")
            return conferences
            
        except Exception as e:
            logger.error(f"분야별 학회 목록 조회 실패: {e}")
            raise
    
    async def get_random_paper_preview(self, field: str, conference: str) -> Optional[Dict[str, Any]]:
        """특정 분야와 학회의 랜덤 논문 미리보기"""
        try:
            logger.info(f"랜덤 논문 미리보기: {field} - {conference}")
            
            # Supabase 클라이언트를 통해 랜덤 논문 조회
            from app.shared.infra.external.supabase_client import supabase_client
            paper_data = await supabase_client.get_random_paper_by_field_and_conference(field, conference)
            
            if not paper_data:
                return None
            
            # 해당 학회의 총 논문 수도 함께 조회
            total_papers = await supabase_client.get_papers_count_by_conference(field, conference)
            
            # Paper 엔티티로 변환
            paper = Paper.create(
                title=paper_data.get('title', ''),
                abstract=paper_data.get('abstract', ''),
                authors=paper_data.get('authors', '').split(', ') if paper_data.get('authors') else [],
                conference=paper_data.get('conference'),
                year=paper_data.get('year'),
                field=paper_data.get('field'),
                url=paper_data.get('url')
            )
            
            # ID 복원 (문자열로 변환)
            paper.id = str(paper_data.get('id', ''))
            
            result = {
                'paper': paper.to_dict(),
                'field': field,
                'conference': conference,
                'can_reselect': total_papers > 1,  # 논문이 2개 이상이면 재선택 가능
                'total_papers_in_conference': total_papers
            }
            
            logger.info(f"논문 미리보기 생성 완료: {paper.title[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"랜덤 논문 미리보기 실패: {e}")
            raise
    
    async def reselect_paper(self, field: str, conference: str, current_paper_id: str = None) -> Optional[Dict[str, Any]]:
        """같은 조건으로 다른 논문 재선택"""
        try:
            logger.info(f"논문 재선택: {field} - {conference}")
            
            # 최대 10번 시도해서 다른 논문 찾기
            max_attempts = 10
            for attempt in range(max_attempts):
                paper_preview = await self.get_random_paper_preview(field, conference)
                
                if not paper_preview:
                    break
                
                # 현재 논문과 다른 논문이면 반환
                if not current_paper_id or paper_preview['paper']['id'] != current_paper_id:
                    logger.info(f"재선택 성공 (시도 {attempt + 1}회): {paper_preview['paper']['title'][:50]}...")
                    return paper_preview
            
            # 다른 논문을 찾지 못한 경우, 그냥 아무 논문이나 반환
            logger.warning(f"재선택에서 다른 논문을 찾지 못함, 기존 로직 사용")
            return await self.get_random_paper_preview(field, conference)
            
        except Exception as e:
            logger.error(f"논문 재선택 실패: {e}")
            raise
    
    async def get_podcast_analysis(self, analysis_id: str) -> Optional[PodcastAnalysis]:
        """팟캐스트 분석 결과 조회"""
        try:
            logger.info(f"팟캐스트 분석 결과 조회: {analysis_id}")
            
            # "generating" 상태인 경우 임시 응답 반환 (더 이상 사용되지 않지만 호환성을 위해 유지)
            if analysis_id == "generating":
                logger.info("generating 상태 감지, 임시 응답 생성")
                temp_analysis = PodcastAnalysis.create(
                    field="분석 중...",
                    papers=[],
                    analysis_text="팟캐스트가 생성 중입니다. 잠시만 기다려주세요.",
                    audio_file_path="",
                    duration_seconds=0
                )
                return temp_analysis
            
            # 데이터베이스에서 실제 분석 결과 조회
            analysis = await self.podcast_repository.get_analysis_by_id(analysis_id)
            return analysis
            
        except Exception as e:
            logger.error(f"팟캐스트 분석 결과 조회 실패: {e}")
            return None
    
    async def _generate_single_paper_analysis(self, paper: Paper) -> str:
        """단일 논문에 대한 통합 분석 수행 (한 번의 LLM 호출)"""
        try:
            logger.info(f"단일 논문 통합 분석 시작: {paper.title}")
            
            # 프롬프트 엔지니어링으로 한 번에 모든 분석 수행
            analysis_text = await self._analyze_paper_with_comprehensive_prompt(paper)
            
            logger.info("단일 논문 통합 분석 완료")
            return analysis_text
            
        except Exception as e:
            logger.error(f"단일 논문 분석 실패: {e}")
            raise
    
    async def _analyze_paper_with_comprehensive_prompt(self, paper: Paper) -> str:
        """포괄적인 프롬프트로 논문을 한 번에 분석"""
        try:
            prompt = f"""
당신은 AI/ML 분야의 논문을 전문적으로 분석하는 연구자입니다. 
다음 논문을 체계적이고 깊이 있게 분석해주세요.

## 분석 대상 논문
**제목**: {paper.title}
**저자**: {', '.join(paper.authors) if paper.authors else 'N/A'}
**학회/저널**: {paper.conference or 'N/A'}
**연도**: {paper.year or 'N/A'}
**분야**: {paper.field}
**URL**: {paper.url or 'N/A'}

**초록**:
{paper.abstract}

## 분석 요구사항

다음 구조로 마크다운 형식의 상세한 논문 분석 리포트를 작성해주세요:

### 📄 논문 정보 (Paper Information)
- 논문의 기본 정보를 정리
- 저자들의 배경과 연구 분야
- 학회/저널의 영향력과 중요도

### 🎯 문제 정의 (Problem Definition)
- 이 논문이 해결하고자 하는 핵심 문제는 무엇인가?
- 연구의 배경과 동기는 무엇인가?
- 왜 이 문제가 중요한가?

### ⚠️ 기존 접근법 한계 (Limitations of Existing Approaches)
- 기존 연구들이 가진 한계점은 무엇인가?
- 현재 기술의 부족한 점은?
- 왜 새로운 접근이 필요한가?

### 🔬 제안 기법 (Proposed Method)
- 이 논문에서 제안하는 해결책은 무엇인가?
- 핵심 아이디어와 기술적 혁신점은?
- 방법론의 구조와 작동 원리는?

### 🧪 실험 설계 (Experiment Design)
- 어떤 데이터셋을 사용했는가?
- 평가 메트릭은 무엇인가?
- 비교 대상은 누구인가? (SOTA 등)

### 📊 주요 성능 (Key Performance)
- 핵심 실험 결과와 성능 지표
- 기존 방법 대비 개선 사항
- 수치적 비교 결과

### 💭 한줄 요약 (One-line Summary)
- 이 논문을 한 문장으로 요약

### 💡 아이디어/확장 (Idea/Extension)
- 내 연구에 어떻게 적용할 수 있을까?
- 개선할 수 있는 부분은?
- 향후 연구 방향은?

### 🤔 SO WHAT?
- 이 연구가 왜 중요한가?
- 학문적/실용적 의의는?
- 산업계에 미치는 영향은?

## 작성 가이드라인
1. **깊이 있는 분석**: 표면적이 아닌 본질적인 내용 분석
2. **구체적이고 명확한 설명**: 전문용어는 쉽게 풀어서 설명
3. **비판적 사고**: 장점뿐만 아니라 한계점도 포함
4. **실용적 관점**: 실제 적용 가능성과 현실적 고려사항
5. **미래 지향적**: 향후 연구 방향과 발전 가능성

분석 결과는 마크다운 형식으로 작성하고, 각 섹션은 명확하게 구분해주세요.
"""

            openai_client = get_openai_client()
            response = await openai_client._call_chat_completion(prompt)
            return response
            
        except Exception as e:
            logger.error(f"포괄적 논문 분석 실패: {e}")
            raise
    
    # _merge_single_paper_analysis 메서드는 더 이상 사용하지 않음 (통합 프롬프트로 대체)
    
    async def _generate_tts_script(self, paper: Paper, analysis_text: str) -> str:
        """논문 분석 결과를 바탕으로 TTS 대본 생성"""
        try:
            prompt = f"""
다음은 {paper.field} 분야의 논문에 대한 상세한 분석 결과입니다.
이 분석 결과를 바탕으로 팟캐스트용 TTS 대본을 작성해주세요.

## 분석 대상 논문
- 제목: {paper.title}
- 저자: {', '.join(paper.authors) if paper.authors else 'N/A'}
- 학회/저널: {paper.conference or 'N/A'}
- 연도: {paper.year or 'N/A'}

## 논문 분석 결과
{analysis_text}

위의 분석 결과를 바탕으로 팟캐스트용 TTS 대본을 작성해주세요.

=== 팟캐스트 구성 ===
1. 인사 및 논문 소개 (30초 - 1분)
2. 연구 배경 및 문제 정의 (2-3분)
3. 제안하는 방법론 (3-4분)
4. 실험 및 결과 (2-3분)
5. 연구 의의 및 마무리 (1-2분)

=== 작성 가이드라인 ===
- 자연스럽고 친근한 톤으로 작성
- 전문용어는 쉽게 풀어서 설명
- 각 섹션이 자연스럽게 연결되도록
- 총 길이는 약 8-12분 정도 (약 1500-2000단어)
- 청취자가 흥미를 잃지 않도록 생동감 있게 작성
- 한국어로 작성

=== 중요: 순수 대사만 작성 ===
- 마크다운 형식, 제목, 개요, 블릿 포인트 등을 절대 사용하지 마세요
- "인사말:", "1.", "2.", "제목:", "개요:" 같은 텍스트를 포함하지 마세요
- 순수하게 읽을 수 있는 대사만 작성하세요
- 마치 실제로 누군가에게 말하는 것처럼 자연스럽게 작성하세요

예시:
❌ 잘못된 예시:
"인사말: 안녕하세요. 오늘은..."
"1. 연구 배경: 이 연구는..."
"제목: 논문 소개"

✅ 올바른 예시:
"안녕하세요. 오늘은 AI 분야의 흥미로운 논문을 소개해드리겠습니다..."
"이 연구는 기존 방법의 한계를 극복하기 위해..."
"이 논문의 핵심 아이디어는..."

순수한 대사만 작성해주세요.
"""

            openai_client = get_openai_client()
            response = await openai_client._call_chat_completion(prompt)
            return response
            
        except Exception as e:
            logger.error(f"TTS 대본 생성 실패: {e}")
            raise
    
    async def get_all_podcast_analyses(self, limit: int = 10, offset: int = 0) -> List[PodcastAnalysis]:
        """모든 팟캐스트 분석 결과 조회"""
        try:
            return await self.podcast_repository.get_all_analyses(limit, offset)
        except Exception as e:
            logger.error(f"팟캐스트 분석 목록 조회 실패: {e}")
            return []
    
    async def delete_podcast_analysis(self, analysis_id: str) -> bool:
        """팟캐스트 분석 결과 삭제"""
        try:
            return await self.podcast_repository.delete_analysis(analysis_id)
        except Exception as e:
            logger.error(f"팟캐스트 분석 결과 삭제 실패: {e}")
            return False 