import pytest

from main import main

register_file = "./tests/test_files/test_register_export.csv"
bad_register_file = "./tests/test_files/bad_file.txt"


def test_loads_register(tmp_path):
    test_args = [register_file, str(tmp_path)]
    main(test_args)


def test_bad_file_raises(tmp_path):
    test_args = [bad_register_file, str(tmp_path)]
    with pytest.raises(KeyError):
        main(test_args)
