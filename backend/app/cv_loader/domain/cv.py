class CV:
    def __init__(self, filename: str, text: str):
        self.filename = filename
        self.text = text

class CVAnalysisResult:
    def __init__(self, summary: str, strengths: str, weaknesses: str, suggestions: str, projects: str):
        self.summary = summary
        self.strengths = strengths
        self.weaknesses = weaknesses
        self.suggestions = suggestions
        self.projects = projects