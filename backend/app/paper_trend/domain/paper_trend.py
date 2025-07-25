from typing import List

class Paper:
    def __init__(self, title: str, abstract: str, conference: str, year: int, url: str = None, relevance_score: float = 0.0):
        self.title = title
        self.abstract = abstract
        self.conference = conference
        self.year = year
        self.url = url
        self.relevance_score = relevance_score

class PaperTrendResult:
    def __init__(self, trend_summary: str, papers: List[Paper]):
        self.trend_summary = trend_summary
        self.papers = papers
