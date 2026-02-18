import pytest

from matchmaker.main import main

register_file = "./tests/test_files/test_register_short.csv"
collection_file = "./tests/test_files/test_collection_short.tsv"
bad_register_file = "./tests/test_files/bad_file.txt"
publisher_index_file = "./tests/test_files/test_publisher_index.csv"


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


def test_publishers_single_collection_does_not_raise(tmp_path):
    test_args = [
        "publishers",
        str(tmp_path),
        register_file
    ]
    main(test_args)


def test_publishers_multiple_collections_do_not_raise(tmp_path):
    test_args = [
        "publishers",
        str(tmp_path),
        register_file,
        collection_file
    ]
    main(test_args)


def test_publishers_no_collections_raises(tmp_path):
    test_args = [
        "publishers",
        str(tmp_path)
    ]
    with pytest.raises(SystemExit):
        main(test_args)


def test_publishers_bad_collection_raises(tmp_path):
    test_args = [
        "publishers",
        str(tmp_path),
        bad_register_file
    ]
    with pytest.raises(KeyError):
        main(test_args)
