import glob
import pandas as pd
import pytest

from src.cli.n_gram_list import main
from lib.n_gram import n_gram_frequency, multi_n_gram_frequency
from pandas.testing import assert_series_equal
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
    main(temp_output, test_paths, ["clean_title"], 20, 100)
    csv_outputs = glob.glob(str(temp_output) + "/*.csv")
    png_outputs = glob.glob(str(temp_output) + "/*.png")
    assert len(csv_outputs) > 0
    assert len(png_outputs) > 0


def test_missing_column_throws(tmp_path):
    with pytest.raises(KeyError):
        main(tmp_path, test_collections, ["spurious_column"], 20, 100)


test_data = [
    "the",
    "the quick",
    "the quick brown",
    "the quick brown fox",
    "the quick brown fox jumps",
    "the quick brown fox jumps over",
    "the quick brown fox jumps over the",
    "the quick brown fox jumps over the lazy",
    "the quick brown fox jumps over the lazy dog",
]

expected_frequencies = [
    (
        1,
        {
            "the": 12,
            "quick": 8,
            "brown": 7,
            "fox": 6,
            "jumps": 5,
            "over": 4,
            "lazy": 2,
            "dog": 1,
        },
    ),
    (
        2,
        {
            "the quick": 8,
            "quick brown": 7,
            "brown fox": 6,
            "fox jumps": 5,
            "jumps over": 4,
            "over the": 3,
            "the lazy": 2,
            "lazy dog": 1,
        },
    ),
]


@pytest.mark.parametrize("degree, expected_data", expected_frequencies)
def test_n_gram_frequency(degree, expected_data):
    test_series = pd.Series(test_data)
    n_gram_df = n_gram_frequency(test_series, degree)
    n_gram_df.to_csv(temp_output / "n_gram_count.csv")
    expected_data_series = pd.Series(data=expected_data)
    expected_data_series.name = "count"
    assert_series_equal(n_gram_df, expected_data_series)


expected_data = {
    "the": 12,
    "quick": 8,
    "the quick": 8,
    "brown": 7,
    "quick brown": 7,
    "the quick brown": 7,
    "brown fox": 6,
    "fox": 6,
    "quick brown fox": 6,
    "the quick brown fox": 6,
    "fox jumps": 5,
    "jumps": 5,
    "quick brown fox jumps": 5,
    "the quick brown fox jumps": 5,
    "brown fox jumps": 5,
    "over": 4,
    "quick brown fox jumps over": 4,
    "the quick brown fox jumps over": 4,
    "fox jumps over": 4,
    "brown fox jumps over": 4,
    "jumps over": 4,
    "jumps over the": 3,
    "the quick brown fox jumps over the": 3,
    "fox jumps over the": 3,
    "brown fox jumps over the": 3,
    "quick brown fox jumps over the": 3,
    "over the": 3,
    "lazy": 2,
    "the lazy": 2,
    "quick brown fox jumps over the lazy": 2,
    "over the lazy": 2,
    "jumps over the lazy": 2,
    "brown fox jumps over the lazy": 2,
    "the quick brown fox jumps over the lazy": 2,
    "fox jumps over the lazy": 2,
    "dog": 1,
    "the lazy dog": 1,
    "lazy dog": 1,
    "jumps over the lazy dog": 1,
    "over the lazy dog": 1,
    "fox jumps over the lazy dog": 1,
    "brown fox jumps over the lazy dog": 1,
    "quick brown fox jumps over the lazy dog": 1,
    "the quick brown fox jumps over the lazy dog": 1,
}


def test_multi_n_gram_frequency():
    test_series = pd.Series(test_data)
    n_gram_series = multi_n_gram_frequency(test_series)
    n_gram_series.to_csv(temp_output / "n_gram_count.csv")
    expected_data_series = pd.Series(data=expected_data)
    assert_series_equal(n_gram_series, expected_data_series)
