"""Helper functions for text matching."""

import nltk
import pandas as pd

from nltk.corpus import stopwords
from typing import Optional

nltk.download("stopwords")
stopwords = set(stopwords.words("english"))


def filter_stop_words(text: str) -> Optional[str]:
    """Replace stopwords with None."""
    return text if text not in stopwords else None


def apply_publishers_index(
    publisher_string: str, publishers_index: pd.DataFrame
) -> str:
    """
    Replace a cleaned_publisher name with an indexed_publisher name.

    If the cleaned_publisher name exists in the publishers index then it will
    be replaced by the indexed_publisher entry that corresponds to that name.
    If it doesn't exist then the name is not changed

    :param publisher_string: This string is checked for in the index,
    and is replaced if found
    :type publisher_string: str
    :param publishers_index: Index of strings with the indexed_publisher string
    that they can be replaced by
    :type publishers_index: pd.DataFrame
    :return: The new string if found, or the same one if not
    :rtype: str
    """
    publishers_index.set_index("clean_publisher")
    try:
        match_row = publishers_index.loc[publisher_string]
        indexed_value = match_row["indexed_publisher"]
    except KeyError:
        indexed_value = publisher_string
    return indexed_value
