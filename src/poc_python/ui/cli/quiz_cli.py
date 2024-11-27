from src.poc_python.quiz.chapters import SuperChapter, SubChapter
from src.poc_python.quiz.questions import Question, OptionQuestion
from src.poc_python.quiz.quiz import Quiz


class QuizCliUi:

    def __init__(self, quiz: Quiz):
        self.name = quiz.name
        self.quiz = quiz


    def start_quiz(self):
        print(f"CLI Quiz on the subject of {self.name}\n")
        quiz = self.quiz
        questions_total = 0
        score = 0

        for chapter in quiz.chapters:
            if isinstance(chapter, SuperChapter):
                pass # TODO
            if True: # isinstance(chapter, SubChapter): TODO WTF?
                print(f"Chapter \"{chapter.name}\":")
                for question in chapter.questions:
                    questions_total += 1
                    answer = input(self.get_prompt(question))
                    if question.evaluate_answer(int(answer) - 1): # correction of 0-based index
                        score += 1
                    print("-" * 100)

        print(f"Quiz finished with score: {score} of {questions_total}")

    def get_prompt(self, question: Question):
        underline = '    '.join(question.options) # if isinstance(question, OptionQuestion) else "" TODO WTF?
        return f"{question.text}\n\n{underline}\n\n"