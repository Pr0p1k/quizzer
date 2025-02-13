import json
import re
import time
from os import makedirs, listdir
from os.path import join, isdir
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage


def get_output(response: Any) -> str:
    if isinstance(response, dict):
        if "choices" not in response:  # TODO follow some structure
            return response["output"]
        return response["choices"][0]["text"]

    if isinstance(response, BaseMessage):
        return response.content


def split_outline_list(outline: str) -> list:
    return re.sub(r'\d+\. ', '', outline).split("\n")


def get_key_points_list_json(json_str: str) -> list[dict]:
    return json.loads(json_str)

def split_markup_text_json(json_content: Any) -> list[dict]:
    if isinstance(json_content, BaseMessage):
        json_string = json_content.content
    elif isinstance(json_content, str):
        json_string = json_content
    else:
        raise Exception(f"Invalid type of json content: {type(json_content)}")

    return json.loads(json_string)


def persist_generated(base_path: str, source_file_name: str, output: dict):
    """
    Save generated quiz to cache in <base_path>/<source_file_name>/<timestamp>.json
    """
    destination_dir = join(base_path, source_file_name)
    if not isdir(destination_dir):
        makedirs(destination_dir)

    with open(join(destination_dir, str(int(time.time())) + ".json"), "w") as output_file:
        output_file.write(json.dumps(output, default=lambda o: f'<{type(o)}_non-serializable>'))


def load_generated(base_path: str, source_file_name: str, version_offset: int = 0) -> dict:
    """
    Load previously generated quiz from cache
    :param base_path: path where the caches are stored
    :param source_file_name: source file name
    :param version_offset: if needed to load a non-latest version, offset is taken from the end
    :return: loaded json object
    """
    # names are <timestamp>.json, str comparison is fine due to slowly changing length of timestamps
    latest_version = max(listdir(join(base_path, source_file_name)))

    with open(join(base_path, source_file_name, latest_version)) as json_file:
        return json.loads(json_file.read())
