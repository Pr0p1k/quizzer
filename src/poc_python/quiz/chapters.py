from __future__ import annotations
from abc import abstractmethod, ABC

from .questions import Question


# TODO multiple questions per key point?

# TODO docs
class Chapter(ABC):
    name: str

    def __str__(self):
        return self.name

class SuperChapter(Chapter):

    def __init__(self, name: str, sub_chapters: list[Chapter]):
        self.name = name
        self.sub_chapters = sub_chapters

class SubChapter(Chapter):

    def __init__(self, name: str, source_content: str, questions: list[Question]):
        self.name = name
        self.source_content = source_content
        self.questions = questions
