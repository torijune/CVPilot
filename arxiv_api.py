import requests
import feedparser

title = "Review-driven Personalized Preference Reasoning with Large Language Models for Recommendation"
base_url = "http://export.arxiv.org/api/query"
params = {
    "search_query": f'all:"{title}"',
    "max_results": 5
}
response = requests.get(base_url, params=params)
feed = feedparser.parse(response.text)

if feed.entries:
    abstract = feed.entries[0].summary
    print(abstract)  # 논문 초록 출력
else:
    print("논문을 찾을 수 없습니다.")
