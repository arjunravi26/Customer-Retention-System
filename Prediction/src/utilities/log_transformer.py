import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd


class LogTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, offset=1):
        self.offset = offset

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        if isinstance(X, pd.DataFrame):
            X = X.to_numpy()
        elif not isinstance(X, np.ndarray):
            X = np.array(X)
        return np.log(X + self.offset)


