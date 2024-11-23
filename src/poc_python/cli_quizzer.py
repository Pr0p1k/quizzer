import os
from os.path import isfile, join

from splitter import LLMSplitMarkup
from src.poc_python.markup_splitter import split_markup_text
from src.poc_python.output_utils import get_output, split_outline_list
from src.poc_python.question.questions import Question
from src.poc_python.question_extraction import QuestionExtractor
from src.poc_python.question_generation import QuestionGenerator
from src.poc_python.ui.cli.quiz_cli import QuizCliUi

if os.environ.get("QUIZZER_NO_CACHE_1"):
    struct_parser = LLMSplitMarkup(27000)

    with open("/Users/user/IdeaProjects/quizzer_poc/src/main/resources/sample_book_serbia.txt") as file:
        file_content = file.read()

    structure_str = struct_parser.get_structure(file_content)
else:
    # TODO pick random file from path
    with open("/Users/user/IdeaProjects/quizzer_poc/src/poc_python/saved_output/markup/serbia_1.txt") as file:
        structure_str = file.read()

topics = split_markup_text(structure_str)

if os.environ.get("QUIZZER_NO_CACHE_2"):
    extractor = QuestionExtractor(8000, temperature=0.1) # TODO wrong place for temperature

    outlines = []

    for topic in topics:
        response = extractor.get_response(topic[0], topic[1])
        outlines.append(get_output(response))
else:
    cached_dir = "/Users/user/IdeaProjects/quizzer_poc/src/poc_python/saved_output/key_points/serbia_1"
    outline_files = [f for f in os.listdir(cached_dir) if isfile(join(cached_dir, f))]
    outlines = []
    for file in sorted(outline_files): # TODO add names of topics
        outlines.append(open(join(cached_dir, file)).read())

TOPIC_NUMBER = 4 # politics TODO cycle each

selected_outline = outlines[TOPIC_NUMBER]

generated_questions = []

questions = []

if os.environ.get("QUIZZER_NO_CACHE_3"):
    generator = QuestionGenerator(n_ctx=2500)

    for question in split_outline_list(selected_outline)[0:5]:
        response = generator.get_response(question, topics[TOPIC_NUMBER][1])
        generated_questions.append(get_output(response))

    print(generated_questions)
else:
    cached_dir = join("/Users/user/IdeaProjects/quizzer_poc/src/poc_python/saved_output/questions/serbia_1", str(TOPIC_NUMBER))
    question_files = [f for f in os.listdir(cached_dir) if isfile(join(cached_dir, f)) and os.path.splitext(f)[1] == ".json"]
    for question_file in question_files:
        with open(join(cached_dir, question_file)) as file:
            json_str = file.read()
            question = Question.from_json_str(json_str)
            questions.append(question)

quiz = QuizCliUi("Serbia", questions)

quiz.start_game()

