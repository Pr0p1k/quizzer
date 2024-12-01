from typing import Any


def find_subclass_by_name(cls, name) -> type | None:
    subs = cls.__subclasses__()

    # breadth-first search
    while len(subs) > 0:
        sub_cls = subs.pop(0)
        if sub_cls.__name__ == name:
            return sub_cls
        subs.extend(sub_cls.__subclasses__())

    return None