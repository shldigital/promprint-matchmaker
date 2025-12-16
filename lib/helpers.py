"""Helper functions for text matching."""
import pandas as pd
import typesense

from lib.typesense_search import make_query_subset
from thefuzz import fuzz


def match_score(text_1: str, text_2: str) -> int:
    """
    Return the similary score of two input texts.

    Expects cleaned, space separated tokens for each text input
    Shorter texts are only matched at the beginning of longer texts.

    :param text_1: First piece of text to match
    :type text_1: str
    :param text_2: Second piece of text to match
    :type text_2: str
    :return: Match score indicating how similar the texts are
    :rtype: int
    """
    toks = [text_1.split(" "), text_2.split(" ")]
    toks.sort(key=len)
    if len(toks[0]) < 4:
        text_1 = " ".join(toks[0])
        text_2 = " ".join(toks[1][:4])
    return fuzz.partial_ratio(text_1, text_2)


def match_titles(
        register_row: tuple[str, pd.Series],
        collection: pd.DataFrame,
        register: pd.DataFrame,
        score_threshold: int,
        word_threshold: int,
        command: str,
        client: typesense.Client = None,
) -> pd.DataFrame:
    """
    Search for the title given in register_row in the given collection.

    The register row must include a "clean_title" column to search with
    Returns matches that are above score_threshold in similarity.

    :param register_row: tuple of row index plus row data (the output of pd.DataFrame.iterrows())
    :type register_row: tuple[str, pd.Series]
    :param collection: DataFrame containing the collection entries to search through
    :type pandas.DataFrame
    :param register: DataFrame containing all the register entries
    :type register: pandas.DataFrame
    :param score_threshold: Only return matches with a similarity score above this value
    :type score_threshold: int
    :param word_threshold: Titles in the collection must be this length or longer to be considered for matching
    :type word_threshold: int
    :param command: "local" uses a collection loaded from file, "typesense" uses a collection indexed on a typesense instance
    :type command: str
    :param client: if command is "typesense" then this is a client collection to the typesense instance hosting the collection
    """
    match_columns = [
        "id_register",
        "id_collection",
    ]
    index, row = register_row
    title = row["clean_title"]
    row_id = index
    matches = pd.DataFrame(columns=match_columns)
    if not isinstance(title, str):
        return matches
    if command == "typesense":
        collection = make_query_subset(title, collection, 2, client)
    min_len = collection["clean_title"].map(lambda t: len(t.split(" ")) >= word_threshold)
    collection = collection[min_len]
    if collection.shape[0] > 0:
        matches["id_collection"] = collection.index
        scores = collection["clean_title"].apply(lambda t: match_score(title, t))
        scores.name = "score"
        matches = matches.join(scores, on="id_collection")
        matches = matches[matches["score"] > score_threshold]
        matches["id_register"] = pd.Series([row_id] * matches.shape[0], index=matches.index)
        matches = matches.join(
            collection, on="id_collection", lsuffix='_register', rsuffix='_collection')
        matches = matches.set_index("id_register")
        matches = register.join(
            matches, how="inner", lsuffix="_register", rsuffix='_collection')
        matches = matches.sort_values(by='score', ascending=False)
    return matches
