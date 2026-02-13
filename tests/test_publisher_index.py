import glob
import pandas as pd
import pytest

from pathlib import Path
from src.cli.publisher_index import main

test_register = Path("./tests/test_files/test_register_cleaned.csv")
test_collection = Path("./tests/test_files/test_collection_cleaned.tsv")
no_publisher_column = Path("./tests/test_files/test_register_no_publisher.csv")
temporary_test_path = Path("./tests/")


def test_outputs_csv_file(tmp_path):
    main([test_register, test_collection], tmp_path)
    outputs = glob.glob(str(tmp_path) + "/*.csv")
    assert len(outputs) > 0


def test_raises_key_error_on_bad_columns(tmp_path):
    with pytest.raises(KeyError):
        main([no_publisher_column], tmp_path)


def test_outputs_publisher_frequencies(tmp_path):
    main([test_register, test_collection], temporary_test_path)
    publisher_frequency_df = pd.read_csv(
        temporary_test_path / "publisher_frequency.csv"
    )
    assert (
        publisher_frequency_df["clean_publisher"][0] == "simpkin and co"
        and publisher_frequency_df["count"][0] == 395
    )


def test_outputs_publisher_index(tmp_path):
    main([test_register, test_collection], temporary_test_path)
    publisher_index_df = pd.read_csv(
        temporary_test_path / "publisher_index.csv", index_col=0
    )
    expected_data = {
        "clean_publisher": ["simpkin", "simpkin and marshall"],
        "match_score": [100, 92],
        "common_name": ["simpkin and co", "simpkin and co"],
    }
    expected_df = pd.DataFrame(data=expected_data, index=[1296, 44])
    for index, row in expected_df.iterrows():
        assert publisher_index_df.loc[index].equals(row)
