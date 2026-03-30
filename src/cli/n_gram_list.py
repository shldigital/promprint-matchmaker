import matplotlib.pyplot as plt
import pandas as pd
from lib.n_gram import multi_n_gram_frequency, sort_n_grams_by_degree
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
    catalog: list[Path],
    columns: list[str],
    n_top: int,
    score_threshold: int,
    debug: bool = False,
    **kwargs: Any,
):
    """
    Create a list and plot of top n-grams that appear in the selected columns of each catalog.

    :param outpath: Path to the compiled list of top n-grams, saved as csv
    :type outpath: pathlib.Path
    :param catalog: List of Paths to files containing catalog data
    :type catalog: pathlib.Path
    :param n_top: Output a filtered list of only the n_top most frequent n-grams
    :type n_top: int
    :param score_threshold: n-grams with similarity higher than this threshold are
      grouped together
    :type score_threshold: int
    """
    outpath.mkdir(parents=False, exist_ok=True)
    collected_df = collect_columns(catalog, columns)
    token_list = collected_df["clean_title"].str.split()
    n_gram_frame = multi_n_gram_frequency(token_list)
    n_gram_frame.loc[n_gram_frame["count"] > 2].to_csv(outpath / "n_gram_list.csv")

    n_gram_top = n_gram_frame.iloc[:n_top]
    n_gram_top.to_csv(outpath / "n_gram_top.csv")

    n_gram_top_ordered = sort_n_grams_by_degree(n_gram_top)
    n_gram_top_ordered.to_csv(outpath / "n_gram_top_ordered.csv")

    n_gram_top_plot = n_gram_top["count"].set_axis(range(n_top), axis=0)

    fig, ax = plt.subplots()
    ax.bar(
        n_gram_top_plot.index,
        n_gram_top_plot,
        width=1,
        edgecolor="white",
        linewidth=0.7,
    )
    plt.savefig(outpath / "top_n_grams.png")
