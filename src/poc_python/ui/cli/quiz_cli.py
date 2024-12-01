from src.poc_python import CONFIG
from src.poc_python.quiz.chapters import SuperChapter
from src.poc_python.quiz.questions import Question
from src.poc_python.quiz.quiz import Quiz


class QuizCliUi:

    def __init__(self, quiz: Quiz):
        self.name = quiz.name
        self.quiz = quiz
        self.give_answers = CONFIG.quiz_general.give_answers


    def start_quiz(self):
        print(f"CLI Quiz on the subject of {self.name}\n")
        quiz = self.quiz
        questions_total = 0
        score = 0

        for chapter in quiz.chapters:
            if isinstance(chapter, SuperChapter):
                pass # not implemented yet
            if True: # isinstance(chapter, SubChapter): TODO WTF? isinstance doesn't work
                print(f"Chapter \"{chapter.name}\":")
                for question in chapter.questions:
                    questions_total += 1
                    answer = input(self.get_prompt(question))

                    is_correct = question.evaluate_answer(int(answer))

                    score += int(is_correct) # add 0 or 1

                    if self.give_answers:
                        print("Correct." if is_correct else f"Incorrect, correct answer: {question.correct_answer()}")

                    print("-" * 100)

        print(f"Quiz finished with score: {score} of {questions_total}")

    def get_prompt(self, question: Question):
        underline = '    '.join(question.options) # if isinstance(question, OptionQuestion) else "" TODO isinstance
        return f"{question.text}\n\n{underline}\n\n"