"""Find register's hall entries in registers of library data."""

import datetime
import pandas as pd

from functools import partial
from lib.helpers import apply_publishers_index
from lib.matching import match_titles
from multiprocessing import Pool
from pathlib import Path
from typing import Any

register_columns = [
    "register",
    "block",
    "page",
    "line",
    "title",
    "publisher",
    "creator",
    "clean_title",
]


def main(
    debug: bool,
    register: Path,
    collection: Path,
    outpath: Path,
    score_threshold: int,
    word_threshold: int,
    processes: int,
    publishers_index: Path = None,
    **kwargs: Any,
) -> None:
    """
    Create one file each for lists of matched entries (brief), matched entries (full)
    and unmatched entries.

    The brief matched entries will only provide the top match, the full matched entries
    provides every match that is above the `score_threshold`, and unmatched entries
    provides every entry that had no matches scoring above the `score_threshold`.

    :param debug: Log debug info
    :type debug: bool
    :param register: Cleaned stationers register data in csv format
    :type register: Path
    :param collection: Cleaned library collecton data, in tsv format
    :type collection: Path
    :param outpath: Path to place the output files in
    :type outpath: Path
    :param score_threshold: matches are only counted if the match score is
      above this threshold
    :type score_threshold: int
    :param word_threshold: Titles in the collection must be this length or
      longer to be considered for matching
    :type word_threshold: int
    :param publishers_index: path to a publisher's index. Providing this will cause
      publisher names in the register and collection files to be replaced by their index
    :type publishers_index: Path
    :param processes: Number of threads to use in search, if > 1 will run searches in parallel
    :type processes: int
    """
    outpath.mkdir(parents=False, exist_ok=True)
    register = pd.read_csv(register)
    if not all(name in register.columns for name in register_columns):
        raise KeyError(
            "Input file does not have the expected columns: " f"{register_columns}"
        )
    register = register.set_index("id")

    collection = pd.read_csv(collection, sep="\t")
    collection = collection.set_index("id")

    if publishers_index:
        publishers_index = pd.read_csv(publishers_index)
        register["indexed_publisher"] = register["clean_publisher"].map(
            lambda p: apply_publishers_index(p, publishers_index)
        )
        collection["indexed_publisher"] = collection["clean_publisher"].map(
            lambda p: apply_publishers_index(p, publishers_index)
        )

    match_titles_p = partial(
        match_titles,
        collection=collection,
        register=register,
        score_threshold=score_threshold,
        word_threshold=word_threshold,
    )

    if processes > 1:
        with Pool(processes) as pool:
            match_list = pool.map(match_titles_p, register.iterrows())
    else:
        match_list = map(match_titles_p, register.iterrows())

    matches: pd.DataFrame = pd.concat(match_list)

    today = datetime.date.today().strftime("%Y-%m-%d")
    register_name = matches["register_register"].iloc[0]
    library_name = matches["source_library"].iloc[0]
    output_base = today + "-" + register_name + "-" + library_name

    matches.to_csv(outpath / (output_base + "-matches.csv"))
    # NB this assumes that results have been sorted descending
    top_matches = matches[~matches.index.duplicated(keep="first")]
    top_matches.to_csv(outpath / (output_base + "-top-matches.csv"))
    unmatched = register.drop(matches.index, axis="index")
    unmatched.to_csv(outpath / (output_base + "-unmatched.csv"))

    n_register = register.shape[0]
    n_unmatched = unmatched.shape[0]
    n_matched = n_register - n_unmatched
    print(f"No. of matched entries: {n_matched}")
    print(f"No. of unmatched entries: {n_unmatched} / {n_register}")
