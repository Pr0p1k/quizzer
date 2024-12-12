from src.poc_python import Stage, CONFIG
from src.poc_python.utils.class_utils import find_subclass_by_name
from src.poc_python.text_processors import * # force load all Processor's children

__ALLOCATED_PROCESSORS = dict() # TODO do deallocation in the end


def get_processor_lazy(stage: str) -> processors.Processor:
    if not __ALLOCATED_PROCESSORS.get(stage):
        processor_type_name = str(CONFIG.__getattr__(stage).approach)

        cls = find_subclass_by_name(processors.Processor, processor_type_name)
        if not cls:
            raise TypeError(f"Processor type '{processor_type_name}' not found")

        __ALLOCATED_PROCESSORS[stage] = cls()
    return __ALLOCATED_PROCESSORS[stage]
