import pytest
import pandas as pd

from matchmaker.main import main

register_file = "./tests/test_files/test_register_short.csv"
collection_file = "./tests/test_files/test_collection_short.tsv"
bad_register_file = "./tests/test_files/bad_file.txt"
publisher_index_file = "./tests/test_files/test_publisher_index.csv"
n_gram_index_file = "./tests/test_files/test_n_gram_index.csv"

test_catalog_1 = "./tests/test_files/test_register_short.csv"
test_catalog_2 = "./tests/test_files/test_collection_short.tsv"


def test_titles_good_register_does_not_raise(tmp_path):
    test_args = ["titles", register_file, collection_file, str(tmp_path)]
    main(test_args)


def test_titles_good_register_with_publishers_index_does_not_raise(tmp_path):
    test_args = [
        "titles",
        register_file,
        collection_file,
        str(tmp_path),
        f"--publishers_index={publisher_index_file}",
    ]
    main(test_args)


def test_titles_bad_register_file_raises(tmp_path):
    test_args = [
        "titles",
        bad_register_file,
        collection_file,
        str(tmp_path),
    ]
    with pytest.raises(KeyError):
        main(test_args)


def test_titles_with_n_gram_index(tmp_path):
    test_args = [
        "titles",
        register_file,
        collection_file,
        str(tmp_path),
        f"--n_gram_index={n_gram_index_file}",
    ]
    main(test_args)


def test_publishers_single_collection_does_not_raise(tmp_path):
    test_args = ["publishers", str(tmp_path), register_file]
    main(test_args)


def test_publishers_multiple_collections_do_not_raise(tmp_path):
    test_args = ["publishers", str(tmp_path), register_file, collection_file]
    main(test_args)


def test_publishers_no_collections_raises(tmp_path):
    test_args = ["publishers", str(tmp_path)]
    with pytest.raises(SystemExit):
        main(test_args)


def test_publishers_bad_collection_raises(tmp_path):
    test_args = ["publishers", str(tmp_path), bad_register_file]
    with pytest.raises(KeyError):
        main(test_args)


def test_calling_n_gram_list(tmp_path):
    test_args = ["n_grams", str(tmp_path), test_catalog_1, test_catalog_2]
    outfile = tmp_path / "n_gram_clean_title.csv"
    main(test_args)
    assert outfile.exists()


def test_calling_n_gram_list_with_multiple_columns(tmp_path):
    columns = ["clean_title", "clean_publisher"]
    test_args = [
        "n_grams",
        str(tmp_path),
        test_catalog_1,
        test_catalog_2,
        "--columns",
        *columns,
    ]
    main(test_args)
    for column in columns:
        basename = f"n_gram_{column}.csv"
        outfile = tmp_path / basename
        assert outfile.exists()
