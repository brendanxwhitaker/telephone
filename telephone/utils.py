""" Auxiliary functions for translation and testing. """
import re
import random
import itertools
from typing import List, Set, Dict, Tuple

import hypothesis.strategies as st

# pylint: disable=bad-continuation

VALID_CHARACTERS = set(list(" -0123456789"))
FUNCTION_CHARACTERS = set(list("-"))


def find_occurrences(string: str, char: str) -> List[int]:
    """ Returns a list of all occurrences of ``char`` in ``string`` in order. """
    return [i for i, letter in enumerate(string) if letter == char]


def get_substring_starting_index_map(number: str) -> Dict[int, List[str]]:
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


def compute_vocab_map(
    vocabulary: Set[str], letter_map: Dict[str, str]
) -> Dict[str, List[str]]:
    """
    Computes hashes of each word in ``vocabulary`` and maps the hashes to equivalence
    classes of words under the hashing function given by ``letter_map``.

    Parameters
    ----------
    vocabulary : ``Set[str]``.
        A set of strings consisting of lowercase alpha characters only. All nonempty.
    letter_map : ``Dict[str, str]``.
        Mapping from uppercase letters to digits.

    Returns
    -------
    vocab_map : ``Dict[str, List[str]]``.
        A mapping from sequences of numerals to words in a vocabulary which map to them
        under ``letter_map`` which maps letters to numbers not necessarily injectively.
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


def generate_phoneword(data, numformat: str) -> str:
    """
    Generates an arbitrary phoneword given a hypothesis data object.

    Parameters
    ----------
    data : ``st._internal.core.DataObject``.
        Hypothesis data generator.

    Returns
    -------
    phoneword : ``str``.
        Of the form ``1-123-ABC-DEF-456``. Contains dashes and alphanumerics.
    """
    spacer = "&"
    spaced_phoneword = generate_spaced_phoneword(data, numformat, spacer)

    # Throw in dashes.
    phoneword = insert_dashes(spaced_phoneword, spacer=spacer, numformat=numformat)

    return phoneword


def generate_spaced_phoneword(data, numformat: str, spacer: str) -> str:
    """
    Generates an arbitrary phoneword with spacers between consecutive alpha words
    to simulate input to ``insert_dashes()``.

    Parameters
    ----------
    data : ``st._internal.core.DataObject``.
        Hypothesis data generator.

    Returns
    -------
    spaced_phoneword : ``str``.
        Of the form ``1&123ABC&DEF``. Contains spacers and alphanumerics.
    """

    spaced_phoneword = ""
    country_code, base_format = get_country_code_and_base(numformat)
    dashless_format = base_format.replace("-", "")
    segment_lengths = [len(seg) for seg in base_format.split("-")]

    for seg_len in segment_lengths:
        seed = random.randint(0, 10000)
        if seed % 2 == 0:
            segment = data.draw(st.from_regex("[0-9]{%d}" % seg_len, fullmatch=True))
        else:
            segment = data.draw(st.from_regex("[A-Z]{%d}" % seg_len, fullmatch=True))
        if spaced_phoneword and spaced_phoneword[0].isalpha():
            spaced_phoneword = segment + spacer + spaced_phoneword
        else:
            spaced_phoneword = segment + spaced_phoneword
    assert len(spaced_phoneword.replace(spacer, "")) == len(dashless_format)
    spaced_phoneword = country_code + spacer + spaced_phoneword

    return spaced_phoneword


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


def insert_dashes(spaced_phoneword: str, spacer: str, numformat: str) -> str:
    """
    Inserts dashes between appropriate segments of a US phoneword.

    Parameters
    ----------
    spaced_phoneword : ``str``.
        Of the form ``1&123ABC&DEF``. Contains spacers and alphanumerics.

    phoneword : ``str``.
        With dashes added.
    """
    # TODO: Split into a validation function for dashless phonewords.
    # 1. Insert `^` characters where dashes go according to the format.
    # 2. Insert a dash before every inserted word.
    # 3. Replace re.sub(r"([A-Z])^([A-Z])", "\1\2", <string>).
    delim = "*"
    assert spacer != delim

    # Validate input.
    phoneword = spaced_phoneword
    if re.search("[^A-Z0-9%s]" % spacer, phoneword):
        raise ValueError(
            "Word '%s' should only contain '[A-Z0-9%s]'." % (phoneword, spacer)
        )
    assert len(numformat.replace("-", "")) == len(phoneword.replace(spacer, ""))

    # Add delimiters (``*``).
    # Format map: "0-000" -> "0-0*0*0".
    # Phoneword map: "123ABC&DEF" -> "1*2*3*A*B*C&D*E*F".
    delim_format = re.sub("([0-9])(?!(%s|$))" % "-", r"\1" + delim, numformat)
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
    country_code_length = len(numformat.split("-")[0])
    base = phoneword[country_code_length + 1 :]

    # Add dashes at borders between digits and letters.
    base = re.sub(r"([0-9]+)([A-Z]+)", r"\1-\2", base)
    base = re.sub(r"([A-Z]+)([0-9]+)", r"\1-\2", base)

    # Kill dashes within words (but not spacers, which separate adjacent words).
    base = re.sub(r"([A-Z])-(?=[A-Z])", r"\1", base)
    phoneword = phoneword[: country_code_length + 1] + base

    # Replace spacers with dashes.
    phoneword = phoneword.replace(spacer, "-")

    return phoneword
