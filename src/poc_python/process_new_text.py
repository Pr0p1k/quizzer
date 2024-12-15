import logging

from quiz.chapters import SubChapter
from quiz.questions import Question
from quiz.quiz import Quiz
from src.poc_python import MEM, Stage, BYPASS_CACHE
from src.poc_python.utils.output_utils import get_output, get_key_points_list_json, split_markup_text_json
from src.poc_python.text_processors.processor_provider import get_processor_lazy

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)


@MEM.cache()
def generate_markup(text: str) -> dict:
    processor = get_processor_lazy(Stage.MARKUP.value)
    return processor.process(text)

@MEM.cache()
def generate_key_points(subject_name: str, chapter_name: str, chapter_content: str, amount: int) -> dict:
    processor = get_processor_lazy(Stage.KEY_POINTS.value)
    return processor.process(chapter_content, general_subject=subject_name, chapter_name=chapter_name)


@MEM.cache()
def generate_question(chapter_name: str, chapter_content: str, key_point: str, question_type: str) -> dict:
    llm = get_processor_lazy(Stage.QUESTION.value)
    return llm.process(chapter_content, key_point=key_point, general_subject=chapter_name)

# TODO change text: str to some local type. Can later be pdf, video, etc. Need to create processors per type
@MEM.cache()
def generate_full_quiz(subject_name: str, text: str, key_points_per_chapter: int) -> Quiz:
    logger.info(f"Starting processing new text: {subject_name}")
    if BYPASS_CACHE:
        # force calling and rewriting the cache
        markup_output = generate_markup.call(text)[0] # joblib adds extra info, get the first entry
    else:
        markup_output = generate_markup(text)

    chapter_dicts = split_markup_text_json(get_output(markup_output))

    logger.info(f"Text is split into {len(chapter_dicts)} chapters")

    chapters = []

    for chapter_dict in chapter_dicts:
        key_points_output = generate_key_points(subject_name,
                                                chapter_dict["chapter_name"],
                                                chapter_dict["chapter_content"],
                                                key_points_per_chapter)

        key_points: list[dict] = get_key_points_list_json(get_output(key_points_output))

        logger.info(f"Extracted {len(key_points)} key points for chapter '{chapter_dict["chapter_name"]}'")

        questions = []

        # TODO possibly yield asynchronously, so can use the output while it's yet in progress
        # TODO sort based on the number
        for point_dict in key_points[:key_points_per_chapter]: # FIXME remove the limit once it's stable
            question_output = generate_question(chapter_dict["chapter_name"],
                                              chapter_dict["chapter_content"],
                                              point_dict["key_point"],
                                              "OptionQuestion")
            question_output = get_output(question_output)

            logger.info(f"Generated question: {question_output}")
            try:
                question = Question.from_json_str(question_output)
                questions.append(question)
            except KeyError as e:
                logger.warning(f"Exception while creating question: {question_output}, {e}")

        chapter_obj = SubChapter(chapter_dict["chapter_name"], chapter_dict["chapter_content"], questions)
        chapters.append(chapter_obj)

    return Quiz(subject_name, chapters)

