import pandas as pd
from nltk import ngrams


def n_gram_frequency(token_list: pd.Series, degree: int = 1) -> pd.DataFrame:
    """
    Produce a dataframe of frequencies of all n_grams of given degree.

    We collect each n_gram for each list of tokens in the series, and create a flattened
    list of all n-grams in the token list. Each entry also contains a value for the
    'degree' of the n-gram.

    :param token_list: Series of token lists
    :type token_list: pd.Series
    :param degree: Degree of n-gram to be evaluated, e.g. unigrams (1), bigrams (2) etc.
    :type degree: int
    :return: Series of frequencies of n_grams, with the n_gram string as the index
    :rtype: pd.Series
    """
    n_gram_series = pd.Series()

    for tokens in token_list:
        n_grams = ngrams(tokens, degree)
        for n_gram in n_grams:
            n_gram_string = " ".join(n_gram)
            n_gram_series = pd.concat(
                [n_gram_series, pd.Series([n_gram_string])], ignore_index=True
            )

    n_gram_count = n_gram_series.value_counts()
    return n_gram_count


def multi_n_gram_frequency(
    token_list: pd.Series, min_degree: int = 1, max_degree: int = None
) -> pd.DataFrame:
    """
    Produce a DataFrame of frequencies of all n_grams for a range of degrees.

    All degrees between min_degree and max_degree will be collated in the output dataframe


    :param token_list: Series of token lists
    :type token_list: pd.Series
    :param min_degree: Lowest degree of n-gram to be evaluated, e.g. unigrams (1), bigrams (2) etc.
    :type degree: int
    :param max_degree: Highest degree of n-gram to be evaluated, if None, we set the value of
      max_degree to the number of tokens in the longest entry of the series
    :return: DataFrame of frequencies of n_grams, with the n_gram string as index label, and
      the count and degree as columns
    :rtype: pd.DataFrame
    """
    n_gram_frequencies = pd.DataFrame()
    if max_degree is None:
        max_degree = token_list.map(len).max()

    for degree in range(min_degree, max_degree + 1):
        new_n_gram_frequencies = n_gram_frequency(token_list, degree)
        n_gram_frame = pd.DataFrame(new_n_gram_frequencies)
        n_gram_frame["degree"] = [degree] * len(n_gram_frame)
        n_gram_frequencies = pd.concat([n_gram_frequencies, n_gram_frame])

    return n_gram_frequencies.sort_values(by="count", ascending=False)


def sort_n_grams_by_degree(n_gram_frame: pd.DataFrame):
    """
    Sort a list of n-gram frequencies by the number of tokens in the index, descending.

    The list will secondarily by sorted by frequency, descending.

    :param n_gram_frame: DataFrame n-grams with count and degree as columsn
    :type n_gram_frame: pd.DataFrame
    :return: Sorted data Frame
    :rtype: pd.DataFrame
    """
    df = n_gram_frame
    df["degree"] = df.index.map(lambda i: len(i.split()))
    sorted = df.sort_values(by=["degree", "count"], ascending=False)
    return sorted
