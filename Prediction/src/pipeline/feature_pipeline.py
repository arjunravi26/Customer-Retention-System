from typing import Dict, Any, Tuple
import yaml
import pandas as pd
import os
from sklearn.pipeline import Pipeline
from src.components.data_ingestion import DataLoader
from src.components.feature_extraction import FeatureExtraction
from src.components.data_preprocessing import Preprocessor


class ChurnPredictionPipeline:
    """Main pipeline class for customer churn prediction, including data loading and feature extraction."""

    def __init__(self, config_path: str):
        """
        Initialize the pipeline with configuration.

        Args:
            config_path (str): Path to the YAML configuration file.
            save_path (str): Path to save the processed data.
        """
        self.config_path = config_path
        try:
            with open(config_path, 'r') as file:
                self.config = yaml.safe_load(file)

            self.pipeline = Pipeline(steps=[
                ('data_loader', DataLoader(config_path)),
                ('feature_extraction', FeatureExtraction(config_path)),
                ('preprocess', Preprocessor(config_path))
            ])
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize ChurnPredictionPipeline: {str(e)}")

    def fit_transform(self) -> pd.DataFrame:
        """
        Fit and transform the data through the pipeline.

        Returns:
            pd.DataFrame: Processed data after feature extraction.
        """
        try:
            processed_data = self.pipeline.fit_transform(None)
            return processed_data
        except Exception as e:
            raise RuntimeError(f"Error in pipeline fit_transform: {str(e)}")


if __name__ == "__main__":

    pipeline = ChurnPredictionPipeline('config.yaml')
    processed_data = pipeline.fit_transform()

    print("Processed Data:\n", processed_data.head())

    with open('config.yaml', 'r') as f:
        updated_config = yaml.safe_load(f)
    print("\nUpdated Config:\n", updated_config)
