import os
from enum import Enum
from os.path import join
from pathlib import Path

from dynaconf import Dynaconf
from jinja2 import Environment, PackageLoader, select_autoescape
from joblib import Memory

# path to project root
ROOT_DIR = Path(__file__).parents[2]

SAMPLE_INPUTS = "sample_inputs"
SAMPLE_OUTPUTS = "sample_outputs"
GENERATED_QUIZZES = "generated_quizzes"

STAGES = {
    "LANGGRAPH_SPLIT": "langgraph_split",
    "LANGGRAPH_QUESTIONS": "langgraph_questions",
    "LANGGRAPH_ENRICH_QUESTION": "langgraph_enrich_question"
}

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
MEM = Memory(location=CACHE_LOCATION, verbose=0)

# envs
BYPASS_CACHE = os.environ.get("QUIZZER_BYPASS_CACHE") not in [None, ""]

# config
CONFIG = Dynaconf(settings_files=["llms.toml", "quiz.toml", "debug.toml"])

# jinja
JINJA = Environment(loader=PackageLoader("src.poc_python", "prompts"), autoescape=select_autoescape())