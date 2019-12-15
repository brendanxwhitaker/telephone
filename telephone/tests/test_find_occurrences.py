""" Tests for the ``find_occurrences()`` function. """
import re
import random
from typing import List

import hypothesis.strategies as st
from hypothesis import given

from telephone.utils import find_occurrences


@given(st.text())
def test_find_occurrences_finds_correct_quantity(string: str) -> None:
    """ Make sure it finds no more and no less than regex does. """
    if string != "":
        char = random.choice(list(string))
        occurrences: List[int] = find_occurrences(string, char)
        regex_specials = ["\\", "^", "+", "$", ".", "|", "?", "*", "(", ")", "[", "{"]
        if char in regex_specials:
            char = "\\" + char
        founds = re.findall(r"%s" % char, string)
        assert len(occurrences) == len(founds)


@given(st.text())
def test_find_occurrences_finds_correct_places(string: str) -> None:
    """ Make sure it finds no more and no less than regex does. """
    if string != "":
        char = random.choice(list(string))
        occurrences: List[int] = find_occurrences(string, char)
        for i in occurrences:
            if string[i] != char:
                raise ValueError("Char '%s' not at '%d' in '%s'." % (char, i, string))
