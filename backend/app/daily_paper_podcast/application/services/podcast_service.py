from typing import List, Dict, Any, Optional
import logging
from app.daily_paper_podcast.domain.entities.podcast_analysis import PodcastAnalysis
from app.daily_paper_podcast.domain.entities.paper import Paper
from app.daily_paper_podcast.domain.repositories.paper_repository import PaperRepository
from app.daily_paper_podcast.domain.repositories.podcast_repository import PodcastRepository
from app.shared.infra.external.openai_client import openai_client
from app.daily_paper_podcast.application.workflows.nodes.analysis_nodes import (
    ProblemDefinitionNode,
    ProposedMethodNode,
    ExperimentMethodNode,
    KeyResultsNode,
    ResearchSignificanceNode
)
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

    async def generate_tts_from_analysis(self, analysis_id: str) -> PodcastAnalysis:
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
            
            # TTS를 통한 오디오 파일 생성
            audio_file_path = await self.tts_service.generate_audio(tts_script)
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
        """단일 논문에 대한 5단계 분석 수행"""
        try:
            logger.info(f"단일 논문 분석 시작: {paper.title}")
            
            # Paper 객체를 딕셔너리로 변환하여 분석 노드에 전달
            paper_dict = paper.to_dict()
            papers_list = [paper_dict]  # 단일 논문을 리스트로 감싸서 기존 인터페이스 유지
            
            # 1. 각 단계별 분석 수행 (단일 논문 기준)
            problem_definition = await ProblemDefinitionNode.analyze(papers_list, paper.field)
            proposed_method = await ProposedMethodNode.analyze(papers_list, paper.field)
            experiment_method = await ExperimentMethodNode.analyze(papers_list, paper.field)
            key_results = await KeyResultsNode.analyze(papers_list, paper.field)
            research_significance = await ResearchSignificanceNode.analyze(papers_list, paper.field)
            
            # 2. 단일 논문 분석 결과 통합
            merged_analysis = await self._merge_single_paper_analysis(
                paper, problem_definition, proposed_method, 
                experiment_method, key_results, research_significance
            )
            
            logger.info("단일 논문 분석 완료")
            return merged_analysis
            
        except Exception as e:
            logger.error(f"단일 논문 분석 실패: {e}")
            raise
    
    async def _merge_single_paper_analysis(self, paper: Paper, 
                                         problem_definition: str, proposed_method: str,
                                         experiment_method: str, key_results: str,
                                         research_significance: str) -> str:
        """단일 논문 분석 결과 통합"""
        try:
            prompt = f"""
다음은 {paper.field} 분야의 논문에 대한 5단계 분석 결과입니다.
이 결과들을 구조화된 논문 분석 리포트로 작성해주세요.

## 분석 대상 논문
- **제목**: {paper.title}
- **저자**: {', '.join(paper.authors) if paper.authors else 'N/A'}
- **학회/저널**: {paper.conference or 'N/A'}
- **연도**: {paper.year or 'N/A'}
- **URL**: {paper.url or 'N/A'}

## 5단계 분석 결과

### 1. 문제 정의 (Problem Definition)
{problem_definition}

### 2. 제안 방법 (Proposed Method)
{proposed_method}

### 3. 실험 방법 (Experimental Setup)
{experiment_method}

### 4. 주요 결과 (Key Results)
{key_results}

### 5. 연구 의의 (Research Significance)
{research_significance}

위의 분석 결과를 바탕으로 다음과 같은 구조로 마크다운 형식의 논문 분석 리포트를 작성해주세요:

## 📋 논문 분석 리포트

### 📄 논문 정보 (Paper Information)
- **제목**: {paper.title}
- **저자**: {', '.join(paper.authors) if paper.authors else 'N/A'}
- **학회/저널**: {paper.conference or 'N/A'} {paper.year or 'N/A'}
- **URL**: {paper.url or 'N/A'}

### 🎯 문제 정의 (Problem Definition)
- 이 논문이 풀고자 하는 핵심 문제
- 연구의 배경과 동기

### ⚠️ 기존 접근법 한계 (Limitations of Existing Approaches)
- 기존 방법이 가진 한계/제약/문제점
- 현재 기술의 부족한 점

### 🔬 제안 기법 (Proposed Method)
- 이 논문에서 제안하는 해결책
- 구조, 모델, 핵심 아이디어
- 기술적 혁신점

### 🧪 실험 설계 (Experiment Design)
- 사용한 데이터셋
- 평가 메트릭
- 비교 대상 (SOTA 등)

### 📊 주요 성능 (Key Performance)
- 수치 비교표 또는 핵심 성능 결과 요약
- 주요 실험 결과

### 💭 한줄 요약 (One-line Summary)
- 이 논문을 한 문장으로 요약

### 💡 아이디어/확장 (Idea/Extension)
- 내 연구에 어떻게 적용할 수 있을까?
- 개선할 수 있는 부분은?

### 🤔 SO WHAT?
- 이 연구가 왜 중요한가?
- 어떤 의의를 가지는가?

### 👨‍💼 Reviewer
- 내가 학회 리뷰어가 됐다 생각하고 리뷰하기
- 논문의 장단점 분석

### 🛡️ Defender
- 내가 논문 저자라고 생각하고 리뷰 방어하기
- 논문의 가치와 기여도 방어

### 작성 가이드라인
- 마크다운 형식으로 깔끔하게 정리
- 각 섹션별로 명확한 구분
- 객관적이고 분석적인 톤 유지
- 시각적 구분을 위한 이모지 활용
- 전문용어는 쉽게 풀어서 설명
- 총 길이는 약 2000-3000단어 정도
"""

            response = await openai_client._call_chat_completion(prompt)
            return response
            
        except Exception as e:
            logger.error(f"단일 논문 분석 결과 통합 실패: {e}")
            raise
    
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

위의 분석 결과를 바탕으로 다음과 같은 구조로 팟캐스트용 TTS 대본을 작성해주세요:

=== 팟캐스트 구성 ===
1. 인사 및 논문 소개 (30초 - 1분)
   - 오늘 소개할 논문과 분야 소개
   - 논문의 기본 정보 (제목, 저자, 학회 등)

2. 연구 배경 및 문제 정의 (2-3분)
   - 이 연구가 해결하고자 하는 문제는 무엇인가?
   - 기존 연구의 한계점은?

3. 제안하는 방법론 (3-4분)
   - 이 논문만의 새로운 접근법은?
   - 핵심 아이디어와 기술적 혁신점

4. 실험 및 결과 (2-3분)
   - 어떤 실험을 통해 검증했는가?
   - 주요 성과와 개선 사항

5. 연구 의의 및 마무리 (1-2분)
   - 이 연구가 가지는 학문적/실용적 가치
   - 향후 연구 방향과 응용 가능성
   - 논문 URL 안내

=== 작성 가이드라인 ===
- 자연스럽고 친근한 톤으로 작성
- 전문용어는 쉽게 풀어서 설명
- 각 섹션이 자연스럽게 연결되도록
- 총 길이는 약 8-12분 정도 (약 1500-2000단어)
- 청취자가 흥미를 잃지 않도록 생동감 있게 작성
- 한국어로 작성
"""

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