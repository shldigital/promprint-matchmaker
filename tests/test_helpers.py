import pandas as pd
import pytest

from lib.helpers import filter_stop_words, apply_publishers_index
from lib.matching import match_score, match_titles, n_gram_substring_match
from pandas.testing import assert_frame_equal

register_file = "./tests/test_files/test_register_cleaned.csv"
collection_file = "./tests/test_files/test_collection_cleaned.tsv"
index_file = "./tests/test_files/test_publisher_index.csv"

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


def test_empty_string_match_score():
    assert match_score("", "a string") == 0


def test_none_match_score():
    assert match_score(None, "a string") == 0


def test_empty_strings_match():
    assert match_score("", "") == 100


match_title_data = [
    (1, 79, 18),
    (2, 90, 0),
    (2, 95, 0),
    (5, 79, 1),
]


@pytest.mark.parametrize("query_index, score_threshold, n_matches", match_title_data)
def test_title_match(query_index, score_threshold, n_matches):
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


first_word_match_frames = [
    (
        "macmillan dictionary of anthropology",
        {
            "title": ["dictionary of anthropology"],
            "publisher": ["ye olde macmillan book publishing place"],
        },
        100,
    )
]


@pytest.mark.parametrize(
    "register_entry, collection_dict, expected_score", first_word_match_frames
)
def test_match_first_word(register_entry, collection_dict, expected_score):
    collection = pd.DataFrame(collection_dict)
    score = collection["publisher"].apply(
        lambda t: match_score(register_entry.split(" ")[0], t)
    )
    assert score[0] == expected_score


stop_word_match_frames = [
    (
        "the dictionary of anthropology",
        {
            "title": ["dictionary of anthropology"],
            "publisher": ["the olde macmillan book publishing place"],
        },
        0,
    )
]


@pytest.mark.parametrize(
    "register_entry, collection_dict, expected_score", stop_word_match_frames
)
def test_stop_word_no_match(register_entry, collection_dict, expected_score):
    collection = pd.DataFrame(collection_dict)
    score = collection["publisher"].apply(
        lambda t: match_score(filter_stop_words(register_entry.split(" ")[0]), t)
    )
    assert score[0] == expected_score


metadata_match_frames = [
    (
        "Longman & Co.",
        {
            "title": ["alpine journal"],
            "publisher": [" "],
        },
        0,
    )
]


@pytest.mark.parametrize(
    "register_entry, collection_dict, expected_score", metadata_match_frames
)
def test_match_metadata(register_entry, collection_dict, expected_score):
    collection = pd.DataFrame(collection_dict)
    score = collection["publisher"].apply(
        lambda t: match_score(register_entry.split(" ")[0], t)
    )
    assert score[0] == expected_score


publisher_match_frames = [
    (
        {"clean_publisher": ["routledge", "some non-indexed publisher"]},
        {"indexed_publisher": ["routledge and co", "some non-indexed publisher"]},
    )
]


@pytest.mark.parametrize("data_dict, indexed_dict", publisher_match_frames)
def test_apply_publishers_index(data_dict, indexed_dict, tmp_path):
    publishers_index = pd.read_csv(index_file)
    data_df = pd.DataFrame(data_dict)
    data_df["indexed_publisher"] = data_df["clean_publisher"].map(
        lambda p: apply_publishers_index(p, publishers_index)
    )
    expected_dict = data_dict.update(indexed_dict)
    expected_df = pd.DataFrame(data=expected_dict)
    for index, row in expected_df.iterrows():
        assert data_df.iloc[0].equals(row)


n_gram_data_cols = {"count": [1, 2, 1, 3, 2, 1], "degree": [3, 2, 2, 1, 1, 1]}
n_gram_data_index = [
    "quick brown fox",
    "quick brown",
    "brown fox",
    "quick",
    "brown",
    "fox",
]

match_rows = [
    (
        {
            "clean_title_register": ["the quick brown dog"],
            "clean_title_collection": ["the quick brown doll"],
        },
        {"n-gram match": [True], "n-gram": ["quick brown"], "substring score": 92, "match": [True]},
    ),
    (
        {
            "clean_title_register": ["the quick brown dog"],
            "clean_title_collection": ["the quick brown aeroplane"],
        },
        {"n-gram match": [True], "n-gram": ["quick brown"], "substring score": 73, "match": [False]},
    ),
    (
        {
            "clean_title_register": ["the terrifying black dog"],
            "clean_title_collection": ["the terrifying black frog"],
        },
        {"n-gram match": [False], "n-gram": [None], "substring score": None, "match": [True]},
    ),
]


@pytest.mark.parametrize("match_row_cols, expected_row_cols", match_rows)
def test_n_gram_substring_match(match_row_cols, expected_row_cols):
    n_gram_data = pd.DataFrame(data=n_gram_data_cols, index=n_gram_data_index)
    match_row = pd.DataFrame(match_row_cols)
    match_row = n_gram_substring_match(next(match_row.iterrows()), n_gram_data, 80)
    expected_row = match_row_cols.copy()
    expected_row.update(expected_row_cols)
    expected_data = pd.DataFrame(expected_row)
    assert_frame_equal(match_row, expected_data.astype(object))


match_rows_for_count_cutoff = [
    (
        {
            "clean_title_register": ["the quick brown dog"],
            "clean_title_collection": ["the quick brown doll"],
        },
        {"n-gram match": [True], "n-gram": ["quick brown"], "substring score": 92, "match": [True]},
        None,
    ),
    (
        {
            "clean_title_register": ["the quick brown dog"],
            "clean_title_collection": ["the quick brown doll"],
        },
        {"n-gram match": [True], "n-gram": ["quick brown"], "substring score": 92, "match": [True]},
        1,
    ),
    (
        {
            "clean_title_register": ["the quick brown dog"],
            "clean_title_collection": ["the quick brown doll"],
        },
        {"n-gram match": [True], "n-gram": ["quick"], "substring score": 96, "match": [True]},
        2,
    ),
    (
        {
            "clean_title_register": ["the quick brown dog"],
            "clean_title_collection": ["the quick brown frog"],
        },
        {"n-gram match": [False], "n-gram": [None], "substring score": None, "match": [True]},
        3,
    ),
]


@pytest.mark.parametrize(
    "match_row_cols, expected_row_cols, cutoff", match_rows_for_count_cutoff
)
def test_n_gram_substring_match_with_count_cutoff(
    match_row_cols, expected_row_cols, cutoff
):
    n_gram_data = pd.DataFrame(data=n_gram_data_cols, index=n_gram_data_index)
    match_row = pd.DataFrame(match_row_cols)
    match_row = n_gram_substring_match(
        next(match_row.iterrows()), n_gram_data, 80, cutoff
    )
    expected_row = match_row_cols.copy()
    expected_row.update(expected_row_cols)
    expected_data = pd.DataFrame(expected_row)
    assert_frame_equal(match_row, expected_data.astype(object))
