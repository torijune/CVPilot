# 🎓 주피터 노트북용 대학원 랩실 정보 업데이트 가이드

## 📋 사용 방법

### 1. 모듈 Import
```python
from jupyter_lab_updater import add_lab_from_text, show_template, show_status
```

### 2. 입력 템플릿 확인
```python
show_template()
```

### 3. 현재 상태 확인
```python
show_status()
```


### 4. 랩실 정보 추가
```python
# 랩실 정보 텍스트
lab_text = """
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

# 랩실 정보 추가
success = add_lab_from_text(lab_text)

if success:
    print("✅ 성공적으로 추가되었습니다!")
else:
    print("❌ 추가에 실패했습니다.")
```

### 5. 여러 랩실 한 번에 추가
```python
# 여러 랩실 정보
lab_texts = [
    """
대학명: KAIST
대학 약어: KAIST
학과명: 전산학부
랩실명: 인공지능연구실
교수명: 김철수
교수 이메일: kim.ai@kaist.ac.kr
랩실 홈페이지 url: https://ai.kaist.ac.kr/
랩실 연구 분야: 머신러닝, 딥러닝, 자연어처리
Recent publications: Deep Learning for NLP, ACL, 2025
    """,
    """
대학명: 포항공과대학교
대학 약어: POSTECH
학과명: 컴퓨터공학과
랩실명: 컴퓨터비전연구실
교수명: 이영희
교수 이메일: lee.vision@postech.ac.kr
랩실 홈페이지 url: https://vision.postech.ac.kr/
랩실 연구 분야: 컴퓨터비전, 이미지처리, 객체인식
Recent publications: Computer Vision Applications, CVPR, 2025
    """
]

# 모든 랩실 추가
for lab_text in lab_texts:
    success = add_lab_from_text(lab_text)
    if success:
        print("✅ 추가 완료")
    else:
        print("❌ 추가 실패")
```

## 📝 입력 형식

### 필수 정보
- **대학명**: 대학의 공식 명칭
- **대학 약어**: 대학의 공식 약어
- **학과명**: 학과의 공식 명칭
- **랩실명**: 랩실의 공식 명칭
- **교수명**: 교수님의 성함
- **교수 이메일**: 교수님의 이메일 주소

### 선택 정보
- **랩실 홈페이지 url**: 랩실 공식 웹사이트
- **랩실 연구 분야**: 쉼표나 &로 구분된 연구 분야들
- **Recent publications**: 논문 제목, 회의명, 연도 형식

### 예시
```
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
```

## 🔧 주요 기능

### 1. 자동 파싱
- 텍스트에서 정보를 자동으로 추출
- 정규표현식을 사용한 정확한 파싱
- 누락된 정보 자동 감지

### 2. 중복 방지
- 동일한 랩실명 중복 등록 방지
- 기존 정보 보호

### 3. 자동 구조 생성
- 대학/학과가 없으면 자동 생성
- 올바른 JSON 구조 유지

### 4. 메타데이터 자동 업데이트
- 대학 수, 랩실 수 자동 계산
- 최종 수정일 자동 업데이트

## 📊 출력 예시

### 성공 시
```
🔍 파싱된 정보:
  university_name: 서울대학교
  university_abbr: SNU
  department_name: 컴퓨터공학과
  lab_name: 데이터 마이닝 연구실 (Data Mining Lab.)
  professor_name: 강유
  professor_email: ukang@snu.ac.kr
  homepage: https://datalab.snu.ac.kr/
  research_areas: ['Data Intelligence', 'Learning', 'Reasoning', 'Financial AI']
  publications: [{'title': 'SynQ: Accurate Zero-shot Quantization...', 'authors': '강유', 'conference': 'ICLR, 2025'}]

➕ 새 대학이 추가되었습니다: 서울대학교
➕ 새 학과가 추가되었습니다: 컴퓨터공학과
✅ 랩실이 성공적으로 추가되었습니다: 데이터 마이닝 연구실 (Data Mining Lab.)
✅ 설정 파일이 저장되었습니다: school_lab_config.json
```

### 실패 시
```
❌ 필수 정보가 누락되었습니다: ['university_name', 'department_name']
⚠️ 이미 존재하는 랩실입니다: 데이터 마이닝 연구실 (Data Mining Lab.)
```

## 🎯 활용 사례

### 1. 대학원 진학 상담
```python
# CV 분석 결과와 매칭되는 랩실 찾기
show_status()  # 현재 등록된 랩실 확인
```

### 2. 면접 준비
```python
# 특정 연구 분야 랩실 검색
# (검색 기능은 별도 구현 필요)
```

### 3. 데이터 분석
```python
# 랩실 통계 확인
show_status()  # 대학별, 분야별 통계
```

## 🚀 빠른 시작

```python
# 1. 모듈 import
from jupyter_lab_updater import add_lab_from_text, show_template, show_status

# 2. 템플릿 확인
show_template()

# 3. 랩실 정보 추가
lab_text = """
대학명: [대학명]
대학 약어: [약어]
학과명: [학과명]
랩실명: [랩실명]
교수명: [교수명]
교수 이메일: [이메일]
랩실 홈페이지 url: [URL]
랩실 연구 분야: [분야1, 분야2]
Recent publications: [논문제목, 회의명, 연도]
"""

success = add_lab_from_text(lab_text)

# 4. 결과 확인
show_status()
```

이제 주피터 노트북에서 쉽게 대학원 랩실 정보를 관리할 수 있습니다! 🎓 