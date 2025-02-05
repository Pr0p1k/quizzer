import importlib
import inspect

from langchain_community.llms.llamacpp import LlamaCpp
from langchain_core.language_models import BaseLLM
from langchain_openai import OpenAI

from src.poc_python import Stage, CONFIG
from src.poc_python.text_processors import processors, PROCESSOR_MODULE
from src.poc_python.utils.class_utils import find_subclass_by_name

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

def get_llm() -> BaseLLM:
    llm_conf = dict(getattr(CONFIG, "llm_global", {}))
    llm_type = llm_conf.pop("type", None)
    if llm_type == "local":
        return LlamaCpp(**llm_conf)
    if llm_type == "openai":
        return OpenAI(**llm_conf)

    raise Exception(f"LLM not found: type={llm_type}, conf={llm_conf}")