"""Find register's hall entries in registers of library data."""

import argparse
import datetime
import logging
import pandas as pd

from functools import partial
from lib.helpers import match_titles, apply_publishers_index
from multiprocessing import Pool
from pathlib import Path


logger = logging.getLogger("")
logging.basicConfig(
    level=logging.INFO,
    filename="promprint-matchmaker.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",
)

console = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)

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


parser = argparse.ArgumentParser(
    description="Find register's hall entries in collections of library data"
)

parser.add_argument(
    "register",
    type=lambda p: Path(p),
    help="File of cleaned register data in csv format",
)
parser.add_argument(
    "collection",
    type=lambda p: Path(p),
    help="File of cleaned collection data in tsv format",
)
parser.add_argument("outpath", type=lambda p: Path(p), help="Output file location")

parser.add_argument("-d", "--debug", action="store_true", help="Print debug messages")
parser.add_argument(
    "--publishers_index",
    type=lambda p: Path(p),
    help="File of publisher index used to replace publisher strings with more common names",
)
parser.add_argument(
    "-t",
    "--score_threshold",
    type=int,
    default=79,
    help="Threshold fuzzy matching score (0-100), only keep matches with scores above this value",
)
parser.add_argument(
    "-w",
    "--word_threshold",
    type=int,
    default=2,
    help="Threshold number of words/tokens for a collection title to be considered for matching",
)
parser.add_argument(
    "-p",
    "--processes",
    type=int,
    default=1,
    help="Number of threads to use in search, if > 1 will run searches in parallel",
)


def main(args=None) -> None:
    """Entry point for matchmaking functions."""
    args = parser.parse_args(args)

    if args.debug:
        console.setLevel(logging.INFO)
    else:
        console.setLevel(logging.WARNING)
    logging.getLogger("").addHandler(console)

    args.outpath.mkdir(parents=False, exist_ok=True)

    register = pd.read_csv(args.register)
    if not all(name in register.columns for name in register_columns):
        raise KeyError(
            "Input file does not have the expected columns: " f"{register_columns}"
        )
    register = register.set_index("id")

    collection = pd.read_csv(args.collection, sep="\t")
    collection = collection.set_index("id")

    if args.publishers_index:
        publishers_index = pd.read_csv(args.publishers_index)
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
        score_threshold=args.score_threshold,
        word_threshold=args.word_threshold,
    )

    if args.processes > 1:
        with Pool(args.processes) as pool:
            match_list = pool.map(match_titles_p, register.iterrows())
    else:
        match_list = map(match_titles_p, register.iterrows())

    matches: pd.DataFrame = pd.concat(match_list)

    today = datetime.date.today().strftime("%Y-%m-%d")
    register_name = matches["register_register"].iloc[0]
    library_name = matches["source_library"].iloc[0]
    output_base = today + "-" + register_name + "-" + library_name

    matches.to_csv(args.outpath / (output_base + "-matches.csv"))
    # NB this assumes that results have been sorted descending
    top_matches = matches[~matches.index.duplicated(keep="first")]
    top_matches.to_csv(args.outpath / (output_base + "-top-matches.csv"))
    unmatched = register.drop(matches.index, axis="index")
    unmatched.to_csv(args.outpath / (output_base + "-unmatched.csv"))

    n_register = register.shape[0]
    n_unmatched = unmatched.shape[0]
    n_matched = n_register - n_unmatched
    print(f"No. of matched entries: {n_matched}")
    print(f"No. of unmatched entries: {n_unmatched} / {n_register}")


if __name__ == "__main__":
    main()
