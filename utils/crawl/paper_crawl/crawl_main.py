import json
import importlib
import os
import csv
from typing import List, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv
import time

# 환경변수 로드
load_dotenv()

# Supabase 클라이언트 설정
SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_KEY
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️ Supabase 환경변수가 설정되지 않았습니다. DB 저장을 건너뜁니다.")
    supabase: Client = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase 클라이언트 생성 완료")
    
    # 실제 연결 테스트
    try:
        # papers 테이블에 접근해서 연결 상태 확인
        result = supabase.table('papers').select('id').limit(1).execute()
        print("✅ Supabase 연결 및 papers 테이블 접근 성공")
    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        print("⚠️ DB 저장을 건너뜁니다.")
        supabase = None

def load_existing_papers(csv_file: str) -> set:
    """
    기존 CSV 파일에서 논문 제목과 컨퍼런스를 읽어서 중복 체크용 set 반환
    """
    existing_papers = set()
    if os.path.exists(csv_file):
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 제목과 컨퍼런스 조합으로 중복 체크
                    paper_key = (row.get('title', '').strip(), row.get('conference', '').strip())
                    existing_papers.add(paper_key)
            print(f"📖 기존 CSV 파일에서 {len(existing_papers)}개 논문 로드 완료")
        except Exception as e:
            print(f"⚠️ 기존 CSV 파일 읽기 실패: {e}")
    return existing_papers

def check_paper_exists(title: str, conference: str, existing_papers: set) -> bool:
    """
    논문이 이미 CSV에 존재하는지 확인
    """
    paper_key = (title.strip(), conference.strip())
    return paper_key in existing_papers

def save_paper_to_csv(paper: Dict, field_name: str, conf_name: str, csv_file: str, existing_papers: set) -> bool:
    """
    단일 논문을 CSV 파일에 저장 (중복 체크 포함)
    """
    try:
        # 중복 체크
        if check_paper_exists(paper.get('title', ''), conf_name, existing_papers):
            print(f"⏭️ 중복 논문 패스: {paper.get('title', '')[:50]}...")
            return False
        
        # CSV 저장용 데이터 준비
        csv_paper = {
            'title': paper.get('title', ''),
            'abstract': paper.get('abstract', ''),
            'authors': paper.get('authors', ''),
            'conference': conf_name,
            'year': paper.get('year', 2024),
            'field': field_name,
            'url': paper.get('url', '')
        }
        
        # CSV 파일에 추가 (append 모드)
        file_exists = os.path.exists(csv_file)
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ['title', 'abstract', 'authors', 'conference', 'year', 'field', 'url']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # 헤더가 없으면 추가
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(csv_paper)
        
        # 중복 체크용 set에 추가
        paper_key = (paper.get('title', '').strip(), conf_name.strip())
        existing_papers.add(paper_key)
        
        print(f"✅ CSV 저장 완료: {paper.get('title', '')[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ CSV 저장 실패: {e}")
        return False

def main():
    base_dir = os.path.dirname(__file__)
    csv_file = os.path.join(base_dir, "all_papers.csv")
    
    # 기존 CSV 파일에서 중복 체크용 데이터 로드
    existing_papers = load_existing_papers(csv_file)
    
    with open(os.path.join(base_dir, "conference_list.json"), "r", encoding="utf-8") as f:
        conf_data = json.load(f)

    all_results = []
    total_crawled = 0
    total_saved = 0
    total_skipped = 0

    # 이미 크롤링 완료된 학회들 (제외할 학회 목록)
    completed_conferences = {
        "ACL Anthology (ACL, EMNLP, NAACL, COLING)",
        "EMNLP (Empirical Methods in NLP)",
        "NAACL (North American Chapter of ACL)",
        "CVPR (IEEE Conference on Computer Vision and Pattern Recognition)",
        "WACV (Winter Conference on Applications of Computer Vision)",
        "NeurIPS",
        "ECCV (European Conference on Computer Vision)",
        "ICML",
        # 지금 jmlr, icml, iclr 크롤링 중
    }
    
    for field in conf_data["fields"]:
        field_name = field["field"]
        print(f"\n=== {field_name} 분야 크롤링 시작 ===")
        
        for conf in field["conferences"]:
            conf_name = conf["name"]
            conf_url = conf["site"]
            crawler_module = conf.get("crawler")
            
            # 이미 완료된 학회는 건너뛰기
            if conf_name in completed_conferences:
                print(f"[SKIP] {conf_name} (이미 크롤링 완료)")
                continue
            
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
                
                # 실시간 크롤링 및 CSV 저장
                conf_crawled = 0
                conf_saved = 0
                conf_skipped = 0
                
                # 크롤러에서 논문을 하나씩 받아서 실시간 처리
                for paper in crawl_function(conf_url):
                    paper['field'] = field_name
                    paper['conference'] = conf_name
                    all_results.append(paper)
                    conf_crawled += 1
                    
                    # 실시간 CSV 저장
                    if save_paper_to_csv(paper, field_name, conf_name, csv_file, existing_papers):
                        conf_saved += 1
                        total_saved += 1
                    else:
                        conf_skipped += 1
                        total_skipped += 1
                    
                    total_crawled += 1
                
                print(f"[SUCCESS] {conf_name}: {conf_crawled}개 크롤링, {conf_saved}개 저장, {conf_skipped}개 패스")
                
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
    print(f"총 {total_saved}개 논문 CSV 저장 완료!")
    print(f"총 {total_skipped}개 중복 논문 패스!")
    print(f"CSV 파일 저장 위치: {csv_file}")
    print(f"JSON 백업 저장 위치: {output_file}")

if __name__ == "__main__":
    print("SUPABASE_URL: ", os.getenv("SUPABASE_URL"))
    print("SUPABASE_KEY: ", os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

    main()