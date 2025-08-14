import os
import json
import asyncio
import aiohttp
from supabase import create_client
from dotenv import load_dotenv
import time
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class OptimizedICLREmbeddingGenerator:
    def __init__(self):
        # OpenAI API 설정
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_base_url = "https://api.openai.com/v1"
        self.model_name = "text-embedding-3-small"
        
        # Supabase 설정
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        
        # 배치 설정 (더 작게)
        self.batch_size = 5  # 더 작은 배치로 timeout 방지
        self.max_retries = 3
        self.retry_delay = 2
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase 환경변수가 설정되지 않았습니다.")
    
    async def get_embedding_batch(self, session: aiohttp.ClientSession, texts: list) -> list:
        """배치로 여러 텍스트의 임베딩을 한 번에 생성합니다."""
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "input": texts,  # 여러 텍스트를 한 번에 처리
            "model": self.model_name
        }
        
        for attempt in range(self.max_retries):
            try:
                async with session.post(
                    f"{self.openai_base_url}/embeddings",
                    headers=headers,
                    json=data,
                    ssl=False,
                    timeout=aiohttp.ClientTimeout(total=60)  # 타임아웃 설정
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return [item["embedding"] for item in result["data"]]
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenAI API 오류: {response.status} - {error_text}")
                        
                        if response.status == 429:  # Rate limit
                            wait_time = (attempt + 1) * self.retry_delay * 2
                            logger.info(f"Rate limit 도달. {wait_time}초 대기...")
                            await asyncio.sleep(wait_time)
                        else:
                            raise Exception(f"API 오류: {response.status}")
                            
            except Exception as e:
                logger.error(f"배치 임베딩 생성 실패 (시도 {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    raise
        
        raise Exception("최대 재시도 횟수 초과")
    
    def prepare_text_for_embedding(self, title: str, abstract: str) -> str:
        """제목과 초록을 결합하여 임베딩용 텍스트를 준비합니다."""
        title = title.strip() if title else ""
        abstract = abstract.strip() if abstract else ""
        
        # 너무 긴 텍스트는 잘라내기 (OpenAI 토큰 제한 고려)
        if len(abstract) > 1000:
            abstract = abstract[:1000] + "..."
        
        combined_text = f"Title: {title}\n\nAbstract: {abstract}"
        return combined_text
    
    def get_iclr_papers_without_embeddings(self, limit=None):
        """임베딩이 없는 ICLR 논문들을 가져옵니다."""
        try:
            query = self.supabase.table("papers").select("*").eq("conference", "ICLR").is_("combined_embedding", "null")
            
            if limit:
                query = query.limit(limit)
                
            result = query.execute()
            papers = result.data
            
            logger.info(f"임베딩이 없는 ICLR 논문: {len(papers)}개")
            return papers
            
        except Exception as e:
            logger.error(f"ICLR 논문 조회 실패: {e}")
            return []
    
    def update_paper_embeddings_batch(self, paper_updates: list) -> int:
        """배치로 여러 논문의 임베딩을 업데이트합니다."""
        success_count = 0
        
        for update in paper_updates:
            try:
                result = self.supabase.table("papers").update({
                    'title_embedding': update['title_embedding'],
                    'abstract_embedding': update['abstract_embedding'],
                    'combined_embedding': update['combined_embedding']
                }).eq('id', update['paper_id']).execute()
                
                success_count += 1
                logger.info(f"✅ 논문 {update['paper_id']} 임베딩 업데이트 완료")
                
            except Exception as e:
                logger.error(f"논문 {update['paper_id']} 임베딩 업데이트 실패: {e}")
                
        return success_count
    
    async def process_papers_batch(self, session: aiohttp.ClientSession, papers_batch: list) -> int:
        """배치 단위로 논문 임베딩을 처리합니다."""
        try:
            # 각 논문의 텍스트 준비
            titles = []
            abstracts = []
            combined_texts = []
            
            for paper in papers_batch:
                title = paper['title']
                abstract = paper['abstract']
                combined_text = self.prepare_text_for_embedding(title, abstract)
                
                titles.append(title)
                abstracts.append(abstract[:1000] if abstract else "")  # 초록 길이 제한
                combined_texts.append(combined_text)
            
            logger.info(f"배치 임베딩 생성 중... ({len(papers_batch)}개)")
            
            # 배치로 임베딩 생성
            title_embeddings = await self.get_embedding_batch(session, titles)
            await asyncio.sleep(0.5)  # Rate limit 방지
            
            abstract_embeddings = await self.get_embedding_batch(session, abstracts)
            await asyncio.sleep(0.5)  # Rate limit 방지
            
            combined_embeddings = await self.get_embedding_batch(session, combined_texts)
            await asyncio.sleep(0.5)  # Rate limit 방지
            
            # 업데이트 데이터 준비
            paper_updates = []
            for i, paper in enumerate(papers_batch):
                paper_updates.append({
                    'paper_id': paper['id'],
                    'title_embedding': title_embeddings[i],
                    'abstract_embedding': abstract_embeddings[i],
                    'combined_embedding': combined_embeddings[i]
                })
            
            # DB 업데이트 (개별적으로, timeout 방지)
            success_count = 0
            for update in paper_updates:
                try:
                    result = self.supabase.table("papers").update({
                        'combined_embedding': update['combined_embedding']  # 일단 combined만 업데이트
                    }).eq('id', update['paper_id']).execute()
                    
                    success_count += 1
                    logger.info(f"✅ 논문 {update['paper_id']} 임베딩 업데이트 완료")
                    
                except Exception as e:
                    logger.error(f"논문 {update['paper_id']} 임베딩 업데이트 실패: {e}")
                    
                # 각 업데이트 사이에 작은 대기
                await asyncio.sleep(0.1)
            
            return success_count
            
        except Exception as e:
            logger.error(f"배치 처리 실패: {e}")
            return 0
    
    async def generate_iclr_embeddings(self, limit=None):
        """ICLR 논문들의 임베딩을 생성합니다."""
        logger.info("ICLR 논문 임베딩 생성 시작")
        
        # 임베딩이 없는 ICLR 논문들 가져오기
        papers = self.get_iclr_papers_without_embeddings(limit)
        
        if not papers:
            logger.info("모든 ICLR 논문에 임베딩이 이미 생성되어 있습니다.")
            return {"total_processed": 0, "successful_updates": 0}
        
        logger.info(f"처리할 ICLR 논문: {len(papers)}개")
        
        successful_updates = 0
        total_processed = 0
        
        # HTTP 세션 생성 (SSL 검증 비활성화)
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            # 배치 처리
            for i in range(0, len(papers), self.batch_size):
                batch = papers[i:i+self.batch_size]
                batch_num = i // self.batch_size + 1
                total_batches = (len(papers) + self.batch_size - 1) // self.batch_size
                
                logger.info(f"📤 배치 {batch_num}/{total_batches} 처리 중... ({len(batch)}개)")
                
                try:
                    batch_success = await self.process_papers_batch(session, batch)
                    successful_updates += batch_success
                    total_processed += len(batch)
                    
                    logger.info(f"✅ 배치 {batch_num} 완료: {len(batch)}개 중 {batch_success}개 성공")
                    
                    # 진행률 표시
                    progress = (batch_num / total_batches) * 100
                    logger.info(f"📈 진행률: {progress:.1f}% ({successful_updates}/{len(papers)})")
                    
                    # Rate limit 방지
                    if batch_num < total_batches:
                        await asyncio.sleep(2)
                        
                except Exception as e:
                    logger.error(f"배치 {batch_num} 처리 실패: {e}")
                    total_processed += len(batch)
                    continue
        
        # 결과 반환
        stats = {
            "total_processed": total_processed,
            "successful_updates": successful_updates,
            "success_rate": (successful_updates / total_processed * 100) if total_processed > 0 else 0
        }
        
        logger.info(f"ICLR 임베딩 생성 완료: {stats}")
        return stats
    
    def get_iclr_embedding_stats(self):
        """ICLR 논문의 임베딩 통계를 조회합니다."""
        try:
            # 전체 ICLR 논문 수
            total_result = self.supabase.table("papers").select("id", count="exact").eq("conference", "ICLR").execute()
            total_iclr = total_result.count
            
            # 임베딩이 있는 ICLR 논문 수
            with_embeddings_result = self.supabase.table("papers").select("id", count="exact").eq("conference", "ICLR").not_.is_("combined_embedding", "null").execute()
            iclr_with_embeddings = with_embeddings_result.count
            
            # 커버리지 계산
            coverage = (iclr_with_embeddings / total_iclr * 100) if total_iclr > 0 else 0
            
            return {
                "total_iclr_papers": total_iclr,
                "iclr_with_embeddings": iclr_with_embeddings,
                "iclr_without_embeddings": total_iclr - iclr_with_embeddings,
                "embedding_coverage_percent": round(coverage, 1)
            }
            
        except Exception as e:
            logger.error(f"ICLR 통계 조회 실패: {e}")
            return {}

async def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("📚 최적화된 ICLR 논문 임베딩 생성기")
    print("=" * 60)
    
    try:
        # 임베딩 생성기 초기화
        generator = OptimizedICLREmbeddingGenerator()
        
        # 현재 ICLR 임베딩 통계 확인
        print("📊 현재 ICLR 임베딩 통계:")
        stats = generator.get_iclr_embedding_stats()
        for key, value in stats.items():
            print(f"  - {key}: {value}")
        print()
        
        if stats.get('iclr_without_embeddings', 0) == 0:
            print("✅ 모든 ICLR 논문에 임베딩이 이미 생성되어 있습니다.")
            return
        
        # 사용자 입력
        choice = input("처리할 논문 수를 선택하세요:\n1. 전체 논문 처리\n2. 처음 20개만 테스트\n3. 처음 50개만 처리\n선택 (1/2/3): ")
        
        if choice == "1":
            limit = None
        elif choice == "2":
            limit = 20
        elif choice == "3":
            limit = 50
        else:
            print("잘못된 선택입니다.")
            return
        
        papers_to_process = min(limit or stats.get('iclr_without_embeddings', 0), stats.get('iclr_without_embeddings', 0))
        
        response = input(f"🚀 {papers_to_process}개의 ICLR 논문에 임베딩을 생성하시겠습니까? (y/n): ")
        if response.lower() != 'y':
            print("임베딩 생성을 중단합니다.")
            return
        
        # 임베딩 생성 실행
        start_time = time.time()
        results = await generator.generate_iclr_embeddings(limit)
        end_time = time.time()
        
        print(f"\n🎉 처리 완료!")
        print(f"📊 결과:")
        print(f"  - 총 처리 시간: {end_time - start_time:.2f}초")
        print(f"  - 처리된 논문: {results['total_processed']}개")
        print(f"  - 성공한 업데이트: {results['successful_updates']}개")
        print(f"  - 성공률: {results['success_rate']:.1f}%")
        
        # 최종 ICLR 통계 확인
        print(f"\n📈 최종 ICLR 임베딩 통계:")
        final_stats = generator.get_iclr_embedding_stats()
        for key, value in final_stats.items():
            print(f"  - {key}: {value}")
        
    except Exception as e:
        logger.error(f"실행 중 오류 발생: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 