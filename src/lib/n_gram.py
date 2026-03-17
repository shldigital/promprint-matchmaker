import pandas as pd
from nltk import ngrams


def n_gram_frequency(text_series: pd.Series, degree: int = 1) -> pd.Series:
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
    n_gram_frequencies = pd.Series()
    if max_degree is None:
        max_degree = text_series.map(lambda t: len(t.split())).max()

    # TODO: tokenize once, pass tokenized lists to the n_gram_frequency function
    for degree in range(min_degree, max_degree+1):
        new_n_gram_frequencies = n_gram_frequency(text_series, degree)
        n_gram_frequencies = pd.concat([n_gram_frequencies, new_n_gram_frequencies])

    return n_gram_frequencies.sort_values(ascending=False)
