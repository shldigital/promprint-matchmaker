"""Find register's hall entries in registers of library data."""
import argparse
import logging
import os
import pandas as pd
import typesense

from dotenv import load_dotenv
from lib.typesense_search import search
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
parser.add_argument('-d', '--debug',
                    action='store_true',
                    help='Print debug messages')
parser.add_argument('-c', '--collection',
                    type=str,
                    default='nls',
                    choices=['nls'],
                    help="Name of collection to search in")

subparsers = parser.add_subparsers(help="Search algorithms to use",
                                   dest='command')
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

    register = pd.read_csv(args.register)
    if not all(name in register.columns for name in register_columns):
        raise KeyError("Input file does not have the expected columns: "
                       f"{register_columns}")

    client: typesense.Client = None
    if args.command == typesense:
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

    match_columns = [
        "id",
        "clean_title",
        "score",
        "num_tokens_dropped",
        "tokens_matched",
        "typo_prefix_score"
    ]
    matches = pd.DataFrame(columns=match_columns)
    unmatched = pd.DataFrame(columns=["id", "clean_title"])
    for title in register["clean_title"]:
        if args.command == typesense:
            pass


if __name__ == "__main__":
    main()
