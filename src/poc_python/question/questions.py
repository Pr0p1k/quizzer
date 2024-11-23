import json
from abc import abstractmethod, ABC
from typing import Any


class Question(ABC):
    text: str

    @abstractmethod
    def evaluate_answer(self, answer: Any) -> bool:
        ...

    @staticmethod
    def from_json_str(json_str: str) -> "Question": # TODO type
        data = json.loads(json_str)
        subclasses = Question.__all_subclasses(Question)
        question_type = data.pop("type")
        cls = next(c for c in subclasses if c.__name__ == question_type) # TODO default
        if not cls:
            raise Exception(f"Question type not found: {question_type}")

        return cls(**data)


    @staticmethod
    def __all_subclasses(cls) -> set:
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in Question.__all_subclasses(c)])


class OptionQuestion(Question):

    def __init__(self, question: str, options: list[str], correct_answer: int):
        self.text = question
        self.options = options
        self.answer = correct_answer

    def evaluate_answer(self, answer: int) -> bool:
        return answer == self.answer

