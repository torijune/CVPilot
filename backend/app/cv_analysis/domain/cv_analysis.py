from typing import Optional

class CVAnalysisResult:
    def __init__(self, trend: str, professors: str, feedback: str, improvement: str, project: str):
        self.trend = trend
        self.professors = professors
        self.feedback = feedback
        self.improvement = improvement
        self.project = project
