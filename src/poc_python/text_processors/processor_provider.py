from src.poc_python import Stage, CONFIG
from src.poc_python.text_processors.processors import Processor
from src.poc_python.utils.class_utils import find_subclass_by_name

__ALLOCATED_PROCESSORS = dict() # TODO do deallocation in the end


def get_processor_lazy(stage: Stage) -> Processor:
    if not __ALLOCATED_PROCESSORS.get(stage):
        processor_type_name = str(CONFIG.__getattr__(stage.value).approach)

        cls = find_subclass_by_name(Processor, processor_type_name)
        if not cls:
            raise TypeError(f"Processor type '{processor_type_name}' not found")

        __ALLOCATED_PROCESSORS[stage] = cls()
    return __ALLOCATED_PROCESSORS[stage]
