import json
import logging
import operator
from typing import Annotated, TypedDict, Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.types import Send

from src.poc_python import STAGES, CONFIG
from src.poc_python.text_processors.processor_provider import get_processor_lazy
from src.poc_python.utils.output_utils import get_output, split_markup_text_json

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)


class ProcessingState(TypedDict):
    name: str
    input_text: str
    amount_of_questions: int

    stages_metadata: Annotated[list[tuple[str, Any]], operator.add]

    # to be filled by split stage
    chapters_json: list[dict]
    # {chapter_name: [{question}, ...]}
    chapters: Annotated[dict, operator.or_]
    # place additional answers here. {(question, answer): [options]}
    enriched_questions: Annotated[dict, operator.or_]


def do_split(state: ProcessingState):
    processor = get_processor_lazy(STAGES["LANGGRAPH_SPLIT"])  # TODO Stage doesn't work for this flow
    output_dict = processor.process(state["input_text"])
    return {"stages_metadata": [(STAGES["LANGGRAPH_SPLIT"], output_dict)],
            "chapters_json": split_markup_text_json(get_output(output_dict))}


def for_each_chapter(state: ProcessingState):
    # for debug purposes
    chapters_limit = CONFIG.debug.get("chapters_limit")
    chapters = state["chapters_json"]
    chapters = chapters[:chapters_limit] if chapters_limit else chapters

    return [Send("generate_questions_for_chapter",
                 {
                     "subject_name": state["name"],
                     "amount": state["amount_of_questions"]
                 } | chapter)
            for chapter in chapters]


"""
args: subject_name: str, chapter_name: str, chapter_content: str, amount: int
"""


def generate_questions_for_chapter(args: dict):
    processor = get_processor_lazy(STAGES["LANGGRAPH_QUESTIONS"])  # TODO different stages

    questions_output_dict = processor.process(args["chapter_content"],
                                              general_subject=args["subject_name"],
                                              amount=args["amount"])  # TODO **args

    questions_json = split_markup_text_json(get_output(questions_output_dict))

    return {"stages_metadata": [(STAGES["LANGGRAPH_QUESTIONS"], questions_output_dict)],
            "chapters": {args["chapter_name"]: questions_json}}


def for_each_question(state: ProcessingState):
    questions = next(iter(state["chapters"].values()))  # todo get all questions
    return [Send(STAGES["LANGGRAPH_ENRICH_QUESTION"],
                 # {"question_text": json.loads(q)["question_text"], "correct_answer": json.loads(q)["correct_answer"],
                 q | {"number_of_alternatives": 3}) for q in questions]


def enrich_question(args: dict):
    # question: str, correct_answer: str, number_of_alternatives: str
    llm = get_processor_lazy(STAGES["LANGGRAPH_QUESTIONS"])
    enriched_output_dict = llm.process(args["question"], correct_answer=args["correct_answer"],
                                       amount=args["number_of_alternatives"])
    enriched_output = get_output(enriched_output_dict)

    return {"stages_metadata": [(STAGES["LANGGRAPH_ENRICH_QUESTION"], enriched_output_dict)],
            "enriched_questions": {(args["question"], args["correct_answer"]): json.loads(enriched_output)}}


builder = StateGraph(ProcessingState)

builder.add_node(STAGES["LANGGRAPH_SPLIT"], do_split)
builder.add_node("generate_questions_for_chapter", generate_questions_for_chapter)
builder.add_node(STAGES["LANGGRAPH_ENRICH_QUESTION"], enrich_question)

builder.add_edge(START, STAGES["LANGGRAPH_SPLIT"])
builder.add_conditional_edges(STAGES["LANGGRAPH_SPLIT"], for_each_chapter, ["generate_questions_for_chapter"])
builder.add_conditional_edges("generate_questions_for_chapter", for_each_question,
                              [STAGES["LANGGRAPH_ENRICH_QUESTION"]])
builder.add_edge(STAGES["LANGGRAPH_ENRICH_QUESTION"], END)  # TODO reduce

memory_saver = MemorySaver()

graph = builder.compile(checkpointer=memory_saver)

config = {"configurable": {"thread_id": "1"}} # TODO use some id


def process_text(name: str, input_text: str):
    return graph.invoke({
        "name": name,
        "input_text": input_text
    }, config)