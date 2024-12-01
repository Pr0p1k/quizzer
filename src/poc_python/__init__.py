import os
from enum import Enum
from os.path import join
from pathlib import Path

from joblib import Memory
from dynaconf import Dynaconf

# path to project root
ROOT_DIR = Path(__file__).parents[2]

SAMPLE_INPUTS = "sample_inputs"
SAMPLE_OUTPUTS = "sample_outputs"


class Stage(Enum):
    """
    Represents the Stage of quiz creation.
    Markup - read the input text and set boundaries of chapters
    Key points - outline key points of each chapter
    Question - generate quiz questions on the key points within chapters.
    """
    MARKUP = "markup"
    KEY_POINTS = "key_points"
    QUESTION = "question"


# cache
CACHE_LOCATION = join(ROOT_DIR, "generated_quizzes")
MEM = Memory(location=CACHE_LOCATION)

# envs
BYPASS_CACHE = os.environ.get("QUIZZER_BYPASS_CACHE") not in [None, ""]

# config
CONFIG = Dynaconf(settings_files=["llms.toml", "quiz.toml"])
