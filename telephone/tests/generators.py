""" Phoneword generators for testing. """
import random
import hypothesis.strategies as st
from telephone.utils import insert_dashes, get_country_code_and_base

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
