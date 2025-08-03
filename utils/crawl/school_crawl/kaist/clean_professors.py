import json
from typing import Dict, List

def clean_professors_data(input_file: str, output_file: str):
    """교수 데이터를 정리합니다."""
    print(f"🧹 교수 데이터 정리 시작...")
    
    # JSON 파일 로드
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    professors = data.get('professors', [])
    print(f"📊 원본 교수 수: {len(professors)}")
    
    # 중복 제거 및 불완전한 데이터 필터링
    cleaned_professors = []
    seen_combinations = set()
    
    for prof in professors:
        name = prof.get('name', '').strip()
        research_area = prof.get('research_area', '').strip()
        email = prof.get('email', '').strip()
        website = prof.get('website', '').strip()
        
        # 이름과 연구분야가 모두 있는지 확인
        if not name or not research_area:
            print(f"⚠️ 제외: {name} - 이름 또는 연구분야 누락")
            continue
        
        # 이메일과 웹사이트가 모두 있는지 확인
        if not email or not website:
            print(f"⚠️ 제외: {name} - 이메일 또는 웹사이트 누락")
            continue
        
        # 이름 + 연구분야 조합으로 중복 확인
        combination = f"{name}|{research_area}"
        if combination in seen_combinations:
            print(f"⚠️ 제외: {name} - 중복 데이터")
            continue
        
        # 유효한 데이터로 추가
        cleaned_professors.append(prof)
        seen_combinations.add(combination)
        print(f"✅ 유지: {name} - {research_area}")
    
    # 정리된 데이터로 업데이트
    data['professors'] = cleaned_professors
    data['total_professors'] = len(cleaned_professors)
    
    # 정리된 데이터 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 정리 결과:")
    print(f"   원본 교수 수: {len(professors)}")
    print(f"   정리된 교수 수: {len(cleaned_professors)}")
    print(f"   제거된 교수 수: {len(professors) - len(cleaned_professors)}")
    print(f"✅ 정리 완료: {output_file}")
    
    return cleaned_professors

def print_summary(professors: List[Dict]):
    """정리된 교수 목록을 출력합니다."""
    print(f"\n📋 정리된 교수 목록 ({len(professors)}명):")
    
    for i, prof in enumerate(professors, 1):
        print(f"\n   {i}. {prof.get('name', 'N/A')}")
        print(f"      연구분야: {prof.get('research_area', 'N/A')}")
        print(f"      이메일: {prof.get('email', 'N/A')}")
        print(f"      웹사이트: {prof.get('website', 'N/A')}")

def main():
    """메인 실행 함수"""
    input_file = "kaist_gsai_professors_only.json"
    output_file = "kaist_gsai_professors_cleaned.json"
    
    try:
        # 데이터 정리
        cleaned_professors = clean_professors_data(input_file, output_file)
        
        # 결과 요약 출력
        print_summary(cleaned_professors)
        
        print(f"\n🎉 데이터 정리 완료!")
        print(f"   입력 파일: {input_file}")
        print(f"   출력 파일: {output_file}")
        
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {input_file}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main() 