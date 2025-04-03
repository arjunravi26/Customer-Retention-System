import pandas as pd
import logging
import os
import yaml
import io
from typing import Dict, Any
from src.logging import logging
from sklearn.base import BaseEstimator, TransformerMixin


class DataLoader(BaseEstimator, TransformerMixin):
    """Class to handle data loading from a specified source with validation and error handling."""

    def __init__(self, config_path: str):
        """
        Initialize the DataLoader with a configuration file.

        Args:
            config_path (str): Path to the YAML configuration file.
        """
        self.config_path = config_path
        logging.info(f"Data Loader Initialized")
        try:
            with open(self.config_path, 'r') as file:
                self.config: Dict[str, Any] = yaml.safe_load(file)
            self.file_path: str = self.config.get('data_path', '')
            logging.info(
                "DataLoader initialized with configuration from %s", config_path)
        except Exception as e:
            logging.error("Failed to initialize DataLoader: %s", str(e))
            raise

    def _update_config(self, columns: list):
        """
        Update the configuration file with the column names from the dataset.

        Args:
            columns (list): List of column names from the dataset.
        """
        logging.info(f"Data loader update config started..")
        try:
            if 'columns' not in self.config:
                self.config['columns'] = columns
                with open(self.config_path, 'w') as file:
                    yaml.safe_dump(self.config, file)
                logging.info(
                    "Configuration updated with column names: %s", columns)
            else:
                logging.info("Columns already exist in config.yaml")

        except Exception as e:
            logging.error("Failed to update configuration file: %s", str(e))
            raise

    def validate_file(self) -> None:
        """Validate that the data file exists and is accessible."""
        logging.info(f"Data Loader validate file started..")
        if not self.file_path:
            raise ValueError("Data file path not specified in configuration.")
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Data file not found at {self.file_path}")
        if not os.access(self.file_path, os.R_OK):
            raise PermissionError(
                f"No read permission for file {self.file_path}")
        logging.info(f"Validation successful")

    def fit(self, X=None, y=None):
        """Fit method for pipeline compatibility (no-op)."""
        logging.info("Data loader fit.")
        return self

    def transform(self,X:pd.DataFrame) -> pd.DataFrame:
        """
        Load data from the specified file with validation and error handling.

        Returns:
            pd.DataFrame: The loaded dataset.
        """
        logging.info(f"Data loader transform started")
        try:
            self.validate_file()
            data = pd.read_excel(self.file_path)
            logging.info("Data loaded successfully from %s. Shape: %s",
                         self.file_path, data.shape)

            if data.empty:
                raise ValueError("Loaded dataset is empty.")
            if data.duplicated().any():
                logging.warning(
                    "Dataset contains %d duplicate rows. Consider deduplication.", data.duplicated().sum())
            logging.info("Data Loader transformation completed.")
            return data
        except pd.errors.EmptyDataError:
            logging.error("Data file %s is empty or corrupted.",
                          self.file_path)
            raise
        except Exception as e:
            logging.error("Error loading data from %s: %s",
                          self.file_path, str(e))
            raise
