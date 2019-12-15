""" Auxiliary functions for translation and testing. """
import os
import re
import itertools
import urllib.request
from typing import List, Set, Dict, Tuple

# pylint: disable=bad-continuation

VALID_CHARACTERS = set(list(" -0123456789"))
FUNCTION_CHARACTERS = set(list("-"))
VOCAB_URL = (
    "https://raw.githubusercontent.com/first20hours/"
    + "google-10000-english/master/google-10000-english.txt"
)
VOCAB_SAVE_PATH = "data/vocab.txt"


def find_occurrences(string: str, char: str) -> List[int]:
    """ Returns a list of all occurrences of ``char`` in ``string`` in order. """
    if len(char) != 1:
        raise ValueError("Argument char '%s' must have length 1." % char)
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


def get_vocabulary() -> Set[str]:
    """ TODO. """
    if not os.path.isfile(VOCAB_SAVE_PATH):
        urllib.request.urlretrieve(VOCAB_URL, VOCAB_SAVE_PATH)
    with open(VOCAB_SAVE_PATH, "r") as vocab_file:
        vocabulary = vocab_file.readlines()
        vocabulary = [word.strip() for word in vocabulary]
    return set(vocabulary)


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
        if not token.isalpha():
            raise ValueError("Vocabulary word '%s' contains non-alpha chars." % token)
        uppercased_token = token.upper()
        tokenhash = "".join([letter_map[char] for char in uppercased_token])
        if tokenhash in vocab_map:
            vocab_map[tokenhash].append(uppercased_token)
        else:
            vocab_map[tokenhash] = [uppercased_token]

    return vocab_map


def validate(number: str) -> None:
    """
    Determines if a string COULD be a valid phone number according to a general format.

    Parameters
    ----------
    number : ``str``.
        A valid US phone number with country code and dashes. Note that this check is
        intended to be a redundancy only.

    Raises
    ------
    ValueError.
        If the input contains invalid characters or sequences.
    """

    # Treat empty string.
    if number == "":
        return

    # Check for invalid characters.
    for char in FUNCTION_CHARACTERS:
        sanitized_number = number.replace(char, "")
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


def get_country_code_and_base(number: str) -> Tuple[str, str]:
    """ Splits on the first dash. """
    # Treat empty string.
    if number == "":
        return "", ""
    segments = number.split("-")
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
    spacer : ``str``.
        Character to use for preserving word boundaries.
    numformat : ``str``.
        Format of the number using "0" and "-", e.g. "0-000-000-0000" for US numbers.

    phoneword : ``str``.
        With dashes added.
    """
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
