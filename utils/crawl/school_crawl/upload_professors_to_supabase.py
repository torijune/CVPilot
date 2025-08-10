import json
import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# .env 파일 로드 (backend 디렉토리의 .env 파일)
load_dotenv("../../../backend/.env")

def upload_professors_to_supabase():
    """simple_lab_config.json의 데이터를 Supabase professors 테이블에 업로드"""
    
    # Supabase 클라이언트 설정
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase 환경변수가 설정되지 않았습니다.")
        return
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase 연결 성공")
    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        return
    
    # simple_lab_config.json 파일 읽기
    config_path = "simple_lab_config.json"
    if not os.path.exists(config_path):
        print(f"❌ {config_path} 파일을 찾을 수 없습니다.")
        return
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ {config_path} 파일 로드 성공")
    except Exception as e:
        print(f"❌ 파일 로드 실패: {e}")
        return
    
    # 기존 professors 테이블 데이터 삭제
    try:
        result = supabase.table("professors").delete().neq("id", 0).execute()
        print("✅ 기존 professors 데이터 삭제 완료")
    except Exception as e:
        print(f"⚠️ 기존 데이터 삭제 실패: {e}")
    
    # 데이터 변환 및 업로드
    professors_data = []
    total_count = 0
    
    for university in data.get("universities", []):
        university_name = university.get("name", "")
        
        for lab in university.get("labs", []):
            professor_name = lab.get("professor", "")
            lab_url = lab.get("url", "")
            research_areas = lab.get("research_areas", [])
            publications = lab.get("publications", [])
            
            # 연구 분야를 하나의 문자열로 결합
            field_str = ", ".join(research_areas) if research_areas else ""
            
            # 논문 제목을 하나의 문자열로 결합
            publications_str = "; ".join(publications) if publications else ""
            
            professor_data = {
                "name": professor_name,
                "university": university_name,
                "lab": lab_url,
                "field": field_str,
                "publications": publications_str
            }
            
            professors_data.append(professor_data)
            total_count += 1
    
    print(f"📊 총 {total_count}명의 교수 데이터 준비 완료")
    
    # 배치로 데이터 업로드 (한 번에 100개씩)
    batch_size = 100
    uploaded_count = 0
    
    for i in range(0, len(professors_data), batch_size):
        batch = professors_data[i:i + batch_size]
        
        try:
            result = supabase.table("professors").insert(batch).execute()
            uploaded_count += len(batch)
            print(f"✅ 배치 {i//batch_size + 1}: {len(batch)}명 업로드 완료 (총 {uploaded_count}/{total_count})")
        except Exception as e:
            print(f"❌ 배치 {i//batch_size + 1} 업로드 실패: {e}")
            return
    
    print(f"🎉 모든 교수 데이터 업로드 완료! 총 {uploaded_count}명")

if __name__ == "__main__":
    upload_professors_to_supabase() 