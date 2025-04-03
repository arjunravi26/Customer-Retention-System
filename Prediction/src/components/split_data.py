from sklearn.model_selection import train_test_split
from sklearn.base import BaseEstimator, TransformerMixin
from typing import Dict, Any
from src.logging import logging
import yaml
import pandas as pd


class SplitData(BaseEstimator, TransformerMixin):
    """ Class for split the  data into feature and target and save it"""

    def __init__(self,config_path):
        with open(config_path,'r') as file:
            self.config:Dict[str,Any] = yaml.safe_load(file)
        self.target = self.config.get('target','')

    def fit(self, X:pd.DataFrame):
        return self

    def transform(self, X: pd.DataFrame,):
        y: pd.Series
        X_train: pd.DataFrame
        X_test: pd.DataFrame
        y_train: pd.Series
        y_test: pd.Series
        try:
            X,y = X.drop(self.target,axis=1),X[self.target]
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, random_state=42, test_size=0.2)
            return (X_train,X_test,y_train,y_test)
        except Exception as e:
            logging.error(f"An error occured while splitting the data {e}")