""" Tests for the ``get_substring_starting_index_map()`` function. """
from typing import Dict, List

import hypothesis.strategies as st
from hypothesis import given

from telephone.utils import get_substring_starting_index_map


@given(st.text())
def test_get_substring_starting_index_map_finds_correct_indices(string: str) -> None:
    """ Make sure indicies are right. """
    substr_map: Dict[int, List[str]] = get_substring_starting_index_map(string)
    for i, substr_list in substr_map.items():
        for substr in substr_list:
            if string[i : i + len(substr)] != substr:
                raise ValueError(
                    "String '%s' not at '%d' in '%s'." % (substr, i, string)
                )
