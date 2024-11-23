from llm_wrapper import LLMWrapper
from src.poc_python.input_utils import read_prompt_from_resource
from src.poc_python.markup import DEFAULT_MARKUP


class QuestionGenerator:
    def __init__(self, n_ctx, **kwargs):

        self.model = LLMWrapper(n_ctx=n_ctx)

    __prompt = read_prompt_from_resource("generate_question.txt")
    # TODO hardcoded main title, do jinja templates

    def get_response(self, outline: str, topic_content: str) -> dict:

        return self.model.generate(
            prompt=self.format_prompt(QuestionGenerator.__prompt, outline, topic_content),
            max_tokens=300,
            temperature=0.95
        )

    def format_prompt(self, prompt: str, outline: str, topic_content: str):
        return (prompt
                .replace(DEFAULT_MARKUP.topic_content, topic_content)
                .replace(DEFAULT_MARKUP.topic_name, outline)) # TODO
