""" Tests for the ``words_to_number()`` function. """
import json

import hypothesis.strategies as st
from hypothesis import given

from telephone.words_to_number import words_to_number
from telephone.tests.test_utils import find_occurrences, generate_phoneword
from telephone.tests.test_constants import TEST_FORMAT


@given(st.data())
def test_words_to_number_places_dashes_correctly(data) -> None:
    """
    Tests that we generate numbers with the dashes in the right place.

    Parameters
    ----------
    phoneword : ``str``.
        A string consisting of dashes, numbers, and alpha characters. Always starts
        with ``1`` and ends with an alphanumeric character. At most 1 dash in a row.
        e.g. ``1-ALPHA-54792-BRAVO``.
    """
    phoneword = generate_phoneword(data)

    # Read in the letter mapping.
    with open("telephone/settings/mapping.json", "r") as mapping:
        letter_map = json.load(mapping)

    # Translate to a number.
    number = words_to_number(phoneword, letter_map)
    assert find_occurrences(number, "-") == find_occurrences(TEST_FORMAT, "-")


@given(st.data())
def test_words_to_number_output_is_numeric(data) -> None:
    """
    Tests that the function doesn't return anything with letters in it.

    Parameters
    ----------
    phoneword : ``str``.
        A string consisting of dashes, numbers, and alpha characters. Always starts
        with ``1`` and ends with an alphanumeric character. At most 1 dash in a row.
        e.g. ``1-ALPHA-54792-BRAVO``.
    """
    phoneword = generate_phoneword(data)
    # Read in the letter mapping.
    with open("telephone/settings/mapping.json", "r") as mapping:
        letter_map = json.load(mapping)
    number = words_to_number(phoneword, letter_map)
    number_no_dashes = number.replace("-", "")
    assert number_no_dashes.isnumeric()


@given(st.data())
def test_words_to_number_yields_correct_length(data) -> None:
    """
    Tests that we generate numbers with the correct length.

    Parameters
    ----------
    phoneword : ``str``.
        A string consisting of dashes, numbers, and alpha characters. Always starts
        with ``1`` and ends with an alphanumeric character. At most 1 dash in a row.
        e.g. ``1-ALPHA-54792-BRAVO``.
    """
    phoneword = generate_phoneword(data)
    # Read in the letter mapping.
    with open("telephone/settings/mapping.json", "r") as mapping:
        letter_map = json.load(mapping)
    number = words_to_number(phoneword, letter_map)
    assert len(number) == len(TEST_FORMAT)
