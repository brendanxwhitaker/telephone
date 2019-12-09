""" Tests for the ``words_to_number()`` function. """
import json
from typing import Set

import hypothesis.strategies as st
from hypothesis import given

from telephone.all_wordifications import all_wordifications, compute_vocab_map
from telephone.words_to_number import words_to_number
from telephone.tests.test_constants import US_NUMBER, LOWERCASE_ALPHA


@given(
    st.from_regex(US_NUMBER, fullmatch=True),
    st.sets(st.from_regex(LOWERCASE_ALPHA, fullmatch=True)),
)
def test_all_wordifications_output_is_valid(number: str, vocab: Set[str]) -> None:
    """
    Tests that if we first generate all phonewords with ``all_wordifications()`` that
    ``words_to_number()`` maps all of them back to the origin number. This relies on
    the correctness of ``word_to_number()``.

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
        translated_number = words_to_number(word, letter_map)
        if translated_number != number:
            found_mismatch = True
            raise ValueError(
                "Result '%s' does not match '%s'." % (translated_number, number)
            )

    assert not found_mismatch


@given(
    st.from_regex(US_NUMBER, fullmatch=True),
    st.sets(st.from_regex(LOWERCASE_ALPHA, fullmatch=True)),
)
def test_all_wordifications_is_uppercase(number: str, vocab: Set[str]) -> None:
    """
    Does as the test function name suggests.

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
    for word in phonewords:
        if word.upper() != word:
            raise ValueError("Word '%s' contains lowercase letters." % word)
