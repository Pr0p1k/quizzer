from src.poc_python.llm_wrapper import LLMWrapper

class LLMSplitMarkup:
    def __init__(self, limit: int):
        self.limit = int(limit * 2.5)
        self.model = LLMWrapper(self.limit)

    __prompt = open("/Users/user/IdeaProjects/quizzer_poc/src/main/resources/prompts/split_text.txt").read() # TODO

    def get_response(self, text: str) -> dict:
        return self.model.generate(
            prompt=LLMSplitMarkup.__prompt + text,
            max_tokens=self.limit,
            temperature=0.8
        )


    def get_structure(self, text: str) -> str:
        response = self.get_response(text)

        return response["choices"][0]["text"]