import json
import os
import re
from typing import Dict, List
from datetime import datetime

class SimpleLabInput:
    def __init__(self, config_file: str = "simple_lab_config.json"):
        """
        간소화된 랩실 정보 입력 시스템 초기화
        
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
                "version": "2.0",
                "description": "간소화된 대학원 랩실 정보 데이터베이스",
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
                total_labs += len(university.get("labs", []))
            self.data["metadata"]["total_labs"] = total_labs
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"✅ 설정 파일이 저장되었습니다: {self.config_file}")
        except Exception as e:
            print(f"❌ 설정 파일 저장 실패: {e}")
    
    def parse_lab_info_from_text(self, text: str) -> Dict:
        """텍스트에서 랩실 정보를 파싱합니다."""
        info = {}
        
        # 대학명 추출 (여러 패턴 지원)
        university_match = re.search(r'대학명:\s*([^\n]+)', text)
        if university_match:
            info['university'] = university_match.group(1).strip()
        
        # 교수명 추출
        professor_match = re.search(r'교수명:\s*([^\n]+)', text)
        if professor_match:
            info['professor'] = professor_match.group(1).strip()
        
        # 연구실 URL 추출 (개선된 버전 - 여러 패턴 지원)
        url_patterns = [
            r'연구실 url:\s*([^\n]+)',
            r'연구실 홈페이지 url:\s*([^\n]+)',
            r'랩실 홈페이지 url:\s*([^\n]+)',
            r'홈페이지 url:\s*([^\n]+)',
            r'랩실 홈페이지:\s*([^\n]+)',
            r'홈페이지:\s*([^\n]+)'
        ]
        
        for pattern in url_patterns:
            url_match = re.search(pattern, text)
            if url_match:
                info['url'] = url_match.group(1).strip()
                break
        
        # 연구 분야 추출 (여러 패턴 지원)
        research_patterns = [
            r'연구실 연구 분야:\s*([^\n]+)',
            r'랩실 연구 분야:\s*([^\n]+)',
            r'연구 분야:\s*([^\n]+)'
        ]
        
        for pattern in research_patterns:
            research_match = re.search(pattern, text)
            if research_match:
                research_text = research_match.group(1).strip()
                # 쉼표, &, 그리고 줄바꿈으로 구분된 연구 분야를 리스트로 변환
                research_areas = []
                for area in re.split(r'[,&\n]', research_text):
                    clean_area = area.strip()
                    if clean_area:
                        research_areas.append(clean_area)
                info['research_areas'] = research_areas
                break
        
        # 추가 필드들 파싱
        # 대학 약어
        abbreviation_match = re.search(r'대학 약어:\s*([^\n]+)', text)
        if abbreviation_match:
            info['university_abbreviation'] = abbreviation_match.group(1).strip()
        
        # 학과명
        department_match = re.search(r'학과명:\s*([^\n]+)', text)
        if department_match:
            info['department'] = department_match.group(1).strip()
        
        # 랩실명
        lab_name_match = re.search(r'랩실명:\s*([^\n]+)', text)
        if lab_name_match:
            info['lab_name'] = lab_name_match.group(1).strip()
        
        # 교수 이메일
        email_match = re.search(r'교수 이메일:\s*([^\n]+)', text)
        if email_match:
            info['professor_email'] = email_match.group(1).strip()
        
        # Recent publications 추출 (개선된 버전)
        publications = []
        
        # "Recent publications:" 다음에 오는 모든 텍스트를 찾기
        pub_section_match = re.search(r'Recent publications:\s*(.*?)(?=\n\n|\n[A-Z][a-z]+:|$)', text, re.DOTALL)
        if pub_section_match:
            pub_text = pub_section_match.group(1).strip()
            
            # 각 줄을 분리하고 빈 줄 제거
            lines = [line.strip() for line in pub_text.split('\n') if line.strip()]
            
            current_pub = ""
            for line in lines:
                # 빈 줄이 아니고 "없음"이 아닌 경우만 추가
                if line and line.lower() != "없음" and line.lower() != "none":
                    # 줄 끝의 쉼표나 마침표 제거
                    clean_line = line.rstrip('.,')
                    
                    # 괄호로 시작하는 줄은 이전 논문의 일부로 간주
                    if clean_line.startswith('(') or clean_line.startswith('*'):
                        if current_pub:
                            current_pub += " " + clean_line
                    else:
                        # 이전 논문이 있으면 저장
                        if current_pub:
                            publications.append(current_pub.strip())
                        # 새 논문 시작
                        current_pub = clean_line
            
            # 마지막 논문 추가
            if current_pub:
                publications.append(current_pub.strip())
        
        info['publications'] = publications
        
        return info
    
    def parse_multiple_labs_from_text(self, text: str) -> List[Dict]:
        """텍스트에서 여러 랩실 정보를 파싱합니다."""
        labs = []
        
        # 숫자로 시작하는 섹션들을 찾기 (1., 2., 3. 등) - 더 정확한 패턴
        sections = re.split(r'\n\s*(\d+)\.\s*\n', text)
        
        # 첫 번째 섹션은 빈 문자열이므로 제거
        if sections and not sections[0].strip():
            sections = sections[1:]
        
        # 섹션들을 2개씩 묶어서 처리 (숫자 + 내용)
        for i in range(0, len(sections), 2):
            if i + 1 < len(sections):
                section_number = sections[i]
                section_content = sections[i + 1]
                
                if section_content.strip():
                    lab_info = self.parse_lab_info_from_text(section_content.strip())
                    if lab_info.get('university') and lab_info.get('professor') and lab_info.get('url'):
                        labs.append(lab_info)
                        print(f"✅ 섹션 {section_number} 파싱 성공: {lab_info.get('professor')}")
                    else:
                        print(f"❌ 섹션 {section_number} 파싱 실패: 필수 정보 누락")
        
        return labs
    
    def add_multiple_labs_from_text(self, text: str) -> List[bool]:
        """텍스트에서 여러 랩실 정보를 파싱하고 추가합니다."""
        results = []
        labs = self.parse_multiple_labs_from_text(text)
        
        print(f"🔍 총 {len(labs)}개의 랩실 정보를 발견했습니다.")
        
        for i, lab_info in enumerate(labs, 1):
            print(f"\n📝 랩실 {i} 처리 중...")
            print(f"  대학: {lab_info.get('university')}")
            print(f"  교수: {lab_info.get('professor')}")
            print(f"  URL: {lab_info.get('url')}")
            print(f"  논문 수: {len(lab_info.get('publications', []))}")
            
            # 대학 찾기 또는 생성
            university = self._find_or_create_university(lab_info['university'])
            
            # 랩실 정보 구성 (기본 필드만 저장)
            lab_data = {
                "professor": lab_info['professor'],
                "url": lab_info['url'],
                "publications": lab_info.get('publications', [])
            }
            
            # 연구 분야가 있으면 추가
            if lab_info.get('research_areas'):
                lab_data["research_areas"] = lab_info['research_areas']
            
            # 중복 확인
            duplicate = False
            for lab in university.get("labs", []):
                if lab["professor"] == lab_data["professor"]:
                    print(f"  ⚠️ 이미 존재하는 교수입니다: {lab_data['professor']}")
                    results.append(False)
                    duplicate = True
                    break
            
            if not duplicate:
                # 랩실 추가
                if "labs" not in university:
                    university["labs"] = []
                university["labs"].append(lab_data)
                results.append(True)
                print(f"  ✅ 랩실이 성공적으로 저장되었습니다: {lab_data['professor']}")
        
        # 모든 랩실 처리 후 저장
        if any(results):
            self._save_config()
            print(f"\n🎉 총 {sum(results)}개의 랩실이 성공적으로 저장되었습니다!")
        
        return results
    
    def add_lab_from_text(self, text: str) -> bool:
        """텍스트에서 랩실 정보를 파싱하고 추가합니다."""
        try:
            # 텍스트 파싱
            parsed_info = self.parse_lab_info_from_text(text)
            
            print("🔍 파싱된 정보:")
            for key, value in parsed_info.items():
                print(f"  {key}: {value}")
            
            # 필수 정보 확인
            required_fields = ['university', 'professor', 'url']
            missing_fields = [field for field in required_fields if not parsed_info.get(field)]
            
            if missing_fields:
                print(f"❌ 필수 정보가 누락되었습니다: {missing_fields}")
                return False
            
            # 대학 찾기 또는 생성
            university = self._find_or_create_university(parsed_info['university'])
            
            # 랩실 정보 구성 (기본 필드만 저장)
            lab_info = {
                "professor": parsed_info['professor'],
                "url": parsed_info['url'],
                "publications": parsed_info.get('publications', [])
            }
            
            # 연구 분야가 있으면 추가
            if parsed_info.get('research_areas'):
                lab_info["research_areas"] = parsed_info['research_areas']
            
            # 중복 확인
            for lab in university.get("labs", []):
                if lab["professor"] == lab_info["professor"]:
                    print(f"⚠️ 이미 존재하는 교수입니다: {lab_info['professor']}")
                    return False
            
            # 랩실 추가
            if "labs" not in university:
                university["labs"] = []
            university["labs"].append(lab_info)
            
            # 저장
            self._save_config()
            
            print(f"✅ 랩실이 성공적으로 저장되었습니다: {lab_info['professor']}")
            return True
            
        except Exception as e:
            print(f"❌ 랩실 저장 실패: {e}")
            return False
    
    def _find_or_create_university(self, name: str) -> Dict:
        """대학 찾기 또는 생성"""
        for uni in self.data["universities"]:
            if uni["name"] == name:
                return uni
        
        # 새 대학 생성
        new_university = {
            "name": name,
            "labs": []
        }
        self.data["universities"].append(new_university)
        print(f"➕ 새 대학이 추가되었습니다: {name}")
        return new_university
    
    def print_current_status(self):
        """현재 상태 출력"""
        print("\n📊 현재 등록된 정보:")
        print(f"  - 대학 수: {len(self.data['universities'])}")
        
        total_labs = 0
        for uni in self.data["universities"]:
            print(f"\n🎓 {uni['name']}")
            lab_count = len(uni.get("labs", []))
            total_labs += lab_count
            print(f"  📖 {lab_count}개 랩실")
            for lab in uni.get("labs", []):
                print(f"    🔬 {lab['professor']} - {lab['url']}")
                print(f"       논문 수: {len(lab.get('publications', []))}개")
        
        print(f"\n📈 총 랩실 수: {total_labs}")

class JupyterLabUpdater:
    """주피터 노트북에서 사용하기 위한 랩실 정보 업데이터"""
    
    def __init__(self, config_file: str = "simple_lab_config.json"):
        self.updater = SimpleLabInput(config_file)
    
    def add_lab_from_text(self, text: str) -> bool:
        """텍스트에서 랩실 정보를 파싱하고 추가"""
        return self.updater.add_lab_from_text(text)
    
    def add_multiple_labs_from_text(self, text: str) -> List[bool]:
        """텍스트에서 여러 랩실 정보를 파싱하고 추가"""
        return self.updater.add_multiple_labs_from_text(text)
    
    def show_status(self):
        """현재 상태 출력"""
        self.updater.print_current_status()
    
    def get_current_data(self) -> Dict:
        """현재 데이터 반환"""
        return self.updater.data

# 편의 함수들
def add_lab_from_text(text: str, config_file: str = "simple_lab_config.json") -> bool:
    """
    텍스트에서 랩실 정보를 파싱하고 추가 (편의 함수)
    
    Args:
        text (str): 랩실 정보 텍스트
        config_file (str): 설정 파일 경로
        
    Returns:
        bool: 성공 여부
    """
    updater = SimpleLabInput(config_file)
    return updater.add_lab_from_text(text)

def add_multiple_labs_from_text(text: str, config_file: str = "simple_lab_config.json") -> List[bool]:
    """
    텍스트에서 여러 랩실 정보를 파싱하고 추가 (편의 함수)
    
    Args:
        text (str): 여러 랩실 정보 텍스트 (1., 2., 3. 등으로 구분)
        config_file (str): 설정 파일 경로
        
    Returns:
        List[bool]: 각 랩실의 성공 여부 리스트
    """
    updater = SimpleLabInput(config_file)
    return updater.add_multiple_labs_from_text(text)

def show_status(config_file: str = "simple_lab_config.json"):
    """현재 상태 출력"""
    updater = SimpleLabInput(config_file)
    updater.print_current_status()

def main():
    """메인 실행 함수"""
    print("🎓 간소화된 대학원 랩실 정보 관리 시스템")
    print("=" * 50)
    
    input_system = SimpleLabInput()
    
    while True:
        print("\n📋 메뉴 선택:")
        print("1. 랩실 정보 입력")
        print("2. 현재 상태 확인")
        print("3. 종료")
        
        choice = input("\n선택하세요 (1-3): ").strip()
        
        if choice == "1":
            print("\n📝 랩실 정보를 입력해주세요:")
            print("(입력 완료 후 Ctrl+D 또는 Ctrl+Z를 누르세요)")
            
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            
            text = "\n".join(lines)
            
            # 텍스트에서 랩실 정보 파싱 및 저장
            success = input_system.add_lab_from_text(text)
            
            if success:
                print("✅ 랩실 정보가 성공적으로 저장되었습니다!")
            else:
                print("❌ 랩실 정보 저장에 실패했습니다.")
                
        elif choice == "2":
            input_system.print_current_status()
        elif choice == "3":
            print("👋 프로그램을 종료합니다.")
            break
        else:
            print("⚠️ 올바른 선택을 해주세요.")

if __name__ == "__main__":
    main() 