import pandas as pd
import joblib
import os
import yaml
from sklearn.linear_model import LogisticRegression
from sklearn.base import BaseEstimator, TransformerMixin
from src.logging import logging
from typing import Dict, Any, Tuple

class ModelTrainer(BaseEstimator, TransformerMixin):
    """Class to train a Logistic Regression model and save it for production use."""

    def __init__(self, config_path: str):
        """Initialize the ModelTrainer with configuration.

        Args:
            config_path (str): Path to the YAML configuration file.
        """
        self.config_path = config_path
        try:
            with open(config_path, 'r') as file:
                self.config: Dict[str, Any] = yaml.safe_load(file)
            self.model_path = self.config.get('model_path', '')
            self.model_params = self.config.get('model_params', {})
        except Exception as e:
            logging.error(f"Failed to load config.yaml file: {str(e)}")
            raise RuntimeError(f"Failed to load config.yaml file: {str(e)}")

        try:
            self.model = LogisticRegression(**self.model_params, random_state=42)
        except Exception as e:
            logging.error(f"Failed to initialize LogisticRegression: {str(e)}")
            raise RuntimeError(f"Failed to initialize LogisticRegression: {str(e)}")

    def fit(self, X: Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series], y=None):
        """Fit the Logistic Regression model on the training data.

        Args:
            X (Tuple): Tuple containing (X_train, X_test, y_train, y_test).
            y: Not used, included for scikit-learn compatibility.

        Returns:
            self: Fitted ModelTrainer instance.
        """
        try:
            X_train, X_test, y_train, y_test = X
            logging.info("Starting model training with Logistic Regression...")

            if X_train.empty or y_train.empty:
                raise ValueError("Training data or labels are empty.")

            self.model.fit(X_train,y_train)
            logging.info("Model training completed successfully.")
            logging.info(f"Fitted models is : {self.model}")
            model_dir = os.path.dirname(self.model_path)
            if model_dir and not os.path.exists(model_dir):
                os.makedirs(model_dir)
                logging.info(f"Created directory: {model_dir}")
            joblib.dump(self.model, self.model_path)
            logging.info(f"Model saved to {self.model_path}")

            return self
        except Exception as e:
            logging.error(f"Error in ModelTrainer fit: {str(e)}")
            raise RuntimeError(f"Error in ModelTrainer fit: {str(e)}")

    def transform(self, X: pd.DataFrame, y: pd.Series=None) -> Tuple:
        """Pass through the data for the next step in the pipeline.

        Args:
            X (Tuple): Tuple containing (X_train, X_test, y_train, y_test).

        Returns:
            Tuple: Same input tuple (X_train, X_test, y_train, y_test).
        """
        return X