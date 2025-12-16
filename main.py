"""Find register's hall entries in registers of library data."""
import argparse
import logging
import os
import pandas as pd
import typesense

from dotenv import load_dotenv
from functools import partial
from lib.helpers import match_titles
from multiprocessing import Pool
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load env variables from .env file if defined
env_path = BASE_DIR / ".env"
load_dotenv(env_path, override=True)

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
parser.add_argument('outpath',
                    type=lambda p: Path(p),
                    help='Output file location')


parser.add_argument('-d', '--debug',
                    action='store_true',
                    help='Print debug messages')
parser.add_argument('-c', '--collection',
                    type=str,
                    default='nls',
                    choices=['nls'],
                    help="Name of collection to search in")
parser.add_argument('-t', '--score_threshold',
                    type=int,
                    default=79,
                    help="Threshold fuzzy matching score, keep scores above this")

parser.add_argument('-w', '--word_threshold',
                    type=int,
                    default=2,
                    help="Threshold number of words/tokens for a collection title to be considered for matching")

parser.add_argument('-p', '--processes',
                    type=int,
                    default=1,
                    help="Number of threads to use in search, if > 1 will run searches in parallel")

subparsers = parser.add_subparsers(help="Search algorithms to use",
                                   dest='command')

subparsers.required = True

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

local_parser = subparsers.add_parser('local',
                                     help='Use full local collection')
local_parser.add_argument('collection',
                          type=lambda p: Path(p),
                          help='File of cleaned collection data in tsv format')


def main(args=None) -> None:
    """Entry point for matchmaking functions."""
    args = parser.parse_args(args)

    if args.debug:
        console.setLevel(logging.INFO)
    else:
        console.setLevel(logging.WARNING)
    logging.getLogger('').addHandler(console)

    register = pd.read_csv(args.register)
    if not all(name in register.columns for name in register_columns):
        raise KeyError("Input file does not have the expected columns: "
                       f"{register_columns}")
    register = register.set_index("id")

    client: typesense.Client = None
    if args.command == "typesense":
        API_KEY = os.environ.get('TYPESENSE_KEY', args.key)
        HOSTNAME = os.environ.get('TYPESENSE_HOST', args.address)
        PORT = os.environ.get('TYPESENSE_PORT', args.port)
        client = typesense.Client({
            'api_key': API_KEY,
            'nodes': [{
                'host': HOSTNAME,
                'port': PORT,
                'protocol': 'http'
            }],
            'connection_timeout_seconds': 2
        })

    collection = pd.DataFrame()
    if args.command == "local":
        collection = pd.read_csv(args.collection, sep='\t')
        collection = collection.set_index("id")

    match_titles_p = partial(match_titles,
                             collection=collection,
                             register=register,
                             score_threshold=args.score_threshold,
                             word_threshold=args.word_threshold,
                             command=args.command,
                             client=client)

    if args.processes > 1:
        with Pool(args.processes) as pool:
            match_list = pool.map(match_titles_p, register.iterrows())
    else:
        match_list = map(match_titles_p, register.iterrows())

    matches: pd.DataFrame = pd.concat(match_list)
    matches.to_csv(args.outpath / "matches.csv")
    unmatched = register.drop(matches.index, axis='index')
    unmatched.to_csv(args.outpath / "unmatched.csv")

    n_register = register.shape[0]
    n_unmatched = unmatched.shape[0]
    n_matched = n_register - n_unmatched
    print(f'No. of matched entries: {n_matched}')
    print(f'No. of unmatched entries: {n_unmatched} / {n_register}')


if __name__ == "__main__":
    main()
