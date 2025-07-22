from typing import List

class Paper:
    def __init__(self, title: str, abstract: str, conference: str, year: int):
        self.title = title
        self.abstract = abstract
        self.conference = conference
        self.year = year

class PaperTrendResult:
    def __init__(self, trend_summary: str, papers: List[Paper]):
        self.trend_summary = trend_summary
        self.papers = papers
