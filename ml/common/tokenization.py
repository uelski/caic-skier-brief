import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer(
    max_features=10_000,
    ngram_range=(1, 2),
    dtype=np.float32,
    lowercase=True
)