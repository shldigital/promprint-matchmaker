import glob
import pandas as pd
import pytest

from src.cli.n_gram_list import main
from lib.n_gram import n_gram_frequency, multi_n_gram_frequency, sort_n_grams_by_degree
from pandas.testing import assert_frame_equal, assert_series_equal
from pathlib import Path

test_collections = [
    Path("./tests/test_files/test_collection_short.tsv"),
    Path("./tests/test_files/test_register_short.csv"),
]
single_and_multi_file = [[test_collections[0]], test_collections]
test_n_gram_frequencies = Path("./tests/test_files/n_gram_count.csv")

temp_output = Path("./tests/output_examples")


@pytest.mark.parametrize(
    "test_paths", single_and_multi_file, ids=["single", "multiple"]
)
def test_single_and_multi_file(test_paths, tmp_path):
    main(temp_output, test_paths, ["clean_title"], 100, 100)
    csv_outputs = glob.glob(str(temp_output) + "/*.csv")
    png_outputs = glob.glob(str(temp_output) + "/*.png")
    assert len(csv_outputs) > 0
    assert len(png_outputs) > 0


def test_missing_column_throws(tmp_path):
    with pytest.raises(KeyError):
        main(tmp_path, test_collections, ["spurious_column"], 20, 100)


n_gram_test_data = [
    "quick",
    "quick brown",
    "quick brown fox",
]

expected_frequencies = [
    (
        1,
        {"quick": 3, "brown": 2, "fox": 1},
    ),
    (
        2,
        {"quick brown": 2, "brown fox": 1},
    ),
]


@pytest.mark.parametrize("degree, expected_data", expected_frequencies)
def test_n_gram_frequency(degree, expected_data):
    test_series = pd.Series(n_gram_test_data)
    test_tokens = test_series.str.split()
    n_grams = n_gram_frequency(test_tokens, degree)
    n_grams.to_csv(temp_output / "n_gram_count.csv")
    expected_data = pd.Series(data=expected_data, name="count")
    assert_series_equal(n_grams, expected_data)


n_gram_output = {
    "count": {
        "quick": 3,
        "brown": 2,
        "quick brown": 2,
        "fox": 1,
        "brown fox": 1,
        "quick brown fox": 1,
    },
    "degree": {
        "quick": 1,
        "brown": 1,
        "quick brown": 2,
        "fox": 1,
        "brown fox": 2,
        "quick brown fox": 3,
    },
}


def test_multi_n_gram_frequency():
    test_series = pd.Series(n_gram_test_data)
    test_tokens = test_series.str.split()
    n_gram_frame = multi_n_gram_frequency(test_tokens)
    n_gram_frame.to_csv(temp_output / "n_gram_count.csv")
    expected_data = pd.DataFrame(data=n_gram_output)
    assert_frame_equal(n_gram_frame, expected_data)


n_gram_output_sorted = {
    "count": {
        "quick brown fox": 1,
        "quick brown": 2,
        "brown fox": 1,
        "quick": 3,
        "brown": 2,
        "fox": 1,
    },
    "degree": {
        "quick brown fox": 3,
        "quick brown": 2,
        "brown fox": 2,
        "quick": 1,
        "brown": 1,
        "fox": 1,
    },
}


def test_sort_n_grams_by_degree():
    n_gram_frame = pd.DataFrame(n_gram_output)
    n_gram_sorted = sort_n_grams_by_degree(n_gram_frame)
    print(n_gram_sorted.to_dict())
    expected_data = pd.DataFrame(n_gram_output_sorted)
    assert_frame_equal(n_gram_sorted, expected_data)
