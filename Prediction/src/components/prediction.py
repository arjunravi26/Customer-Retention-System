# src/components/predictor.py
import pandas as pd
import joblib
import yaml
from src.logging import logging
from typing import Dict, Any

class Predictor:
    """Class to make predictions using a trained model."""

    def __init__(self, config_path: str, model_path: str):
        """Initialize the Predictor with configuration and model path.

        Args:
            config_path (str): Path to the YAML configuration file.
            model_path (str): Path to the trained model file.
        """
        logging.info(f"Predictor Initialized")
        self.config_path = config_path
        self.model_path = model_path
        try:
            with open(config_path, 'r') as file:
                self.config: Dict[str, Any] = yaml.safe_load(file)
        except Exception as e:
            logging.error(f"Failed to load config.yaml file: {str(e)}")
            raise RuntimeError(f"Failed to load config.yaml file: {str(e)}")

        try:
            self.model = joblib.load(self.model_path)
            logging.info(f"Model loaded from {self.model_path}")
        except Exception as e:
            logging.error(f"Failed to load model from {self.model_path}: {str(e)}")
            raise RuntimeError(f"Failed to load model from {self.model_path}: {str(e)}")

    def predict(self, X: pd.DataFrame) -> pd.Series:
        """Make predictions on new data.

        Args:
            X (pd.DataFrame): Input features for prediction.

        Returns:
            pd.Series: Predicted labels.
        """
        try:
            logging.info("Starting prediction...")

            if X.empty:
                raise ValueError("Input data is empty.")

            predictions = self.model.predict(X)
            predictions_series = pd.Series(predictions, index=X.index, name='predictions')
            logging.info("Predictions generated successfully.")
            
            return predictions_series
        except Exception as e:
            logging.error(f"Error in Predictor predict: {str(e)}")
            raise RuntimeError(f"Error in Predictor predict: {str(e)}")