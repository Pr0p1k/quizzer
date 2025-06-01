from __future__ import annotations
import json
from abc import abstractmethod, ABC
from typing import Any

from src.poc_python.utils.class_utils import find_subclass_by_name


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
        question_type = data.pop("type")

        # find the class with the name of question type, e.g. OptionQuestion
        cls = find_subclass_by_name(Question, question_type)

        return cls(**data)

    @staticmethod
    def from_fields(question_type: str, question: str, correct_answer: str, options: list[str]):
        cls = find_subclass_by_name(Question, question_type)  # currently only OptionQuestion is implemented anyway

        return cls(question=question, correct_answer=correct_answer, options=options)


class QuestionAnswer(Question):

    def __init__(self, question_text: str, correct_answer: str):
        self.text = question_text
        self.answer = correct_answer

    def evaluate_answer(self, answer: Any) -> bool:
        raise NotImplementedError()

    def correct_answer(self):
        return self.answer


class OptionQuestion(Question):
    def __init__(self, question_text: str, incorrect_options: list[str], correct_answer: str):
        self.text = question_text
        self.incorrect_options = incorrect_options
        self.answer = correct_answer

    @staticmethod
    def from_question_answer(question_answer: QuestionAnswer, options: list[str]) -> OptionQuestion:
        return OptionQuestion(question_answer.text, options, question_answer.answer)

    def evaluate_answer(self, answer: str) -> bool:

        # get the answer by its number, correct 1-based index to 0-based
        if answer.isnumeric():
            num = int(answer)
            options = self.get_options()
            if num >= len(options):
                return False
            return options[num] == self.answer
        else:
            return answer == self.answer  # TODO what if the answer is numeric?

    def correct_answer(self):
        return self.answer

    def get_options(self) -> list[str]:
        return self.incorrect_options + [self.answer]  # TODO shuffling
