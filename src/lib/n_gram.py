import pandas as pd
from nltk import ngrams


def n_gram_frequency(text_series: pd.Series, degree: int = 1) -> pd.DataFrame:
    df = pd.DataFrame(text_series)
    n_gram_df = pd.DataFrame(columns=["n_gram"])

    for _, row in df.iterrows():
        tokens = row["title"].split()
        n_grams = ngrams(tokens, degree)
        for n_gram in n_grams:
            n_gram_string = " ".join(n_gram)
            new_row = pd.DataFrame({"n_gram": [n_gram_string]})
            n_gram_df = pd.concat([n_gram_df, new_row], ignore_index=True)

    print(n_gram_df)
    n_gram_frequency_df = n_gram_df.value_counts()
    return n_gram_frequency_df
