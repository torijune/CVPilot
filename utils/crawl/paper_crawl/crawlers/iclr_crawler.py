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
    # TODO: ICLR 사이트에 맞는 선택자로 수정 필요
    paper_tags = soup.find_all("a", class_=lambda c: c and "align-middle" in c.split())

    papers = []
    for tag in paper_tags:
        title = tag.text.strip()
        # 제목이 비어 있거나 특정 키워드면 건너뜀
        if not title or title.lower() in {"pdf", "bib", "abs"}:
            continue

        href = tag['href']
        link = href if href.startswith("http") else "https://openreview.net" + href

        papers.append({"title": title, "url": link})
    return papers

def fetch_abstract_and_authors(paper_url: str):
    response = requests.get(paper_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # TODO: ICLR 사이트에 맞는 선택자로 수정 필요
    # Abstract
    abstract_div = soup.find("div", class_="card-body acl-abstract")
    abstract = abstract_div.find("span").text.strip() if abstract_div and abstract_div.find("span") else "Abstract not found"

    # Authors
    lead_p = soup.find("p", class_="lead")
    authors = lead_p.get_text(separator=", ").strip() if lead_p else "Authors not found"

    return abstract, authors

def crawl_all_papers(url: str):
    """
    주어진 URL에서 모든 논문을 크롤링하여 하나씩 실시간으로 반환
    """
    print(f"🔍 ICLR 크롤링 시작: {url}")
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
                'year': 2024  # 기본값
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
    output_path = os.path.join(base_dir, "iclr_papers_2024.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"총 {len(all_results)}개 논문이 {output_path}에 저장되었습니다.")
    return all_results

if __name__ == "__main__":
    iclr_crawler()
