""" Tests for the ``insert_dashes()`` function. """
import re

import hypothesis.strategies as st
from hypothesis import given

from telephone.utils import find_occurrences, insert_dashes
from telephone.tests.generators import generate_spaced_phoneword
from telephone.tests.test_constants import GENERAL_FORMAT


@given(st.data(), st.from_regex(GENERAL_FORMAT, fullmatch=True))
def test_insert_dashes_doesnt_doubledash(data, numformat: str) -> None:
    """ TODO. """
    dashless_format = numformat.replace("-", "")
    dashless_phoneword = data.draw(
        st.from_regex(r"[A-Z0-9]{%d}" % len(dashless_format), fullmatch=True)
    )
    dashed = insert_dashes(dashless_phoneword, spacer="&", numformat=numformat)
    assert "--" not in dashed


@given(st.data(), st.from_regex(GENERAL_FORMAT, fullmatch=True))
def test_insert_dashes_is_uppercase(data, numformat: str) -> None:
    """ TODO. """
    dashless_format = numformat.replace("-", "")
    dashless_phoneword = data.draw(
        st.from_regex(r"[A-Z0-9]{%d}" % len(dashless_format), fullmatch=True)
    )
    dashed = insert_dashes(dashless_phoneword, spacer="&", numformat=numformat)
    assert not re.search(r"[a-z]", dashed)


@given(st.data(), st.from_regex(GENERAL_FORMAT, fullmatch=True))
def test_insert_dashes_keeps_dashes_inside(data, numformat: str) -> None:
    """ Make sure it doesn't put dashes at the ends. """
    dashless_format = numformat.replace("-", "")
    dashless_phoneword = data.draw(
        st.from_regex(r"[A-Z0-9]{%d}" % len(dashless_format), fullmatch=True)
    )
    dashed = insert_dashes(dashless_phoneword, spacer="&", numformat=numformat)
    assert not re.search(r"(^-)|(-$)", dashed)


@given(st.data(), st.from_regex(GENERAL_FORMAT, fullmatch=True))
def test_insert_dashes_places_dashes_correctly(data, numformat: str) -> None:
    """ Make sure a classical phone number is treated correctly. """
    dashless_format = numformat.replace("-", "")
    dashless_number = data.draw(
        st.from_regex(r"[0-9]{%d}" % len(dashless_format), fullmatch=True)
    )
    dashed = insert_dashes(dashless_number, spacer="&", numformat=numformat)
    try:
        assert find_occurrences(dashed, "-") == find_occurrences(numformat, "-")
    except AssertionError:
        raise ValueError("Dash mismatch in '%s'." % dashed)


@given(st.data(), st.from_regex(GENERAL_FORMAT, fullmatch=True))
def test_insert_dashes_handles_spacers(data, numformat: str) -> None:
    """ Make sure spacers are replaced with dashes. """
    spacer = "&"
    spaced_phoneword = generate_spaced_phoneword(
        data, numformat=numformat, spacer=spacer
    )
    segments = spaced_phoneword.split(spacer)
    letter_segments = [re.sub(r"[0-9]", "", segment) for segment in segments]
    phoneword = insert_dashes(spaced_phoneword, spacer=spacer, numformat=numformat)
    dashed_segments = phoneword.split("-")
    for segment in letter_segments:
        if segment and segment not in dashed_segments:
            raise ValueError("Word '%s' not found in '%s'." % (segment, phoneword))
