import json
import os.path
import time
from os import listdir
from os.path import join, isfile, isdir
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

from src.poc_python import ROOT_DIR, SAMPLE_INPUTS, BYPASS_CACHE, GENERATED_QUIZZES
from src.poc_python.process_new_text_langgraph import process_text
from src.poc_python.ui.cli.quiz_cli import QuizCliUi

SOURCES_PATH = str(join(ROOT_DIR, SAMPLE_INPUTS))
GENERATED_QUIZZES_PATH = str(join(ROOT_DIR, GENERATED_QUIZZES, "langgraph"))

def get_text_name(file_name: str) -> str:
    return os.path.splitext(file_name)[0].replace("_", " ").title()


def read_file(file_name: str) -> str:
    with open(join(ROOT_DIR, SAMPLE_INPUTS, file_name)) as file:
        return file.read()


def num_of_processed_versions(file_name: str) -> int:
    # if it was processed before, it is saved as a dir with the same name as source file
    cache_dir = join(GENERATED_QUIZZES_PATH, file_name)
    if file_name in listdir(GENERATED_QUIZZES_PATH) and isdir(cache_dir):
        return len(listdir(cache_dir))

    return 0


def main():
    found_files = [(f, num_of_processed_versions(f)) for f in listdir(SOURCES_PATH) if isfile(join(SOURCES_PATH, f))]

    texts = list(map(lambda num_to_file:
                     f"{num_to_file[0] + 1}. {Fore.BLUE}{num_to_file[1][0]}{Style.RESET_ALL}" +
                     f" -> {
                     f"{Fore.GREEN}Already processed{Style.RESET_ALL} - {num_to_file[1][1]} version(s)" if num_to_file[1][1] > 0
                     else
                     f"{Fore.RED}Not yet processed{Style.RESET_ALL}"}",
                     enumerate(found_files)))

    colorama_init(autoreset=True)

    print(f"Found following texts:\n    {'\n    '.join(texts)}")

    text_number = int(input("Select the number of a text to start quiz: "))

    (selected_file_name, num_of_versions) = found_files[text_number - 1]

    # if there's no versions processed or set to bypass the cache
    if num_of_versions == 0 or BYPASS_CACHE:
        display_name = get_text_name(selected_file_name)
        text = open(join(ROOT_DIR, SAMPLE_INPUTS, selected_file_name)).read()
        result = process_text(display_name, text)

        with open(join(GENERATED_QUIZZES_PATH, selected_file_name, str(int(time.time())) + ".json"), "w") as output_file:
            output_file.write(json.dumps(result))
    else:
        # names are <timestamp>.json, str comparison is fine due to slowly changing length of timestamps
        latest_version = max(listdir(join(GENERATED_QUIZZES_PATH, selected_file_name)))

        with open(join(GENERATED_QUIZZES_PATH, selected_file_name, latest_version)) as json_file:
            result = json.loads(json_file.read())

    quiz_cli = QuizCliUi.from_state(result)

    quiz_cli.start_quiz()

if __name__ == "__main__":
    main()