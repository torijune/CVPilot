import requests
from bs4 import BeautifulSoup
import json
import re
import os

def get_preview_sentences(text, num_sentences=2):
    sentences = re.split(r'(?<=[.!?])\s+', text)  # 문장 분리
    return " ".join(sentences[:num_sentences])

def fetch_paper_titles_and_links(url: str):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    # ECCV 사이트에 맞는 선택자: class="ptitle"인 dt 태그 안의 a 태그 (WACV와 동일)
    paper_tags = soup.find_all("dt", class_="ptitle")

    papers = []
    for tag in paper_tags:
        # dt 태그 안의 a 태그 찾기
        link_tag = tag.find("a")
        if not link_tag:
            continue
            
        title = link_tag.text.strip()
        # 제목이 비어 있거나 특정 키워드면 건너뜀
        if not title or title.lower() in {"pdf", "bib", "abs"}:
            continue

        href = link_tag.get('href')
        if not href:
            continue
            
        # ECCV 사이트의 올바른 URL 구조로 수정
        if href.startswith("http"):
            link = href
        else:
            # 상대 경로인 경우 openaccess.thecvf.com 도메인 사용
            link = "https://www.ecva.net/" + href

        papers.append({"title": title, "url": link})
    return papers

def fetch_abstract_and_authors(paper_url: str):
    response = requests.get(paper_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # ECCV 사이트의 정확한 구조에 맞게 수정 (WACV와 동일)
    # Authors - id="authors"인 div에서 저자 정보 추출
    authors = "Authors not found"
    authors_div = soup.find("div", id="authors")
    if authors_div:
        # 저자 정보는 <i> 태그 안에 있음 (WACV와 동일)
        author_i_tag = authors_div.find("i")
        if author_i_tag:
            authors = author_i_tag.get_text(strip=True)
        else:
            # <i> 태그가 없으면 전체 텍스트에서 저자 부분만 추출
            full_text = authors_div.get_text(strip=True)
            # 세미콜론 이전 부분이 저자명 (WACV와 동일)
            if ";" in full_text:
                authors = full_text.split(";")[0].strip()

    # Abstract - id="abstract"인 div에서 초록 추출
    abstract = "Abstract not found"
    abstract_div = soup.find("div", id="abstract")
    if abstract_div:
        abstract = abstract_div.get_text(strip=True)

    return abstract, authors

def crawl_all_papers(url: str):
    """
    주어진 URL에서 모든 논문을 크롤링하여 하나씩 실시간으로 반환
    """
    print(f"🔍 ECCV 크롤링 시작: {url}")
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
                'year': 2024  # ECCV 2024
            }
            
            print(f"✅ 논문 {i}: {paper['title'][:50]}...")
            yield paper_data  # 실시간으로 하나씩 반환

        except Exception as e:
            print(f"❌ 논문 {i} 처리 실패: {e}")

    print(f"총 {len(papers)}개 논문 크롤링 완료")

def eccv_crawler():
    """
    기존 함수 - conference_list.json에서 ECCV 관련 컨퍼런스들을 모두 크롤링
    """
    # conference_list.json 파일 경로
    base_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(base_dir, "conference_list.json")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    conference_urls = {}
    for field in config['fields']:
        for conf in field['conferences']:
            if conf.get('crawler') == 'eccv_crawler':
                conference_urls[conf['name']] = conf['site']

    all_results = []

    for conf_name, url in conference_urls.items():
        print(f"🔍 [{conf_name}] 크롤링 중...")
        for paper in crawl_all_papers(url):
            paper['conference'] = conf_name
            all_results.append(paper)

    # 전체 최종 저장
    output_path = os.path.join(base_dir, "eccv_papers_2024.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"총 {len(all_results)}개 논문이 {output_path}에 저장되었습니다.")
    return all_results

if __name__ == "__main__":
    eccv_crawler()
