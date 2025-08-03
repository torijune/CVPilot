import requests
import feedparser

# 논문 제목 일부만 사용
partial_title = "Review-driven Personalized Preference Reasoning"
base_url = "http://export.arxiv.org/api/query"
params = {
    "search_query": f'all:\"{partial_title}\"',
    "max_results": 5
}
response = requests.get(base_url, params=params)
feed = feedparser.parse(response.text)

found = False
for entry in feed.entries:
    print("검색결과 제목:", entry.title)
    if "Review-driven Personalized Preference Reasoning with Large Language Models for Recommendation".lower() in entry.title.lower():
        print("찾은 논문의 초록:", entry.summary)
        found = True
        break

if not found:
    print("논문을 찾을 수 없습니다.")
