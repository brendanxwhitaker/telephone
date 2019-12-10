""" Test utilities. """
import random
from typing import List

import hypothesis.strategies as st

from telephone.all_wordifications import insert_dashes
from telephone.tests.test_constants import TEST_FORMAT


def find_occurrences(string: str, char: str) -> List[int]:
    """ Does what its name sugggests. """
    return [i for i, letter in enumerate(string) if letter == char]


def generate_phoneword(data) -> str:
    """ Generates an arbitrary phoneword given a hypothesis data object. """
    # TODO: Add format.

    dashless_phoneword = ""
    dashless_format = TEST_FORMAT.replace("-", "")
    while len(dashless_phoneword) < len(dashless_format):
        seed = random.randint(0, 10000)
        remaining_length = len(dashless_format) - len(dashless_phoneword)
        if seed % 2 == 0:
            segment = data.draw(st.from_regex(r"[0-9]+", fullmatch=True))
        else:
            segment = data.draw(st.from_regex(r"[A-Z]+", fullmatch=True))
        segment = segment[:remaining_length]
        dashless_phoneword = segment + dashless_phoneword
    assert len(dashless_phoneword) == len(dashless_format)

    # Throw in dashes.
    phoneword = insert_dashes(dashless_phoneword)

    return phoneword
