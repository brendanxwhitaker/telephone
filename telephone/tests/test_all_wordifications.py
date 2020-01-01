""" Tests for the ``words_to_number()`` function. """
import re
import datetime
from typing import Set, Dict

import hypothesis.strategies as st
from hypothesis import given, settings

from telephone.words_to_number import words_to_number
from telephone.all_wordifications import all_wordifications
from telephone.tests.test_constants import (
    US_NUMBER,
    LOWERCASE_ALPHA,
    US_LETTER_MAP,
    US_FORMAT,
)

# pylint: disable=bad-continuation


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
    phonewords: Set[str] = all_wordifications(number, US_FORMAT, vocab, US_LETTER_MAP)
    found_mismatch = False
    for word in phonewords:
        translated_number = words_to_number(word, US_FORMAT, US_LETTER_MAP)
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
    st.dictionaries(
        keys=st.from_regex(r"[A-Z]", fullmatch=True),
        values=st.from_regex(r"[0-9]", fullmatch=True),
        min_size=26,
    ),
)
def test_all_wordifications_output_handles_arbitrary_letter_map(
    number: str, vocab: Set[str], letter_map: Dict[str, str]
) -> None:
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
    letter_map : ``Dict[str, str]``.
        Maps uppercase English letters to digits.
    """
    phonewords: Set[str] = all_wordifications(number, US_FORMAT, vocab, letter_map)
    found_mismatch = False
    for word in phonewords:
        translated_number = words_to_number(word, US_FORMAT, letter_map)
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
    phonewords: Set[str] = all_wordifications(number, US_FORMAT, vocab, US_LETTER_MAP)
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
    phonewords: Set[str] = all_wordifications(number, US_FORMAT, vocab, US_LETTER_MAP)
    for word in phonewords:
        if word.upper() != word:
            raise ValueError("Word '%s' contains lowercase letters." % word)


def test_all_wordifications_manual() -> None:
    """ Manual check. """
    number = "0-000-000"
    numformat = "0-000-000"

    phonewords: Set[str] = all_wordifications(number, numformat, None, US_LETTER_MAP)
    assert phonewords
    for word in phonewords:
        translated_number = words_to_number(word, numformat, US_LETTER_MAP)
        if translated_number != number:
            found_mismatch = True
            raise ValueError(
                "Result '%s' does not match '%s'." % (translated_number, number)
            )


def test_all_wordifications_uses_default_arguments() -> None:
    """ Manual check. """
    number = "0-000-000"
    numformat = "0-000-000"

    phonewords: Set[str] = all_wordifications(number)
    assert phonewords
    for word in phonewords:
        translated_number = words_to_number(word, numformat)
        if translated_number != number:
            found_mismatch = True
            raise ValueError(
                "Result '%s' does not match '%s'." % (translated_number, number)
            )
