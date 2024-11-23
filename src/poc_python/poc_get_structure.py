from src.poc_python.llm_wrapper import LLMWrapper

class StructureByLLM:
    def __init__(self):

        self.model = LLMWrapper()

    __prompt = open("/Users/user/IdeaProjects/quizzer_poc/src/main/resources/prompts/get_text_structure.txt").read() # TODO

    def get_response(self) -> dict:
        with open("/Users/user/IdeaProjects/quizzer_poc/src/main/resources/sample_book_serbia_short.txt") as file:
            file_content = file.readlines()

        return self.model.generate(
            prompt=StructureByLLM.__prompt + "\n".join(file_content),
            max_tokens=160,
            temperature=0.8
        )


    def get_structure(self) -> str:
        response = self.get_response()

        return response["choices"][0]["text"]