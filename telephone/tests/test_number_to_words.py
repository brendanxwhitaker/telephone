""" Tests for the ``number_to_words()`` function. """
from typing import List, Set

import hypothesis.strategies as st
from hypothesis import given

from telephone.number_to_words import number_to_words
from telephone.words_to_number import words_to_number
from telephone.tests.test_constants import (
    US_MAP,
    US_NUMBER,
    US_ALPHANUMERIC,
    UPPERCASE_ALPHA,
    LOWERCASE_ALPHA,
)

# pylint: disable=bad-continuation


@given(
    st.from_regex(US_NUMBER, fullmatch=True),
    st.sets(st.from_regex(LOWERCASE_ALPHA, fullmatch=True)),
)
def test_number_to_words_generates_alphanumerics(number: str, vocab: Set[str]) -> None:
    """
    Tests generation from US phone numbers yields alphanumberic substitutions.

    Parameters
    ----------
    number : ``str``.
        A valid US phone number with country code and dashes.
    vocab : ``Set[str]``.
        A set of strings consisting of lowercase alpha characters only. All nonempty.
    """
    phoneword = number_to_words(number, vocab, US_MAP)
    phoneword_no_dashes = phoneword.replace("-", "")
    assert US_ALPHANUMERIC.match(phoneword_no_dashes)


@given(
    st.from_regex(US_NUMBER, fullmatch=True),
    st.sets(st.from_regex(LOWERCASE_ALPHA, fullmatch=True)),
)
def test_number_to_words_stays_in_vocabulary(number: str, vocab: Set[str]) -> None:
    """
    Tests that substitutions made are valid words from the given vocabulary.

    Parameters
    ----------
    number : ``str``.
        A valid US phone number with country code and dashes.
    vocab : ``Set[str]``.
        A set of strings consisting of lowercase alpha characters only. All nonempty.
    """
    phoneword = number_to_words(number, vocab, US_MAP)
    matches: List[str] = UPPERCASE_ALPHA.findall(phoneword)

    found_invalid = False
    for match in matches:
        if match.lower() not in vocab:
            raise ValueError("Token '%s' not found in vocab." % match)


@given(
    st.from_regex(US_NUMBER, fullmatch=True),
    st.sets(st.from_regex(LOWERCASE_ALPHA, fullmatch=True)),
)
def test_number_to_words_is_left_inverse_of_words_to_number(
    number: str, vocab: Set[str]
) -> None:
    """
    Tests that the phoneword generated is mapped back to ``number`` by
    ``words_to_number()``. This tests that ``number_to_words`` behaves as expected
    given that ``words_to_number()`` is correct.

    Parameters
    ----------
    number : ``str``.
        A valid US phone number with country code and dashes.
    vocab : ``Set[str]``.
        A set of strings consisting of lowercase alpha characters only. All nonempty.
    """
    phoneword = number_to_words(number, vocab, US_MAP)
    resultant_number = words_to_number(phoneword, US_MAP)
    assert number == resultant_number
