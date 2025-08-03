#!/usr/bin/env python3
"""
연구실 검색 기능 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.shared.application.services.lab_search_service import LabSearchService
from app.shared.domain.value_objects.research_area_mapper import ResearchAreaMapper

def test_research_area_mapping():
    """연구 분야 매핑 테스트"""
    print("🔍 연구 분야 매핑 테스트")
    print("=" * 50)
    
    # 테스트 케이스들
    test_cases = [
        ["자연어처리", "빅데이터분석", "기계학습(딥러닝)"],
        ["Computer Vision", "Domain Adaptaion", "Federeated Learning"],
        ["기계학습", "강화학습", "시스템 최적화"],
        ["딥러닝 최적화", "음성/영상처리", "IoT 시스템 설계"],
        ["IC design", "neuromorphic HW설계"]
    ]
    
    for i, areas in enumerate(test_cases, 1):
        print(f"\n📝 테스트 케이스 {i}: {areas}")
        scores = ResearchAreaMapper.map_research_areas_to_categories(areas)
        primary = ResearchAreaMapper.get_primary_category(areas)
        
        print(f"  주요 카테고리: {primary}")
        print("  카테고리별 점수:")
        for category, score in scores.items():
            if score > 0:
                print(f"    {category}: {score:.2f}")

def test_lab_search():
    """연구실 검색 테스트"""
    print("\n🔍 연구실 검색 테스트")
    print("=" * 50)
    
    service = LabSearchService()
    
    # 카테고리별 검색 테스트
    categories = [
        "Natural Language Processing (NLP)",
        "Computer Vision",
        "Multimodal", 
        "Machine Learning / Deep Learning"
    ]
    
    for category in categories:
        print(f"\n📊 {category} 카테고리 검색:")
        labs = service.search_labs_by_category(category, min_score=0.3)
        print(f"  발견된 연구실 수: {len(labs)}")
        
        if labs:
            print("  상위 3개 연구실:")
            for i, lab in enumerate(labs[:3], 1):
                print(f"    {i}. {lab['professor']} ({lab['university']})")
                print(f"       점수: {lab.get('category_score', 0):.2f}")
                print(f"       연구 분야: {', '.join(lab.get('research_areas', []))}")
    
    # 키워드 검색 테스트
    print(f"\n🔍 키워드 검색 테스트:")
    keywords = ["자연어", "비전", "딥러닝", "강화학습"]
    
    for keyword in keywords:
        labs = service.search_labs_by_keyword(keyword)
        print(f"  '{keyword}' 검색 결과: {len(labs)}개")
    
    # 통계 테스트
    print(f"\n📈 카테고리별 통계:")
    stats = service.get_category_statistics()
    for category, count in stats.items():
        print(f"  {category}: {count}개")

def test_specific_labs():
    """특정 연구실 테스트"""
    print("\n🔍 특정 연구실 상세 정보 테스트")
    print("=" * 50)
    
    service = LabSearchService()
    
    # 테스트할 연구실들
    test_labs = [
        ("고영중", "성균관대학교"),
        ("김광수", "성균관대학교"),
        ("김유성", "성균관대학교")
    ]
    
    for professor, university in test_labs:
        print(f"\n📝 {professor} ({university}) 연구실:")
        lab = service.get_lab_details(professor, university)
        
        if lab:
            print(f"  교수: {lab['professor']}")
            print(f"  대학: {lab['university']}")
            print(f"  URL: {lab['url']}")
            print(f"  연구 분야: {', '.join(lab.get('research_areas', []))}")
            
            if 'category_scores' in lab:
                print("  카테고리별 점수:")
                for category, score in lab['category_scores'].items():
                    if score > 0:
                        print(f"    {category}: {score:.2f}")
            
            print(f"  논문 수: {len(lab.get('publications', []))}")
        else:
            print(f"  ❌ 연구실을 찾을 수 없습니다")

if __name__ == "__main__":
    print("🧪 연구실 검색 기능 테스트 시작")
    print("=" * 60)
    
    try:
        test_research_area_mapping()
        test_lab_search()
        test_specific_labs()
        
        print("\n✅ 모든 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc() 