import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional
import time

class KAISTGSAICrawler:
    def __init__(self):
        self.base_url = "https://gsai.kaist.ac.kr"
        self.people_url = "https://gsai.kaist.ac.kr/people-2/?lang=ko"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_page_content(self, url: str) -> Optional[str]:
        """웹페이지 내용을 가져옵니다."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"❌ 페이지 로드 실패: {e}")
            return None
    
    def extract_professor_info(self, professor_element) -> Dict:
        """개별 교수 정보를 추출합니다."""
        info = {}
        
        try:
            # 이름 추출 - strong 태그에서 찾기
            name_element = professor_element.find('strong')
            if name_element:
                name_text = name_element.get_text(strip=True)
                # 괄호 안의 직위 제거 (예: "정송 (대학원장)" -> "정송")
                name = re.sub(r'\s*\([^)]*\)', '', name_text)
                info['name'] = name.strip()
            
            # 모든 텍스트 정보 추출
            text_content = professor_element.get_text()
            
            # 연구분야 추출
            research_match = re.search(r'연구분야\s*:\s*([^\n]+)', text_content)
            if research_match:
                info['research_area'] = research_match.group(1).strip()
            
            # 이메일 추출
            email_match = re.search(r'이메일\s*:\s*([^\s\n]+)', text_content)
            if email_match:
                info['email'] = email_match.group(1).strip()
            
            # 웹사이트 추출
            website_element = professor_element.find('a', href=True)
            if website_element:
                website_url = website_element.get('href')
                if website_url:
                    # 상대 URL을 절대 URL로 변환
                    if website_url.startswith('/'):
                        website_url = self.base_url + website_url
                    elif not website_url.startswith('http'):
                        website_url = self.base_url + '/' + website_url
                    info['website'] = website_url
            
        except Exception as e:
            print(f"⚠️ 교수 정보 추출 중 오류: {e}")
        
        return info
    
    def is_professor(self, text_content: str) -> bool:
        """텍스트가 교수 정보인지 확인합니다."""
        # 교수 관련 키워드가 있는지 확인
        professor_keywords = ['교수', '부교수', '조교수', '석좌교수', 'Professor', 'Associate Professor', 'Assistant Professor']
        
        # 직위 정보에서 교수 관련 키워드 확인
        position_match = re.search(r'직위\s*:\s*([^\n]+)', text_content)
        if position_match:
            position = position_match.group(1).strip()
            for keyword in professor_keywords:
                if keyword in position:
                    return True
        
        # 이름이 있고 연구분야가 있는 경우 (교수일 가능성이 높음)
        if '연구분야' in text_content and '이메일' in text_content:
            return True
        
        return False
    
    def crawl_professors(self) -> List[Dict]:
        """교수 정보만 크롤링합니다."""
        print("🔍 KAIST GSAI 교수 정보 크롤링 시작...")
        
        content = self.get_page_content(self.people_url)
        if not content:
            return []
        
        soup = BeautifulSoup(content, 'html.parser')
        professors = []
        
        # 더 구체적인 선택자로 교수 정보 찾기
        professor_containers = []
        
        # 방법 1: 특정 클래스명으로 찾기
        possible_classes = ['professor', 'member', 'people', 'faculty', 'staff', 'team-member']
        for class_name in possible_classes:
            containers = soup.find_all(['div', 'article'], class_=re.compile(class_name, re.I))
            if containers:
                professor_containers.extend(containers)
                print(f"✅ '{class_name}' 클래스로 {len(containers)}개 컨테이너 발견")
        
        # 방법 2: 특정 구조 패턴으로 찾기
        if not professor_containers:
            # 이미지와 이름이 함께 있는 구조 찾기
            all_divs = soup.find_all('div', recursive=True)
            for div in all_divs:
                # 이미지와 strong 태그(이름)가 모두 있는 div 찾기
                if div.find('img') and div.find('strong'):
                    # 텍스트에 "연구분야" 또는 "이메일"이 포함된 경우만
                    text = div.get_text()
                    if '연구분야' in text or '이메일' in text:
                        professor_containers.append(div)
        
        # 중복 제거 및 교수만 필터링
        unique_containers = []
        seen_texts = set()
        
        for container in professor_containers:
            text_content = container.get_text().strip()
            if text_content and text_content not in seen_texts:
                # 교수인지 확인
                if self.is_professor(text_content):
                    unique_containers.append(container)
                    seen_texts.add(text_content)
        
        print(f"📊 발견된 고유 교수 컨테이너 수: {len(unique_containers)}")
        
        for i, container in enumerate(unique_containers):
            print(f"\n🔍 교수 {i+1} 정보 추출 중...")
            
            professor_info = self.extract_professor_info(container)
            
            if professor_info.get('name'):
                # 필요한 정보만 포함
                filtered_info = {
                    'name': professor_info.get('name', ''),
                    'research_area': professor_info.get('research_area', ''),
                    'email': professor_info.get('email', ''),
                    'website': professor_info.get('website', '')
                }
                professors.append(filtered_info)
                print(f"✅ {filtered_info['name']} - {filtered_info.get('research_area', 'N/A')}")
            else:
                print(f"⚠️ 이름을 찾을 수 없는 교수 정보 건너뛰기")
            
            # 서버 부하 방지를 위한 딜레이
            time.sleep(0.2)
        
        return professors
    
    def save_to_json(self, professors: List[Dict], filename: str = "kaist_gsai_professors_only.json"):
        """교수 정보를 JSON 파일로 저장합니다."""
        data = {
            "university": "KAIST",
            "department": "Graduate School of AI",
            "crawled_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_professors": len(professors),
            "professors": professors
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 교수 정보 저장 완료: {filename}")
            return True
        except Exception as e:
            print(f"❌ 파일 저장 실패: {e}")
            return False
    
    def print_summary(self, professors: List[Dict]):
        """크롤링 결과 요약을 출력합니다."""
        print(f"\n📊 크롤링 결과 요약:")
        print(f"   총 교수 수: {len(professors)}")
        
        for i, prof in enumerate(professors, 1):
            print(f"\n   {i}. {prof.get('name', 'N/A')}")
            print(f"      연구분야: {prof.get('research_area', 'N/A')}")
            print(f"      이메일: {prof.get('email', 'N/A')}")
            print(f"      웹사이트: {prof.get('website', 'N/A')}")

def main():
    """메인 실행 함수"""
    crawler = KAISTGSAICrawler()
    
    # 교수 정보 크롤링
    professors = crawler.crawl_professors()
    
    if professors:
        # 결과 출력
        crawler.print_summary(professors)
        
        # JSON 파일로 저장
        crawler.save_to_json(professors)
        
        print(f"\n🎉 크롤링 완료! 총 {len(professors)}명의 교수 정보를 수집했습니다.")
    else:
        print("❌ 크롤링 실패: 교수 정보를 찾을 수 없습니다.")

if __name__ == "__main__":
    main()
