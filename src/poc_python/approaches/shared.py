import operator
from typing import Any, Annotated, TypedDict
import logging

from src.poc_python.stages_approaches import STAGES
from src.poc_python.text_processors.processor_provider import get_processor_lazy
from src.poc_python.utils.output_utils import split_markup_text_json, get_output

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)


class ProcessingState(TypedDict):
    name: str
    input_text: str
    questions_per_chapter: int  # amount of question to generate per chapter

    stages_metadata: Annotated[list[tuple[str, Any]], operator.add]

    # to be filled by split stage
    chapters_json: list[dict]
    # {chapter_name: [{question}, ...]}
    chapters: Annotated[dict, operator.or_]
    # place additional answers here. {(question, answer): [options]}
    enriched_questions: Annotated[dict, operator.or_]
    summary: Any
    # topics extracted from each chapter
    rag_extracts: Annotated[dict, operator.or_]


def do_split(state: ProcessingState):
    logger.info(f"Started split stage for text '{state["name"]}'")
    try:
        processor = get_processor_lazy(STAGES["LANGGRAPH_SPLIT"])
        output_dict = processor.process(state["input_text"])
        return {"stages_metadata": [(STAGES["LANGGRAPH_SPLIT"], output_dict)],
                "chapters_json": split_markup_text_json(get_output(output_dict))}
    except Exception as e:
        logger.error(e)

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

    return Chroma.from_documents(chunks, embeddings, persist_directory="/Users/user/IdeaProjects/quizzer_poc/src/main/resources")
