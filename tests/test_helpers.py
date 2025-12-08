import pytest

from lib.helpers import match_score

four_token_partial_match_data = [
    ("quick brown fox jumps", "quick brown fox jumps over", 100),
    ("quick brown fox jumps", "the quick brown fox jumps", 100),
    ("quick brown fox jumps", "the quick brown fox jumps over the lazy dog", 100),
    ("quick brown fox jumps", "brown fox jumps over", 86),
]

@pytest.mark.parametrize("text_1, text_2, score", four_token_partial_match_data)
def test_four_token_partial_match_score(text_1, text_2, score):
    assert match_score(text_1, text_2) == score
