import requests
from bs4 import BeautifulSoup
import json
import re
import os
import time

def get_preview_sentences(text, num_sentences=2):
    sentences = re.split(r'(?<=[.!?])\s+', text)  # 문장 분리
    return " ".join(sentences[:num_sentences])

def fetch_paper_titles_and_links(url: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 다양한 방법으로 논문 찾기 시도
    papers = []
    
    # 방법 1: class="text-muted"인 a 태그들에서 논문 URL 찾기
    paper_links = soup.find_all("a", class_="text-muted")
    
    for link in paper_links:
        href = link.get('href')
        if href:
            # 논문 제목 찾기 (같은 컨테이너 내의 card-title)
            title_element = link.find_next("div", class_="card-title")
            if title_element:
                title = title_element.get_text(strip=True)
                
                # 제목이 비어 있거나 특정 키워드면 건너뜀
                if not title or title.lower() in {"pdf", "bib", "abs", "download"}:
                    continue
                
                # URL 구성
                if href.startswith("http"):
                    paper_url = href
                else:
                    # 상대 경로를 절대 경로로 변환
                    if href.startswith('/'):
                        paper_url = "https://icml.cc" + href
                    else:
                        # 이미 virtual/2025/poster/로 시작하는 경우 그대로 사용
                        if href.startswith('virtual/2025/poster/'):
                            paper_url = "https://icml.cc/" + href
                        else:
                            paper_url = "https://icml.cc/" + href
                
                papers.append({"title": title, "url": paper_url})
    
    # 방법 2: 모든 a 태그에서 논문 링크 찾기
    if not papers:
        all_links = soup.find_all("a", href=True)
        
        for link in all_links:
            href = link.get('href', '')
            link_text = link.get_text(strip=True)
            
            # 논문 관련 링크인지 확인 (poster/로 시작하는 URL만)
            if (href and len(link_text) > 10 and 
                'poster/' in href and  # poster/가 포함된 URL만
                not any(keyword in link_text.lower() for keyword in ["pdf", "bib", "abs", "download", "home", "schedule", "tutorials", "skip", "select", "main", "help", "contact", "privacy", "code", "diversity", "future", "archives"])):
                
                # URL 구성
                if href.startswith("http"):
                    paper_url = href
                else:
                    # 상대 경로를 절대 경로로 변환
                    if href.startswith('/'):
                        paper_url = "https://icml.cc" + href
                    else:
                        # 이미 virtual/2025/poster/로 시작하는 경우 그대로 사용
                        if href.startswith('virtual/2025/poster/'):
                            paper_url = "https://icml.cc/" + href
                        else:
                            paper_url = "https://icml.cc/" + href
                
                # 제목 찾기 (링크 텍스트 또는 주변 요소에서)
                title = link_text
                if len(title) < 5:  # 링크 텍스트가 짧으면 주변에서 찾기
                    parent = link.parent
                    if parent:
                        title_elem = parent.find("div", class_="card-title") or parent.find("h3") or parent.find("h4")
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                
                if title and len(title) > 5:
                    papers.append({"title": title, "url": paper_url})
    
    # 방법 3: poster/ 링크만 직접 찾기
    if not papers:
        poster_links = soup.find_all("a", href=re.compile(r'poster/\d+'))
        
        for link in poster_links:
            href = link.get('href', '')
            link_text = link.get_text(strip=True)
            
            if href and len(link_text) > 10:
                # URL 구성
                if href.startswith("http"):
                    paper_url = href
                else:
                    # 상대 경로를 절대 경로로 변환
                    if href.startswith('/'):
                        paper_url = "https://icml.cc" + href
                    else:
                        # 이미 virtual/2025/poster/로 시작하는 경우 그대로 사용
                        if href.startswith('virtual/2025/poster/'):
                            paper_url = "https://icml.cc/" + href
                        else:
                            paper_url = "https://icml.cc/" + href
                
                # 제목 찾기
                title = link_text
                if len(title) < 5:
                    parent = link.parent
                    if parent:
                        title_elem = parent.find("div", class_="card-title") or parent.find("h3") or parent.find("h4")
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                
                if title and len(title) > 5:
                    papers.append({"title": title, "url": paper_url})
    
    # 방법 4: card-title 클래스를 가진 요소들 찾기
    if not papers:
        title_elements = soup.find_all("div", class_="card-title")
        
        for title_elem in title_elements:
            title = title_elem.get_text(strip=True)
            if title and len(title) > 10:
                # 해당 요소 근처의 링크 찾기
                parent = title_elem.parent
                if parent:
                    link_elem = parent.find("a", href=True)
                    if link_elem:
                        href = link_elem.get('href')
                        if href.startswith("http"):
                            paper_url = href
                        else:
                            # 상대 경로를 절대 경로로 변환
                            if href.startswith('/'):
                                paper_url = "https://icml.cc" + href
                            else:
                                # 이미 virtual/2025/poster/로 시작하는 경우 그대로 사용
                                if href.startswith('virtual/2025/poster/'):
                                    paper_url = "https://icml.cc/" + href
                                else:
                                    paper_url = "https://icml.cc/" + href
                        
                        papers.append({"title": title, "url": paper_url})
    
    # 방법 5: JavaScript 데이터에서 논문 정보 찾기
    if not papers:
        scripts = soup.find_all("script")
        for script in scripts:
            if script.string and "paper" in script.string.lower():
                # 논문 관련 데이터 패턴 찾기
                paper_matches = re.findall(r'"title":\s*"([^"]+)"[^}]*"url":\s*"([^"]+)"', script.string)
                for title, paper_url in paper_matches:
                    if title and len(title) > 10:
                        papers.append({"title": title, "url": paper_url})
    
    return papers

def fetch_abstract_and_authors(paper_url: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    time.sleep(1) # 잠시 대기 (요청 제한 방지)
    
    try:
        response = requests.get(paper_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Abstract 추출: 동적으로 표시되는 초록 처리
        abstract = "Abstract not found"
        
        # 방법 1: 이미 표시된 초록 찾기 (collapse.show 클래스가 있는 경우)
        abstract_div = soup.find("div", class_="collapse show")
        if abstract_div:
            abstract_text = abstract_div.find("span", class_="font-weight-bold")
            if abstract_text:
                abstract = abstract_text.get_text(strip=True)
                print(f"초록 찾음 (이미 표시됨): {len(abstract)}자")
        
        # 방법 2: 숨겨진 초록 찾기 (collapse 클래스만 있는 경우)
        if abstract == "Abstract not found":
            abstract_div = soup.find("div", class_="collapse")
            if abstract_div:
                abstract_text = abstract_div.find("span", class_="font-weight-bold")
                if abstract_text:
                    abstract = abstract_text.get_text(strip=True)
                    print(f"초록 찾음 (숨겨진 상태): {len(abstract)}자")
        
        # 방법 3: 다른 초록 요소들 찾기
        if abstract == "Abstract not found":
            # 다양한 초록 관련 클래스들 시도
            abstract_selectors = [
                "div.font-weight-bold",
                "span.font-weight-bold", 
                "div#abstractExample",
                "div.abstract",
                "p.abstract"
            ]
            
            for selector in abstract_selectors:
                abstract_elem = soup.select_one(selector)
                if abstract_elem:
                    text = abstract_elem.get_text(strip=True)
                    if len(text) > 50:  # 의미있는 길이인지 확인
                        abstract = text
                        print(f"초록 찾음 ({selector}): {len(abstract)}자")
                        break
        
        # Authors 추출: h3 태그에서 찾기 (이미지에서 확인된 구조)
        authors = "Authors not found"
        authors_h3 = soup.find("h3", class_="card-subtitle mb-2 text-muted text-center")
        if authors_h3:
            authors = authors_h3.get_text(strip=True)
            print(f"저자 찾음: {authors}")
        
        # 방법 2: 다른 저자 관련 요소들 찾기
        if authors == "Authors not found":
            authors_selectors = [
                "div.card-subtitle.mb-2.text-muted.text-center",
                "h3.card-subtitle",
                "div.authors",
                "span.authors"
            ]
            
            for selector in authors_selectors:
                authors_elem = soup.select_one(selector)
                if authors_elem:
                    text = authors_elem.get_text(strip=True)
                    if "·" in text:  # 저자 구분자가 있는지 확인
                        authors = text
                        print(f"저자 찾음 ({selector}): {authors}")
                        break
        
        return abstract, authors
        
    except requests.exceptions.RequestException as e:
        print(f"요청 오류: {e}")
        return "Abstract not found", "Authors not found"

def crawl_all_papers(url: str):
    """
    주어진 URL에서 모든 논문을 크롤링하여 하나씩 실시간으로 반환
    """
    papers = fetch_paper_titles_and_links(url)

    for i, paper in enumerate(papers, 1):
        try:
            # 제목이 비어있는 경우 건너뜀
            if not paper['title'].strip():
                continue

            abstract, authors = fetch_abstract_and_authors(paper['url'])
            
            paper_data = {
                'title': paper['title'],
                'abstract': abstract,
                'authors': authors,
                'url': paper['url'],
                'year': 2025  # ICML 2025
            }
            print("Title: ", paper['title'])
            print("Abstract: ", abstract)
            print("Authors: ", authors)
            print("URL: ", paper['url'])
            print("Year: ", 2025)
            print("-" * 100)
            
            yield paper_data  # 실시간으로 하나씩 반환

        except Exception as e:
            print(f"❌ 논문 {i} 처리 실패: {e}")

    print(f"총 {len(papers)}개 논문 크롤링 완료")

def icml_crawler():
    """
    기존 함수 - conference_list.json에서 ICML 관련 컨퍼런스들을 모두 크롤링
    """
    # conference_list.json 파일 경로
    base_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(base_dir, "conference_list.json")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    conference_urls = {}
    for field in config['fields']:
        for conf in field['conferences']:
            if conf.get('crawler') == 'icml_crawler':
                conference_urls[conf['name']] = conf['site']

    all_results = []

    for conf_name, url in conference_urls.items():
        print(f"🔍 [{conf_name}] 크롤링 중...")
        for paper in crawl_all_papers(url):
            paper['conference'] = conf_name
            all_results.append(paper)

    # 전체 최종 저장
    output_path = os.path.join(base_dir, "icml_papers_2025.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"총 {len(all_results)}개 논문이 {output_path}에 저장되었습니다.")
    return all_results

if __name__ == "__main__":
    icml_crawler()
