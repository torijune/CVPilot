#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주피터 노트북용 대학원 랩실 정보 자동 업데이트 도구
텍스트 입력을 받아서 JSON 형식으로 변환하고 config 파일에 추가
"""

import json
import os
import re
from typing import Dict, List, Optional
from datetime import datetime

class JupyterLabUpdater:
    def __init__(self, config_file: str = "school_lab_config.json"):
        """
        주피터 노트북용 랩실 정보 업데이터 초기화
        
        Args:
            config_file (str): 설정 파일 경로
        """
        self.config_file = config_file
        self.data = self._load_config()
    
    def _load_config(self) -> Dict:
        """설정 파일 로드"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._create_default_structure()
        except Exception as e:
            print(f"설정 파일 로드 실패: {e}")
            return self._create_default_structure()
    
    def _create_default_structure(self) -> Dict:
        """기본 JSON 구조 생성"""
        return {
            "universities": [],
            "metadata": {
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "version": "1.0",
                "description": "대학원 랩실 정보 데이터베이스",
                "total_universities": 0,
                "total_labs": 0
            }
        }
    
    def _save_config(self):
        """설정 파일 저장"""
        try:
            # 메타데이터 업데이트
            self.data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            self.data["metadata"]["total_universities"] = len(self.data["universities"])
            
            total_labs = 0
            for university in self.data["universities"]:
                for department in university.get("departments", []):
                    total_labs += len(department.get("labs", []))
            self.data["metadata"]["total_labs"] = total_labs
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"✅ 설정 파일이 저장되었습니다: {self.config_file}")
        except Exception as e:
            print(f"❌ 설정 파일 저장 실패: {e}")
    
    def parse_lab_info_from_text(self, text: str) -> Dict:
        """
        텍스트에서 랩실 정보를 파싱
        
        Args:
            text (str): 파싱할 텍스트
            
        Returns:
            Dict: 파싱된 랩실 정보
        """
        info = {}
        
        # 대학명 추출
        uni_match = re.search(r'대학명:\s*(.+)', text)
        if uni_match:
            info['university_name'] = uni_match.group(1).strip()
        
        # 대학 약어 추출
        abbr_match = re.search(r'대학 약어:\s*(.+)', text)
        if abbr_match:
            info['university_abbr'] = abbr_match.group(1).strip()
        
        # 학과명 추출
        dept_match = re.search(r'학과명:\s*(.+)', text)
        if dept_match:
            info['department_name'] = dept_match.group(1).strip()
        
        # 랩실명 추출
        lab_match = re.search(r'랩실명:\s*(.+)', text)
        if lab_match:
            info['lab_name'] = lab_match.group(1).strip()
        
        # 교수명 추출
        prof_match = re.search(r'교수명:\s*(.+)', text)
        if prof_match:
            info['professor_name'] = prof_match.group(1).strip()
        
        # 교수 이메일 추출
        email_match = re.search(r'교수 이메일:\s*(.+)', text)
        if email_match:
            info['professor_email'] = email_match.group(1).strip()
        
        # 홈페이지 URL 추출
        homepage_match = re.search(r'랩실 홈페이지 url:\s*(.+)', text)
        if homepage_match:
            info['homepage'] = homepage_match.group(1).strip()
        
        # 연구 분야 추출
        research_match = re.search(r'랩실 연구 분야[^:]*:\s*(.+)', text)
        if research_match:
            research_text = research_match.group(1).strip()
            if research_text != "없음":
                # 쉼표나 &로 구분된 연구 분야를 리스트로 변환
                research_areas = [area.strip() for area in re.split(r'[,&]', research_text) if area.strip()]
                info['research_areas'] = research_areas
            else:
                info['research_areas'] = []
        else:
            info['research_areas'] = []
        
        # Recent publications 추출
        publications = []
        
        # "Recent publications:" 다음에 오는 모든 텍스트를 찾기
        pub_section_match = re.search(r'Recent publications:\s*(.*)', text, re.DOTALL)
        if pub_section_match:
            pub_text = pub_section_match.group(1).strip()
            
            # 각 논문을 줄바꿈으로 분리하고 빈 줄 제거
            pub_lines = [line.strip() for line in pub_text.split('\n') if line.strip()]
            
            for line in pub_lines:
                # 논문 제목, 회의명, 연도 패턴 매칭
                # 예: "SynQ: Accurate Zero-shot Quantization by Synthesis-aware Fine-tuning, ICLR, 2025"
                # 또는 "Accurate Link Prediction for Edge-Incomplete Graphs via PU Learning, AAAI 2025"
                
                # 패턴 1: 쉼표가 있는 경우 (ICLR, 2025)
                match1 = re.match(r'^(.+?),\s*([^,]+),\s*(\d{4})$', line.strip())
                if match1:
                    title, conference, year = match1.groups()
                    publications.append({
                        "title": title.strip(),
                        "authors": info.get('professor_name', 'Unknown'),  # 교수명 사용
                        "conference": f"{conference.strip()}, {year}"
                    })
                    continue
                
                # 패턴 2: 쉼표가 없는 경우 (AAAI 2025)
                match2 = re.match(r'^(.+?),\s*([^,]+)\s+(\d{4})$', line.strip())
                if match2:
                    title, conference, year = match2.groups()
                    publications.append({
                        "title": title.strip(),
                        "authors": info.get('professor_name', 'Unknown'),  # 교수명 사용
                        "conference": f"{conference.strip()}, {year}"
                    })
                    continue
                
                # 패턴이 맞지 않는 경우 전체 라인을 제목으로 처리
                publications.append({
                    "title": line.strip(),
                    "authors": info.get('professor_name', 'Unknown'),
                    "conference": "Unknown"
                })
        
        info['publications'] = publications
        
        return info
    
    def add_lab_from_text(self, text: str) -> bool:
        """
        텍스트에서 랩실 정보를 파싱하고 추가
        
        Args:
            text (str): 랩실 정보 텍스트
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 텍스트 파싱
            parsed_info = self.parse_lab_info_from_text(text)
            
            print("🔍 파싱된 정보:")
            for key, value in parsed_info.items():
                print(f"  {key}: {value}")
            
            # 필수 정보 확인
            required_fields = ['university_name', 'department_name', 'lab_name', 'professor_name', 'professor_email']
            missing_fields = [field for field in required_fields if not parsed_info.get(field)]
            
            if missing_fields:
                print(f"❌ 필수 정보가 누락되었습니다: {missing_fields}")
                return False
            
            # 대학 추가/확인
            university = self._find_or_create_university(parsed_info['university_name'], parsed_info.get('university_abbr', ''))
            
            # 학과 추가/확인
            department = self._find_or_create_department(university, parsed_info['department_name'])
            
            # 랩실 정보 구성
            lab_info = {
                "name": parsed_info['lab_name'],
                "professor": {
                    "name": parsed_info['professor_name'],
                    "email": parsed_info['professor_email'],
                    "title": "교수"  # 기본값
                },
                "homepage": parsed_info.get('homepage', ''),
                "research_areas": parsed_info.get('research_areas', []),
                "description": f"{parsed_info['lab_name']}에서 {', '.join(parsed_info.get('research_areas', []))} 연구를 수행합니다.",
                "Recent publications": parsed_info.get('publications', [])
            }
            
            # 중복 확인
            for lab in department.get("labs", []):
                if lab["name"] == lab_info["name"]:
                    print(f"⚠️ 이미 존재하는 랩실입니다: {lab_info['name']}")
                    return False
            
            # 랩실 추가
            if "labs" not in department:
                department["labs"] = []
            department["labs"].append(lab_info)
            
            # 저장
            self._save_config()
            
            print(f"✅ 랩실이 성공적으로 추가되었습니다: {lab_info['name']}")
            return True
            
        except Exception as e:
            print(f"❌ 랩실 추가 실패: {e}")
            return False
    
    def _find_or_create_university(self, name: str, abbreviation: str) -> Dict:
        """대학 찾기 또는 생성"""
        for uni in self.data["universities"]:
            if uni["name"] == name:
                return uni
        
        # 새 대학 생성
        new_university = {
            "name": name,
            "abbreviation": abbreviation,
            "departments": []
        }
        self.data["universities"].append(new_university)
        print(f"➕ 새 대학이 추가되었습니다: {name}")
        return new_university
    
    def _find_or_create_department(self, university: Dict, dept_name: str) -> Dict:
        """학과 찾기 또는 생성"""
        for dept in university.get("departments", []):
            if dept["name"] == dept_name:
                return dept
        
        # 새 학과 생성
        new_department = {
            "name": dept_name,
            "labs": []
        }
        university["departments"].append(new_department)
        print(f"➕ 새 학과가 추가되었습니다: {dept_name}")
        return new_department
    
    def print_current_status(self):
        """현재 상태 출력"""
        print("\n📊 현재 등록된 정보:")
        print(f"  - 대학 수: {len(self.data['universities'])}")
        
        total_labs = 0
        for uni in self.data["universities"]:
            print(f"\n🎓 {uni['name']} ({uni.get('abbreviation', 'N/A')})")
            for dept in uni.get("departments", []):
                lab_count = len(dept.get("labs", []))
                total_labs += lab_count
                print(f"  📖 {dept['name']} - {lab_count}개 랩실")
                for lab in dept.get("labs", []):
                    print(f"    🔬 {lab['name']} (교수: {lab['professor']['name']})")
        
        print(f"\n📈 총 랩실 수: {total_labs}")

def create_lab_info_template():
    """랩실 정보 입력 템플릿 출력"""
    template = """
