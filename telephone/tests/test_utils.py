""" Test utilities. """
import random
from typing import List

import hypothesis.strategies as st

from telephone.all_wordifications import insert_dashes, get_country_code_and_base
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


def generate_spaced_phoneword(data) -> str:
    """ Generates an arbitrary phoneword given a hypothesis data object. """
    # TODO: Add format.

    spacer = "&"
    spaced_phoneword = ""
    country_code, base_format = get_country_code_and_base(TEST_FORMAT)
    dashless_format = base_format.replace("-", "")
    remaining_length = len(dashless_format)
    while remaining_length > 0:
        seed = random.randint(0, 10000)
        if seed % 2 == 0:
            segment = data.draw(st.from_regex(r"[0-9]+", fullmatch=True))
        else:
            segment = data.draw(st.from_regex(r"[A-Z]+", fullmatch=True))
        segment = segment[:remaining_length]
        if spaced_phoneword and spaced_phoneword[0].isalpha():
            spaced_phoneword = segment + spacer + spaced_phoneword
        else:
            spaced_phoneword = segment + spaced_phoneword
        remaining_length -= len(segment)
        print(spaced_phoneword)
    assert len(spaced_phoneword.replace(spacer, "")) == len(dashless_format)
    spaced_phoneword = country_code + spacer + spaced_phoneword

    return spaced_phoneword
