import pandas as pd
import joblib
import yaml
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.base import BaseEstimator, TransformerMixin
from src.logging import logging
from typing import Dict, Any, Tuple


class ModelEvaluator(BaseEstimator, TransformerMixin):
    """Class to evaluate the trained model on test data."""

    def __init__(self, config_path: str):
        """Initialize the ModelEvaluator with configuration.

        Args:
            config_path (str): Path to the YAML configuration file.
        """
        logging.info(f"Model Evaluator Initialized")
        self.config_path = config_path
        try:
            with open(config_path, 'r') as file:
                self.config: Dict[str, Any] = yaml.safe_load(file)
            self.model_path = self.config.get('model_path', '')
        except Exception as e:
            logging.error(f"Failed to load config.yaml file: {str(e)}")
            raise RuntimeError(f"Failed to load config.yaml file: {str(e)}")

    def fit(self, X: Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series], y=None):
        """Fit method for pipeline compatibility (not used).

        Args:
            X (Tuple): Tuple containing (X_train, X_test, y_train, y_test).
            y: Not used, included for scikit-learn compatibility.

        Returns:
            self: ModelEvaluator instance.
        """
        logging.info(f"Model Evaluation fit.")
        return self

    def transform(self, X: Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]) -> Dict[str, Any]:
        """Evaluate the model on the test data.

        Args:
            X (Tuple): Tuple containing (X_train, X_test, y_train, y_test).

        Returns:
            Dict[str, Any]: Dictionary containing evaluation metrics.

        """
        try:
            logging.info(f"Model Evaluation transform started..")
            X_train, X_test, y_train, y_test = X
            self.model = joblib.load(self.model_path)
            logging.info(f"Model loaded from {self.model_path}")
        except Exception as e:
            logging.error(
                f"Failed to load model from {self.model_path}: {str(e)}")
            raise RuntimeError(
                f"Failed to load model from {self.model_path}: {str(e)}")
        try:
            _, X_test, _, y_test = X
            logging.info("Starting model evaluation...")

            if X_test.empty or y_test.empty:
                raise ValueError("Test data or labels are empty.")

            y_pred = self.model.predict(X_test)
            logging.info("Predictions generated successfully.")

            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, average='weighted'),
                'recall': recall_score(y_test, y_pred, average='weighted'),
                'f1': f1_score(y_test, y_pred, average='weighted'),
                'classification_report': classification_report(y_test, y_pred, output_dict=True)
            }

            logging.info(f"Evaluation metrics: {metrics}")
            logging.info(f"Model Evaluation ended.")
            return metrics
        except Exception as e:
            logging.error(f"Error in ModelEvaluator transform: {str(e)}")
            raise RuntimeError(f"Error in ModelEvaluator transform: {str(e)}")
