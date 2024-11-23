from src.poc_python.question.questions import Question


class QuizCliUi:

    def __init__(self, name: str, questions: list[Question]):
        self.name = name
        self.questions = questions
        self.score = 0
        self.total_count = len(questions)


    def start_game(self):
        print(f"CLI Quiz on the subject of {self.name}\n")
        for question in self.questions:
            answer = input(self.get_prompt(question))
            if question.evaluate_answer(int(answer) - 1): # correction of 0-based index
                self.score += 1

        print(f"Quiz finished with score: {self.score} of {self.total_count}")

    def get_prompt(self, question):
        return f"{question.text}\n\n{'    '.join(question.options)}\n\n" # TODO come up with structure of question types