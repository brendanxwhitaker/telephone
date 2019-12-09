""" Tests for the ``words_to_number()`` function. """
import re
from typing import Set

import hypothesis.strategies as st
from hypothesis import given

from telephone.all_wordifications import all_wordifications
from telephone.words_to_number import words_to_number

PHONEWORD = re.compile(r"^1(-([A-Z]|[0-9]){1,10}){1,10}$")
US_NUMBER = re.compile(r"1-[0-9]{3}-[0-9]{3}-[0-9]{4}")
LOWERCASE_ALPHA = re.compile(r"[a-z]+")
US_FORMAT = "0-000-000-0000"
TEST_FORMAT = US_FORMAT


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
    phonewords: Set[str] = all_wordifications(number, vocab)
    found_mismatch = False
    for word in phonewords:
        if words_to_number(word) != number:
            found_mismatch = True

    assert not found_mismatch
