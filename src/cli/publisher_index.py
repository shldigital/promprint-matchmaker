"""Create a grouped index of publishers from a cleaned collection."""

import numpy as np
import pandas as pd
from lib.helpers import match_score
from pathlib import Path

expected_columns = ["clean_publisher"]


def main(
    collection_paths: list[Path],
    output_folder: Path,
    N: int = 20,
    score_threshold: int = 90,
):
    """
    Create a grouped index of publishers from a cleaned collection.

    The index groups entities that have misspellings or spelling drifts such
    that common publishing entities may be referred to via single index.

    :param collection_paths: List of Paths to csv file containing register
      or catalog data, publishers from each of these files will be collected
    :type collection_path: pathlib.Path
    :param output_folder: Path to folder where results will be save as csv
    :type collection_path: pathlib.Path
    :param N: Check only the top N most frequent publisher names for grouping
    :type N: int
    :param score_threshold: Only publisher strings with similarity score greather
      than this threshold are grouped
    """
    publishers_df = pd.DataFrame()
    for path in collection_paths:
        df = pd.read_csv(path, sep=("\t" if "tsv" in str(path) else ","))
        if not all(name in df.columns for name in expected_columns):
            raise KeyError(
                f"Input file '{path}' does not have relevant columns: {expected_columns}"
            )
        publishers_df = pd.concat(
            [publishers_df, df.filter(expected_columns, axis=1).astype("str")]
        )
    publisher_frequency_df = (
        publishers_df["clean_publisher"].value_counts().reset_index()
    )
    pf_working = publisher_frequency_df.copy().drop(columns=["count"])

    top_publishers_df = publisher_frequency_df.head(N)
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

    publishers_df["indexed_publisher"] = publishers_df["clean_publisher"]
    publishers_df["id_pub_score"] = np.nan

    publisher_frequency_df.to_csv(output_folder / "publisher_frequency.csv")
    matches.to_csv(output_folder / "publisher_index.csv")
