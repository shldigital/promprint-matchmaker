import pandas as pd
from nltk import ngrams


def n_gram_frequency(text_series: pd.Series, degree: int = 1) -> pd.Series:
    """
    Produce a list of frequencies of all n_grams of given degree

    Each string in the input series will be split into tokens using space as a separator.
    We then collect each n_gram for the resulting list of tokens that corresponds to the
    original string. This list of n_grams is collated with the n_grams associated with
    every other entry in the series

    :param text_series: Series of cleaned text strings, with tokens separated by space
    :type text_series: pd.Series
    :param degree: Degree of n-gram to be evaluated, e.g. unigrams (1), bigrams (2) etc.
    :type degree: int
    :return: Series of frequencies of n_grams, with the actual n_gram as index label
    :rtype: pd.Series
    """
    n_gram_series = pd.Series(name="n_gram")

    for row in text_series:
        tokens = row.split()
        n_grams = ngrams(tokens, degree)
        for n_gram in n_grams:
            n_gram_string = " ".join(n_gram)
            n_gram_series = pd.concat(
                [n_gram_series, pd.Series([n_gram_string])], ignore_index=True
            )

    return n_gram_series.value_counts()


def multi_n_gram_frequency(
    text_series: pd.Series, min_degree: int = 1, max_degree: int = None
) -> pd.Series:
    """
    Produce a list of frequencies of all n_grams for a range of degrees

    All integral degrees between min_degree and max_degree will be collated in the output series

    :param text_series: Series of cleaned text strings, with tokens separated by space
    :type text_series: pd.Series
    :param min_degree: Lowest degree of n-gram to be evaluated, e.g. unigrams (1), bigrams (2) etc.
    :type degree: int
    :param max_degree: Highest degree of n-gram to be evaluated, if None, we set the value of
      max_degree to the number of tokens in the longest entry of the series
    :return: Series of frequencies of n_grams, with the actual n_gram as index label
    :rtype: pd.Series
    """

    n_gram_frequencies = pd.Series()
    if max_degree is None:
        max_degree = text_series.map(lambda t: len(t.split())).max()

    # TODO: tokenize once, pass tokenized lists to the n_gram_frequency function
    for degree in range(min_degree, max_degree + 1):
        new_n_gram_frequencies = n_gram_frequency(text_series, degree)
        n_gram_frequencies = pd.concat([n_gram_frequencies, new_n_gram_frequencies])

    return n_gram_frequencies.sort_values(ascending=False)
