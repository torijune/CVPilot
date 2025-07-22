import json
import importlib
import os
from typing import List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv
import time

# 환경변수 로드
load_dotenv()

# Supabase 클라이언트 설정
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️ Supabase 환경변수가 설정되지 않았습니다. DB 저장을 건너뜁니다.")
    supabase: Client = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase 클라이언트 연결 성공")

def check_paper_exists(title: str, conference: str) -> bool:
    """
    논문이 이미 DB에 존재하는지 확인
    """
    if not supabase:
        return False
    
    try:
        result = supabase.table('papers').select('id').eq('title', title).eq('conference', conference).execute()
        return len(result.data) > 0
    except Exception as e:
        print(f"❌ 중복 체크 실패: {e}")
        return False

def insert_single_paper_to_supabase(paper: Dict, field_name: str, conf_name: str) -> bool:
    """
    단일 논문을 Supabase DB에 삽입
    """
    if not supabase:
        print("⚠️ Supabase 클라이언트가 없어 DB 저장을 건너뜁니다.")
        return False
    
    try:
        # 중복 체크
        if check_paper_exists(paper.get('title', ''), conf_name):
            print(f"⏭️ 중복 논문 패스: {paper.get('title', '')[:50]}...")
            return False
        
        # DB 삽입용 데이터 준비
        db_paper = {
            'title': paper.get('title', ''),
            'abstract': paper.get('abstract', ''),
            'conference': conf_name,
            'year': paper.get('year', 2024),
            'field': field_name,
            'url': paper.get('url', '')
        }
        
        # 단일 논문 삽입
        result = supabase.table('papers').insert(db_paper).execute()
        print(f"✅ DB 저장 완료: {paper.get('title', '')[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ DB 저장 실패: {e}")
        return False

def main():
    base_dir = os.path.dirname(__file__)
    with open(os.path.join(base_dir, "conference_list.json"), "r", encoding="utf-8") as f:
        conf_data = json.load(f)

    all_results = []
    total_crawled = 0
    total_inserted = 0
    total_skipped = 0

    for field in conf_data["fields"]:
        field_name = field["field"]
        print(f"\n=== {field_name} 분야 크롤링 시작 ===")
        
        for conf in field["conferences"]:
            conf_name = conf["name"]
            conf_url = conf["site"]
            crawler_module = conf.get("crawler")
            
            if not crawler_module:
                print(f"[SKIP] {conf_name} (crawler 미지정)")
                continue
                
            try:
                # 동적 모듈 import (상대 경로 사용)
                module_path = f"crawlers.{crawler_module}"
                crawler_module_obj = importlib.import_module(module_path)
                
                # 크롤러 함수 호출 (모듈에서 crawl_all_papers 함수 찾기)
                if hasattr(crawler_module_obj, 'crawl_all_papers'):
                    crawl_function = getattr(crawler_module_obj, 'crawl_all_papers')
                elif hasattr(crawler_module_obj, f'{crawler_module}_crawler'):
                    crawl_function = getattr(crawler_module_obj, f'{crawler_module}_crawler')
                else:
                    print(f"[ERROR] {conf_name}: crawl_all_papers 함수를 찾을 수 없습니다")
                    continue
                
                print(f"[INFO] {field_name} - {conf_name} 크롤링 시작")
                
                # 실시간 크롤링 및 DB 저장
                conf_crawled = 0
                conf_inserted = 0
                conf_skipped = 0
                
                # 크롤러에서 논문을 하나씩 받아서 실시간 처리
                for paper in crawl_function(conf_url):
                    paper['field'] = field_name
                    paper['conference'] = conf_name
                    all_results.append(paper)
                    conf_crawled += 1
                    
                    # 실시간 DB 저장
                    if insert_single_paper_to_supabase(paper, field_name, conf_name):
                        conf_inserted += 1
                        total_inserted += 1
                    else:
                        conf_skipped += 1
                        total_skipped += 1
                    
                    total_crawled += 1
                
                print(f"[SUCCESS] {conf_name}: {conf_crawled}개 크롤링, {conf_inserted}개 저장, {conf_skipped}개 패스")
                
            except ImportError as e:
                print(f"[ERROR] {conf_name}: 크롤러 모듈을 찾을 수 없습니다 - {e}")
            except Exception as e:
                print(f"[ERROR] {conf_name} 크롤링 실패: {e}")

    # 결과 저장 (로컬 백업용)
    output_file = os.path.join(base_dir, "all_papers.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 크롤링 완료 ===")
    print(f"총 {total_crawled}개 논문 크롤링 완료!")
    print(f"총 {total_inserted}개 논문 DB 저장 완료!")
    print(f"총 {total_skipped}개 중복 논문 패스!")
    print(f"로컬 백업 저장 위치: {output_file}")

if __name__ == "__main__":
    main()