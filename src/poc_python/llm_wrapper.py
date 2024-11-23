from llama_cpp import Llama

class LLMWrapper:

    def __init__(self, **kwargs):
        self.model = Llama(
            model_path="/Users/user/Library/Application Support/nomic.ai/GPT4All/Meta-Llama-3-8B-Instruct.Q4_0.gguf",
            **kwargs
        )

    def generate(self, prompt: str, **kwargs):
        response = self.model(prompt, repeat_penalty=1.2, **kwargs)

        return response
