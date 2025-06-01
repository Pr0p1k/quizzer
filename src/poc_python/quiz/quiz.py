from typing import Union

from .chapters import Chapter
from ..approaches.shared import BaseState, ChapterState


class Quiz:

    def __init__(self, name: str, state: Union[BaseState | ChapterState]):
        self.name = name
        self.chapters = state["chapters_with_questions"]

    def questions_total(self):
        total = 0
        for chapter in self.chapters:
            total += chapter.questions_total()

        return total
