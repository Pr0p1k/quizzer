from abc import ABC, abstractmethod

from src.poc_python import Stage, CONFIG


class Processor(ABC):

    @abstractmethod
    def process(self, input_text: str, **kwargs) -> dict: # TODO remove the first arg and leave only the kwargs
        """
        Get the input text and produce the output based on the logic of implemented processor
        :param input_text: The input
        :param kwargs: additional arguments to LLM or other underlying processor
        :return: dictionary with the output and meta info from LLM or other processor # TODO define structure
        """
        ...


class LlamaWrapper:
    """
    A wrapper class to use local LLama
    """

    def __init__(self, stage: Stage):
        # avoid top-level import if no llama is installed
        from llama_cpp import Llama, LlamaGrammar

        global_conf = dict(CONFIG.__getattr__(stage.value))
        self.prompting_conf = dict(CONFIG.__getattr__("prompting").__getattr__(stage.value))
        self.model = Llama(**global_conf)

    def generate(self, prompt: str, grammar: "LlamaGrammar") -> dict:
        response = self.model(prompt, **self.prompting_conf, grammar=grammar)  # TODO grammar should be put into config

        return response
