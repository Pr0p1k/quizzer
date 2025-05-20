import importlib

from langchain_community.llms.llamacpp import LlamaCpp
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI


from src.poc_python import CONFIG
from src.poc_python.text_processors import processors, PROCESSOR_MODULE

__ALLOCATED_PROCESSORS = dict() # TODO do deallocation in the end


def get_processor_lazy(stage: str) -> processors.Processor:
    if not __ALLOCATED_PROCESSORS.get(stage):
        processor_type_name = str(CONFIG.__getattr__(stage).approach)

        module_name = PROCESSOR_MODULE[processor_type_name]
        cls = getattr(importlib.import_module("text_processors." + module_name), processor_type_name)
        if not cls:
            raise TypeError(f"Processor type '{processor_type_name}' not found")

        __ALLOCATED_PROCESSORS[stage] = cls()
    return __ALLOCATED_PROCESSORS[stage]

def get_llm() -> BaseLanguageModel:
    llm_conf = dict(getattr(CONFIG, "llm_global", {}))
    llm_type = llm_conf.pop("type", None)
    if llm_type == "local":
        # avoid top-level import, llama might not be installed
        from llama_cpp.llama_grammar import JSON_ARR_GBNF

        return LlamaCpp(**llm_conf, grammar=JSON_ARR_GBNF)
    if llm_type == "openai":
        return ChatOpenAI(
            *llm_conf,
            model_kwargs={"response_format": {"type": "json_object"}}
        )

    raise Exception(f"LLM not found: type={llm_type}, conf={llm_conf}")