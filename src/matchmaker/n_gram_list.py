from lib.helpers import collect_columns, save_run_config
from lib.n_gram import multi_n_gram_frequency
from pathlib import Path
from typing import Any


def main(
    outpath: Path,
    catalog: list[Path],
    columns: list[str],
    n_top: int,
    min_degree: int,
    max_degree: int,
    min_frequency: int,
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
    :param n_top: number of top n-grams to include in the index
    :type n_top: int
    :param min_degree: minimum degree of n-gram to include in output list
    :type min_degree: int
    :param max_degree: maximum degree of n-gram to include in output list
    :type max_degree: int
    :param min_frequency: minimum frequency of n-gram to include in output list
    :type min_frequency: int
    """
    arguments = locals()

    outpath.mkdir(parents=False, exist_ok=True)
    run_metadata = {
        "script": {__file__},
    }
    run_metadata.update(arguments)

    save_run_config(outpath, run_metadata)

    collected_df = collect_columns(catalog, columns)
    for column in columns:
        token_list = collected_df[column].str.split()
        n_gram_frame = multi_n_gram_frequency(
            token_list, min_degree=min_degree, max_degree=max_degree
        )

        basename = f"n_gram_{column}"
        list_file = basename + ".csv"
        n_gram_frame = n_gram_frame.loc[n_gram_frame["count"] > min_frequency]
        n_gram_frame.to_csv(outpath / list_file)

        n_gram_top = n_gram_frame.iloc[:n_top]
        top_file = basename + "_top.csv"
        n_gram_top.to_csv(outpath / top_file)
