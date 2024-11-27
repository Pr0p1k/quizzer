from .chapters import Chapter


class Quiz:

    def __init__(self, name: str, chapters: list[Chapter]):
        self.name = name
        self.chapters = chapters
