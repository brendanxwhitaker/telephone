""" Tests for the ``words_to_number()`` function. """
import json
from typing import Set

import pytest # type: ignore
import hypothesis.strategies as st
from hypothesis import given, assume

from telephone.words_to_number import words_to_number
from telephone.all_wordifications import all_wordifications, compute_vocab_map
from telephone.tests.test_utils import find_occurrences
from telephone.tests.test_constants import (
    PHONEWORD,
    US_NUMBER,
    LOWERCASE_ALPHA,
    TEST_FORMAT,
)


@pytest.mark.skip
@given(
    st.from_regex(US_NUMBER, fullmatch=True),
    st.sets(st.from_regex(LOWERCASE_ALPHA, fullmatch=True)),
)
def test_words_to_number_matches_origin_number(number: str, vocab: Set[str]) -> None:
    """
    Tests that if we first generate all phonewords with ``all_wordifications()`` that
    ``words_to_number()`` maps all of them back to the origin number.

    Parameters
    ----------
    number : ``str``.
        A valid US phone number with country code and dashes.
    vocab : ``Set[str]``.
        A set of strings consisting of lowercase alpha characters only. All nonempty.
    """
    # Read in the letter mapping.
    with open("telephone/settings/mapping.json", "r") as mapping:
        letter_map = json.load(mapping)
    vocab_map = compute_vocab_map(vocab, letter_map)
    phonewords: Set[str] = all_wordifications(number, vocab_map)
    found_mismatch = False
    for word in phonewords:
        if words_to_number(word, letter_map) != number:
            found_mismatch = True

    assert not found_mismatch


@pytest.mark.skip
@given(st.from_regex(PHONEWORD, fullmatch=True))
def test_words_to_number_places_dashes_correctly(phoneword: str) -> None:
    """
    Tests that we generate numbers with the dashes in the right place.

    Parameters
    ----------
    phoneword : ``str``.
        A string consisting of dashes, numbers, and alpha characters. Always starts
        with ``1`` and ends with an alphanumeric character. At most 1 dash in a row.
        e.g. ``1-ALPHA-54792-BRAVO``.
    """
    # Read in the letter mapping.
    with open("telephone/settings/mapping.json", "r") as mapping:
        letter_map = json.load(mapping)
    assume(len(phoneword.replace("-", "")) == len(TEST_FORMAT))
    number = words_to_number(phoneword, letter_map)
    assert find_occurrences(number, "-") == find_occurrences(TEST_FORMAT, "-")


@pytest.mark.skip
@given(st.from_regex(PHONEWORD, fullmatch=True))
def test_words_to_number_output_is_numeric(phoneword: str) -> None:
    """
    Tests that the function doesn't return anything with letters in it.

    Parameters
    ----------
    phoneword : ``str``.
        A string consisting of dashes, numbers, and alpha characters. Always starts
        with ``1`` and ends with an alphanumeric character. At most 1 dash in a row.
        e.g. ``1-ALPHA-54792-BRAVO``.
    """
    # Read in the letter mapping.
    with open("telephone/settings/mapping.json", "r") as mapping:
        letter_map = json.load(mapping)
    assume(len(phoneword.replace("-", "")) == len(TEST_FORMAT))
    number = words_to_number(phoneword, letter_map)
    number_no_dashes = number.replace("-", "")
    assert number_no_dashes.isnumeric()


@pytest.mark.skip
@given(st.from_regex(PHONEWORD, fullmatch=True))
def test_words_to_number_yields_correct_length(phoneword: str) -> None:
    """
    Tests that we generate numbers with the correct length.

    Parameters
    ----------
    phoneword : ``str``.
        A string consisting of dashes, numbers, and alpha characters. Always starts
        with ``1`` and ends with an alphanumeric character. At most 1 dash in a row.
        e.g. ``1-ALPHA-54792-BRAVO``.
    """
    # Read in the letter mapping.
    with open("telephone/settings/mapping.json", "r") as mapping:
        letter_map = json.load(mapping)
    assume(len(phoneword.replace("-", "")) == len(TEST_FORMAT))
    number = words_to_number(phoneword, letter_map)
    assert len(number) == len(TEST_FORMAT)
