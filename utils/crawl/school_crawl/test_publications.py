#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
논문 파싱 로직 테스트
"""

from jupyter_lab_updater import add_lab_from_text

# 테스트용 랩실 정보
test_text = """
대학명: 서울대학교
대학 약어: SNU
학과명: 컴퓨터공학과
랩실명: 데이터 마이닝 연구실 (Data Mining Lab.)
교수명: 강유
교수 이메일: ukang@snu.ac.kr
랩실 홈페이지 url: https://datalab.snu.ac.kr/
랩실 연구 분야: Data Intelligence, Learning & Reasoning, Financial AI
Recent publications: SynQ: Accurate Zero-shot Quantization by Synthesis-aware Fine-tuning, ICLR, 2025
Accurate Link Prediction for Edge-Incomplete Graphs via PU Learning, AAAI 2025
Sequentially Diversified and Accurate Recommendations in Chronological Order for a Series of Users, WSDM 2025
Fast and Accurate PARAFAC2 Decomposition for Time Range Queries on Irregular Tensors, CIKM 2024
FreQuant: A Reinforcement-Learning based Adaptive Portfolio Optimization with Multi-frequency Decomposition, KDD 2024
"""

print("🧪 논문 파싱 테스트")
print("=" * 50)

# 랩실 정보 추가
success = add_lab_from_text(test_text)

if success:
    print("\n✅ 테스트 성공!")
    
    # 결과 확인을 위해 JSON 파일 읽기
    import json
    with open('school_lab_config.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 논문 정보 출력
    if data['universities']:
        uni = data['universities'][0]
        if uni['departments']:
            dept = uni['departments'][0]
            if dept['labs']:
                lab = dept['labs'][0]
                publications = lab.get('Recent publications', [])
                
                print(f"\n📚 파싱된 논문 수: {len(publications)}")
                for i, pub in enumerate(publications, 1):
                    print(f"\n{i}. {pub['title']}")
                    print(f"   저자: {pub['authors']}")
                    print(f"   회의: {pub['conference']}")
else:
    print("\n❌ 테스트 실패!") 