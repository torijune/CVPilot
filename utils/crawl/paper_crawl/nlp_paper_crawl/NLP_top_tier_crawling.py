# Target URL: 
# https://aclanthology.org/volumes/2024.emnlp-main/
# https://aclanthology.org/volumes/2024.acl-long/
# https://aclanthology.org/volumes/2024.naacl-long/
# title class= "align-middle", 해당 title의 링크 : href= ~
# 해당 논문 페이지에 들어와서는 보이는 Abstract class= "card-body acl-abstract"의 span -> 이걸 분석
import requests
from bs4 import BeautifulSoup
import json
import re

# 크롤링 대상 컨퍼런스들
conference_urls = {
    "ACL 2024": "https://aclanthology.org/volumes/2024.acl-long/",
    "EMNLP 2024": "https://aclanthology.org/volumes/2024.emnlp-main/",
    "NAACL 2024": "https://aclanthology.org/volumes/2024.naacl-long/"
}

def get_preview_sentences(text, num_sentences=2):
    sentences = re.split(r'(?<=[.!?])\s+', text)  # 문장 분리
    return " ".join(sentences[:num_sentences])

def fetch_paper_titles_and_links(url: str):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    paper_tags = soup.find_all("a", class_=lambda c: c and "align-middle" in c.split())

    papers = []
    for tag in paper_tags:
        title = tag.text.strip()
        # 제목이 비어 있거나 특정 키워드면 건너뜀
        if not title or title.lower() in {"pdf", "bib", "abs"}:
            continue

        href = tag['href']
        link = href if href.startswith("http") else "https://aclanthology.org" + href

        papers.append({"title": title, "url": link})
    return papers

def fetch_abstract_and_authors(paper_url: str):
    response = requests.get(paper_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Abstract
    abstract_div = soup.find("div", class_="card-body acl-abstract")
    abstract = abstract_div.find("span").text.strip() if abstract_div and abstract_div.find("span") else "Abstract not found"

    # Authors
    lead_p = soup.find("p", class_="lead")
    authors = lead_p.get_text(separator=", ").strip() if lead_p else "Authors not found"

    return abstract, authors

if __name__ == "__main__":
    all_results = []

    for conf_name, url in conference_urls.items():
        print(f"🔍 [{conf_name}] 크롤링 중...")
        papers = fetch_paper_titles_and_links(url)

        for i, paper in enumerate(papers, 1):
            try:
                # 제목이 비어있는 경우 건너뜀
                if not paper['title'].strip():
                    continue

                abstract, authors = fetch_abstract_and_authors(paper['url'])
                paper['abstract'] = abstract
                paper['authors'] = authors
                paper['conference'] = conf_name
                all_results.append(paper)

                preview = get_preview_sentences(abstract, num_sentences=2)

                print(f"✅ 논문 {i} ({conf_name})")
                print(f"제목: {paper['title']}")
                print(f"링크: {paper['url']}")
                print(f"저자: {paper['authors']}")
                print(f"Abstract (preview): {preview}\n{'-'*60}")

                # 20개마다 중간 저장
                if len(all_results) % 20 == 0:
                    with open("papers_partial_2024.json", "w", encoding="utf-8") as f:
                        json.dump(all_results, f, ensure_ascii=False, indent=2)

            except Exception as e:
                print(f"❌ 논문 {i} 처리 실패: {e}\n{'-'*60}")

    # 전체 최종 저장
    with open("papers_combined_2024.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)