from langchain_text_splitters import RecursiveCharacterTextSplitter
from llama_cpp import LlamaGrammar
from llama_cpp.llama_grammar import JSON_ARR_GBNF

from src.poc_python import Stage, JINJA
from src.poc_python.text_processors.processor_provider import get_llm
from src.poc_python.text_processors.processors import LlamaWrapper, Processor
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


class LLMKeyPointsExtractor(Processor):
    __prompt_template = JINJA.get_template("extract_points_json.txt")

    def __init__(self):
        self.model = get_llm()


    def process(self, chapter_content: str, **kwargs) -> dict:
        """
        :param chapter_content: chapter content
        :param kwargs: general_subject: str, chapter_name: str
        """

        return self.model.invoke(
            input=self.__prompt_template.render(chapter_content=chapter_content, **kwargs),
            # grammar=LlamaGrammar.from_string(JSON_ARR_GBNF) # TODO put it into config
        )


class RAGKeyPointsExtractor(Processor):
    def process(self, input_text: str, **kwargs) -> dict:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=50,
        )
        chunks = text_splitter.create_documents([input_text])

        embeddings = OpenAIEmbeddings()
        embedded_chunks = [embeddings.embed_query(chunk.page_content) for chunk in chunks]

        vector_store = Chroma.from_documents(chunks, embeddings, persist_directory="/Users/user/IdeaProjects/quizzer_poc/src/main/resources")

        query = "key fact"
        amount = kwargs["amount"]
        results = vector_store.similarity_search(query, k=amount)  # Retrieve top 5 results
        # TODO