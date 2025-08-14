import json
from supabase import create_client
import os
from dotenv import load_dotenv
import sys
import time

# 환경변수 로드
load_dotenv()

def create_supabase_client():
    """Supabase 클라이언트 생성"""
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Supabase 환경변수가 설정되지 않았습니다.")
        return None
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        # 연결 테스트
        result = supabase.table('papers').select('id').limit(1).execute()
        print("✅ Supabase 연결 성공")
        return supabase
    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        return None

def load_iclr_papers():
    """개선된 ICLR 논문 데이터 로드"""
    json_file = "iclr_papers_2025_improved.json"
    
    if not os.path.exists(json_file):
        print(f"❌ JSON 파일을 찾을 수 없습니다: {json_file}")
        return None
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        
        print(f"📖 JSON 파일에서 {len(papers)}개 논문 로드 완료")
        return papers
        
    except Exception as e:
        print(f"❌ JSON 파일 로드 실패: {e}")
        return None

def check_duplicates(supabase, papers):
    """중복 논문 체크 및 필터링"""
    print("🔍 중복 논문 체크 중...")
    
    new_papers = []
    duplicate_count = 0
    
    for i, paper in enumerate(papers, 1):
        title = paper['title']
        print(f"체크 중 {i}/{len(papers)}: {title[:50]}...")
        
        try:
            # 제목으로 중복 체크
            result = supabase.table('papers').select('id, title').eq('title', title).execute()
            
            if len(result.data) > 0:
                print(f"  ⏭️ 중복 발견: {title[:50]}...")
                duplicate_count += 1
            else:
                new_papers.append(paper)
                print(f"  ✅ 새 논문: {title[:50]}...")
                
        except Exception as e:
            print(f"  ❌ 체크 실패: {e}")
            # 오류 시 새 논문으로 간주
            new_papers.append(paper)
    
    print(f"\n📊 중복 체크 결과:")
    print(f"  - 전체 논문: {len(papers)}개")
    print(f"  - 중복 논문: {duplicate_count}개")
    print(f"  - 새 논문: {len(new_papers)}개")
    
    return new_papers

def upload_papers_to_supabase(supabase, papers, batch_size=10):
    """논문들을 Supabase에 배치 업로드"""
    if not papers:
        print("⚠️ 업로드할 논문이 없습니다.")
        return 0, 0
    
    print(f"🚀 Supabase 업로드 시작 (배치 크기: {batch_size})")
    
    total_papers = len(papers)
    total_batches = (total_papers + batch_size - 1) // batch_size
    success_count = 0
    error_count = 0
    
    for i in range(0, total_papers, batch_size):
        batch_num = i // batch_size + 1
        batch = papers[i:i+batch_size]
        
        print(f"📤 배치 {batch_num}/{total_batches} 업로드 중... ({len(batch)}개)")
        
        try:
            # 데이터 준비 (필요한 필드만)
            batch_data = []
            for paper in batch:
                paper_data = {
                    'title': paper.get('title', '').strip(),
                    'abstract': paper.get('abstract', '').strip(),
                    'authors': paper.get('authors', '').strip(),
                    'conference': paper.get('conference', 'ICLR').strip(),
                    'year': int(paper.get('year', 2025)),
                    'field': paper.get('field', 'Machine Learning / Deep Learning (ML/DL)').strip(),
                    'url': paper.get('url', '').strip()
                }
                batch_data.append(paper_data)
            
            # Supabase에 업로드
            result = supabase.table('papers').insert(batch_data).execute()
            success_count += len(batch)
            
            print(f"✅ 배치 {batch_num} 성공: {len(batch)}개")
            
            # 진행률 표시
            progress = (batch_num / total_batches) * 100
            print(f"📈 진행률: {progress:.1f}% ({success_count}/{total_papers})")
            
            # 요청 제한 방지를 위한 대기
            if batch_num < total_batches:
                time.sleep(0.5)
                
        except Exception as e:
            error_count += len(batch)
            print(f"❌ 배치 {batch_num} 실패: {e}")
            
            # 재시도
            try:
                print(f"🔄 배치 {batch_num} 재시도...")
                time.sleep(2)
                result = supabase.table('papers').insert(batch_data).execute()
                success_count += len(batch)
                error_count -= len(batch)
                print(f"✅ 배치 {batch_num} 재시도 성공")
            except Exception as e2:
                print(f"❌ 배치 {batch_num} 재시도 실패: {e2}")
    
    print(f"\n=== 업로드 완료 ===")
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {error_count}개")
    print(f"📊 성공률: {success_count/(success_count+error_count)*100:.1f}%")
    
    return success_count, error_count

def verify_upload(supabase):
    """업로드 결과 확인"""
    print("\n🔍 업로드 결과 확인...")
    
    try:
        # ICLR 논문 수 확인
        result = supabase.table('papers').select('id', count='exact').eq('conference', 'ICLR').execute()
        iclr_count = result.count
        
        print(f"📊 DB에 저장된 ICLR 논문 수: {iclr_count}개")
        
        # 최근 업로드된 ICLR 논문 몇 개 확인
        result = supabase.table('papers').select('title, conference, year').eq('conference', 'ICLR').eq('year', 2025).limit(5).execute()
        recent_papers = result.data
        
        print(f"\n📄 최근 업로드된 ICLR 2025 논문 (처음 5개):")
        for paper in recent_papers:
            print(f"  - {paper['title'][:60]}... ({paper['year']})")
            
    except Exception as e:
        print(f"❌ 결과 확인 실패: {e}")

def main():
    """메인 함수"""
    print("=" * 60)
    print("📚 ICLR Papers (Improved) to Supabase Uploader")
    print("=" * 60)
    
    # 1. Supabase 클라이언트 생성
    supabase = create_supabase_client()
    if supabase is None:
        sys.exit(1)
    
    # 2. ICLR 논문 데이터 로드
    papers = load_iclr_papers()
    if papers is None:
        sys.exit(1)
    
    # 3. 중복 체크
    new_papers = check_duplicates(supabase, papers)
    
    if not new_papers:
        print("✅ 모든 논문이 이미 DB에 존재합니다. 업로드할 새 논문이 없습니다.")
        verify_upload(supabase)
        sys.exit(0)
    
    # 4. 업로드 확인
    print(f"\n📋 업로드 정보:")
    print(f"  - 전체 논문: {len(papers)}개")
    print(f"  - 새 논문: {len(new_papers)}개")
    print(f"  - 첫 번째 논문: {new_papers[0]['title'][:50]}...")
    print(f"  - 마지막 논문: {new_papers[-1]['title'][:50]}...")
    
    response = input(f"\n{len(new_papers)}개의 새 논문을 업로드하시겠습니까? (y/n): ")
    if response.lower() != 'y':
        print("업로드를 중단합니다.")
        sys.exit(0)
    
    # 5. Supabase 업로드
    success_count, error_count = upload_papers_to_supabase(supabase, new_papers)
    
    # 6. 결과 확인
    if success_count > 0:
        print(f"\n🎉 업로드 완료! {success_count}개 ICLR 논문이 Supabase에 저장되었습니다.")
        verify_upload(supabase)
    else:
        print(f"\n❌ 업로드 실패! {error_count}개 논문이 업로드되지 않았습니다.")

if __name__ == "__main__":
    main() 