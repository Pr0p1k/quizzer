from importlib import resources
from os.path import join

from src.poc_python import ROOT_DIR, SAMPLE_INPUTS


def read_prompt_from_resource(name: str) -> str:
    with open(resources.files("src.poc_python") / "prompts" / (name + ".txt")) as file: # TODO weird behavior with modules
        return file.read()


def read_file_from_sample_inputs(file_name: str) -> str:
    with open(join(ROOT_DIR, SAMPLE_INPUTS, file_name)) as file:
        return file.read()
