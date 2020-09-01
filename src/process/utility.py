"""
Utility functions
"""
import re
from typing import List, Union

from telethon import Button

from config import REPLIES


def check_fsm(user):
    if user.fsm_state in REPLIES['FSM'].keys():
        return True

    return False


def keyboard_gen(
    labels: List[List[str]],
    data: List[List[str]],
    kind: Button = Button.inline,
    language: str = None
) -> List[List[Button]]:
    """
    Generates telethon-compatible keyboards
    """
    if type(labels) == dict:  # if they have a language property
        labels = labels[language]
    # uninitialized matrix
    button_matrix = [[None for j in range(len(i))] for i in labels]

    for i in range(len(labels)):
        for j in range(len(labels[i])):
            button_matrix[i][j] = kind(
                labels[i][j], data[i][j]
            )

    return button_matrix


def expand_text(unexpanded: str, expand_keys: dict, language: str) -> str:
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
        substitute.append(traverse_dict(expression, expand_keys)[language])

    expanded = unexpanded
    for to_replace, with_replace in zip(expressions, substitute):
        expanded = expanded.replace(to_replace, with_replace)

    return expanded


def share_link_gen(link: str) -> str:
    return f"https://t.me/share/url?url={link}"
