""" A function to generate all possible phonewords from a given number. """
import re
from typing import Set, Dict, List, Tuple, Optional

from telephone.utils import (
    validate,
    get_vocabulary,
    compute_vocab_map,
    get_country_code_and_base,
    get_substring_starting_index_map,
    insert_dashes,
)
from telephone.tests.test_constants import US_LETTER_MAP

# pylint: disable=bad-continuation, too-many-locals, too-many-nested-blocks


def all_wordifications(
    number: str,
    numformat: str = "",
    vocabulary: Optional[Set[str]] = None,
    letter_map: Dict[str, str] = US_LETTER_MAP,
) -> Set[str]:
    """
    Generates all phonewords from ``number`` using words from ``vocabulary``.

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

    Returns
    -------
    phonewords : ``Set[str]``.
        The set of all possible phonewords which can be generated from ``number`` with
        the given ``vocab_map``. All letters are uppercase.
    """
    validate(number)
    if number == "":
        return set([])

    vocab: Set[str] = get_vocabulary() if vocabulary is None else vocabulary
    vocabulary_map: Dict[str, List[str]] = compute_vocab_map(vocab, letter_map)

    # Format inference.
    if numformat == "":
        numformat = re.sub(r"[0-9]", "0", number)

    spacer = "&"
    country_code, base_number = get_country_code_and_base(number)
    substrs_map = get_substring_starting_index_map(base_number)

    # Gives the list of all phonewords for ``base_number[i:]``.
    phoneword_map: Dict[int, List[Tuple[str, int]]] = {}

    # NOTE: Optimizations. If ``previous_list`` is sorted, then ``gap`` will get larger
    # as we iterate over it. So all ``gap_substrs`` lists will be subsets of the
    # subsequent one. But does this actually take any time? Only if ``vocabulary_map``
    # contains many collisions.

    # Tuples are of the form (substr, index of first non-numeric character).
    # NOTE: Lists should be sorted by order of indices.
    phoneword_map[len(base_number)] = [("", len(base_number))]
    i = len(base_number) - 1
    while i >= 0:
        substrs_starting_at_i = substrs_map[i]
        new_list: List[Tuple[str, int]] = []
        previous_list: List[Tuple[str, int]] = phoneword_map[i + 1]

        # Wordifications of a substring are still valid wordifications.
        # Add the phonewords you get by just adding ``base_number[i]`` to phonewords of
        # ``base_number[i + 1:]``.
        # i.e. ``4bike`` from ``bike`` for ``base_number == 42453``.
        new_list.extend([(base_number[i] + substr, k) for substr, k in previous_list])
        for old_phoneword, end_index in previous_list:

            # Compute the gap between the beginning of the current string
            # ``base_number[i:]`` and the first alphabetic substitution in
            # ``old_phoneword``.
            gap: str = base_number[i:end_index]
            gap_substrs = substrs_starting_at_i[: len(gap)]

            # For each substring of ``gap`` which includes first char of ``gap``.
            for gap_substr in gap_substrs:

                # If the substring has 1 or more wordifications, grab them as a list.
                if gap_substr in vocabulary_map:
                    substr_wordifications: List[str] = vocabulary_map[gap_substr]

                    # For each word in the list, make the substitution and add to list.
                    for word in substr_wordifications:

                        # Placing two words adjacent to each other; delimit them.
                        # Make sure we don't put a spacer at the very end.
                        if len(word) == len(gap) and end_index < len(base_number):
                            phoneword = word + spacer + old_phoneword[len(word) - 1 :]
                        else:
                            # print("No spacer for word '%s'." % word)
                            # print("End index:", end_index)
                            # print("Len base_number:", len(base_number))
                            phoneword = word + old_phoneword[len(word) - 1 :]
                        new_list.append((phoneword, i))

        phoneword_map[i] = new_list
        i -= 1

    # Note that at this point, the phonewords may have spacer tokens in them.
    phonewords = {word.upper() for word, _ in phoneword_map[0]}
    phonewords = {country_code + spacer + word for word in phonewords}
    phonewords = {insert_dashes(word, spacer, numformat) for word in phonewords}

    return phonewords
