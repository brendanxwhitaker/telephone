""" Tests for the ``words_to_number()`` function. """
import re

import hypothesis.strategies as st
from hypothesis import given, assume

from telephone.words_to_number import words_to_number

PHONEWORD = re.compile(r"^1(-([A-Z]|[0-9]){1,10}){1,10}$")


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
    assume(len(phoneword.replace("-", "")) == 11)
    number = words_to_number(phoneword)

    raise NotImplementedError


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
    assume(len(phoneword.replace("-", "")) == 11)
    number = words_to_number(phoneword)
    number_no_dashes = number.replace("-", "")
    assert number_no_dashes.isnumeric()
