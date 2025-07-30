#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주피터 노트북 테스트용 코드
"""

# 1. 모듈 import 테스트
try:
    from jupyter_lab_updater import add_lab_from_text, show_template, show_status
    print("✅ 모듈 import 성공")
except Exception as e:
    print(f"❌ 모듈 import 실패: {e}")

# 2. 현재 상태 확인
try:
    print("\n📊 현재 상태:")
    show_status()
except Exception as e:
    print(f"❌ 상태 확인 실패: {e}")

# 3. 템플릿 출력 테스트
try:
    print("\n📝 템플릿:")
    show_template()
except Exception as e:
    print(f"❌ 템플릿 출력 실패: {e}")

# 4. 간단한 랩실 추가 테스트
test_text = """
대학명: 테스트대학교
대학 약어: TEST
학과명: 테스트학과
랩실명: 테스트 연구실
교수명: 테스트교수
교수 이메일: test@test.ac.kr
랩실 홈페이지 url: https://test.ac.kr/
랩실 연구 분야: 테스트 연구
Recent publications: 테스트 논문, TEST, 2024
"""

try:
    print("\n🧪 랩실 추가 테스트:")
    success = add_lab_from_text(test_text)
    if success:
        print("✅ 랩실 추가 성공")
    else:
        print("❌ 랩실 추가 실패")
except Exception as e:
    print(f"❌ 랩실 추가 테스트 실패: {e}")

print("\n🎯 주피터 노트북에서 사용할 수 있는 함수들:")
print("- add_lab_from_text(text): 텍스트에서 랩실 정보를 파싱하고 추가")
print("- show_template(): 입력 템플릿 출력")
print("- show_status(): 현재 등록된 정보 출력") 