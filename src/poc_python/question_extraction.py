from llm_wrapper import LLMWrapper
from src.poc_python.markup import DEFAULT_MARKUP


class QuestionExtractor:
    def __init__(self, n_ctx, **kwargs):

        self.model = LLMWrapper(n_ctx)

    __prompt = open("/Users/user/IdeaProjects/quizzer_poc/src/main/resources/prompts/extract_points.txt").read()
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


    def get_output(self, topic_name, topic_content) -> str:
        response = self.get_response(topic_name, topic_content)

        return response["choices"][0]["text"]