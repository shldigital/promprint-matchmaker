"""Helper functions for text matching."""
from thefuzz import fuzz


def match_score(text_1: str, text_2: str) -> int:
    """
    Return the similary score of two input texts.

    Expects cleaned, space separated tokens for each text input
    Shorter texts are only matched at the beginning of longer texts.

    :param text_1: First piece of text to match
    :type text_1: str
    :param text_2: Second piece of text to match
    :type text_2: str
    :return: Match score indicating how similar the texts are
    :rtype: int
    """
    toks = [text_1.split(" "), text_2.split(" ")]
    toks.sort(key=len)
    if len(toks[0]) < 4:
        text_1 = " ".join(toks[0])
        text_2 = " ".join(toks[1][:4])
    return fuzz.partial_ratio(text_1, text_2)
