"""Functions for matching entry texts."""

import pandas as pd

from lib.helpers import filter_english_words
from thefuzz import fuzz
from typing import Optional


# Source for find_index function - https://stackoverflow.com/a/426168
# Posted by jfs, modified by community. See post 'Timeline' for change history
# Retrieved 2026-04-13, License - CC BY-SA 3.0
def find_index(subseq, seq):
    """Return an index of `subseq`uence in the `seq`uence.

    Or `-1` if `subseq` is not a subsequence of the `seq`.

    The time complexity of the algorithm is O(n*m), where

        n, m = len(seq), len(subseq)

    >>> find_index([1,2], range(5))
    1
    >>> find_index(range(1, 6), range(5))
    -1
    >>> find_index(range(5), range(5))
    0
    >>> find_index([1,2], [0, 1, 0, 1, 2])
    3
    """
    i, n, m = -1, len(seq), len(subseq)
    try:
        while True:
            i = seq.index(subseq[0], i + 1, n - m + 1)
            if subseq == seq[i : i + m]:
                return i
    except ValueError:
        return -1


def match_score(
    text_1: Optional[str],
    text_2: Optional[str],
    match_empty: bool = False,
    short_len: Optional[int] = None,
) -> int:
    """
    Return the similary score of two input texts.

    Expects cleaned, space separated tokens for each text input.

    :param text_1: First piece of text to match
    :type text_1: str
    :param text_2: Second piece of text to match
    :type text_2: str
    :param match_empty: if true returns a score of 100 when one string is empty
    :type match_empty: bool
    :param short_len: If `short_len` is given then texts with fewer tokens than
    this are only matched at the beginning of longer texts.
    :type short_len: Optional[int]
    :return: Match score indicating how similar the texts are
    :rtype: int
    """
    if match_empty and ((text_1 == "") or (text_2 == "")):
        # Manually handle the case where one entry is empty because the
        # full string was just a frequent n-gram that was then deleted.
        # This would normally result in score 0. This condition also covers
        # the case where both entries are just a frequent n-gram but gives the
        # same result as without this exception (score 100)
        return 100
    if (text_1 is None) or (text_2 is None):
        return None
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
        "creator_guess",
        "id_register",
        "id_collection",
    ]
    index, row = register_row
    title = str(row["clean_title"])
    publisher = str(row["clean_publisher"])

    # Creator matches only looks at the first word of the
    # register title, as long as it's not an English word
    creator_guess = filter_english_words(title.split(" ")[0])

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
        scores["publisher_score"] = collection["clean_publisher"].apply(
            lambda p: match_score(publisher, p)
        )

        scores["creator_score"] = collection["clean_creator"].apply(
            lambda c: match_score(creator_guess, c)
        )

        matches = matches.join(scores, on="id_collection")
        matches = matches[matches["title_score"] > score_threshold]
        matches["id_register"] = pd.Series(
            [index] * matches.shape[0], index=matches.index
        )
        matches["creator_guess"] = pd.Series(
            [creator_guess] * matches.shape[0],
            index=matches.index,
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
    row: tuple[str, pd.Series],
    n_gram_data: pd.DataFrame,
    match_col_1: str,
    match_col_2: str,
    score_threshold: int,
    n_gram_count_cutoff: Optional[int] = None,
    drop_first: bool = False,
) -> pd.DataFrame:
    """
    Evaluates string similarity between column data by identifying common n-grams and
    scoring the remaining substrings.

    The function filters the n-gram dataset, identifies the highest-priority shared
    n-gram between two strings, and calculates a match score based on the text
    left over after the n-gram is removed.

    :param match_row: A Single dataframe row including corresponding, matched entries
        from two columns defined by match_col_1 and match_col_2 e.g.
        'clean_title_register' and 'clean_title_collection'
    :type match_row: pd.DataFrame
    :param n_gram_data: A DataFrame where the index contains n-gram strings and
        columns include 'degree' and 'count' for sorting and filtering.
    :type n_gram_data: pd.DataFrame
    :param match_col_1: match data from this column against data from match_col_2
    :type match_col_1: str
    :param match_col_2: match data from this column against data from match_col_1
    :type match_col_2: str
    :param score_threshold: The minimum integer score required for the remaining
        substrings to be considered a valid match.
    :type score_threshold: int
    :param n_gram_count_cutoff: The minimum frequency count required for an n-gram
        to be included in the search. If None, no filtering is applied.
    :type n_gram_count_cutoff: Optional[int]
    :param drop_first: If the difference in match status is down to the first word being
        missing, then retry the match without the first word, in case it's
        a missing author name or article like 'the'
    :type drop_first: bool
    :returns: The modified input DataFrame row with additional columns: 'n-gram match',
        'substring score', and 'match'.
    :rtype: pd.DataFrame
    """
    n_gram_match = False
    matched_n_gram = None
    score = None
    is_match = True

    index, match_row = row
    try:
        match_entries = (
            str(match_row[match_col_1]).split(),
            str(match_row[match_col_2]).split(),
        )
    except KeyError:
        raise KeyError(
            f"Input row: {match_row}\ndoes not have relevant columns: {match_col_1, match_col_2}"
        )

    if n_gram_count_cutoff is not None:
        n_gram_data = n_gram_data.loc[n_gram_data["count"] > n_gram_count_cutoff]
    n_gram_data = n_gram_data.sort_values(by=["degree", "count"], ascending=False)

    for n_gram in n_gram_data.index:
        n_gram_tokens = str(n_gram).split()
        n_gram_token_len = len(n_gram_tokens)
        n_gram_indices = list(
            map(lambda seq: find_index(n_gram_tokens, seq), match_entries)
        )
        if all(index > -1 for index in n_gram_indices):
            n_gram_match = True
            matched_n_gram = n_gram
            substrings = []
            for i, entry_tokens in enumerate(match_entries):
                sub_index = n_gram_indices[i]
                del entry_tokens[sub_index : sub_index + n_gram_token_len]
                substrings.append(" ".join(entry_tokens))

            score = match_score(substrings[0], substrings[1], match_empty=True)
            is_match = score > score_threshold

            index_diff = n_gram_indices[0] - n_gram_indices[1]
            if drop_first and (abs(index_diff) == 1) and not is_match:
                greater_index = 0
                if index_diff < 0:
                    greater_index = 1
                del match_entries[greater_index][0]
                substrings = list(map(lambda tokens: " ".join(tokens), match_entries))
                score = match_score(substrings[0], substrings[1], match_empty=True)
                is_match = score > score_threshold
            break  # Match status is now definitive
    match_row["n-gram match"] = n_gram_match
    match_row["n-gram"] = matched_n_gram
    match_row["substring score"] = score
    match_row["match"] = is_match
    return match_row.to_frame().T
