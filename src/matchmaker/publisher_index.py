"""Create a grouped index of publishers from a cleaned collection."""

import numpy as np
import pandas as pd
from functools import partial
from lib.helpers import collect_columns
from lib.matching import match_score, n_gram_substring_match
from math import floor
from pathlib import Path
from typing import Any

expected_columns = ["clean_publisher"]
publisher_blacklist = [
    "london",
    "oxford",
    "edinburgh",
    "paris",
    "dublin",
    "cambridge",
    "glasgow",
    "nan",
    "s l",
    "society",
    "manchester",
    "new york",
    "london s n",
    "office",
    "s l s n",
    "liverpool",
    "edinburgh s n",
    "scotland s n",
    "philadelphia",
    "aberdeen",
    "leipzig",
    "washington",
    "glasgow s n",
    "berlin",
    "richmond",
    "birmingham",
    "milano",
    "philadelphia s n",
    "south kensington",
    "halifax",
    "londres",
    "bristol",
    "dublin s n",
    "stuttgart",
    "bath",
    "madrid",
    "n p",
    "new york s n",
    "wien",
    "london s p c k",
    "washington d c s n",
    "boston",
    "salisbury",
    "calcutta",
    "exeter",
    "mu nchen",
    "boston mass" "stockholm",
    "u s s n",
    "dundee",
    "leeds",
    "sheffield",
    "derby",
    "brighton",
    "boston s n",
    "norwich",
    "do",
    "albany",
    "durham",
    "preston",
    "rochdale",
    "belfast",
    "hamburg",
    "stirling",
    "sunderland",
    "southampton",
    "york",
    "melbourne",
    "england s n",
    "washington d c g p o",
    "lisboa",
    "toronto",
    "madras",
    "institute",
    "dresden",
    "bombay",
    "tunbridge wells",
    "bordeaux",
    "torino",
    "northampton",
    "hannover",
    "amsterdam",
    "lancaster",
    "leicester",
    "gloucester",
    "reading",
    "chicago",
    "enfield",
    "chester",
    "chelmsford",
    "westminster",
    "bombay",
    "winchester",
    "hull",
    "portsea",
    "roma",
    "perth",
    "charlottetown",
    "portsmouth",
    "reigate",
]


def main(
    outpath: Path,
    collections: list[Path],
    n_top: int,
    score_threshold: int,
    n_gram_index: Path = None,
    debug: bool = False,
    **kwargs: Any,
) -> None:
    """
    Create a grouped index of publishers from a cleaned collection.

    The index groups entities that have misspellings or spelling drifts such
    that common publishing entities may be referred to via single index.

    :param outpath: Path to folder where results will be save as csv
    :type collection_path: pathlib.Path
    :param collections: List of Paths to csv or tsv file containing register
      or catalog data, publishers from each of these files will be collected
    :type collections: pathlib.Path
    :param n_top: Check only the top N most frequent publisher names for grouping
    :type n_top: int
    :param score_threshold: Only publisher strings with similarity score greather
      than this threshold are grouped
    :type score_threshold: int
    :param n_gram_index: Index of common n-grams found in the publisher column.
      This is used to refine matching when publisher names contain very common
      n-gram substrings
    :type n_gram_index: Path
    """
    outpath.mkdir(parents=False, exist_ok=True)
    publishers_df = collect_columns(collections, expected_columns)
    publisher_frequency_df = (
        publishers_df["clean_publisher"]
        .value_counts()
        .drop(publisher_blacklist, errors="ignore")
        .reset_index()
    )
    n_publishers = publisher_frequency_df.shape[0]

    pf_working = publisher_frequency_df.copy().drop(columns=["count"])

    top_publishers_df = publisher_frequency_df.head(n_top)

    matches = pd.DataFrame()
    for publisher_row in top_publishers_df.iterrows():
        index, row = publisher_row
        publisher = row["clean_publisher"]
        pf_working.drop(index, inplace=True)
        scores = pf_working.copy()
        scores["match_score"] = pf_working["clean_publisher"].apply(
            lambda p: match_score(publisher, p)
        )
        scores["common_name"] = publisher
        scores = scores[scores["match_score"] > score_threshold]
        matches = pd.concat([scores, matches])

    if n_gram_index is not None:
        n_gram_df = pd.read_csv(n_gram_index, index_col=0)
        substring_match_p = partial(
            n_gram_substring_match,
            n_gram_data=n_gram_df,
            match_col_1="clean_publisher",
            match_col_2="common_name",
            score_threshold=score_threshold,
            n_gram_count_cutoff=floor(
                n_publishers / 1000
            ),

        )

        match_list = map(substring_match_p, matches.iterrows())

        matches: pd.DataFrame = pd.concat(match_list)

    # TODO: issue this up
    publishers_df["indexed_publisher"] = publishers_df["clean_publisher"]
    publishers_df["id_pub_score"] = np.nan

    publisher_frequency_df.to_csv(outpath / "publisher_frequency.csv")
    matches.to_csv(outpath / "publisher_index.csv")
