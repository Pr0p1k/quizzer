import os.path
from os import listdir
from os.path import join, isfile

from src.poc_python import ROOT_DIR, SAMPLE_INPUTS, BYPASS_CACHE
from src.poc_python.process_new_text import generate_full_quiz
from src.poc_python.ui.cli.quiz_cli import QuizCliUi


def get_text_name(file_name: str) -> str:
    return os.path.splitext(file_name)[0].replace("_", " ").title()


def read_file(file_name: str) -> str:
    with open(join(ROOT_DIR, SAMPLE_INPUTS, file_name)) as file:
        return file.read()


def is_processed(file_name: str) -> bool:
    return generate_full_quiz.check_call_in_cache(get_text_name(file_name), read_file(file_name), 10)


SOURCES_PATH = str(join(ROOT_DIR, SAMPLE_INPUTS))

found_files = [f for f in listdir(SOURCES_PATH) if isfile(join(SOURCES_PATH, f))]

texts = list(map(lambda num_to_file:
                 f"{num_to_file[0] + 1}. {num_to_file[1]}" +
                 f" -> {"Already processed" if is_processed(num_to_file[1]) else "Not yet processed"}",
                 enumerate(found_files)))

print(f"Found following texts:\n    {'\n    '.join(texts)}")

text_number = int(input("Select a number of text to start quiz: "))

selected_text = found_files[text_number - 1]

NAME = get_text_name(selected_text)

text = open(join(ROOT_DIR, SAMPLE_INPUTS, selected_text)).read()

if BYPASS_CACHE:
    quiz = generate_full_quiz.call(NAME, text, 10)[0]
else:
    quiz = generate_full_quiz(NAME, text, 10)

quiz_cli = QuizCliUi(quiz)

quiz_cli.start_quiz()
