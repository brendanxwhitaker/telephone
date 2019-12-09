""" A function to generate all possible phonewords from a given number. """
import json
import itertools
from typing import Set, Dict, List

# pylint: disable=bad-continuation

VALID_CHARACTERS = set(list(" -0123456789"))
FUNCTION_CHARACTERS = set(list("-"))


def validate(number: str) -> str:
    """
    Determines if a string is a valid number given a format.

    Parameters
    ----------
    number : ``str``.
        A valid US phone number with country code and dashes. Note that this check is
        intended to be a redundancy only.

    Returns
    -------
    sanitized_number : ``str``.
        The input but without whitespace or anything except numerals.

    Raises
    ------
    ValueError.
        If the input contains invalid characters or sequences.
    """

    # Strip whitespace.
    sanitized_number = "".join(number.split())

    # Check for invalid characters.
    for char in FUNCTION_CHARACTERS:
        sanitized_number = sanitized_number.replace(char, "")
    if not sanitized_number.isnumeric():
        raise ValueError(
            "The number '%s' contains invalid characters. " % number
            + "Only characters from the set '%s' are allowed." % str(VALID_CHARACTERS)
        )

    # Check for invalid arrangements of function characters.
    fn_combs = itertools.combinations_with_replacement(FUNCTION_CHARACTERS, 2)
    fn_strs = ["".join(comb) for comb in fn_combs]
    for fn_str in fn_strs:
        if fn_str in number:
            raise ValueError(
                "Invalid arrangement '%s' of function characters from '%s' in '%s'."
                % (fn_str, str(FUNCTION_CHARACTERS), number)
            )

    return sanitized_number


def compute_substrings(number: str) -> Dict[int, List[str]]:
    """ Compute all substrings of ``number``. """
    if number == "":
        return {}
    substrs_map: Dict[int, List[str]] = {}
    num: str = validate(number)
    for i in range(len(num)):
        substrs_starting_at_i: List[str] = []
        for j in range(i, len(num)):
            substr = num[i : j + 1]
            substrs_starting_at_i.append(substr)
        substrs_map[i] = substrs_starting_at_i
    return substrs_map


def all_wordifications(
    number: str, vocab_map: Dict[str, List[str]], letter_map: Dict[str, str]
) -> Set[str]:
    """
    Generates all phonewords from ``number`` using words from ``vocabulary``.

    Parameters
    ----------
    number : ``str``.
        A valid US phone number with country code and dashes.
    vocabulary : ``Set[str]``.
        A set of strings consisting of lowercase alpha characters only. All nonempty.
    """

    number = validate(number)
    substrs_map = compute_substrings(number)

    # Gives the list of all phonewords for ``number[i:]``.
    phoneword_map: Dict[int, List[Tuple[str, int]]] = {}

    # TODO: Optimizations. If ``previous_list`` is sorted, then ``gap`` will get larger
    # as we iterate over it. So all ``gap_substrs`` lists will be subsets of the
    # subsequent one. But does this actually take any time? Only if ``vocab_map``
    # contains many collisions.

    # Tuples are of the form (substr, index of first non-numeric character).
    # TODO: Lists should be sorted by order of indices.
    phoneword_map[len(number)] = [("", len(number))]
    i = len(number) - 1
    while i >= 0:
        substrs_starting_at_i = substrs_map[i]
        new_list: List[str] = []
        previous_list: List[str] = phoneword_map[i + 1]
        substitutions_at_i: List[str] = []

        # Wordifications of a substring are still valid wordifications.
        # Add the phonewords you get by just adding ``number[i]`` to phonewords of
        # ``number[i + 1:]``.
        # i.e. ``4bike`` from ``bike`` for ``number == 42453``.
        new_list.extend([(number[i] + substr, k) for substr, k in previous_list])
        for old_phoneword, end_index in previous_list:

            # Compute the gap between the beginning of the current string ``number[i:]``
            # and the first alphabetic substitution in ``old_phoneword``.
            gap: str = number[i:end_index]
            gap_substrs = substrs_starting_at_i[: len(gap)]

            # For each substring of ``gap`` which includes first char of ``gap``.
            for gap_substr in gap_substrs:

                # If the substring has 1 or more wordifications, grab them as a list.
                if gap_substr in vocab_map:
                    substr_wordifications: List[str] = vocab_map[gap_substr]

                    # For each word in the list, make the substitution and add to list.
                    for word in substr_wordifications:
                        phoneword = word + old_phoneword[len(word) - 1 :]
                        new_list.append((phoneword, i))

        phoneword_map[i] = new_list
        i -= 1
    complete_phonewords = set([token for token, _ in phoneword_map[0]])

    return complete_phonewords


def compute_hash_token_map(
    vocabulary: Set[str], letter_map: Dict[str, str]
) -> Dict[str, List[str]]:
    """
    Computes hashes of each word in ``vocabulary`` and maps the hashes to equivalence
    classes of words under the hashing function given by ``letter_map``.
    """
    # Construct vocab_map.
    hash_token_map: Dict[str, List[str]] = {}
    for token in tokens:
        tokenhash = "".join([letter_map[char] for char in token])
        print(tokenhash)
        if tokenhash in hash_token_map:
            hash_token_map[tokenhash].append(token)
        else:
            hash_token_map[tokenhash] = [token]

    return hash_token_map


def main():
    """ Temporary. """
    # Read in the vocabulary.
    with open(
        "../../data/telephone/google-10000-english.txt", "r", encoding="utf-8"
    ) as english:
        tokens = [word.rstrip() for word in english.readlines()]
    tokens.sort()
    tokens = [token for token in tokens if len(token) > 2]

    # Read in the letter mapping.
    with open("settings/mapping.json", "r") as mapping:
        letter_map = json.load(mapping)

    hash_token_map = compute_hash_token_map(tokens, letter_map)

    all_wordifications("12255", hash_token_map, letter_map)


if __name__ == "__main__":
    main()
