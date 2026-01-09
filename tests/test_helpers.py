import pandas as pd
import pytest

from lib.helpers import match_score, match_titles

register_file = "./tests/test_files/test_register_export.csv"
collection_file = "./tests/test_files/test_docs.tsv"

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
    ("dorset", "worse than death etc", 83),
]


@pytest.mark.parametrize("text_1, text_2, score", four_token_partial_match_data)
def test_four_token_partial_match_score(text_1, text_2, score):
    assert match_score(text_1, text_2, short_len=4) == score


@pytest.mark.parametrize("text_1, text_2, score", three_token_partial_match_data)
def test_three_token_partial_match_score(text_1, text_2, score):
    assert match_score(text_1, text_2, short_len=4) == score


local_match_title_data = [
    (1, 79, 1),  # Single match
    (2, 90, 2),  # Two matches at lower threshold
    (2, 95, 1),  # One match at higher threshold
    (5, 79, 0),  # No match
]


@pytest.mark.parametrize(
    "query_index, score_threshold, n_matches", local_match_title_data
)
def test_local_title_match(query_index, score_threshold, n_matches):
    register = pd.read_csv(register_file)
    register = register.set_index("id")
    register_row = list(register.iterrows())[query_index]
    collection = pd.read_csv(collection_file, sep="\t")
    collection = collection.set_index("id")
    word_threshold = 1

    matches: pd.DataFrame = match_titles(
        register_row, collection, register, score_threshold, word_threshold
    )

    assert matches.shape[0] == n_matches


publisher_match_frames = [
    (
        "macmillan dictionary of anthropology",
        {
            "title": ["dictionary of anthropology"],
            "publisher": ["ye olde macmillan book publisher"],
        },
        100,
    )
]


@pytest.mark.parametrize(
    "register_title, collection_dict, expected_score", publisher_match_frames
)
def test_match_publisher(register_title, collection_dict, expected_score):
    collection = pd.DataFrame(collection_dict)
    score = collection["publisher"].apply(lambda t: match_score(register_title, t))
    assert score[0] == expected_score