📝 랩실 정보 입력 템플릿:

대학명: [대학명 입력]
대학 약어: [대학 약어 입력]
학과명: [학과명 입력]
랩실명: [랩실명 입력]
교수명: [교수명 입력]
교수 이메일: [교수 이메일 입력]
랩실 홈페이지 url: [홈페이지 URL 입력]
랩실 연구 분야: [연구 분야1, 연구 분야2, 연구 분야3]
Recent publications: [논문 제목1, [회의명1], [연도1], [논문 제목2, [회의명2], [연도2], ...]
"""
    print(template)

# 주피터 노트북에서 사용할 편의 함수들
def add_lab_from_text(text: str, config_file: str = "school_lab_config.json") -> bool:
    """
    텍스트에서 랩실 정보를 파싱하고 추가 (편의 함수)
    
    Args:
        text (str): 랩실 정보 텍스트
        config_file (str): 설정 파일 경로
        
    Returns:
        bool: 성공 여부
    """
    updater = JupyterLabUpdater(config_file)
    return updater.add_lab_from_text(text)

def show_template():
    """입력 템플릿 출력"""
    create_lab_info_template()

def show_status(config_file: str = "school_lab_config.json"):
    """현재 상태 출력"""
    updater = JupyterLabUpdater(config_file)
    updater.print_current_status()

# 사용 예시
if __name__ == "__main__":
    # 예시 텍스트
    example_text = """
    
- 대학명: 서울대학교
- 대학 약어: SNU
- 학과명: 컴퓨터공학과
- 랩실명: 데이터 마이닝 연구실 (Data Mining Lab.)
- 교수명: 강유
- 교수 이메일: ukang@snu.ac.kr
- 랩실 홈페이지 url: https://datalab.snu.ac.kr/
- 랩실 연구 분야(있으면 넣고 없으면 "없음"): Data Intelligence, Learning &
Reasoning, Financial AI
- Recent publications: SynQ: Accurate Zero-shot Quantization by Synthesis-aware Fine-tuning, ICLR, 2025
Accurate Link Prediction for Edge-Incomplete Graphs via PU Learning, AAAI 2025
Sequentially Diversified and Accurate Recommendations in Chronological Order for a Series of Users, WSDM 2025
Fast and Accurate PARAFAC2 Decomposition for Time Range Queries on Irregular Tensors, CIKM 2024
FreQuant: A Reinforcement-Learning based Adaptive Portfolio Optimization with Multi-frequency Decomposition, KDD 2024
"""
    
    print("🎓 주피터 노트북용 랩실 정보 업데이트 도구")
    print("=" * 50)
    
    # 템플릿 출력
    show_template()
    
    # 예시 실행
    print("\n📝 예시 실행:")
    success = add_lab_from_text(example_text)
    
    if success:
        print("\n📊 업데이트 후 상태:")
        show_status() 