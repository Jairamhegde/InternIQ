"""
Compare the old TF-IDF classifier with the new embedding classifier
on a hand-labelled sample of jobs (testing/embedding_sample.csv).

The sample only contains jobs with unclear titles, so none of them
were used to train the embedding model.

Run:  python -m testing.test_embedding_classifier
"""

import pandas as pd

from keyword_match.dev_trend import similarity_check
from keyword_match.embedding_classifier import predict_field

SAMPLE_FILE = "testing/embedding_sample.csv"


def load_sample():
    df = pd.read_csv(SAMPLE_FILE)
    df["skills"] = df["skills"].str.split(";")
    return df


def add_predictions(df):
    # Old classifier is called the same way insertCleanData.py calls it
    df["tfidf"] = [similarity_check(t, t, s)[0] for t, s in zip(df["title"], df["skills"])]
    df["embedding"] = [predict_field(t, s)[0] for t, s in zip(df["title"], df["skills"])]
    return df


def accuracy(df, column):
    return (df[column] == df["true_field"]).mean()


def test_embedding_beats_tfidf():
    df = add_predictions(load_sample())
    assert accuracy(df, "embedding") > accuracy(df, "tfidf")


if __name__ == "__main__":
    df = add_predictions(load_sample())

    print(f"Jobs tested:          {len(df)}")
    print(f"TF-IDF accuracy:      {accuracy(df, 'tfidf'):.0%}")
    print(f"Embedding accuracy:   {accuracy(df, 'embedding'):.0%}")

    mistakes = df[df["embedding"] != df["true_field"]]
    print(f"\nEmbedding mistakes ({len(mistakes)}):")
    print(mistakes[["title", "true_field", "embedding", "tfidf"]].to_string(index=False))
