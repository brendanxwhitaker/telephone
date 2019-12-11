""" A function to generate phonewords. """
from typing import Set, List, Dict

from telephone.all_wordifications import (
    get_country_code_and_base,
    get_substring_length_map,
    insert_dashes,
)
# pylint: disable=bad-continuation


def number_to_words(
    number: str, vocabulary: Set[str], letter_map: Dict[str, str]
) -> str:
    """
    Generates a phoneword from ``number`` using words from ``vocabulary``.

    Parameters
    ----------
    number : ``str``.
        A valid US phone number with country code and dashes.
    vocabulary : ``Set[str]``.
        A set of strings consisting of lowercase alpha characters only. All nonempty.
    """
    spacer = "&"
    country_code, base_number = get_country_code_and_base(number)
    substring_length_map: Dict[int, List[str]] = get_substring_length_map(base_number)
    phoneword = base_number

    for token in vocabulary:
        uppercased_token = token.upper()
        token_len = len(uppercased_token)
        if token_len in substring_length_map:
            tokenhash = "".join([letter_map[char] for char in uppercased_token])
            for substr in substring_length_map[token_len]:
                if substr == tokenhash:
                    phoneword = base_number.replace(substr, uppercased_token, 1)
                    break
    phoneword = insert_dashes(country_code + spacer + phoneword)

    return phoneword
