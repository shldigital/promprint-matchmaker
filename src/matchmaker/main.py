"""
CLI to Find register's hall entries in registers of library data or
create a publishers index.
"""

import argparse
import logging

from cli import publisher_index, titles_match
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


def main(args=None) -> None:
    """Entry point for matchmaking functions."""
    parser = argparse.ArgumentParser(
        description="Find register's hall entries in collections of library data"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Print debug messages"
    )

    subparsers = parser.add_subparsers(help="Matching subjects")

    titles_parser = subparsers.add_parser(
        "titles", help="Match titles in register to those in a collection"
    )
    titles_parser.add_argument(
        "register",
        type=lambda p: Path(p),
        help="File of cleaned register data in csv format",
    )
    titles_parser.add_argument(
        "collection",
        type=lambda p: Path(p),
        help="File of cleaned collection data in tsv format",
    )
    titles_parser.add_argument(
        "outpath", type=lambda p: Path(p), help="Output file location"
    )

    titles_parser.add_argument(
        "--publishers_index",
        type=lambda p: Path(p),
        help="File of publisher index used to replace publisher strings with more common names",
    )
    titles_parser.add_argument(
        "-t",
        "--score_threshold",
        type=int,
        default=79,
        help="Threshold fuzzy matching score (0-100), only keep matches with scores above this value",
    )
    titles_parser.add_argument(
        "-w",
        "--word_threshold",
        type=int,
        default=2,
        help="Threshold number of words/tokens for a collection title to be considered for matching",
    )
    titles_parser.add_argument(
        "-p",
        "--processes",
        type=int,
        default=1,
        help="Number of threads to use in search, if > 1 will run searches in parallel",
    )

    titles_parser.set_defaults(func=titles_match.main)

    publishers_parser = subparsers.add_parser(
        "publishers",
        help="Create a publishers index by grouping similar publisher names",
    )
    publishers_parser.add_argument(
        "outpath", type=lambda p: Path(p), help="Output file location"
    )

    publishers_parser.add_argument(
        "collections",
        nargs='+',
        type=lambda p: Path(p),
        help="Path to collections with publishers to be collated",
    )
    publishers_parser.add_argument(
        "-n",
        "--n_top",
        type=int,
        default=20,
        help="Group similar matches for only the n_top most frequent publisher names",
    )
    publishers_parser.add_argument(
        "-t",
        "--score_threshold",
        type=int,
        default=90,
        help="Threshold fuzzy matching score (0-100), only keep matches with scores above this value",
    )

    publishers_parser.set_defaults(func=publisher_index.main)

    args = parser.parse_args(args)

    if args.debug:
        console.setLevel(logging.INFO)
    else:
        console.setLevel(logging.WARNING)
    logging.getLogger("").addHandler(console)

    args.func(**vars(args))


if __name__ == "__main__":
    main()
