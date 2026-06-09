import glob
import pandas as pd
import pytest

from pathlib import Path
from src.cli.publisher_index import main

test_register = Path("./tests/test_files/test_register_cleaned.csv")
test_collection = Path("./tests/test_files/test_collection_cleaned.tsv")
no_publisher_column = Path("./tests/test_files/test_register_no_publisher.csv")
n_gram_index = Path("./tests/test_files/test_publisher_n_gram_index.csv")
temporary_test_path = Path("./tests/")


def test_outputs_csv_file(tmp_path):
    main(tmp_path, [test_register, test_collection], 20, 90)
    outputs = glob.glob(str(tmp_path) + "/*.csv")
    assert len(outputs) > 0


def test_raises_key_error_on_bad_columns(tmp_path):
    with pytest.raises(KeyError):
        main(tmp_path, [no_publisher_column], 20, 90)


def test_outputs_publisher_frequencies(tmp_path):
    main(tmp_path, [test_register, test_collection], 20, 90)
    publisher_frequency_df = pd.read_csv(tmp_path / "publisher_frequency.csv")
    assert (
        publisher_frequency_df["clean_publisher"][0] == "simpkin and co"
        and publisher_frequency_df["count"][0] == 395
    )


def test_outputs_publisher_index(tmp_path):
    main(tmp_path, [test_register, test_collection], 20, 90)
    publisher_index_df = pd.read_csv(tmp_path / "publisher_index.csv", index_col=0)
    expected_data = {
        "clean_publisher": ["simpkin", "simpkin and marshall"],
        "match_score": [100, 92],
        "common_name": ["simpkin and co", "simpkin and co"],
    }
    expected_df = pd.DataFrame(data=expected_data, index=[1296, 44])
    for index, row in expected_df.iterrows():
        assert publisher_index_df.loc[index].equals(row)


def test_publisher_index_with_n_gram_check(tmp_path):
    main(tmp_path, [test_register, test_collection], 20, 90, n_gram_index)
    publisher_index_df = pd.read_csv(tmp_path / "publisher_index.csv", index_col=0)
    expected_data = {
        "clean_publisher": ["simpkin", "simpkin and marshall"],
        "match_score": [100, 92],
        "common_name": ["simpkin and co", "simpkin and co"],
        "n-gram match": [True, True],
        "n-gram": ["simpkin", "simpkin and"],
        "substring score": [100, 0],
        "match": [True, False],
    }
    expected_df = pd.DataFrame(data=expected_data, index=[1296, 44])
    for index, row in expected_df.iterrows():
        print(publisher_index_df.loc[index])
        assert publisher_index_df.loc[index].equals(row)
