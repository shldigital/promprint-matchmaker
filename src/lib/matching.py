"""Functions for matching entry texts."""

import pandas as pd

from lib.helpers import filter_stop_words
from thefuzz import fuzz
from typing import Optional


def match_score(text_1: str, text_2: str, short_len: Optional[int] = None) -> int:
    """
    Return the similary score of two input texts.

    Expects cleaned, space separated tokens for each text input.

    :param text_1: First piece of text to match
    :type text_1: str
    :param text_2: Second piece of text to match
    :type text_2: str
    :param short_len: If `short_len` is given then texts with fewer tokens than
    this are only matched at the beginning of longer texts.
    :type short_len: Optional[int]
    :return: Match score indicating how similar the texts are
    :rtype: int
    """
    if short_len:
        toks = [text_1.split(" "), text_2.split(" ")]
        toks.sort(key=len)
        if len(toks[0]) < short_len:
            text_1 = " ".join(toks[0])
            text_2 = " ".join(toks[1][:short_len])
    return fuzz.partial_ratio(text_1, text_2)


def match_titles(
    register_row: tuple[str, pd.Series],
    collection: pd.DataFrame,
    register: pd.DataFrame,
    score_threshold: int,
    word_threshold: int,
) -> pd.DataFrame:
    """
    Search for the title given in register_row in the given collection.

    The register row must include a "clean_title" column to search with
    Returns matches that are above score_threshold in similarity.

    :param register_row: tuple of row index plus row data (the output of
        pd.DataFrame.iterrows())
    :type register_row: tuple[str, pd.Series]
    :param collection: DataFrame containing the collection entries to
        search through
    :type pandas.DataFrame
    :param register: DataFrame containing all the register entries
    :type register: pandas.DataFrame
    :param score_threshold: Only return matches with a similarity score above
        this value
    :type score_threshold: int
    :param word_threshold: Titles in the collection must be this length or
         longer to be considered for matching
    :type word_threshold: int
    """
    match_columns = [
        "id_register",
        "id_collection",
    ]
    index, row = register_row
    title = row["clean_title"]
    publisher = row["publisher"]
    matches = pd.DataFrame(columns=match_columns)
    if not isinstance(title, str):
        return matches
    # Filter out collection titles that are too short and will create spurious matches
    min_len = collection["clean_title"].map(
        lambda t: len(t.split(" ")) >= word_threshold
    )
    collection = collection[min_len]
    if collection.shape[0] > 0:
        matches["id_collection"] = collection.index
        scores = pd.DataFrame()

        # scores will have the same index as collection
        scores["title_score"] = collection["clean_title"].apply(
            lambda t: match_score(title, t, short_len=4)
        )

        # publisher match doesn't use `short_len` because entries are all expected
        # to be short
        scores["publisher_score"] = collection["publisher"].apply(
            lambda p: match_score(publisher, p)
        )

        # Creator matches only looks at the first word of the
        # register title, as long as it's not a stopword
        title_first_word = filter_stop_words(title.split(" ")[0])
        scores["creator_score"] = collection["creator"].apply(
            lambda c: match_score(title_first_word, c)
        )

        matches = matches.join(scores, on="id_collection")
        matches = matches[matches["title_score"] > score_threshold]
        matches["id_register"] = pd.Series(
            [index] * matches.shape[0], index=matches.index
        )

        # Add all the collection item metadata into the match frame
        matches = matches.join(
            collection, on="id_collection", lsuffix="_register", rsuffix="_collection"
        )
        matches = matches.set_index("id_register")

        # Add all the register item metadata into the match frame
        matches = register.join(
            matches, how="inner", lsuffix="_register", rsuffix="_collection"
        )
        matches = matches.sort_values(by="title_score", ascending=False)
    return matches


def n_gram_substring_match(
    match_row: pd.DataFrame,
    n_gram_data: pd.DataFrame,
    score_threshold: int,
    n_gram_count_cutoff: Optional[int] = None,
):
    """
    Evaluates string similarity between register and collection titles by identifying
    common n-grams and scoring the remaining substrings.

    The function filters the n-gram dataset, identifies the highest-priority shared
    n-gram between two strings, and calculates a match score based on the text
    left over after the n-gram is removed.

    :param match_row: A Single dataframe row including corresponding, matched entries
        from two catalogs e.g. 'clean_title_register' and 'clean_title_collection'
    :type match_row: pd.DataFrame
    :param n_gram_data: A DataFrame where the index contains n-gram strings and
        columns include 'degree' and 'count' for sorting and filtering.
    :type n_gram_data: pd.DataFrame
    :param score_threshold: The minimum integer score required for the remaining
        substrings to be considered a valid match.
    :type score_threshold: int
    :param n_gram_count_cutoff: The minimum frequency count required for an n-gram
        to be included in the search. If None, no filtering is applied.
    :type n_gram_count_cutoff: Optional[int]
    :returns: The modified input DataFrame row with additional columns: 'n-gram match',
        'substring score', and 'match'.
    :rtype: pd.DataFrame
    """
    is_match = True
    n_gram_match = False
    score = None

    match_strings = (
        str(match_row["clean_title_register"]),
        str(match_row["clean_title_collection"]),
    )

    if n_gram_count_cutoff is not None:
        n_gram_data = n_gram_data.loc[n_gram_data["count"] > n_gram_count_cutoff]
    n_gram_data = n_gram_data.sort_values(by=["degree", "count"], ascending=False)
    for n_gram in n_gram_data.index:
        if all(n_gram in text for text in match_strings):
            n_gram_match = True
            substrings = list(
                text.replace(n_gram, "").strip() for text in match_strings
            )
            score = match_score(substrings[0], substrings[1])
            is_match = score > score_threshold
            break  # Match status is now definitive
    match_row["n-gram match"] = n_gram_match
    match_row["substring score"] = score
    match_row["match"] = is_match
    return match_row
