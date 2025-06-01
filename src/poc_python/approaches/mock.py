from threading import Lock

from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END, START
from langgraph.graph import StateGraph

from src.poc_python.approaches.approach import Approach
from src.poc_python.approaches.mock_functions import *
from src.poc_python.approaches.shared import split_chapters

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)

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

    topic_model = None  # lazy init


    def __init__(self):
        logger.info("Initializing BERT")

    def get_langgraph_graph(self):
        """
        Build the graph. See the graph schema in readme
        """

        builder = StateGraph(MockState)

        builder.add_node(Nodes.SPLIT, split_chapters)
        builder.add_node(Nodes.SUMMARIZE_CHAPTER, summarize_chapter)
        builder.add_node(Nodes.GENERATE_QUESTIONS, generate_questions_for_topic)
        builder.add_node(Nodes.ENRICH_QUESTION, enrich_question)
        builder.add_node(Nodes.COLLECT_QUESTIONS, collect_questions)

        # TODO try to add nodes with annotations

        # START: split input text on chapters
        builder.add_edge(START, Nodes.SPLIT)
        # for each chapter
        # summarize topics per chapter
        builder.add_conditional_edges(Nodes.SPLIT, for_each_chapter, [Nodes.SUMMARIZE_CHAPTER])

        # for each topic
        # generate question(s)
        builder.add_conditional_edges(Nodes.SUMMARIZE_CHAPTER, for_each_topic,
                                      [Nodes.GENERATE_QUESTIONS])
        # for each question
        # enrich question
        builder.add_conditional_edges(Nodes.GENERATE_QUESTIONS, for_each_question,
                                      [Nodes.ENRICH_QUESTION])

        # collect questions into for the topic
        builder.add_edge(Nodes.ENRICH_QUESTION, Nodes.COLLECT_QUESTIONS)

        # done
        builder.add_edge(Nodes.COLLECT_QUESTIONS, END)

        memory_saver = MemorySaver()

        return builder.compile()
