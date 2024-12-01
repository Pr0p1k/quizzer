from src.poc_python import CONFIG
from src.poc_python.quiz.chapters import SuperChapter
from src.poc_python.quiz.questions import Question
from src.poc_python.quiz.quiz import Quiz
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style


def get_prompt(question: Question, number: int):
    options = list(
        map(
            lambda num_str: f"{' ' * 8}{num_str[0] + 1}. {num_str[1]}\n",
            enumerate(question.options)
        )
    )  # if isinstance(question, OptionQuestion) else "" TODO isinstance
    return (f"    {Fore.BLUE}Question {number + 1}: {Style.RESET_ALL}{question.text}\n\n" +
            f"    {Fore.BLUE}Options:\n{Style.RESET_ALL}{''.join(options)}\n\n")


class QuizCliUi:

    def __init__(self, quiz: Quiz):
        self.name = quiz.name
        self.quiz = quiz
        self.give_answers = CONFIG.quiz_general.give_answers

    def start_quiz(self):
        colorama_init(autoreset=True)
        print(f"{Fore.GREEN}CLI Quiz on the subject of {Fore.BLUE}{self.name}")
        print(f"{Fore.YELLOW}{self.quiz.questions_total()}{Style.RESET_ALL} questions total.\n")

        quiz = self.quiz
        questions_seen_total = 0
        score = 0

        for chapter in quiz.chapters:
            if isinstance(chapter, SuperChapter):
                pass  # not implemented yet
            if True:  # isinstance(chapter, SubChapter): TODO WTF? isinstance doesn't work
                print(f"Chapter {Fore.BLUE}{chapter.name}{Style.RESET_ALL}, {Fore.YELLOW}{chapter.questions_total()}{Style.RESET_ALL} questions:")
                for number, question in enumerate(chapter.questions):
                    questions_seen_total += 1
                    answer = input(get_prompt(question, number))

                    is_correct = question.evaluate_answer(int(answer))

                    score += int(is_correct)  # add 0 or 1

                    if self.give_answers:
                        print(
                            f"{Fore.LIGHTGREEN_EX}Correct." if is_correct else f"{Fore.LIGHTRED_EX}Incorrect, correct answer: {Fore.BLUE}{question.correct_answer()}")

                    print("-" * 100)

        print(f"Quiz finished with score: {Fore.YELLOW}{score} of {questions_seen_total}{Style.RESET_ALL} questions passed.")
