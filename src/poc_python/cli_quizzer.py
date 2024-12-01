import os.path
from os.path import join

from src.poc_python import ROOT_DIR, SAMPLE_INPUTS, BYPASS_CACHE
from src.poc_python.process_new_text import generate_full_quiz
from src.poc_python.ui.cli.quiz_cli import QuizCliUi

SOURCE_FILE = "president_of_serbia.txt"

NAME = os.path.splitext(SOURCE_FILE)[0].replace("_", " ").title()

text = open(join(ROOT_DIR, SAMPLE_INPUTS, SOURCE_FILE)).read()


if BYPASS_CACHE:
    quiz = generate_full_quiz.call(NAME, text, 10)[0]
else:
    quiz = generate_full_quiz(NAME, text, 10)

quiz_cli = QuizCliUi(quiz)

quiz_cli.start_quiz()