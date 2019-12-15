""" Tests for the ``get_substring_length_map()`` function. """
import hypothesis.strategies as st
from hypothesis import given

from telephone.utils import get_substring_length_map


@given(st.text())
def test_get_substring_length_map(string: str) -> None:
    """ Make sure indicies are right. """
    substr_map = get_substring_length_map(string)
    for length, substr_list in substr_map.items():
        for substr in substr_list:
            assert len(substr) == length
            assert substr in string
