import re


def get_output(response: dict) -> str:
    return response["choices"][0]["text"]

def split_outline_list(outline: str) -> list:
    return re.sub(r'\d+\. ', '', outline).split("\n")