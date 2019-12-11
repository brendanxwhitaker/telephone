""" Translation of phonewords to US phone numbers. """
from typing import List, Dict
from telephone.utils import insert_dashes


def words_to_number(phoneword: str, letter_map: Dict[str, str]) -> str:
    """
    Maps a phoneword back to the origin phone number.

    Parameters
    ----------
    phoneword : ``str``.
        A valid US phone number with some of its digits replaced by uppercase alpha
        characters. Contiguous sequences of alpha characters are separated by dashes.
    """
    if phoneword.upper() != phoneword:
        raise ValueError("Word '%s' contains lowercase letters." % phoneword)

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
    translated_number_no_dashes = "".join(translated_segments)
    number = insert_dashes(translated_number_no_dashes)

    return number
