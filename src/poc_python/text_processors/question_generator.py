from llama_cpp import LlamaGrammar
from llama_cpp.llama_grammar import JSON_GBNF, JSON_ARR_GBNF

from src.poc_python import Stage, JINJA
from src.poc_python.text_processors.processors import LlamaWrapper, Processor


class LLMQuestionGenerator(Processor):
    # TODO try to write a custom grammar for the output?
    __prompt_template = JINJA.get_template("generate_question_json.txt")

    def __init__(self):
        self.model = LlamaWrapper(stage=Stage.QUESTION)

    def process(self, chapter_content: str, **kwargs) -> dict:
        """
        :param chapter_content: The content of the chapter for which the question is to be generated
        :param kwargs: general_subject: str, key_point: str
        """
        return self.model.generate(
            prompt=self.__prompt_template.render(chapter_content=chapter_content, **kwargs),
            grammar=LlamaGrammar.from_string(JSON_GBNF)  # output in json
        )


class LLMQuestionAnswerGenerator(Processor):
    """
        Generate a number of questions with 1 correct answer only to later be enriched with incorrect options.
    """
    __prompt_template = JINJA.get_template("generate_question_and_answer_json.txt")

    def __init__(self):
        self.model = LlamaWrapper(stage=Stage.QUESTION)

    def process(self, chapter_content: str, **kwargs) -> dict:
        """
        :param chapter_content: chapter_content
        :param kwargs: general_subject: str, amount: int
        """
        return self.model.generate(
            prompt=self.__prompt_template.render(chapter_content=chapter_content, **kwargs),
            grammar=LlamaGrammar.from_string(JSON_ARR_GBNF)  # output in json array
        )


class LLMEnrichQuestion(Processor):
    """
        Generate additional (incorrect) answer options for a question generated previously
    """
    __prompt_template = JINJA.get_template("enrich_question_json.txt")

    def __init__(self):
        self.model = LlamaWrapper(stage=Stage.QUESTION)

    def process(self, question_text: str, **kwargs) -> dict:
        """
        :param question_text: the text of the question without the answer
        :param kwargs:
            correct_answer: str - the correct answer
            num_of_options: int - amount of incorrect answers to generate
        """
        return self.model.generate(
            prompt=self.__prompt_template.render(question_text=question_text, **kwargs),
            grammar=LlamaGrammar.from_string(JSON_ARR_GBNF)  # output in json array
        )
