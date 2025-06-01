import operator
from typing import Any, Annotated, TypedDict, Union
import logging

from src.poc_python import CONFIG
from src.poc_python.quiz.chapters import Chapter
from src.poc_python.stages_approaches import STAGES
from src.poc_python.text_processors.processor_provider import get_processor_lazy
from src.poc_python.utils.output_utils import split_markup_text_json, get_llm_output, get_chapters_dict_from_json

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)


import traceback


def log_exceptions():
    def decorator(func):
        def wrapper(state):
            try:
                logger.info(f"Executing node: {func.__name__}: {state}")
                return func(state)
            except Exception as e:
                tb = traceback.format_exc()
                logger.error(f"Exception in node {func.__name__}: {e}\n{tb}")
                raise e

        return wrapper

    return decorator

class BaseState(TypedDict):
    name: str
    input_text: str


class MetadataState(TypedDict):
    stages_metadata: Annotated[list[tuple[str, Any]], operator.add]


class ChapterState(TypedDict):
    # chapter_name -> chapter_content
    chapters_content: Annotated[dict[str, str], operator.or_]
    questions_per_chapter: int  # amount of question to generate per chapter # TODO extract to config.
    # ready chapters with all questions inside
    chapters_with_questions: Annotated[list[Chapter], operator.add]


class ProcessingState(TypedDict):
    name: str
    input_text: str
    questions_per_chapter: int  # amount of question to generate per chapter

    stages_metadata: Annotated[list[tuple[str, Any]], operator.add]

    # to be filled by split stage. {chapter_name: chapter_content}
    chapters_json: list[dict]
    # {chapter_name: [{question}, ...]}
    chapters: Annotated[dict, operator.or_]
    # place additional answers here. {(question, answer): [options]}
    enriched_questions: Annotated[dict, operator.or_]
    summary: Any
    # topics extracted from each chapter
    rag_extracts: Annotated[dict, operator.or_]


def apply_config_chapter_limit(state: ChapterState):
    """
    Limit the amount of chapters in the quiz if chapters_limit is applied.
    """
    chapters_limit = CONFIG.debug.get("chapters_limit")
    chapters = state["chapters_content"]
    return dict(list(chapters.items())[:chapters_limit]) if chapters_limit else chapters


def split_chapters(state: Union[BaseState, ChapterState]) -> ChapterState:
    logger.info(f"Split stage for text '{state["name"]}'")
    try:
        processor = get_processor_lazy(STAGES["LANGGRAPH_SPLIT"])
        output_dict = processor.process(state["input_text"])

        return ChapterState(chapters_content=get_chapters_dict_from_json(get_llm_output(output_dict)))
    except Exception as e:
        logger.error(e)
        raise e


def rag_text_to_vector_store(text: str):
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50,
    )
    chunks = text_splitter.create_documents([text])

    from langchain_openai import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings()
    embedded_chunks = [embeddings.embed_query(chunk.page_content) for chunk in chunks]

    from langchain_community.vectorstores import Chroma

    return Chroma.from_documents(chunks, embeddings,
                                 persist_directory="/Users/user/IdeaProjects/quizzer_poc/src/main/resources")
