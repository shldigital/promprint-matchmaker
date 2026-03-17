import numpy as np
import pandas as pd
from lib.helpers import match_score
from pathlib import Path
from typing import Any


def collect_columns(data_paths: list[Path], columns: list[str]) -> pd.DataFrame:
    """
    Load a list dataframes and collect columns from each into one dataframe.

    :param data_paths: List of Paths to files containing data
    :type data_paths: pathlib.Path
    :param columns: Columns to extract from each of the files. Throws if a column
      is missing
    :type columns: list[str]
    """
    collected_df = pd.DataFrame()
    for path in data_paths:
        df = pd.read_csv(path, sep=("\t" if "tsv" in str(path) else ","))
        if not all(name in df.columns for name in columns):
            raise KeyError(
                f"Input file '{path}' does not have relevant columns: {columns}"
            )
        collected_df = pd.concat(
            [collected_df, df.filter(columns, axis=1).astype("str")]
        )
    return collected_df


def main(
    outpath: Path,
    catalogs: list[Path],
    columns: list[str],
    n_top: int,
    score_threshold: int,
    debug: bool = False,
    **kwargs: Any,
):
    """
    Create a list of top n-grams that appear in the selected column of each catalog.

    :param outpath: Path to the compiled list of top n-grams, saved as csv
    :type outpath: pathlib.Path
    :param catalogs: List of Paths to files containing catalog data,
      n-grams from each of these files will be collected
    :type catalogs: pathlib.Path
    :param n_top: Check only the n_top most frequent n-grams
    :type n_top: int
    :param score_threshold: n-grams with similarity higher than this threshold are
      grouped together
    :type score_threshold: int
    """
    # TODO: This section is reusable, e.g. in publishers index: should be a function
    outpath.mkdir(parents=False, exist_ok=True)
    collected_df = collect_columns(catalogs, columns)
    collected_df.to_csv(outpath / "n_gram_list.csv")
