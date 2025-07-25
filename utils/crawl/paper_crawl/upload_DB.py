import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv
import time
import sys

# 환경변수 로드
load_dotenv()

def create_supabase_client():
    """Supabase 클라이언트 생성"""
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Supabase 환경변수가 설정되지 않았습니다.")
        print("SUPABASE_URL과 SUPABASE_KEY를 .env 파일에 설정해주세요.")
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

def load_csv_file(csv_path):
    """CSV 파일 로드 및 전처리"""
    try:
        print(f"📖 CSV 파일 로드 중: {csv_path}")
        df = pd.read_csv(csv_path)
        
        # 컬럼명 확인
        expected_columns = ['title', 'abstract', 'authors', 'conference', 'year', 'field', 'url']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ 누락된 컬럼: {missing_columns}")
            return None
        
        # 데이터 전처리
        df = df.fillna('')  # NaN 값을 빈 문자열로 변환
        
        # year 컬럼을 정수형으로 변환
        df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(2024).astype(int)
        
        print(f"✅ CSV 로드 완료: {len(df)}개 행")
        print(f"📊 컬럼: {list(df.columns)}")
        
        return df
        
    except FileNotFoundError:
        print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")
        return None
    except Exception as e:
        print(f"❌ CSV 파일 로드 실패: {e}")
        return None

def check_existing_data(supabase, df):
    """기존 데이터와 중복 체크"""
    try:
        print("🔍 기존 데이터 중복 체크 중...")
        
        # 기존 데이터 수 확인
        result = supabase.table('papers').select('id').execute()
        existing_count = len(result.data)
        print(f"📊 기존 데이터: {existing_count}개")
        
        if existing_count == 0:
            print("✅ 기존 데이터 없음 - 전체 업로드 가능")
            return df
        
        # 중복 체크 (샘플로 확인)
        sample_titles = df['title'].head(10).tolist()
        duplicates = []
        
        for title in sample_titles:
            result = supabase.table('papers').select('id').eq('title', title).execute()
            if len(result.data) > 0:
                duplicates.append(title)
        
        if duplicates:
            print(f"⚠️ 중복 데이터 발견 (샘플): {len(duplicates)}개")
            print("처음 3개 중복 제목:")
            for title in duplicates[:3]:
                print(f"  - {title[:50]}...")
            
            # 중복 제거 옵션
            response = input("업로드할 데이터에서 중복을 제거하시겠습니까? (y/n): ")
            if response.lower() == 'y':
                # 중복 제거 로직 (제목 기준) - 업로드할 데이터에서만 제거
                print("업로드할 데이터에서 중복 제거 중...")
                original_count = len(df)
                
                # DB에 이미 존재하는 제목들을 찾아서 제거
                titles_to_remove = []
                for title in df['title']:
                    result = supabase.table('papers').select('id').eq('title', title).execute()
                    if len(result.data) > 0:
                        titles_to_remove.append(title)
                
                # 중복된 제목들을 제거
                df = df[~df['title'].isin(titles_to_remove)]
                
                removed_count = original_count - len(df)
                print(f"✅ 중복 제거 완료: {removed_count}개 제거, {len(df)}개 남음")
            else:
                print("업로드를 중단합니다.")
                return None
        else:
            print("✅ 중복 데이터 없음")
        
        return df
        
    except Exception as e:
        print(f"❌ 중복 체크 실패: {e}")
        return df

def upload_to_supabase(supabase, df, batch_size=2000):
    """Supabase에 데이터 업로드"""
    try:
        print(f"🚀 Supabase 업로드 시작 (배치 크기: {batch_size})")
        
        total_rows = len(df)
        total_batches = (total_rows + batch_size - 1) // batch_size
        
        success_count = 0
        error_count = 0
        start_time = time.time()
        
        for i in range(0, total_rows, batch_size):
            batch_num = i // batch_size + 1
            batch = df.iloc[i:i+batch_size]
            data = batch.to_dict('records')
            
            print(f"📤 배치 {batch_num}/{total_batches} 업로드 중... ({len(data)}개)")
            
            try:
                result = supabase.table('papers').insert(data).execute()
                success_count += len(data)
                print(f"✅ 배치 {batch_num} 성공: {len(data)}개")
                
                # 진행률 표시
                progress = (batch_num / total_batches) * 100
                print(f"📈 진행률: {progress:.1f}% ({success_count}/{total_rows})")
                
            except Exception as e:
                error_count += len(data)
                print(f"❌ 배치 {batch_num} 실패: {e}")
                
                # 실패한 배치 재시도 (선택사항)
                try:
                    time.sleep(1)
                    result = supabase.table('papers').insert(data).execute()
                    success_count += len(data)
                    error_count -= len(data)
                    print(f"✅ 배치 {batch_num} 재시도 성공")
                except Exception as e2:
                    print(f"❌ 배치 {batch_num} 재시도 실패: {e2}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n=== 업로드 완료 ===")
        print(f"✅ 성공: {success_count}개")
        print(f"❌ 실패: {error_count}개")
        print(f"📊 성공률: {success_count/(success_count+error_count)*100:.1f}%")
        print(f"⏱️ 총 소요 시간: {total_time:.2f}초")
        print(f"🚀 초당 처리: {success_count/total_time:.0f}개")
        
        return success_count, error_count
        
    except Exception as e:
        print(f"❌ 업로드 실패: {e}")
        return 0, total_rows

def main():
    """메인 함수"""
    print("=" * 50)
    print("📚 Papers CSV to Supabase Uploader")
    print("=" * 50)
    
    # 1. Supabase 클라이언트 생성
    supabase = create_supabase_client()
    if supabase is None:
        sys.exit(1)
    
    # 2. CSV 파일 경로 설정
    csv_path = "all_papers.csv"
    if not os.path.exists(csv_path):
        print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")
        print("현재 디렉토리에 all_papers.csv 파일이 있는지 확인해주세요.")
        sys.exit(1)
    
    # 3. CSV 파일 로드
    df = load_csv_file(csv_path)
    if df is None:
        sys.exit(1)
    
    # 4. 기존 데이터 중복 체크
    df = check_existing_data(supabase, df)
    if df is None:
        sys.exit(1)
    
    # 5. 업로드 확인
    print(f"\n📋 업로드 정보:")
    print(f"  - 파일: {csv_path}")
    print(f"  - 행 수: {len(df)}개")
    print(f"  - 컬럼: {list(df.columns)}")
    
    response = input("\n업로드를 시작하시겠습니까? (y/n): ")
    if response.lower() != 'y':
        print("업로드를 중단합니다.")
        sys.exit(0)
    
    # 6. Supabase 업로드
    success_count, error_count = upload_to_supabase(supabase, df)
    
    if success_count > 0:
        print(f"\n🎉 업로드 완료! {success_count}개 논문이 Supabase에 저장되었습니다.")
    else:
        print(f"\n❌ 업로드 실패! {error_count}개 논문이 업로드되지 않았습니다.")

if __name__ == "__main__":
    main()
