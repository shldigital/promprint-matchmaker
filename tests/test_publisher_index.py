import glob
import pandas as pd
import pytest

from pathlib import Path
from src.cli.publisher_index import main, expected_columns

test_register = Path("./tests/test_files/test_register_cleaned.csv")
no_publisher_column = Path("./tests/test_files/test_register_no_publisher.csv")
new_columns = ["id_pub_score", "indexed_publisher"]
temporary_test_path = Path("./tests/test_files/")


def test_outputs_csv_file(tmp_path):
    main(test_register, tmp_path)
    outputs = glob.glob(str(tmp_path) + "/*.csv")
    assert len(outputs) > 0


def test_raises_key_error_on_bad_columns(tmp_path):
    with pytest.raises(KeyError):
        main(no_publisher_column, tmp_path)


def test_outputs_new_columns(tmp_path):
    main(test_register, tmp_path)
    publishers_df = pd.read_csv(tmp_path / "publishers.csv")
    output_columns = expected_columns + new_columns
    assert all(col in publishers_df.columns for col in output_columns)


def test_outputs_publisher_frequencies(tmp_path):
    main(test_register, temporary_test_path)
    publisher_frequency_df = pd.read_csv(temporary_test_path / "publisher_frequency.csv")
    assert (
        publisher_frequency_df["clean_publisher"][0] == "simpkin and co"
        and publisher_frequency_df["count"][0] == 395
    )


def test_outputs_publisher_index(tmp_path):
    main(test_register, temporary_test_path)
    publisher_index_df = pd.read_csv(temporary_test_path / "publisher_index.csv", index_col=0)
    expected_data = {
        "clean_publisher": ["simpkin", "simpkin and marshall"],
        "match_score": [100, 92],
        "common_name": ["simpkin and co", "simpkin and co"],
    }
    expected_df = pd.DataFrame(data=expected_data, index=[561, 42])
    for index, row in expected_df.iterrows():
        assert publisher_index_df.loc[index].equals(row)
