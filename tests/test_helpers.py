import pytest

from lib.helpers import match_score

four_token_partial_match_data = [
    ("quick brown fox jumps", "quick brown fox jumps over", 100),
    ("quick brown fox jumps", "the quick brown fox jumps", 100),
    ("quick brown fox jumps", "the quick brown fox jumps over the lazy dog", 100),
    ("quick brown fox jumps", "brown fox jumps over", 86),
    ("brown fox jumps over", "quick brown fox jumps", 86),
]

# Note that if the shorter string is less than 3 tokens long then we're only
# interested if it matches at the *start* of the other string
# This assumes "title:subtitle" structure (which may not always be the case)
# and thereby filters out junk matches of very short texts in very long texts
three_token_partial_match_data = [
    ("quick brown fox", "the quick brown fox jumps over the lazy dog", 100),
    ("quick brown fox", "the quick brown fox", 100),
    ("the lazy dog", "the quick brown fox jumps over the lazy dog", 50),
    ("the lazy dog", "the quick brown fox", 50),
    ("novellos collections of the favourite songs andc", "songs", 60),
    ("songs", "novellos collections of the favourite songs andc", 60),
    ("dorset", "worse than death etc", 83)]


@pytest.mark.parametrize("text_1, text_2, score", four_token_partial_match_data)
def test_four_token_partial_match_score(text_1, text_2, score):
    assert match_score(text_1, text_2) == score


@pytest.mark.parametrize("text_1, text_2, score", three_token_partial_match_data)
def test_three_token_partial_match_score(text_1, text_2, score):
    assert match_score(text_1, text_2) == score
