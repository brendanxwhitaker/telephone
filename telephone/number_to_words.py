""" A function to generate phonewords. """
import re
from typing import Set, List, Dict, Optional

from telephone.utils import (
    validate,
    insert_dashes,
    get_country_code_and_base,
    get_substring_length_map,
    get_vocabulary,
)
from telephone.tests.test_constants import US_LETTER_MAP

# pylint: disable=bad-continuation


def number_to_words(
    number: str,
    numformat: str = "",
    vocabulary: Optional[Set[str]] = None,
    letter_map: Dict[str, str] = US_LETTER_MAP,
) -> str:
    """
    Generates a phoneword from ``number`` using words from ``vocabulary``.

    Parameters
    ----------
    number : ``str``.
        A valid US phone number with country code and dashes.
    numformat : ``str``.
        Format of the number using "0" and "-", e.g. "0-000-000-0000" for US numbers.
    vocabulary : ``Optional[Set[str]]``.
        Set of lowercase, alphabetical-only vocabulary words. Pass ``None`` to download
        and use a default US vocabulary.
    letter_map : ``Dict[str, str]``.
        Maps uppercase English letters to digits.
    """
    validate(number)
    if number == "":
        return ""

    vocab: Set[str] = get_vocabulary() if vocabulary is None else vocabulary

    # Format inference.
    if numformat == "":
        numformat = re.sub(r"[0-9]", "0", number)

    spacer = "&"
    country_code, base_number = get_country_code_and_base(number)
    substring_length_map: Dict[int, List[str]] = get_substring_length_map(base_number)
    phoneword = base_number

    for token in vocab:
        uppercased_token = token.upper()
        token_len = len(uppercased_token)
        if token_len in substring_length_map:
            tokenhash = "".join([letter_map[char] for char in uppercased_token])
            for substr in substring_length_map[token_len]:
                if substr == tokenhash:
                    phoneword = base_number.replace(substr, uppercased_token, 1)
                    break
    phoneword = insert_dashes(country_code + spacer + phoneword, spacer, numformat)

    return phoneword
