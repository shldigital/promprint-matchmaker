import glob
import pandas as pd
import pytest

from src.cli.n_gram_list import main
from lib.n_gram import n_gram_frequency
from pandas.testing import assert_series_equal
from pathlib import Path

test_collections = [
    Path("./tests/test_files/test_collection_cleaned.tsv"),
    Path("./tests/test_files/test_register_cleaned.csv"),
]
temp_output = Path("./tests/output_examples")
single_and_multi_file = [[test_collections[0]], test_collections]


@pytest.mark.parametrize(
    "test_paths", single_and_multi_file, ids=["single", "multiple"]
)
def test_single_and_multi_file(test_paths, tmp_path):
    main(tmp_path, test_paths, ["clean_title"], 20, 100)
    outputs = glob.glob(str(tmp_path) + "/*.csv")
    assert len(outputs) > 0


def test_missing_column_throws(tmp_path):
    with pytest.raises(KeyError):
        main(tmp_path, test_collections, ["spurious_column"], 20, 100)


test_column = [
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

expected_frequencies = {
    "the": 12,
    "quick": 8,
    "brown": 7,
    "fox": 6,
    "jumps": 5,
    "over": 4,
    "lazy": 2,
    "dog": 1,
}


def test_n_gram_frequency():
    test_series = pd.Series(test_column)
    n_gram_df = n_gram_frequency(test_series, 1)
    n_gram_df.to_csv(temp_output / "n_gram_count.csv")
    expected_frequencies_series = pd.Series(data=expected_frequencies)
    expected_frequencies_series.name = "count"
    assert_series_equal(n_gram_df, expected_frequencies_series)
