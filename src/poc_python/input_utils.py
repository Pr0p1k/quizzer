from importlib import resources


def read_prompt_from_resource(name: str) -> str:
    with open(resources.files("src.poc_python") / "prompts" / name) as file: # TODO weird behavior with modules
        return file.read()