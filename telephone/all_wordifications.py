""" A function to generate all possible phonewords from a given number. """
import re
import json
import itertools
from typing import Set, Dict, List, Tuple

# pylint: disable=bad-continuation

VALID_CHARACTERS = set(list(" -0123456789"))
FUNCTION_CHARACTERS = set(list("-"))


def get_country_code_and_base(number: str) -> Tuple[str, str]:
    """
    Determines if a string COULD be a valid phone number according to a general format.

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
    stripped_number = "".join(number.split())

    # Check for invalid characters.
    for char in FUNCTION_CHARACTERS:
        sanitized_number = stripped_number.replace(char, "")
    if not sanitized_number.isnumeric():
        raise ValueError(
            "The number '%s' contains invalid characters. " % number
            + "Only characters from the set '%s' are allowed." % str(VALID_CHARACTERS)
        )

    # Check for invalid arrangements of function characters.
    fn_combs = itertools.combinations_with_replacement(FUNCTION_CHARACTERS, 2)
    fn_strs = ["".join(comb) for comb in fn_combs]
    for fn_str in fn_strs:
        if fn_str in stripped_number:
            raise ValueError(
                "Invalid arrangement '%s' of function characters from '%s' in '%s'."
                % (fn_str, str(FUNCTION_CHARACTERS), stripped_number)
            )

    segments = stripped_number.split("-")
    country_code = segments[0]
    base_number = "".join(segments[1:])

    return country_code, base_number


def get_substring_map(number: str) -> Dict[int, List[str]]:
    """ Map starting indices to substrings of ``number``. """
    if number == "":
        return {}
    substrs_map: Dict[int, List[str]] = {}
    for i in range(len(number)):
        substrs_starting_at_i: List[str] = []
        for j in range(i, len(number)):
            substr = number[i : j + 1]
            substrs_starting_at_i.append(substr)
        substrs_map[i] = substrs_starting_at_i
    return substrs_map


def get_substring_length_map(number: str) -> Dict[int, List[str]]:
    """ Compute sorted list of substrings of ``number``. """
    if number == "":
        return {}
    substring_length_map: Dict[int, List[str]] = {}
    for i in range(len(number)):
        for j in range(i, len(number)):
            substr = number[i : j + 1]
            substr_len = len(substr)
            if substr_len in substring_length_map:
                substring_length_map[substr_len].append(substr)
            else:
                substring_length_map[substr_len] = [substr]
    return substring_length_map


def all_wordifications(number: str, vocab_map: Dict[str, List[str]]) -> Set[str]:
    """
    Generates all phonewords from ``number`` using words from ``vocabulary``.

    Parameters
    ----------
    number : ``str``.
        A valid US phone number with country code and dashes.
    vocab_map : ``Dict[str, List[str]]``.
        A mapping from sequences of numerals to words in a vocabulary which map to them
        under some ``letter_map`` which maps letters to numbers not necessarily
        injectively.

    Returns
    -------
    dashed_phonewords : ``Set[str]``.
        The set of all possible phonewords which can be generated from ``number`` with
        the given ``vocab_map``. All letters are uppercase.
    """

    spacer = "&"
    country_code, base_number = get_country_code_and_base(number)
    substrs_map = get_substring_map(base_number)

    # Gives the list of all phonewords for ``base_number[i:]``.
    phoneword_map: Dict[int, List[Tuple[str, int]]] = {}

    # TODO: Optimizations. If ``previous_list`` is sorted, then ``gap`` will get larger
    # as we iterate over it. So all ``gap_substrs`` lists will be subsets of the
    # subsequent one. But does this actually take any time? Only if ``vocab_map``
    # contains many collisions.

    # Tuples are of the form (substr, index of first non-numeric character).
    # TODO: Lists should be sorted by order of indices.
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

                # TODO: Can we make this its own function?
                # If the substring has 1 or more wordifications, grab them as a list.
                if gap_substr in vocab_map:
                    substr_wordifications: List[str] = vocab_map[gap_substr]

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
    complete_phonewords = {word.upper() for word, _ in phoneword_map[0]}
    complete_phonewords = {country_code + spacer + word for word in complete_phonewords}
    dashed_phonewords = {insert_dashes(word) for word in complete_phonewords}

    return dashed_phonewords


def insert_dashes(spaced_phoneword: str) -> str:
    """ Inserts dashes between appropriate segments of a US phoneword. """
    # TODO: Make format an argument.
    # TODO: Split into a validation function for dashless phonewords.
    # 1. Insert `^` characters where dashes go according to the format.
    # 2. Insert a dash before every inserted word.
    # 3. Replace re.sub(r"([A-Z])^([A-Z])", "\1\2", <string>).
    spacer = "&"
    delim = "*"
    US_FORMAT = "0-000-000-0000"

    # Validate input.
    phoneword = spaced_phoneword
    if re.search("[^A-Z0-9%s]" % spacer, phoneword):
        raise ValueError("Word '%s' should only contain '[A-Z0-9&]'." % phoneword)
    assert len(US_FORMAT.replace("-", "")) == len(phoneword.replace(spacer, ""))

    # Add delimiters (``*``).
    # Format map: "0-000" -> "0-0*0*0".
    # Phoneword map: "123ABC&DEF" -> "1*2*3*A*B*C&D*E*F".
    delim_format = re.sub("([0-9])(?!(%s|$))" % "-", r"\1" + delim, US_FORMAT)
    delim_phoneword = re.sub("([A-Z0-9])(?!(%s|$))" % spacer, r"\1" + delim, phoneword)
    assert len(delim_format) == len(delim_phoneword)

    # Wherever there is a dash in ``delim_format``, replace the delimiter in the
    # ``delim_phoneword`` with a dash, unless it's a spacer.
    for i, char in enumerate(delim_format):
        if char == "-":
            # Don't replace spacers because these need to stay put between alpha chars.
            if delim_phoneword[i] == delim:
                delim_phoneword = delim_phoneword[:i] + char + delim_phoneword[i + 1 :]

    # Remove remaining delimiters.
    phoneword = delim_phoneword.replace(delim, "")

    # TODO: Don't do substitution on the country code.
    # Treat the country code, hardcoded for US ``1`` for now.
    base = phoneword[2:]

    # Add dashes at borders between digits and letters.
    base = re.sub(r"([0-9]+)([A-Z]+)", r"\1-\2", base)
    base = re.sub(r"([A-Z]+)([0-9]+)", r"\1-\2", base)

    # Kill dashes within words (but not spacers, which separate adjacent words).
    base = re.sub(r"([A-Z])-([A-Z])", r"\1\2", base)
    phoneword = phoneword[:2] + base

    # Replace spacers with dashes.
    phoneword = phoneword.replace(spacer, "-")

    return phoneword


def compute_vocab_map(
    vocabulary: Set[str], letter_map: Dict[str, str]
) -> Dict[str, List[str]]:
    """
    Computes hashes of each word in ``vocabulary`` and maps the hashes to equivalence
    classes of words under the hashing function given by ``letter_map``.
    """
    # Construct vocab_map.
    vocab_map: Dict[str, List[str]] = {}
    for token in vocabulary:
        uppercased_token = token.upper()
        tokenhash = "".join([letter_map[char] for char in uppercased_token])
        if tokenhash in vocab_map:
            vocab_map[tokenhash].append(uppercased_token)
        else:
            vocab_map[tokenhash] = [uppercased_token]

    return vocab_map


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

    vocab_map = compute_vocab_map(tokens, letter_map)

    all_wordifications("12255", vocab_map)


if __name__ == "__main__":
    main()
