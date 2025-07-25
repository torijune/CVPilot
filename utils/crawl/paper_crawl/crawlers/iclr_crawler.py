import requests
from bs4 import BeautifulSoup
import json
import re
import os
import time

def get_preview_sentences(text, num_sentences=2):
    sentences = re.split(r'(?<=[.!?])\s+', text)  # 문장 분리
    return " ".join(sentences[:num_sentences])

def test_single_paper():
    """단일 논문 테스트"""
    test_url = "https://openreview.net/forum?id=odjMSBSWRt"  # 사진에서 보인 논문
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"테스트 논문 URL: {test_url}")
    
    try:
        response = requests.get(test_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"페이지 제목: {soup.title.text if soup.title else 'No title'}")
        print(f"HTML 길이: {len(response.text)}")
        
        # 제목 찾기
        title = "Title not found"
        title_elements = soup.find_all("h1") + soup.find_all("h2") + soup.find_all("h3") + soup.find_all("h4")
        for elem in title_elements:
            if elem.get_text(strip=True) and len(elem.get_text(strip=True)) > 10:
                title = elem.get_text(strip=True)
                print(f"제목 찾음: {title}")
                break
        
        # 초록 찾기
        abstract = "Abstract not found"
        
        # 방법 1: class="note-content-value markdown-rendered"
        abstract_div = soup.find("div", class_="note-content-value markdown-rendered")
        if abstract_div:
            abstract = abstract_div.get_text(strip=True)
            print(f"초록 찾음 (방법 1): {len(abstract)}자")
        else:
            # 방법 2: class="note-content"
            abstract_div = soup.find("div", class_="note-content")
            if abstract_div:
                abstract = abstract_div.get_text(strip=True)
                print(f"초록 찾음 (방법 2): {len(abstract)}자")
            else:
                # 방법 3: TL;DR 찾기
                tldr_elements = soup.find_all(string=re.compile(r"TL;DR:", re.IGNORECASE))
                if tldr_elements:
                    for elem in tldr_elements:
                        parent = elem.parent
                        if parent:
                            abstract = parent.get_text(strip=True)
                            print(f"초록 찾음 (방법 3): {len(abstract)}자")
                            break
        
        # 저자 찾기
        authors = "Authors not found"
        
        # 방법 1: class="forum-authors" - 실제 HTML 구조에 맞게 수정
        authors_div = soup.find("div", class_="forum-authors")
        if authors_div:
            print(f"forum-authors div 발견: {authors_div}")
            author_text = authors_div.get_text(strip=True)
            if author_text and len(author_text) > 5:
                # 쉼표로 구분된 저자들을 분리
                author_names = [name.strip() for name in author_text.split(',') if name.strip()]
                if author_names:
                    authors = ", ".join(author_names)
                    print(f"저자 찾음 (방법 1): {len(author_names)}명 - {authors}")
        
        # 방법 2: class="note-authors" - 기존 방법도 유지
        if authors == "Authors not found":
            authors_div = soup.find("div", class_="note-authors")
            if authors_div:
                print(f"note-authors div 발견: {authors_div}")
                author_links = authors_div.find_all("a")
                print(f"저자 링크 수: {len(author_links)}")
                if author_links:
                    author_names = []
                    for i, author_link in enumerate(author_links):
                        author_name = author_link.get_text(strip=True)
                        print(f"저자 {i+1}: {author_name}")
                        if author_name and len(author_name) > 1:  # 의미있는 이름인지 확인
                            author_names.append(author_name)
                    if author_names:
                        authors = ", ".join(author_names)
                        print(f"저자 찾음 (방법 2): {len(author_names)}명 - {authors}")
        
        # 방법 3: 저자 정보가 있는 다른 요소들
        if authors == "Authors not found":
            # 저자 이름이 포함된 텍스트 찾기
            author_elements = soup.find_all(string=re.compile(r"Esben Kran|Hieu Minh Nguyen|Akash Kundu|Sami Jawhar|Jinsuk Park|Mateusz Maria Jurewicz", re.IGNORECASE))
            if author_elements:
                for elem in author_elements:
                    parent = elem.parent
                    if parent:
                        author_text = parent.get_text(strip=True)
                        if len(author_text) > 10 and len(author_text) < 500:  # 적절한 길이인지 확인
                            authors = author_text
                            print(f"저자 찾음 (방법 3): {authors}")
                            break
        
        # 방법 4: 모든 a 태그에서 저자 찾기
        if authors == "Authors not found":
            all_links = soup.find_all("a", href=True)
            author_links = []
            for link in all_links:
                href = link.get('href', '')
                if '/profile?id=' in href:
                    author_name = link.get_text(strip=True)
                    if author_name and len(author_name) > 1:
                        author_links.append(author_name)
            
            if author_links:
                authors = ", ".join(author_links)
                print(f"저자 찾음 (방법 4): {len(author_links)}명 - {authors}")
        
        # 방법 5: JavaScript에서 저자 정보 추출
        if authors == "Authors not found":
            scripts = soup.find_all("script")
            for script in scripts:
                if script.string and "authors" in script.string.lower():
                    # 다양한 패턴 시도
                    author_patterns = [
                        r'"authors":\s*\[([^\]]+)\]',
                        r'"authors":\s*"([^"]+)"',
                        r'"author":\s*"([^"]+)"'
                    ]
                    
                    for pattern in author_patterns:
                        authors_match = re.search(pattern, script.string)
                        if authors_match:
                            authors_text = authors_match.group(1)
                            if '[' in authors_text:  # 배열 형태인 경우
                                # 따옴표로 둘러싸인 저자 이름들 추출
                                author_names = re.findall(r'"([^"]+)"', authors_text)
                                if author_names:
                                    authors = ", ".join(author_names)
                                    print(f"저자 찾음 (방법 5): {len(author_names)}명 - {authors}")
                                    break
                            else:  # 단일 문자열인 경우
                                authors = authors_text
                                print(f"저자 찾음 (방법 5): {authors}")
                                break
                    if authors != "Authors not found":
                        break
        
        print(f"\n=== 테스트 결과 ===")
        print(f"제목: {title}")
        print(f"초록: {abstract[:100]}...")
        print(f"저자: {authors}")
        
        return {
            'title': title,
            'abstract': abstract,
            'authors': authors,
            'url': test_url
        }
        
    except Exception as e:
        print(f"테스트 실패: {e}")
        return None

