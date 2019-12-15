""" Translation of phonewords to US phone numbers. """
import re
from typing import List, Dict
from telephone.utils import insert_dashes
from telephone.tests.test_constants import US_LETTER_MAP

# pylint: disable=bad-continuation


def words_to_number(
    phoneword: str, numformat: str = "", letter_map: Dict[str, str] = US_LETTER_MAP
) -> str:
    """
    Maps a phoneword back to the origin phone number.

    Parameters
    ----------
    phoneword : ``str``.
        A valid US phone number with some of its digits replaced by uppercase alpha
        characters. Contiguous sequences of alpha characters are separated by dashes.
    numformat : ``str``.
        Format of the number using "0" and "-", e.g. "0-000-000-0000" for US numbers.
    letter_map : ``Dict[str, str]``.
        Maps uppercase English letters to digits.

    Returns
    -------
    number : ``str``.
        The translated number represented a la ``numformat``.
    """
    if phoneword == "":
        return ""
    if phoneword.upper() != phoneword:
        raise ValueError("Word '%s' contains lowercase letters." % phoneword)

    # Format inference.
    if numformat == "":
        numformat = re.sub(r"[A-Z0-9]", "0", phoneword)

    segments: List[str] = phoneword.split("-")
    translated_segments: List[str] = []
    for segment in segments:
        if not segment.isnumeric():
            try:
                segment_hash = "".join([letter_map[char] for char in segment])
            except KeyError:
                raise ValueError(
                    "Found invalid character in '%s' for mapping domain '%s'."
                    % (segment, str(letter_map.keys()))
                )
        else:
            segment_hash = segment
        translated_segments.append(segment_hash)
    translated_dashless_number = "".join(translated_segments)
    dashless_format = numformat.replace("-", "")
    translated_dashless_number = translated_dashless_number[: len(dashless_format)]
    number = insert_dashes(translated_dashless_number, spacer="&", numformat=numformat)

    return number
