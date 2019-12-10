""" Tests for the ``insert_dashes()`` function. """
import re
import hypothesis.strategies as st
from hypothesis import given

from telephone.all_wordifications import insert_dashes
from telephone.tests.test_utils import find_occurrences
from telephone.tests.test_constants import (
    US_ALPHANUMERIC,
    US_NUMBER_NODASH,
    TEST_FORMAT,
)


@given(st.from_regex(US_ALPHANUMERIC, fullmatch=True))
def test_insert_dashes_doesnt_doubledash(phoneword_no_dashes: str) -> None:
    """ TODO. """
    dashed = insert_dashes(phoneword_no_dashes)
    assert "--" not in dashed


@given(st.from_regex(US_ALPHANUMERIC, fullmatch=True))
def test_insert_dashes_is_uppercase(phoneword_no_dashes: str) -> None:
    """ TODO. """

    dashed = insert_dashes(phoneword_no_dashes)
    assert not re.search(r"[a-z]", dashed)


@given(st.from_regex(US_ALPHANUMERIC, fullmatch=True))
def test_insert_dashes_keeps_words_contiguous(phoneword_no_dashes: str) -> None:
    """ TODO. """

    dashed = insert_dashes(phoneword_no_dashes)
    assert not re.search(r"[A-Z]-[A-Z]", dashed)


@given(st.from_regex(US_ALPHANUMERIC, fullmatch=True))
def test_insert_dashes_keeps_dashes_inside(phoneword_no_dashes: str) -> None:
    """ TODO. """

    dashed = insert_dashes(phoneword_no_dashes)
    assert not re.search(r"(^-)|(-$)", dashed)


@given(st.from_regex(US_NUMBER_NODASH, fullmatch=True))
def test_insert_dashes_places_dashes_in_correct_place(phoneword_no_dashes: str) -> None:
    """ TODO. """

    dashed = insert_dashes(phoneword_no_dashes)
    assert find_occurrences(dashed, "-") == find_occurrences(TEST_FORMAT, "-")