def fetch_paper_titles_and_links(url: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # 먼저 단일 논문 테스트
    print("단일 논문 테스트 실행...")
    test_result = test_single_paper()
    
    if test_result:
        print("테스트 성공! 이제 전체 크롤링 시도...")
    
    # OpenReview 메인 페이지에서 논문 목록 가져오기
    print("OpenReview 메인 페이지에서 논문 목록 가져오기...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"페이지 제목: {soup.title.text if soup.title else 'No title'}")
        print(f"HTML 길이: {len(response.text)}")
        
        # JavaScript 데이터에서 논문 정보 찾기
        scripts = soup.find_all("script")
        papers = []
        
        for i, script in enumerate(scripts):
            if script.string:
                # forum 링크 찾기
                forum_matches = re.findall(r'/forum\?id=([^"\s&]+)', script.string)
                if forum_matches:
                    print(f"Script {i}에서 {len(forum_matches)}개의 forum 링크 발견")
                    
                    # 해당 script의 내용 일부 출력 (디버깅용)
                    script_content = script.string[:500]
                    print(f"Script {i} 내용 (처음 500자): {script_content}")
                    
                    for paper_id in forum_matches:
                        print(f"논문 ID 처리 중: {paper_id}")
                        
                        # 제목 찾기 - 다양한 패턴 시도
                        title_patterns = [
                            rf'"id":\s*"{paper_id}"[^}}]*"title":\s*"([^"]+)"',
                            rf'"id":\s*"{paper_id}"[^}}]*"content":\s*{{[^}}]*"title":\s*{{[^}}]*"value":\s*"([^"]+)"',
                            rf'"{paper_id}"[^}}]*"title":\s*"([^"]+)"',
                            rf'"id":\s*"{paper_id}"[^}}]*"value":\s*"([^"]+)"',
                            rf'"{paper_id}"[^}}]*"value":\s*"([^"]+)"'
                        ]
                        
                        title = None
                        for j, pattern in enumerate(title_patterns):
                            title_match = re.search(pattern, script.string)
                            if title_match:
                                title = title_match.group(1)
                                print(f"패턴 {j}로 제목 찾음: {title[:50]}...")
                                break
                        
                        if title and len(title) > 5:  # 의미있는 제목인지 확인
                            paper_url = f"https://openreview.net/forum?id={paper_id}"
                            papers.append({"title": title, "url": paper_url, "id": paper_id})
                            print(f"논문 추가: {title[:50]}...")
                        else:
                            print(f"제목을 찾을 수 없음: {paper_id}")
        
        print(f"JavaScript에서 찾은 논문 수: {len(papers)}")
        
        # 중복 제거
        unique_papers = []
        seen_ids = set()
        for paper in papers:
            if paper['id'] not in seen_ids:
                unique_papers.append(paper)
                seen_ids.add(paper['id'])
        
        print(f"중복 제거 후 논문 수: {len(unique_papers)}")
        
        if unique_papers:
            return unique_papers
        
    except Exception as e:
        print(f"메인 페이지 접근 실패: {e}")
    
    # 모든 방법 실패 시 테스트 데이터 반환
    print("모든 방법 실패. 테스트 데이터 사용...")
    if test_result:
        return [test_result]
    
    return []

def fetch_abstract_and_authors(paper_url: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # 잠시 대기 (요청 제한 방지)
    time.sleep(1)
    
    response = requests.get(paper_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Abstract 추출: 다양한 선택자 시도
    abstract = "Abstract not found"
    
    # 방법 1: class="note-content-value markdown-rendered"
    abstract_div = soup.find("div", class_="note-content-value markdown-rendered")
    if abstract_div:
        abstract = abstract_div.get_text(strip=True)
        print(f"방법 1로 초록 찾음: {len(abstract)}자")
    else:
        # 방법 2: class="note-content"
        abstract_div = soup.find("div", class_="note-content")
        if abstract_div:
            abstract = abstract_div.get_text(strip=True)
            print(f"방법 2로 초록 찾음: {len(abstract)}자")
        else:
            # 방법 3: TL;DR 찾기
            tldr_div = soup.find("div", string=re.compile(r"TL;DR:", re.IGNORECASE))
            if tldr_div:
                abstract = tldr_div.get_text(strip=True)
                print(f"방법 3으로 초록 찾음: {len(abstract)}자")
            else:
                # 방법 4: JavaScript에서 추출
                scripts = soup.find_all("script")
                for script in scripts:
                    if script.string and "abstract" in script.string.lower():
                        abstract_match = re.search(r'"abstract":\s*"([^"]+)"', script.string)
                        if abstract_match:
                            abstract = abstract_match.group(1)
                            print(f"방법 4로 초록 찾음: {len(abstract)}자")
                            break
    
    # Authors 추출: 다양한 선택자 시도
    authors = "Authors not found"
    
    # 방법 1: class="forum-authors" - 실제 HTML 구조에 맞게 수정
    authors_div = soup.find("div", class_="forum-authors")
    if authors_div:
        print(f"forum-authors div 발견: {authors_div}")
        author_text = authors_div.get_text(strip=True)
        if author_text and len(author_text) > 5:
            # 쉼표로 구분된 저자들을 분리
            author_names = [name.strip() for name in author_text.split(',') if name.strip()]
            if author_names:
                authors = ", ".join(author_names)
                print(f"방법 1로 저자 찾음: {len(author_names)}명 - {authors}")
    
    # 방법 2: class="note-authors" - 기존 방법도 유지
    if authors == "Authors not found":
        authors_div = soup.find("div", class_="note-authors")
        if authors_div:
            print(f"note-authors div 발견: {authors_div}")
            author_links = authors_div.find_all("a")
            print(f"저자 링크 수: {len(author_links)}")
            if author_links:
                author_names = []
                for i, author_link in enumerate(author_links):
                    author_name = author_link.get_text(strip=True)
                    print(f"저자 {i+1}: {author_name}")
                    if author_name and len(author_name) > 1:  # 의미있는 이름인지 확인
                        author_names.append(author_name)
                if author_names:
                    authors = ", ".join(author_names)
                    print(f"방법 2로 저자 찾음: {len(author_names)}명 - {authors}")
    
    # 방법 3: 저자 정보가 있는 다른 요소들
    if authors == "Authors not found":
        # 저자 이름이 포함된 텍스트 찾기
        author_elements = soup.find_all(string=re.compile(r"Esben Kran|Hieu Minh Nguyen|Akash Kundu|Sami Jawhar|Jinsuk Park|Mateusz Maria Jurewicz", re.IGNORECASE))
        if author_elements:
            for elem in author_elements:
                parent = elem.parent
                if parent:
                    author_text = parent.get_text(strip=True)
                    if len(author_text) > 10 and len(author_text) < 500:  # 적절한 길이인지 확인
                        authors = author_text
                        print(f"방법 3으로 저자 찾음: {authors}")
                        break
    
    # 방법 4: 모든 a 태그에서 저자 찾기
    if authors == "Authors not found":
        all_links = soup.find_all("a", href=True)
        author_links = []
        for link in all_links:
            href = link.get('href', '')
            if '/profile?id=' in href:
                author_name = link.get_text(strip=True)
                if author_name and len(author_name) > 1:
                    author_links.append(author_name)
        
        if author_links:
            authors = ", ".join(author_links)
            print(f"방법 4로 저자 찾음: {len(author_links)}명 - {authors}")
    
    # 방법 5: JavaScript에서 저자 정보 추출
    if authors == "Authors not found":
        scripts = soup.find_all("script")
        for script in scripts:
            if script.string and "authors" in script.string.lower():
                # 다양한 패턴 시도
                author_patterns = [
                    r'"authors":\s*\[([^\]]+)\]',
                    r'"authors":\s*"([^"]+)"',
                    r'"author":\s*"([^"]+)"'
                ]
                
                for pattern in author_patterns:
                    authors_match = re.search(pattern, script.string)
                    if authors_match:
                        authors_text = authors_match.group(1)
                        if '[' in authors_text:  # 배열 형태인 경우
                            # 따옴표로 둘러싸인 저자 이름들 추출
                            author_names = re.findall(r'"([^"]+)"', authors_text)
                            if author_names:
                                authors = ", ".join(author_names)
                                print(f"방법 5로 저자 찾음: {len(author_names)}명 - {authors}")
                                break
                        else:  # 단일 문자열인 경우
                            authors = authors_text
                            print(f"방법 5로 저자 찾음: {authors}")
                            break
                if authors != "Authors not found":
                    break

    return abstract, authors

def crawl_all_papers(url: str):
    """
    주어진 URL에서 모든 논문을 크롤링하여 하나씩 실시간으로 반환
    """
    print(f"🔍 ICLR 크롤링 시작: {url}")
    papers = fetch_paper_titles_and_links(url)
    
    print(f"찾은 논문 수: {len(papers)}")
    if papers:
        print(f"첫 번째 논문 예시: {papers[0]}")

    for i, paper in enumerate(papers, 1):
        try:
            # 제목이 비어있는 경우 건너뜀
            if not paper['title'].strip():
                continue

            print(f"📄 논문 {i} 처리 중: {paper['url']}")
            abstract, authors = fetch_abstract_and_authors(paper['url'])
            
            paper_data = {
                'title': paper['title'],
                'abstract': abstract,
                'authors': authors,
                'url': paper['url'],
                'year': 2025  # ICLR 2025
            }
            
            print(f"✅ 논문 {i}: {paper['title'][:50]}...")
            yield paper_data  # 실시간으로 하나씩 반환

        except Exception as e:
            print(f"❌ 논문 {i} 처리 실패: {e}")

    print(f"총 {len(papers)}개 논문 크롤링 완료")

def iclr_crawler():
    """
    기존 함수 - conference_list.json에서 ICLR 관련 컨퍼런스들을 모두 크롤링
    """
    # conference_list.json 파일 경로
    base_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(base_dir, "conference_list.json")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    conference_urls = {}
    for field in config['fields']:
        for conf in field['conferences']:
            if conf.get('crawler') == 'iclr_crawler':
                conference_urls[conf['name']] = conf['site']

    all_results = []

    for conf_name, url in conference_urls.items():
        print(f"🔍 [{conf_name}] 크롤링 중...")
        for paper in crawl_all_papers(url):
            paper['conference'] = conf_name
            all_results.append(paper)

    # 전체 최종 저장
    output_path = os.path.join(base_dir, "iclr_papers_2025.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"총 {len(all_results)}개 논문이 {output_path}에 저장되었습니다.")
    return all_results

if __name__ == "__main__":
    iclr_crawler()
