""" Tests for the ``insert_dashes()`` function. """
import re

import hypothesis.strategies as st
from hypothesis import given

from telephone.all_wordifications import insert_dashes
from telephone.tests.test_utils import find_occurrences, generate_spaced_phoneword
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
def test_insert_dashes_keeps_dashes_inside(phoneword_no_dashes: str) -> None:
    """ Make sure it doesn't put dashes at the ends. """
    dashed = insert_dashes(phoneword_no_dashes)
    assert not re.search(r"(^-)|(-$)", dashed)


@given(st.from_regex(US_NUMBER_NODASH, fullmatch=True))
def test_insert_dashes_places_dashes_correctly(phoneword_no_dashes: str) -> None:
    """ Make sure a classical phone number is treated correctly. """
    dashed = insert_dashes(phoneword_no_dashes)
    assert find_occurrences(dashed, "-") == find_occurrences(TEST_FORMAT, "-")


@given(st.data())
def test_insert_dashes_handles_spacers(data) -> None:
    """ Make sure spacers are replaced with dashes. """
    spacer = "&"
    spaced_phoneword = generate_spaced_phoneword(data)
    segments = spaced_phoneword.split(spacer)
    letter_segments = [re.sub(r"[0-9]", "", segment) for segment in segments]
    phoneword = insert_dashes(spaced_phoneword)
    dashed_segments = phoneword.split("-")
    for segment in letter_segments:
        if segment and segment not in dashed_segments:
            raise ValueError("Word '%s' not found in '%s'." % (segment, phoneword))
