from typing import List

class Professor:
    def __init__(self, name: str, university: str, lab: str, field: str, homepage: str, profile: str, publications: str):
        self.name = name
        self.university = university
        self.lab = lab
        self.field = field
        self.homepage = homepage
        self.profile = profile
        self.publications = publications

class ProfessAnalysisResult:
    def __init__(self, summary: str, professors: List[Professor]):
        self.summary = summary
        self.professors = professors
