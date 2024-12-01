from typing import Any

from src.poc_python import Stage
from src.poc_python.text_processors.chapter_splitter import SpacyAndRegexSplitter
from src.poc_python.text_processors.processors import LlamaWrapper, Processor
from src.poc_python.text_processors.key_points_extractor import KeyPointsExtractor
from src.poc_python.text_processors.question_generator import QuestionGenerator

__ALLOCATED_PROCESSORS = dict()


def get_processor_lazy(stage: Stage) -> Processor:
    if not __ALLOCATED_PROCESSORS.get(stage):
        kwargs = {} # TODO get from a config for the stage
        if stage == Stage.MARKUP: # TODO move stage to processor mapping somewhere else. Should I?
            processor = SpacyAndRegexSplitter()
        elif stage == Stage.KEY_POINTS:
            processor = KeyPointsExtractor()
        else:
            processor = QuestionGenerator()
        __ALLOCATED_PROCESSORS[stage] = processor
    return __ALLOCATED_PROCESSORS[stage]