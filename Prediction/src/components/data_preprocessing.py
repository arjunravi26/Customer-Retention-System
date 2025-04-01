# data_pipeline.py
import pandas as pd
import os
import yaml
from typing import Dict, Any, List
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from src.logging import logging
from sklearn.base import BaseEstimator, TransformerMixin


class Preprocessor(BaseEstimator, TransformerMixin):
    """Class to handle data preprocessing including imputation, encoding, and scaling."""

    def __init__(self, config_path: str):
        """
        Initialize the Preprocessor with feature lists and configuration.

        Args:
            numerical_features (List[str]): List of numerical feature names.
            categorical_features (List[str]): List of categorical feature names.
            config_path (str): Path to the configuration file.
        """
        self.X: pd.DataFrame
        self.config_path = config_path
        try:
            with open(self.config_path, 'r') as file:
                self.config: Dict[str, Any] = yaml.safe_load(file)
            self.save_path = self.config['preprocessed_file']
            logging.info(
                "Sucessfully loaded config.yaml in Data Preprocessing")
        except Exception as e:
            logging.error(f"Failed to load config file ")

    def _save_preprocess_data(self):
        """Function to save preprocessed data"""
        if self.save_path:
            self.X.to_excel(self.save_path)

    def fit(self, X: pd.DataFrame = None, y: pd.DataFrame = None):
        """Fit method for pipeline compatibility (no-op)."""
        return self

    def read_config(self):
        """
        Function to read config file
        Args:
            None
        Return:
            numerical_cols (List[str]): List of numerical feature names.
            categorical_cols (List[str]): List of categorical feature names.

            """
        numerical_cols: List[str] = self.config['numerical_cols']
        categorical_cols: List[str] = self.config['categorical_cols']
        return numerical_cols, categorical_cols

    def transform(self, X: pd.DataFrame):
        pass
