from llama_cpp import LlamaGrammar
from llama_cpp.llama_grammar import JSON_ARR_GBNF

from src.poc_python import Stage
from src.poc_python.utils.input_utils import read_prompt_from_resource
from src.poc_python.text_processors.processors import LlamaWrapper, Processor
from src.poc_python.markup import DEFAULT_MARKUP

class LLMKeyPointsExtractor(Processor):
    __prompt = read_prompt_from_resource("extract_points_json")

    def __init__(self):
        self.model = LlamaWrapper(stage=Stage.KEY_POINTS)


    def process(self, chapter_content: str, **kwargs) -> dict:
        """
        :param chapter_content: chapter content
        :param kwargs: general_subject: str, chapter_name: str
        """

        return self.model.generate(
            prompt=self.__format_prompt(LLMKeyPointsExtractor.__prompt, **kwargs, chapter_content=chapter_content),
            grammar=LlamaGrammar.from_string(JSON_ARR_GBNF) # TODO put it into config
        )

    def __format_prompt(self, prompt: str, general_subject: str, chapter_name: str, chapter_content: str):
        return (prompt
                .replace("<SUBJECT_NAME>", general_subject) # TODO jinja
                .replace(DEFAULT_MARKUP.topic_name, chapter_name)
                .replace(DEFAULT_MARKUP.topic_content, chapter_content))
