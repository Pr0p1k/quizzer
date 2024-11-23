from dataclasses import dataclass


@dataclass
class Markup:
    text_content_start: str
    topic_name: str
    topic_content: str
    text_content_end: str

DEFAULT_MARKUP = Markup("<TEXT_CONTENT_START>", "<TOPIC_NAME>", "<TOPIC_CONTENT>", "<TEXT_CONTENT_END>")
