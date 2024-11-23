from llm_wrapper import LLMWrapper
from src.poc_python.markup import DEFAULT_MARKUP


class QuestionGenerator:
    def __init__(self, n_ctx, **kwargs):

        self.model = LLMWrapper(n_ctx)

    __prompt = open("/Users/user/IdeaProjects/quizzer_poc/src/main/resources/prompts/generate_question.txt").read()
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
