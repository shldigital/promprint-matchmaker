import pandas as pd
from nltk import ngrams


def n_gram_frequency(text_series: pd.Series, degree: int = 1) -> pd.DataFrame:
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
