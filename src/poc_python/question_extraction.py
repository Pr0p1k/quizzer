from llm_wrapper import LLMWrapper
from src.poc_python.input_utils import read_prompt_from_resource
from src.poc_python.markup import DEFAULT_MARKUP


class QuestionExtractor:
    def __init__(self, n_ctx, **kwargs):

        self.model = LLMWrapper(n_ctx=n_ctx)

    __prompt = read_prompt_from_resource("extract_points.txt")
    # TODO hardcoded main title, do jinja templates

    def get_response(self, topic_name: str, topic_content: str) -> dict:

        return self.model.generate(
            prompt=self.format_prompt(QuestionExtractor.__prompt, topic_name, topic_content),
            max_tokens=300,
            temperature=0.8
        )

    def format_prompt(self, prompt: str, topic_name: str, topic_content: str):
        return (prompt
                .replace(DEFAULT_MARKUP.topic_name, topic_name)
                .replace(DEFAULT_MARKUP.topic_content, topic_content))