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
    
    papers = []
    
    # dl 태그 내의 dt 태그들에서 제목 찾기 (이미지에서 확인된 구조)
    dl_tags = soup.find_all("dl")
    for dl in dl_tags:
        dt_tags = dl.find_all("dt")
        for dt in dt_tags:
            title = dt.get_text(strip=True)
            if title and len(title) > 10:  # 의미있는 제목인지 확인
                # 해당 dt의 다음 dd 태그에서 링크 찾기
                dd = dt.find_next_sibling("dd")
                if dd:
                    # dd 내의 링크들 찾기
                    links = dd.find_all("a", href=True)
                    abs_url = None
                    pdf_url = None
                    
                    for link in links:
                        href = link.get('href')
                        link_text = link.get_text(strip=True).lower()
                        
                        # abs 링크 찾기 (상세 페이지 URL)
                        if link_text == "abs" and href:
                            if href.startswith("http"):
                                abs_url = href
                            else:
                                abs_url = "https://jmlr.org" + href
                        
                        # pdf 링크 찾기 (논문 URL)
                        elif link_text == "pdf" and href:
                            if href.startswith("http"):
                                pdf_url = href
                            else:
                                pdf_url = "https://jmlr.org" + href
                    
                    # abs URL이 있으면 저장 (저자, 제목, 초록을 가져올 URL)
                    if abs_url:
                        papers.append({
                            "title": title, 
                            "abs_url": abs_url,  # 상세 페이지 URL
                            "pdf_url": pdf_url   # 논문 PDF URL
                        })
    
    return papers

def get_detailed_title(abs_url: str):
    """
    상세 페이지에서 정확한 제목을 가져오는 함수
    """
    try:
        response = requests.get(abs_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # id="content" 내의 h2 태그에서 제목 찾기
        content_div = soup.find("div", id="content")
        if content_div:
            h2_tag = content_div.find("h2")
            if h2_tag:
                title = h2_tag.get_text(strip=True)
                return title
        
        return "Title not found"
    except Exception as e:
        return "Title not found"

def fetch_abstract_and_authors(abs_url: str):
    response = requests.get(abs_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Abstract 추출: class="abstract"인 p 태그에서 찾기
    abstract = "Abstract not found"
    abstract_elem = soup.find("p", class_="abstract")
    if abstract_elem:
        abstract = abstract_elem.get_text(strip=True)
    
    # 백업 방법: 다른 초록 관련 요소들 찾기
    if abstract == "Abstract not found":
        abstract_selectors = [
            "div.abstract",
            "div#abstract", 
            "p.abstract",
            "div.card-body",
            "div.lead"
        ]
        
        for selector in abstract_selectors:
            abstract_elem = soup.select_one(selector)
            if abstract_elem:
                text = abstract_elem.get_text(strip=True)
                if len(text) > 50:  # 의미있는 길이인지 확인
                    abstract = text
                    break

    # Authors 추출: id="content" 내의 p>b>i 구조에서 찾기
    authors = "Authors not found"
    content_div = soup.find("div", id="content")
    if content_div:
        # p 태그 내의 i 태그에서 저자 찾기
        p_tags = content_div.find_all("p")
        for p in p_tags:
            i_tag = p.find("i")
            if i_tag:
                text = i_tag.get_text(strip=True)
                if len(text) > 5 and "," in text:  # 저자 구분자가 있는지 확인
                    authors = text
                    break
    
    # 백업 방법: 다른 저자 관련 요소들 찾기
    if authors == "Authors not found":
        author_selectors = [
            "p.lead",
            "div.authors",
            "span.authors",
            "div.author",
            "p.author"
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                text = author_elem.get_text(strip=True)
                if len(text) > 5 and any(char in text for char in [",", "and", "&"]):
                    authors = text
                    break

    return abstract, authors

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

            # abs_url에서 초록과 저자 가져오기
            abstract, authors = fetch_abstract_and_authors(paper['abs_url'])
            
            # 상세 페이지에서 정확한 제목 가져오기 (id="content" 내의 h2 태그)
            detailed_title = get_detailed_title(paper['abs_url'])
            if detailed_title and detailed_title != "Title not found":
                paper['title'] = detailed_title
            
            paper_data = {
                'title': paper['title'],
                'abstract': abstract,
                'authors': authors,
                'url': paper['pdf_url'],  # PDF URL을 논문 URL로 저장
                'abs_url': paper['abs_url'],  # 상세 페이지 URL도 저장
                'year': 2024  # 기본값
            }
            
            yield paper_data  # 실시간으로 하나씩 반환

        except Exception as e:
            print(f"❌ 논문 {i} 처리 실패: {e}")

    pass

def jmlr_crawler():
    """
    기존 함수 - conference_list.json에서 JMLR 관련 컨퍼런스들을 모두 크롤링
    """
    # conference_list.json 파일 경로
    base_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(base_dir, "conference_list.json")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    conference_urls = {}
    for field in config['fields']:
        for conf in field['conferences']:
            if conf.get('crawler') == 'jmlr_crawler':
                conference_urls[conf['name']] = conf['site']

    all_results = []

    for conf_name, url in conference_urls.items():
        print(f"🔍 [{conf_name}] 크롤링 중...")
        for paper in crawl_all_papers(url):
            paper['conference'] = conf_name
            all_results.append(paper)

    # 전체 최종 저장
    output_path = os.path.join(base_dir, "jmlr_papers_2024.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"총 {len(all_results)}개 논문이 {output_path}에 저장되었습니다.")
    return all_results

if __name__ == "__main__":
    jmlr_crawler()
