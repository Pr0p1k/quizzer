from importlib import resources

from src.poc_python.llm_wrapper import LLMWrapper
from src.poc_python.input_utils import read_prompt_from_resource


class LLMSplitMarkup:
    def __init__(self, limit: int):
        self.limit = int(limit * 2.5)
        self.model = LLMWrapper(n_ctx=self.limit)

    __prompt = read_prompt_from_resource("split_text.txt")

    def get_response(self, text: str) -> dict:
        return self.model.generate(
            prompt=LLMSplitMarkup.__prompt + text,
            max_tokens=self.limit,
            temperature=0
        )
