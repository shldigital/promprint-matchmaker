import matplotlib.pyplot as plt
from lib.helpers import collect_columns
from lib.n_gram import multi_n_gram_frequency, sort_n_grams_by_degree
from pathlib import Path
from typing import Any


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
    :param columns: Which data columns to create n-gram lists from, must exist in both catalogs
    :type columns: list[str]
    :param n_top: Output a filtered list of only the n_top most frequent n-grams
    :type n_top: int
    :param score_threshold: n-grams with similarity higher than this threshold are
      grouped together
    :type score_threshold: int
    """
    outpath.mkdir(parents=False, exist_ok=True)
    collected_df = collect_columns(catalog, columns)
    for column in columns:
        token_list = collected_df[column].str.split()
        n_gram_frame = multi_n_gram_frequency(token_list)
        basename = f"n_gram_{column}"
        list_file = basename + ".csv"
        n_gram_frame.loc[n_gram_frame["count"] > 2].to_csv(outpath / list_file)

        n_gram_top = n_gram_frame.iloc[:n_top]
        top_file = basename + "_top.csv"
        n_gram_top.to_csv(outpath / top_file)

        n_gram_top_ordered = sort_n_grams_by_degree(n_gram_top)
        ordered_file = basename + "_top_ordered.csv"
        n_gram_top_ordered.to_csv(outpath / ordered_file)

        n_gram_top_plot = n_gram_top["count"].set_axis(range(n_top), axis=0)

        fig, ax = plt.subplots()
        ax.bar(
            n_gram_top_plot.index,
            n_gram_top_plot,
            width=1,
            edgecolor="white",
            linewidth=0.7,
        )
        graph_file = basename + "_top.png"
        plt.savefig(outpath / graph_file)
