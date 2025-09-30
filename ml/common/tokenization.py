import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Tuple
import joblib


def fit_tfidf(
    texts: List[str],
    max_features: int = 10_000,
    ngram_range: tuple = (1, 2),
) -> TfidfVectorizer:
    vec = TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        lowercase=True,
        dtype=np.float32,
    )
    vec.fit(texts)
    return vec

def transform_dense(vec: TfidfVectorizer, texts: List[str]) -> np.ndarray:
    # Dense for PyTorch MLP
    return vec.transform(texts).toarray().astype(np.float32)

def save_vectorizer(vec: TfidfVectorizer, path: str) -> None:
    joblib.dump(vec, path)

def load_vectorizer(path: str) -> TfidfVectorizer:
    return joblib.load(path)