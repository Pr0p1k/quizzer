import json
import logging
import operator
from collections import defaultdict
from enum import Enum
from typing import TypedDict, Annotated, Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.types import Send

from src.poc_python import CONFIG
from src.poc_python.approaches.shared import split_chapters, rag_text_to_vector_store, BaseState, \
    apply_config_chapter_limit, ChapterState
from src.poc_python.quiz.chapters import SubChapter
from src.poc_python.quiz.questions import OptionQuestion, QuestionAnswer, Question
from src.poc_python.stages_approaches import STAGES
from src.poc_python.text_processors.processor_provider import get_processor_lazy
from src.poc_python.utils.output_utils import get_llm_output, split_markup_text_json

from src.poc_python.approaches.approach import Approach
from threading import Lock

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)

import traceback


def log_exceptions(node_name):
    def decorator(func):
        def wrapper(state):
            try:
                logger.info(f"Executing node: {func.__name__}: {state}")
                return func(state)
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(f"Exception in node {func.__name__}: {e}\n{tb}")
                # Attach error info to state
                state["error"] = str(e)
                state["traceback"] = tb
                state["failed_node"] = node_name
                state["failed"] = True
                raise e

        return wrapper

    return decorator


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
    chapter_topic_enriched: Annotated[dict[str, dict[str, list[QuestionAnswer]]], merge_enriched_questions] # TODO add dict types

    total_questions: int


class MockGraph(Approach):
    """
    Steps:
    - Step 1 - split
    - Step 2 - summarize and extract pieces - BERT and RAG
    - Step 3 - generate questions with context - OpenAI
    - Step 4 - simplify answer if applicable (remove redundancy) - BERT??? TODO
    - Step 5 - add wrong options/depending on question type - OpenAI
    - Step 6/4 - remove redundant numbers of options etc. TODO
    """

    # Nodes
    SPLIT = "split_chapters"
    SUMMARIZE_CHAPTER = "summarize_topics_for_chapter"
    GENERATE_QUESTIONS = "generate_questions_for_chapter"
    ENRICH_QUESTION = "enrich_question"
    COLLECT_QUESTIONS = "collect_questions"
    COLLECT_TOPICS = "collect_topics"
    COLLECT_CHAPTERS = "collect_chapters"

    topic_model: "BERTopic"  # lazy init
    mutex = Lock()

    # TODO use some prebuilt dictionary
    FILTER_WORDS = {"of", "and", "the", "is", "in", "by", "on", "to", "with", "as", "was"}

    def __init__(self):
        logger.info("Initializing BERT")

    def get_langgraph_graph(self):
        """
        Build the graph. See the graph schema in readme
        """

        builder = StateGraph(MockState)

        builder.add_node(MockGraph.SPLIT, split_chapters)
        builder.add_node(MockGraph.SUMMARIZE_CHAPTER, self.__summarize_chapter)
        builder.add_node(MockGraph.GENERATE_QUESTIONS, self.__generate_questions_for_topic)
        builder.add_node(MockGraph.ENRICH_QUESTION, self.__enrich_question)
        builder.add_node(MockGraph.COLLECT_QUESTIONS, self.__collect_questions)

        # TODO try to add nodes with annotations

        # START: split input text on chapters
        builder.add_edge(START, MockGraph.SPLIT)
        # for each chapter
        # summarize topics per chapter
        builder.add_conditional_edges(MockGraph.SPLIT, self.__for_each_chapter, [MockGraph.SUMMARIZE_CHAPTER])

        # for each topic
        # generate question(s)
        builder.add_conditional_edges(MockGraph.SUMMARIZE_CHAPTER, self.__for_each_topic,
                                      [MockGraph.GENERATE_QUESTIONS])
        # for each question
        # enrich question
        builder.add_conditional_edges(MockGraph.GENERATE_QUESTIONS, self.__for_each_question,
                                      [MockGraph.ENRICH_QUESTION])

        # collect questions into for the topic
        builder.add_edge(MockGraph.ENRICH_QUESTION, MockGraph.COLLECT_QUESTIONS)

        # done
        builder.add_edge(MockGraph.COLLECT_QUESTIONS, END)

        memory_saver = MemorySaver()

        return builder.compile()

    @staticmethod
    @log_exceptions("")
    def __for_each_chapter(state: MockState):
        # for debug purposes
        chapters = apply_config_chapter_limit(state)

        return [Send(MockGraph.SUMMARIZE_CHAPTER,
                     {
                         "subject_name": state["name"],
                         "amount": state["questions_per_chapter"],
                         "chapter_name": chapter_name,
                         "chapter_content": chapter_content
                     }  # TODO invent a type
                     )
                for chapter_name, chapter_content in chapters.items()]

    @staticmethod
    @log_exceptions("")
    def __summarize_chapter(args: dict):  # TODO extract to key_points_extractor
        # TODO pass state here IF the state is branched
        to_return = {args["chapter_name"]: ["kek", "lol", "aha"]}

        return MockState(rag_extracts=to_return)

    @staticmethod
    @log_exceptions("")
    def __for_each_topic(state: MockState):
        # assuming only one chapter is in the state since it came from chapter branching
        chapter_name, chapter_topics = state["rag_extracts"].popitem()
        return [Send(MockGraph.GENERATE_QUESTIONS,
                     {
                         "chapter_name": chapter_name,
                         "topic": topic
                     }  # TODO invent type
                     ) for topic in chapter_topics]

    @staticmethod
    @log_exceptions("")
    def __generate_questions_for_topic(args: dict):  # TODO add logging
        # {chapter_name: ..., topic: ...}
        questions = list(map(lambda x: QuestionAnswer("topic question" + x, x + " " + x), [args["topic"]] * 3))
        return MockState(chapter_topic_questions={(args["chapter_name"], args["topic"]): questions})

    @staticmethod
    @log_exceptions("")
    def __for_each_question(state: MockState):  # TODO add logging
        chapter_topic, questions = state["chapter_topic_questions"].popitem()  # supposed to have 1 item only
        chapter, topic = chapter_topic

        return [Send(MockGraph.ENRICH_QUESTION,
                     {
                         "chapter_name": chapter,
                         "topic": topic,
                         "question": question
                     }  # TODO invent a type
                     ) for question in questions]

    @staticmethod
    @log_exceptions("")
    def __enrich_question(args: dict[str, Any]):
        qa: QuestionAnswer = args["question"]

        return MockState(chapter_topic_enriched={args["chapter_name"]:
            {args["topic"]: [
                OptionQuestion(qa.text,
                               ["generated", "options", "here"],
                               qa.correct_answer())
            ]}
        })

    @staticmethod
    @log_exceptions("")
    def __collect_questions(state: MockState):
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
