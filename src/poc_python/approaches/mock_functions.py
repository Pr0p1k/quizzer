import logging
import operator
from enum import Enum
from typing import Any, Annotated

from langgraph.types import Send

from src.poc_python.approaches.shared import log_exceptions, apply_config_chapter_limit, BaseState, ChapterState
from src.poc_python.quiz.chapters import SubChapter
from src.poc_python.quiz.questions import QuestionAnswer, OptionQuestion

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)


class Nodes:
    SPLIT = "split_chapters"
    SUMMARIZE_CHAPTER = "summarize_topics_for_chapter"
    GENERATE_QUESTIONS = "generate_questions_for_chapter"
    ENRICH_QUESTION = "enrich_question"
    COLLECT_QUESTIONS = "collect_questions"
    COLLECT_TOPICS = "collect_topics"
    COLLECT_CHAPTERS = "collect_chapters"


# TODO use some prebuilt dictionary
FILTER_WORDS = {"of", "and", "the", "is", "in", "by", "on", "to", "with", "as", "was"}

def merge_enriched_questions(source_dict: dict, new_dict: dict) -> dict:
    for chapter_name, topic_questions in new_dict.items():
        if chapter_name in source_dict:
            for topic, questions in new_dict[chapter_name].items():
                if topic in source_dict[chapter_name]:
                    source_dict[chapter_name][topic] = source_dict[chapter_name][topic] + questions
                else:
                    source_dict[chapter_name][topic] = questions
        else:
            source_dict[chapter_name] = topic_questions

    return source_dict


class MockState(BaseState, ChapterState):
    # topics extracted from each chapter. {chapter_name -> list_of_topics}
    rag_extracts: Annotated[dict[str, list[str]], operator.or_]
    # questions per topic per chapter. {(chapter_name, topic) -> list[question]}
    chapter_topic_questions: Annotated[dict[tuple[str, str], list[QuestionAnswer]], operator.or_]
    # place additional answers here. {chapter_name: {topic -> list[Question]}}
    chapter_topic_enriched: Annotated[
        dict[str, dict[str, list[QuestionAnswer]]], merge_enriched_questions]  # TODO add dict types

    total_questions: int


@log_exceptions()
def summarize_chapter(args: dict):  # TODO extract to key_points_extractor
    to_return = {args["chapter_name"]: ["kek", "lol", "aha"]}

    return MockState(rag_extracts=to_return)


@log_exceptions()
def for_each_chapter(state: MockState):
    # for debug purposes
    chapters = apply_config_chapter_limit(state)

    return [Send(Nodes.SUMMARIZE_CHAPTER,
                 {
                     "subject_name": state["name"],
                     "amount": state["questions_per_chapter"],
                     "chapter_name": chapter_name,
                     "chapter_content": chapter_content
                 }  # TODO invent a type
                 )
            for chapter_name, chapter_content in chapters.items()]


@log_exceptions()
def for_each_topic(state: MockState):
    # assuming only one chapter is in the state since it came from chapter branching
    chapter_name, chapter_topics = state["rag_extracts"].popitem()
    return [Send(Nodes.GENERATE_QUESTIONS,
                 {
                     "chapter_name": chapter_name,
                     "topic": topic
                 }  # TODO invent type
                 ) for topic in chapter_topics]


@log_exceptions()
def generate_questions_for_topic(args: dict):  # TODO add logging
    # {chapter_name: ..., topic: ...}
    questions = list(map(lambda x: QuestionAnswer("topic question" + x, x + " " + x), [args["topic"]] * 3))
    return MockState(chapter_topic_questions={(args["chapter_name"], args["topic"]): questions})


@log_exceptions()
def for_each_question(state: MockState):  # TODO add logging
    chapter_topic, questions = state["chapter_topic_questions"].popitem()  # supposed to have 1 item only
    chapter, topic = chapter_topic

    return [Send(Nodes.ENRICH_QUESTION,
                 {
                     "chapter_name": chapter,
                     "topic": topic,
                     "question": question
                 }  # TODO invent a type
                 ) for question in questions]


@log_exceptions()
def enrich_question(args: dict[str, Any]):
    qa: QuestionAnswer = args["question"]

    return MockState(chapter_topic_enriched={args["chapter_name"]:
        {args["topic"]: [
            OptionQuestion(qa.text,
                           ["generated", "options", "here"],
                           qa.correct_answer())
        ]}
    })


@log_exceptions()
def collect_questions(state: MockState):
    logger.info(f"Collecting all questions")
    chapters = []
    total_questions = 0

    for chapter_name, chapter_topic_dict in state["chapter_topic_enriched"].items():
        questions = [question
                     for questions in chapter_topic_dict.values()  # TODO move topic inside Question class
                     for question in questions]  # flatmap
        total_questions += len(questions)
        chapters.append(
            SubChapter(chapter_name, state["chapters_content"][chapter_name], questions)
        )

    logger.error(f"Total questions collected: {total_questions} in {len(state["chapter_topic_enriched"])} chapters.")
    return MockState(chapters_with_questions=chapters, total_questions=total_questions)
