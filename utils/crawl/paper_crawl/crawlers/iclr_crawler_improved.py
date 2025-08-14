import requests
from bs4 import BeautifulSoup
import json
import re
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_selenium_driver():
    """Selenium WebDriver 설정"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 브라우저 창 안 띄우기
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        logger.info("✅ Selenium WebDriver 설정 완료")
        return driver
    except Exception as e:
        logger.error(f"❌ Selenium WebDriver 설정 실패: {e}")
        return None

def get_iclr_papers_with_selenium(url: str):
    """Selenium을 사용하여 ICLR 논문 목록 수집"""
    driver = setup_selenium_driver()
    if not driver:
        return []
    
    try:
        logger.info(f"🔍 ICLR 페이지 로딩 중: {url}")
        driver.get(url)
        
        # 페이지 로딩 대기
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 추가 로딩 시간
        time.sleep(5)
        
        # 스크롤을 통한 동적 로딩 트리거
        logger.info("📜 페이지 스크롤을 통한 동적 콘텐츠 로딩...")
        for i in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # 페이지 소스 가져오기
        page_source = driver.page_source
        logger.info(f"📄 페이지 소스 길이: {len(page_source)}")
        
        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # 논문 링크 찾기 - 다양한 방법 시도
        papers = []
        
        # 방법 1: forum 링크 직접 찾기
        forum_links = soup.find_all('a', href=re.compile(r'/forum\?id='))
        logger.info(f"방법 1: {len(forum_links)}개 forum 링크 발견")
        
        for link in forum_links:
            href = link.get('href')
            if href and '/forum?id=' in href:
                paper_id = href.split('id=')[1].split('&')[0]
                title = link.get_text(strip=True)
                
                if title and len(title) > 10 and 'forum' not in title.lower():
                    paper_url = f"https://openreview.net{href}" if href.startswith('/') else href
                    papers.append({
                        'title': title,
                        'url': paper_url,
                        'id': paper_id
                    })
                    logger.info(f"논문 발견: {title[:50]}...")
        
        # 방법 2: JavaScript 내용에서 논문 ID 추출
        scripts = soup.find_all('script')
        logger.info(f"방법 2: {len(scripts)}개 스크립트 태그 검사")
        
        for script in scripts:
            if script.string:
                # 다양한 패턴으로 논문 ID 찾기
                id_patterns = [
                    r'"id":\s*"([a-zA-Z0-9_-]{10,})"',
                    r'/forum\?id=([a-zA-Z0-9_-]{10,})',
                    r'"forum_id":\s*"([a-zA-Z0-9_-]{10,})"'
                ]
                
                for pattern in id_patterns:
                    matches = re.findall(pattern, script.string)
                    for match in matches:
                        if len(match) > 10 and match not in [p['id'] for p in papers]:
                            # 제목 찾기 시도
                            title_patterns = [
                                rf'"id":\s*"{match}"[^}}]*"title":\s*"([^"]+)"',
                                rf'"{match}"[^}}]*"title":\s*"([^"]+)"'
                            ]
                            
                            title = None
                            for title_pattern in title_patterns:
                                title_match = re.search(title_pattern, script.string)
                                if title_match:
                                    title = title_match.group(1)
                                    break
                            
                            if title and len(title) > 10:
                                paper_url = f"https://openreview.net/forum?id={match}"
                                papers.append({
                                    'title': title,
                                    'url': paper_url,
                                    'id': match
                                })
                                logger.info(f"스크립트에서 논문 발견: {title[:50]}...")
        
        # 방법 3: note 클래스 찾기
        note_divs = soup.find_all('div', class_=re.compile(r'note'))
        logger.info(f"방법 3: {len(note_divs)}개 note div 검사")
        
        for note in note_divs:
            # 제목 찾기
            title_elem = note.find(['h1', 'h2', 'h3', 'h4', 'a'])
            if title_elem:
                title = title_elem.get_text(strip=True)
                if len(title) > 10 and title not in [p['title'] for p in papers]:
                    # URL 찾기
                    link_elem = note.find('a', href=re.compile(r'/forum\?id='))
                    if link_elem:
                        href = link_elem.get('href')
                        paper_id = href.split('id=')[1].split('&')[0]
                        paper_url = f"https://openreview.net{href}" if href.startswith('/') else href
                        papers.append({
                            'title': title,
                            'url': paper_url,
                            'id': paper_id
                        })
                        logger.info(f"note에서 논문 발견: {title[:50]}...")
        
        # 중복 제거
        unique_papers = []
        seen_ids = set()
        for paper in papers:
            if paper['id'] not in seen_ids and len(paper['title']) > 10:
                unique_papers.append(paper)
                seen_ids.add(paper['id'])
        
        logger.info(f"✅ 총 {len(unique_papers)}개의 고유 논문 발견")
        return unique_papers
        
    except Exception as e:
        logger.error(f"❌ Selenium 크롤링 실패: {e}")
        return []
    finally:
        driver.quit()

def fetch_paper_details_with_requests(paper_url: str):
    """requests를 사용하여 논문 상세 정보 수집"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        time.sleep(1)  # 요청 제한 방지
        response = requests.get(paper_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Abstract 추출
        abstract = "Abstract not found"
        abstract_selectors = [
            "div.note-content-value.markdown-rendered",
            "div.note-content",
            "div[data-testid='abstract']",
            "div.abstract"
        ]
        
        for selector in abstract_selectors:
            abstract_elem = soup.select_one(selector)
            if abstract_elem:
                abstract = abstract_elem.get_text(strip=True)
                if len(abstract) > 50:
                    logger.info(f"초록 발견: {len(abstract)}자")
                    break

        # Authors 추출
        authors = "Authors not found"
        
        # 방법 1: forum-authors
        authors_div = soup.find("div", class_="forum-authors")
        if authors_div:
            author_links = authors_div.find_all("a")
            if author_links:
                author_names = [link.get_text(strip=True) for link in author_links if link.get_text(strip=True)]
                if author_names:
                    authors = ", ".join(author_names)
                    logger.info(f"저자 발견: {len(author_names)}명")

        # 방법 2: profile 링크 찾기
        if authors == "Authors not found":
            profile_links = soup.find_all("a", href=re.compile(r'/profile\?id='))
            if profile_links:
                author_names = [link.get_text(strip=True) for link in profile_links[:10] if link.get_text(strip=True)]
                if author_names:
                    authors = ", ".join(author_names)
                    logger.info(f"프로필에서 저자 발견: {len(author_names)}명")

        return abstract, authors
        
    except Exception as e:
        logger.error(f"❌ 논문 상세 정보 수집 실패: {e}")
        return "Abstract not found", "Authors not found"

def crawl_all_papers(url: str):
    """개선된 ICLR 크롤러 메인 함수"""
    logger.info(f"🔍 개선된 ICLR 크롤링 시작: {url}")
    
    # 1. Selenium으로 논문 목록 수집
    papers = get_iclr_papers_with_selenium(url)
    
    if not papers:
        logger.warning("⚠️ 논문 목록을 찾을 수 없습니다. 기본 크롤러로 시도...")
        # 기본 크롤러로 폴백
        from . import iclr_crawler
        papers = iclr_crawler.fetch_paper_titles_and_links(url)
    
    logger.info(f"📊 수집된 논문 수: {len(papers)}")
    
    # 2. 각 논문의 상세 정보 수집
    for i, paper in enumerate(papers, 1):
        try:
            logger.info(f"📄 논문 {i}/{len(papers)} 처리 중: {paper['title'][:50]}...")
            
            abstract, authors = fetch_paper_details_with_requests(paper['url'])
            
            paper_data = {
                'title': paper['title'],
                'abstract': abstract,
                'authors': authors,
                'url': paper['url'],
                'year': 2025,
                'conference': 'ICLR',
                'field': 'Machine Learning / Deep Learning (ML/DL)'
            }
            
            logger.info(f"✅ 논문 {i} 완료: {paper['title'][:30]}...")
            yield paper_data
            
        except Exception as e:
            logger.error(f"❌ 논문 {i} 처리 실패: {e}")
            continue
    
    logger.info(f"🎉 총 {len(papers)}개 논문 크롤링 완료")

def iclr_crawler_improved():
    """개선된 ICLR 크롤러 진입점"""
    url = "https://openreview.net/group?id=ICLR.cc/2025/Conference#tab-accept-oral"
    
    all_results = []
    for paper in crawl_all_papers(url):
        all_results.append(paper)
    
    # 결과 저장
    base_dir = os.path.dirname(os.path.dirname(__file__))
    output_path = os.path.join(base_dir, "iclr_papers_2025_improved.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 {len(all_results)}개 논문이 {output_path}에 저장되었습니다.")
    return all_results

if __name__ == "__main__":
    iclr_crawler_improved() 