"""Find register's hall entries in registers of library data."""

import argparse
import logging
import pandas as pd

from pathlib import Path

logger = logging.getLogger('')
logging.basicConfig(level=logging.INFO,
                    filename="promprint-matchmaker.log",
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='w')

console = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)

register_columns = [
    "register",
    "block",
    "page",
    "line",
    "title",
    "publisher",
    "creator",
    "clean_title"
]


parser = argparse.ArgumentParser(
    description="Find register's hall entries in registers of library data"
)

parser.add_argument('register',
                    type=lambda p: Path(p),
                    help='File of cleaned register data in csv format')
parser.add_argument('-d', '--debug',
                    action='store_true',
                    help='Print debug messages')

subparsers = parser.add_subparsers(help="Search algorithms to use")
typesense_parser = subparsers.add_parser('typesense',
                                         help='Use typesense to search')
typesense_parser.add_argument('-k', '--key',
                              type=str,
                              help="API key for typesense server")
typesense_parser.add_argument('-a', '--address',
                              type=str,
                              default='localhost',
                              help="Host address for typesense server")
typesense_parser.add_argument('-p', '--port',
                              type=int,
                              default=8108,
                              help="Port for typesense server")
typesense_parser.add_argument('-c', '--collection',
                              type=str,
                              default='nls',
                              help="Name of collection to search in")


def main(args=None) -> None:
    """Entry point for matchmaking functions."""
    args = parser.parse_args(args)

    if args.debug:
        console.setLevel(logging.INFO)
    else:
        console.setLevel(logging.WARNING)
    logging.getLogger('').addHandler(console)

    df = pd.read_csv(args.register)
    if not all(name in df.columns for name in register_columns):
        raise KeyError("Input file does not have the expected columns: "
                       f"{register_columns}")


if __name__ == "__main__":
    main()
