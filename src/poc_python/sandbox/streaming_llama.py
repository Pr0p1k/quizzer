import asyncio

from llama_cpp import LlamaGrammar
from llama_cpp.llama_grammar import JSON_GBNF

from src.poc_python.llm_wrapper import LLMWrapper

model = LLMWrapper(n_ctx=30000)

__prompt = open("/prompts/split_text.txt").read()  # TODO

text = open("/sample_inputs/sample_book_president_serbia.txt").read()

results = []

for output in model.generate(
        prompt=__prompt + text[:10000],
        max_tokens=30000,
        temperature=0,
        stream=True,
        grammar=LlamaGrammar(_grammar=JSON_GBNF)
):
    print(output["choices"][0]["text"], end="", flush=True)
    results.append(output["choices"][0]["text"])
