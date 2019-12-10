""" Test utilities. """
from typing import List


def find_occurrences(string: str, char: str) -> List[int]:
    """ Does what its name sugggests. """
    return [i for i, letter in enumerate(string) if letter == char]
