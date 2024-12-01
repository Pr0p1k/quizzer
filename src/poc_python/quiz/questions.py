from __future__ import annotations
import json
from abc import abstractmethod, ABC
from typing import Any


class Question(ABC):
    text: str

    @abstractmethod
    def evaluate_answer(self, answer: Any) -> bool:
        ...

    @abstractmethod
    def correct_answer(self):
        ...

    @staticmethod
    def from_json_str(json_str: str) -> Question:
        data = json.loads(json_str)
        subclasses = Question.__all_subclasses(Question)
        question_type = data.pop("type")

        # find the class with the name of question type, e.g. OptionQuestion
        cls = next(c for c in subclasses if c.__name__ == question_type)
        if not cls:
            raise Exception(f"Question type not found: {question_type}")

        return cls(**data)

    @staticmethod
    def __all_subclasses(cls) -> set:
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in Question.__all_subclasses(c)])


class OptionQuestion(Question):
    def __init__(self, question: str, options: list[str], correct_answer: str):
        self.text = question
        self.options = options
        self.answer = correct_answer

    def evaluate_answer(self, answer: int) -> bool:
        # get the answer by its number, correct 1-based index to 0-based
        return self.options[answer - 1] == self.answer

    def correct_answer(self):
        return self.answer
