from llama_cpp import LlamaGrammar
from llama_cpp.llama_grammar import JSON_GBNF, JSON_ARR_GBNF

from src.poc_python import Stage
from src.poc_python.utils.input_utils import read_prompt_from_resource
from src.poc_python.text_processors.processors import LlamaWrapper, Processor
from src.poc_python.text_processors.markup import DEFAULT_MARKUP


class LLMQuestionGenerator(Processor):
    # TODO try to write a custom grammar for the output?
    __prompt = read_prompt_from_resource("generate_question_json")

    def __init__(self):
        self.model = LlamaWrapper(stage=Stage.QUESTION)

    def process(self, chapter_content: str, **kwargs) -> dict:
        """
        :param chapter_content: The content of the chapter for which the question is to be generated
        :param kwargs: general_subject: str, key_point: str
        """
        return self.model.generate(
            prompt=self.__format_prompt(self.__prompt, chapter_content=chapter_content, **kwargs),
            grammar=LlamaGrammar.from_string(JSON_GBNF)  # output in json
        )

    @staticmethod
    def __format_prompt(prompt: str, general_subject: str, key_point: str, chapter_content: str):
        return (prompt
                .replace("<SUBJECT_NAME>", general_subject)
                .replace(DEFAULT_MARKUP.topic_content, chapter_content)
                .replace(DEFAULT_MARKUP.topic_name, key_point))  # TODO jinja


class LLMQuestionAnswerGenerator(Processor):
    """
        Generate a question with a correct answer only to later be enriched with incorrect options.
    """
    __prompt = read_prompt_from_resource("generate_question_and_answer_json")

    def __init__(self):
        self.model = LlamaWrapper(stage=Stage.QUESTION)

    def process(self, chapter_content: str, **kwargs) -> dict:
        """
        :param chapter_content: chapter_content
        :param kwargs: general_subject: str, amount: int
        """
        return self.model.generate(
            prompt=self.__format_prompt(self.__prompt, chapter_content=chapter_content, **kwargs),
            grammar=LlamaGrammar.from_string(JSON_ARR_GBNF)  # output in json array
        )

    @staticmethod
    def __format_prompt(prompt: str, general_subject: str, chapter_content: str, amount: int):
        return (prompt
                .replace("<SUBJECT_NAME>", general_subject)
                .replace(DEFAULT_MARKUP.topic_content, chapter_content)
                .replace("<AMOUNT>", str(amount)))  # TODO jinja


class LLMEnrichQuestion(Processor):
    """
        Generate additional (incorrect) answer options for a question generated previously
    """
    __prompt = read_prompt_from_resource("enrich_question_json")

    def __init__(self):
        self.model = LlamaWrapper(stage=Stage.QUESTION)

    def process(self, question_text: str, **kwargs) -> dict:
        """
        :param question_text: the text of the question without the answer
        :param kwargs:
            correct_answer: str - the correct answer
            amount: int - amount of incorrect answers to generate
        """
        return self.model.generate(
            prompt=self.__format_prompt(self.__prompt, question_text=question_text, **kwargs),
            grammar=LlamaGrammar.from_string(JSON_ARR_GBNF)  # output in json array
        )

    @staticmethod
    def __format_prompt(prompt: str, question_text: str, correct_answer: str, amount: int):
        return (prompt
                .replace("<QUESTION_TEXT>", question_text)
                .replace("<ANSWER>", correct_answer)
                .replace("<AMOUNT>", str(amount)))  # TODO jinja
