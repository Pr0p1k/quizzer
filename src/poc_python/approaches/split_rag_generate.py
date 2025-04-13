import json
import logging
from enum import Enum

from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.types import Send

from src.poc_python import CONFIG
from src.poc_python.approaches.shared import do_split, ProcessingState, rag_text_to_vector_store
from src.poc_python.stages_approaches import STAGES
from src.poc_python.text_processors.processor_provider import get_processor_lazy
from src.poc_python.utils.output_utils import get_output, split_markup_text_json

from src.poc_python.approaches.approach import Approach
from threading import Lock

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)


class SplitRagGenerate(Approach):
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
    COLLECT = "collect_all_questions"


    topic_model: "BERTopic" # lazy init
    mutex = Lock()

    # TODO use some prebuilt dictionary
    FILTER_WORDS = {"of", "and", "the", "is", "in", "by", "on", "to", "with", "as", "was"}

    def __init__(self):
        logger.info("Initializing BERT")
        from bertopic import BERTopic
        SplitRagGenerate.topic_model = BERTopic()

    def get_langgraph_graph(self):
        """
        Build the graph. See the graph schema in readme
        """

        builder = StateGraph(ProcessingState)

        builder.add_node(SplitRagGenerate.SPLIT, do_split)  # TODO extract names
        builder.add_node(SplitRagGenerate.SUMMARIZE_CHAPTER, self.__summarize_topics_for_chapter)
        builder.add_node(SplitRagGenerate.GENERATE_QUESTIONS, self.__generate_questions_for_topic)
        builder.add_node(SplitRagGenerate.ENRICH_QUESTION, self.__enrich_question)
        builder.add_node(SplitRagGenerate.COLLECT, self.__collect_all_questions)

        builder.add_edge(START, SplitRagGenerate.SPLIT)
        builder.add_conditional_edges(SplitRagGenerate.SPLIT,
                                      self.__for_each_chapter,
                                      [SplitRagGenerate.SUMMARIZE_CHAPTER])
        builder.add_edge(SplitRagGenerate.SUMMARIZE_CHAPTER, SplitRagGenerate.GENERATE_QUESTIONS)
        builder.add_conditional_edges(SplitRagGenerate.GENERATE_QUESTIONS,
                                      self.__for_each_question,
                                      [SplitRagGenerate.ENRICH_QUESTION])
        builder.add_edge(SplitRagGenerate.ENRICH_QUESTION, SplitRagGenerate.COLLECT)
        builder.add_edge(SplitRagGenerate.COLLECT, END)

        memory_saver = MemorySaver()

        return builder.compile(checkpointer=memory_saver)

    @staticmethod
    def __for_each_chapter(state: ProcessingState):
        try:
            # for debug purposes
            chapters_limit = CONFIG.debug.get("chapters_limit")
            chapters = state["chapters_json"]
            chapters = chapters[:chapters_limit] if chapters_limit else chapters

            return [Send(SplitRagGenerate.SUMMARIZE_CHAPTER,
                         {
                             "subject_name": state["name"],
                             "amount": state["questions_per_chapter"]
                         } | chapter)
                    for chapter in chapters]
        except Exception as e:
            logger.error(e)

    @staticmethod
    def __summarize_topics_for_chapter(args: dict): # TODO extract to key_points_extractor
        with SplitRagGenerate.mutex:  # critical session
            sentences = args["chapter_content"].split("\n")
            if len(sentences) > 10:
                topics, probs = SplitRagGenerate.topic_model.fit_transform(sentences)
            else:
                topics = []
                probs = []

        most_common_words = SplitRagGenerate.topic_model.get_topics()
        # flat map and filter
        filtered = [
            entry
            for entries in map(
                lambda list_entry: filter(
                    lambda word_prob:
                        len(word_prob[0]) > 0 and word_prob[0] not in SplitRagGenerate.FILTER_WORDS,
                    list_entry
                ),
                most_common_words.values()
            )
            for entry in entries
        ]

        words = [word for word, prob in filtered]

        vector_store = rag_text_to_vector_store(args["chapter_content"])

        results = vector_store.similarity_search(", ".join(words), k=5) # Retrieve top 5 results

        return ProcessingState(rag_extracts={args["chapter_name"]: list(set(map(lambda doc: doc.page_content,results)))})


    @staticmethod
    def __for_each_topic(state: ProcessingState):
        # TODO send to __generate
        raise Exception()

    @staticmethod
    def __generate_questions_for_topic(state: ProcessingState): # TODO is it direct to generate or through conditional?

        for chapter in state["chapters_json"]:
            logger.info(f"Started question generation stage for chapter '{chapter["chapter_name"]}'")

            try:
                processor = get_processor_lazy(STAGES["LANGGRAPH_QUESTIONS"])

                questions_output = processor.process() # TODO make a RAG processor

                questions_json = split_markup_text_json(questions_output)

                # TODO quick workaround to unify case where the list is nested
                if isinstance(questions_json, dict) and len(questions_json) == 1:
                    questions_json = list(questions_json.values())[0]

                return {"stages_metadata": [(STAGES["LANGGRAPH_QUESTIONS"], questions_output)],
                        "chapters": {chapter["chapter_name"]: questions_json}}
            except Exception as e:
                logger.error(e)

    @staticmethod
    def __for_each_question(state: ProcessingState):
        try:
            questions = next(iter(state["chapters"].values()))  # todo get all questions
            return [Send(SplitRagGenerate.ENRICH_QUESTION,
                         q | {"number_of_alternatives": 3}) for q in questions]
        except Exception as e:
            logger.error(e)

    @staticmethod
    def __enrich_question(args: dict):
        # args: question: str, correct_answer: str, number_of_alternatives: str

        logger.info(f"Started question enrichment stage for question '{args["question"]}'")

        try:
            llm = get_processor_lazy(STAGES["LANGGRAPH_ENRICH_QUESTION"])  # TODO replace with a class with fields
            enriched_output_dict = llm.process(args["question"], correct_answer=args["correct_answer"],
                                               num_of_options=args["number_of_alternatives"])
            enriched_output = get_output(enriched_output_dict)

            return {"stages_metadata": [(SplitRagGenerate.ENRICH_QUESTION, enriched_output_dict)],
                    "enriched_questions": {args["question"]: json.loads(enriched_output)}}
        except Exception as e:
            logger.error(e)

    @staticmethod
    def __collect_all_questions(state: ProcessingState):
        logger.info("Collecting all questions")

        try:
            return {"summary": len(state["chapters"])}
        except Exception as e:
            logger.error(e)
