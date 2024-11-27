import os
from os.path import join
from pathlib import Path

from joblib import Memory

ROOT_DIR = Path(__file__).parents[2]

SAMPLE_INPUTS = "sample_inputs"
SAMPLE_OUTPUTS = "sample_outputs"

STAGES = ["markup", "key_points", "questions"]

CACHE_LOCATION = join(ROOT_DIR, "generated_quizzes")

mem = Memory(location=CACHE_LOCATION)

BYPASS_CACHE = os.environ.get("QUIZZER_BYPASS_CACHE") is not None