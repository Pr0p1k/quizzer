from __future__ import annotations
from abc import abstractmethod, ABC

from .questions import Question


# TODO multiple questions per key point?

# TODO docs
class Chapter(ABC):
    name: str

    def __str__(self):
        return self.name

    @abstractmethod
    def questions_total(self) -> int:
        ...


class SuperChapter(Chapter):

    def __init__(self, name: str, sub_chapters: list[Chapter]):
        self.name = name
        self.sub_chapters = sub_chapters

    def questions_total(self) -> int:
        total = 0
        for sub_chapter in self.sub_chapters:
            total += sub_chapter.questions_total()

        return total


class SubChapter(Chapter):

    def __init__(self, name: str, source_content: str, questions: list[Question]):
        self.name = name
        self.source_content = source_content
        self.questions = questions

    def questions_total(self) -> int:
        return len(self.questions)
