import json
import re

from markup import DEFAULT_MARKUP

def get_output(response: dict) -> str:
    if "choices" not in response: # TODO follow some structure
        return response["output"]
    return response["choices"][0]["text"]


def split_outline_list(outline: str) -> list:
    return re.sub(r'\d+\. ', '', outline).split("\n")


def get_key_points_list_json(json_str: str) -> list[dict]:
    return json.loads(json_str)


# TODO choose split logic corresponding to the prompt strategy
def split_markup_text(text: str, tags = DEFAULT_MARKUP) -> list[tuple]:
    if tags.text_content_start not in text or tags.text_content_end not in text:
        raise Exception("Invalid markup - no start/end tags")

    topic_name_count = text.count(tags.topic_name)
    topic_content_count = text.count(tags.topic_content)
    if topic_name_count != topic_content_count or topic_name_count == 0:
        raise Exception(f"Invalid markup - topic names: {topic_name_count}, topic contents: {topic_content_count}")

    names_and_topics = []

    current_index = 0

    while True:
        name_index = text.find(tags.topic_name, current_index) # start of the current topic
        content_index = text.find(tags.topic_content, current_index + len(tags.topic_name))

        next_name_index = text.find(tags.topic_name, content_index) # end of the current topic
        name = text[name_index + len(tags.topic_name): content_index].strip()
        if next_name_index == -1:
            content = text[content_index + len(tags.topic_content): text.find(tags.text_content_end)]
            names_and_topics.append((name, content))
            break

        content = text[content_index + len(tags.topic_content): next_name_index]
        names_and_topics.append((name, content))

        current_index = next_name_index

    return names_and_topics


def split_markup_text_json(json_str: str) -> list[dict]:
    return json.loads(json_str)