from __future__ import annotations

from random import shuffle
from typing import Union

from colorama import Fore
from colorama import Style
from colorama import init as colorama_init

from src.poc_python import CONFIG
from src.poc_python.approaches.shared import ChapterState, BaseState
from src.poc_python.process_new_text_langgraph import ProcessingState
from src.poc_python.quiz.chapters import Chapter, SubChapter
from src.poc_python.quiz.questions import Question, OptionQuestion
from src.poc_python.quiz.quiz import Quiz


def get_prompt(question: Question, number: int):
    options = list(
        map(
            lambda num_str: f"{' ' * 8}{num_str[0] + 1}. {num_str[1]}\n",
            enumerate(question.get_options())
        )
    ) if isinstance(question, OptionQuestion) else ""

    return (f"    {Fore.BLUE}Question {number + 1}: {Style.RESET_ALL}{question.text}\n\n" +
            f"    {Fore.BLUE}Options:\n{Style.RESET_ALL}{''.join(options)}\n\n")


def join_and_shuffle_answer_options(state: ProcessingState, q: dict) -> list[str]:
    options = state["enriched_questions"][q["question"]]
    # workaround for cases where LLM returns dict instead of a list
    if isinstance(options, dict):
        if len(options) == 1:
            options = list(options.values())[0]  # extract nested list
        else:
            options = list(options.values())  # extract named entries

    options.append(q["correct_answer"])

    shuffle(options)

    return options


class QuizCliUi:

    def __init__(self, quiz: Quiz):
        self.name = quiz.name
        self.quiz = quiz
        self.give_answers = CONFIG.quiz_general.give_answers

    @staticmethod
    def from_state(state: Union[ChapterState | BaseState]) -> QuizCliUi:

        return QuizCliUi(Quiz(state["name"], state))

    def start_quiz(self):
        colorama_init(autoreset=True)
        print(f"{Fore.GREEN}CLI Quiz on the subject of {Fore.BLUE}{self.name}")
        print(f"{Fore.YELLOW}{self.quiz.questions_total()}{Style.RESET_ALL} questions total.\n")

        quiz = self.quiz
        questions_seen_total = 0
        score = 0

        for chapter in quiz.chapters:
            if isinstance(chapter, SubChapter):
                print(
                    f"Chapter {Fore.BLUE}{chapter.name}{Style.RESET_ALL}, {Fore.YELLOW}{chapter.questions_total()}{Style.RESET_ALL} questions:")
                for number, question in enumerate(chapter.questions):
                    questions_seen_total += 1
                    answer = input(get_prompt(question, number))

                    is_correct = question.evaluate_answer(answer)

                    score += int(is_correct)  # add 0 or 1

                    if self.give_answers:
                        print(
                            f"{Fore.LIGHTGREEN_EX}Correct." if is_correct else f"{Fore.LIGHTRED_EX}Incorrect, correct answer: {Fore.BLUE}{question.correct_answer()}")

                    print("-" * 100)
            else:
                pass  # TODO implement for SuperChapters

        print(
            f"Quiz finished with score: {Fore.YELLOW}{score} of {questions_seen_total}{Style.RESET_ALL} questions passed.")
