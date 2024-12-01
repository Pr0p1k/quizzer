from .chapters import Chapter


class Quiz:

    def __init__(self, name: str, chapters: list[Chapter]):
        self.name = name
        self.chapters = chapters

    def questions_total(self):
        total = 0
        for chapter in self.chapters:
            total += chapter.questions_total()

        return total