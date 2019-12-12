""" Tests for the ``words_to_number()`` function. """
import re
import datetime
from typing import Set

import hypothesis.strategies as st
from hypothesis import given, settings

from telephone.utils import compute_vocab_map
from telephone.words_to_number import words_to_number
from telephone.all_wordifications import all_wordifications
from telephone.tests.test_constants import (
    US_NUMBER,
    LOWERCASE_ALPHA,
    US_LETTER_MAP,
    US_FORMAT,
)


@settings(deadline=datetime.timedelta(milliseconds=20000))
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
    vocab_map = compute_vocab_map(vocab, US_LETTER_MAP)
    phonewords: Set[str] = all_wordifications(number, US_FORMAT, vocab_map)
    found_mismatch = False
    for word in phonewords:
        translated_number = words_to_number(word, US_LETTER_MAP)
        if translated_number != number:
            found_mismatch = True
            raise ValueError(
                "Result '%s' does not match '%s'." % (translated_number, number)
            )

    assert not found_mismatch


@settings(deadline=datetime.timedelta(milliseconds=20000))
@given(
    st.from_regex(US_NUMBER, fullmatch=True),
    st.sets(st.from_regex(LOWERCASE_ALPHA, fullmatch=True)),
)
def test_all_wordifications_only_uses_vocab_words(number: str, vocab: Set[str]) -> None:
    """
    Tests that if we generate all phonewords with ``all_wordifications()`` that all the
    letterstrings in each phoneword are words from the vocabulary.

    Parameters
    ----------
    number : ``str``.
        A valid US phone number with country code and dashes.
    vocab : ``Set[str]``.
        A set of strings consisting of lowercase alpha characters only. All nonempty.
    """
    vocab_map = compute_vocab_map(vocab, US_LETTER_MAP)
    phonewords: Set[str] = all_wordifications(number, US_FORMAT, vocab_map)
    found_mismatch = False
    for word in phonewords:
        alpha_tokens = re.findall(r"[A-Z]+", word)
        for token in alpha_tokens:
            if token.lower() not in vocab:
                raise ValueError("Token '%s' from '%s' not in vocab." % (token, word))


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
    vocab_map = compute_vocab_map(vocab, US_LETTER_MAP)
    phonewords: Set[str] = all_wordifications(number, US_FORMAT, vocab_map)
    for word in phonewords:
        if word.upper() != word:
            raise ValueError("Word '%s' contains lowercase letters." % word)


def test_all_wordifications_manual() -> None:
    """ Manual check. """
    number = "0-000-000"
    numformat = "0-000-000"

    with open("data/google-10000-english.txt", "r") as vocab_file:
        vocab = set(vocab_file.readlines())
        vocab = {token.strip() for token in vocab}
    vocab_map = compute_vocab_map(vocab, US_LETTER_MAP)
    phonewords: Set[str] = all_wordifications(number, numformat, vocab_map)
    assert phonewords
    for word in phonewords:
        translated_number = words_to_number(word, US_LETTER_MAP, numformat)
        if translated_number != number:
            found_mismatch = True
            raise ValueError(
                "Result '%s' does not match '%s'." % (translated_number, number)
            )
