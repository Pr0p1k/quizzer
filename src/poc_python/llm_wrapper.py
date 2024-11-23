from llama_cpp import Llama

class LLMWrapper:

    def __init__(self, n_ctx = 512, **kwargs): # TODO pass args
        self.model = Llama(
            model_path="/Users/user/Library/Application Support/nomic.ai/GPT4All/Meta-Llama-3-8B-Instruct.Q4_0.gguf",
            n_ctx=n_ctx,
            **kwargs
        )

    def generate(self, prompt, max_tokens, temperature):
        response = self.model(prompt, max_tokens=max_tokens, temperature=temperature, repeat_penalty=1.2)

        return response
