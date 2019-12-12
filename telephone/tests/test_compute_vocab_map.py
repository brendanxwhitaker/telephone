""" Tests for the ``compute_vocab_map()`` function. """
from typing import Set

import hypothesis.strategies as st
from hypothesis import given

from telephone.utils import compute_vocab_map
from telephone.words_to_number import words_to_number
from telephone.tests.test_constants import US_LETTER_MAP, LOWERCASE_ALPHA


@given(st.sets(st.from_regex(LOWERCASE_ALPHA, fullmatch=True)))
def test_compute_vocab_map(vocabulary: Set[str]) -> None:
    """ Make sure indicies are right. """
    vocab_map = compute_vocab_map(vocabulary, US_LETTER_MAP)
    for wordhash, words in vocab_map.items():
        for word in words:
            implicit_format = "0" * len(word)
            assert words_to_number(word, US_LETTER_MAP, implicit_format) == wordhash
