import json
import re
import time
from os import makedirs, listdir
from os.path import join, isdir



def get_output(response: dict) -> str:
    if "choices" not in response:  # TODO follow some structure
        return response["output"]
    return response["choices"][0]["text"]


def split_outline_list(outline: str) -> list:
    return re.sub(r'\d+\. ', '', outline).split("\n")


def get_key_points_list_json(json_str: str) -> list[dict]:
    return json.loads(json_str)

def split_markup_text_json(json_str: str) -> list[dict]:
    return json.loads(json_str)


def persist_generated(base_path: str, source_file_name: str, output: dict):
    """
    Save generated quiz to cache in <base_path>/<source_file_name>/<timestamp>.json
    """
    destination_dir = join(base_path, source_file_name)
    if not isdir(destination_dir):
        makedirs(destination_dir)

    with open(join(destination_dir, str(int(time.time())) + ".json"), "w") as output_file:
        output_file.write(json.dumps(output))


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
