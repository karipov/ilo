"""
Utility functions
"""
import re
from typing import List, Union

from telethon import Button


def keyboard_gen(
    labels: List[List[str]],
    data: List[List[str]]
) -> List[List[Button]]:
    """
    Generates telethon-compatible keyboards
    """
    w, h = len(labels[0]), len(labels)
    # uninitialized matrix
    button_matrix = [[None for x in range(w)] for x in range(h)]

    for i in range(h):
        for j in range(w):
            button_matrix[i][j] = Button.inline(
                labels[i][j], data[i][j]
            )

    return button_matrix


def expand_text(unexpanded: str, expand_keys: dict):
    """ Text expansion """

    def traverse_dict(keys: List, tree: dict) -> Union[dict, str]:
        """ Recursive dictionary traversal given a list of nodes (keys) """
        if len(keys) == 0:
            return tree
        else:
            key = keys.pop(0)
            return traverse_dict(keys=keys, tree=tree[key])

    expressions = re.findall(r'\$.*?\$', unexpanded)
    substitute = list()

    for expression in expressions:
        expression = expression[1:-1].split(':')
        substitute.append(traverse_dict(expression, expand_keys))

    print(substitute)

    expanded = unexpanded
    for to_replace, with_replace in zip(expressions, substitute):
        expanded = expanded.replace(to_replace, with_replace)

    return expanded
