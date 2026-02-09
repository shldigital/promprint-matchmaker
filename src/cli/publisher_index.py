"""Create a grouped index of publishers from a cleaned collection."""

import numpy as np
import pandas as pd
from lib.helpers import match_score
from pathlib import Path

expected_columns = ["id", "publisher", "clean_publisher"]


def main(collection_path: Path, output_folder: Path):
    """
    Create a grouped index of publishers from a cleaned collection.

    The index groups entities that have misspellings or known name changes such
    that common publishing entities may be referred to via single index.

    :param collection_path: Path to csv file containing register or catalog data
    :type collection_path: pathlib.Path
    :param output_folder: Path to folder where results will be save as csv
    :type collection_path: pathlib.Path
    """
    df = pd.read_csv(collection_path)
    if not all(name in df.columns for name in expected_columns):
        raise KeyError(f"Input file does not have relevant columns: {expected_columns}")
    publishers_df = df.filter(expected_columns, axis=1).astype("str")
    publishers_df.set_index("id")

    publisher_frequency_df = (
        publishers_df["clean_publisher"].value_counts().reset_index()
    )
    publisher_frequency_df.to_csv(output_folder / "publisher_frequency.csv")

    top_publishers_df = publisher_frequency_df.head(10)
    matches = pd.DataFrame()
    for publisher in top_publishers_df["clean_publisher"]:
        scores = publisher_frequency_df.copy()
        scores["match_score"] = publisher_frequency_df["clean_publisher"].apply(
            lambda p: match_score(publisher, p)
        )
        scores["common_name"] = publisher
        scores = scores[scores["match_score"] > 90]
        matches = pd.concat([matches, scores])

    publishers_df["indexed_publisher"] = publishers_df["clean_publisher"]
    publishers_df["id_pub_score"] = np.nan
    publishers_df.to_csv(output_folder / "publishers.csv")
    matches.to_csv(output_folder / "publisher_index.csv")
