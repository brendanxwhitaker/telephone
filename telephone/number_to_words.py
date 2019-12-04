""" A function to generate phonewords. """
from typing import Set


def number_to_words(number: str, vocabulary: Set[str]) -> str:
    """
    Generates a phoneword from ``number`` using words from ``vocabulary``.

    Parameters
    ----------
    number : ``str``.
        A valid US phone number with country code and dashes.
    vocabulary : ``Set[str]``.
        A set of strings consisting of lowercase alpha characters only. All nonempty.
    """
    raise NotImplementedError
