from llama_cpp import LlamaGrammar
from llama_cpp.llama_grammar import JSON_ARR_GBNF

from src.poc_python import Stage, JINJA
from src.poc_python.text_processors.processors import LlamaWrapper, Processor


class LLMKeyPointsExtractor(Processor):
    __prompt_template = JINJA.get_template("extract_points_json.txt")

    def __init__(self):
        self.model = LlamaWrapper(stage=Stage.KEY_POINTS)


    def process(self, chapter_content: str, **kwargs) -> dict:
        """
        :param chapter_content: chapter content
        :param kwargs: general_subject: str, chapter_name: str
        """

        return self.model.generate(
            prompt=self.__prompt_template.render(chapter_content=chapter_content, **kwargs),
            grammar=LlamaGrammar.from_string(JSON_ARR_GBNF) # TODO put it into config
        )
