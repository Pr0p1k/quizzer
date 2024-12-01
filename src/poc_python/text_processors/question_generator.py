from llama_cpp import LlamaGrammar
from llama_cpp.llama_grammar import JSON_GBNF

from src.poc_python import Stage
from src.poc_python.input_utils import read_prompt_from_resource
from src.poc_python.text_processors.processors import LlamaWrapper, Processor
from src.poc_python.markup import DEFAULT_MARKUP


# TODO should inherit Processor
class QuestionGenerator(Processor):
    # TODO try to write a custom grammar for the output?
    # TODO correct_answer should be the answer itself instead of the number
    __prompt = read_prompt_from_resource("generate_question_json")

    def __init__(self):
        self.model = LlamaWrapper(stage=Stage.QUESTION)


    def process(self, chapter_content: str, **kwargs) -> dict:
        """
        :param chapter_content: The content of the chapter for which the question is to be generated
        :param kwargs: generaL_subject: str, key_point: str
        """
        return self.model.generate(
            prompt=self.__format_prompt(self.__prompt, chapter_content=chapter_content, **kwargs),
            grammar=LlamaGrammar.from_string(JSON_GBNF) # output in json
        )

    @staticmethod
    def __format_prompt(prompt: str, general_subject: str, key_point: str, chapter_content: str):
        return (prompt
                .replace("<SUBJECT_NAME>", general_subject)
                .replace(DEFAULT_MARKUP.topic_content, chapter_content)
                .replace(DEFAULT_MARKUP.topic_name, key_point)) # TODO jinja
