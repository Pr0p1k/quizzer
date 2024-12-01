import json
import re

from src.poc_python import Stage
from src.poc_python.text_processors.processors import Processor

from llama_cpp import LlamaGrammar
from llama_cpp.llama_grammar import JSON_ARR_GBNF

from src.poc_python.input_utils import read_prompt_from_resource
from src.poc_python.text_processors.processors import LlamaWrapper

class SpacyAndRegexSplitter(Processor):
    def __init__(self):
        pass # TODO

    def process(self, input_text: str, **kwargs) -> dict:
        # Assuming chapter titles are standalone lines
        # TODO choose proper upper limit of word count (5)
        chapter_title_pattern = re.compile(r"^(?:[A-Za-z0-9]+(?:\s[A-Za-z0-9]+){0,5})$", re.MULTILINE) # TODO optimize the re

        chapter_matches = list(chapter_title_pattern.finditer(input_text))

        # extract chapters and their names
        chapters_dicts = []
        for i in range(len(chapter_matches)):
            chapter_name_start = chapter_matches[i].start()
            chapter_name_end = chapter_matches[i].end()
            chapter_content_start = chapter_name_end + 1
            chapter_content_end = chapter_matches[i + 1].start() if i + 1 < len(chapter_matches) else len(input_text)
            chapter_name = input_text[chapter_name_start:chapter_name_end].strip()
            chapter_content = input_text[chapter_content_start:chapter_content_end].strip()
            chapters_dicts.append({"chapter_name": chapter_name, "chapter_content": chapter_content})

        chapter_json = json.dumps(chapters_dicts)

        return {"output": chapter_json}


class LLMSplitMarkup(Processor):
    __prompt = read_prompt_from_resource("split_text_json") # TODO consider subchapters

    def __init__(self):
        self.model = LlamaWrapper(stage=Stage.MARKUP)


    def process(self, input_text: str, **kwargs) -> dict:
        return self.model.generate(
            prompt=LLMSplitMarkup.__prompt + input_text,
            grammar=LlamaGrammar.from_string(JSON_ARR_GBNF) # TODO put it into config
        )