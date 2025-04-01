from typing import Dict, Any
from src.logging import logging
from sklearn.base import BaseEstimator, TransformerMixin
import yaml
import pandas as pd
import io


class FeatureExtraction(BaseEstimator, TransformerMixin):
    def __init__(self, config_path: str):
        self.logger = logging
        self.config_path = config_path
        try:
            with open(config_path, 'r') as file:
                self.config: Dict[str, Any] = yaml.safe_load(file)
            self.cols_to_remove: list = self.config.get('cols_to_drop', [])
            self.cols_to_select: list = self.config.get('cols_to_select', [])
            self.selected_data_path =self.config['selected_data_path']
        except Exception as e:
            self.logger.error("Failed to load config.yaml file: %s", str(e))
            raise RuntimeError(f"Failed to load config.yaml file: {str(e)}")

    def _update_config(self, categorical_cols: list, numerical_cols: list) -> None:
        """
        Update the config file with categorical and numerical column names.

        Args:
            categorical_cols (list): List of categorical column names.
            numerical_cols (list): List of numerical column names.
        """
        try:
            if 'categorical_features' not in self.config:
                self.config['categorical_features'] = categorical_cols
            if 'numerical_features' not in self.config:
                self.config['numerical_features'] = numerical_cols

            with open(self.config_path, 'w') as file:
                yaml.safe_dump(self.config, file)
        except Exception as e:
            raise RuntimeError(
                f"Failed to update config.yaml with feature list: {str(e)}")
    def fit(self, X: pd.DataFrame, y=None):
        """Fit method for pipeline compatibility (no-op)."""
        return self

    def transform(self,X: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features by dropping specified columns and splitting into categorical and numerical data.
        Updates the config file with the column names.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Filtered DataFrame, categorical DataFrame, numerical DataFrame.
        """
        # selected_features = X.drop(self.cols_to_remove, axis=1)
        try:
            invalid_cols = [
                col for col in self.cols_to_remove if col not in X.columns]
            if invalid_cols:
                raise ValueError(
                    f"Columns to remove not found in data: {invalid_cols}")
            filtered_data = X.drop(
                columns=self.cols_to_remove, axis=1, errors='ignore')
            if self.cols_to_select:
                missing_cols = [
                    col for col in self.cols_to_select if col not in filtered_data.columns]
                if missing_cols:
                    raise ValueError(
                        f"Columns to select not found in data: {missing_cols}")
                filtered_data = filtered_data[self.cols_to_select]
            category_data = filtered_data.select_dtypes('object')
            numeric_data = filtered_data.select_dtypes('number')
            categorical_cols = category_data.columns.tolist()
            numerical_cols = numeric_data.columns.tolist()
            self._update_config(categorical_cols, numerical_cols)
            if self.selected_data_path:
                filtered_data.to_excel(self.selected_data_path, index=False)
            return filtered_data
        except Exception as e:
            raise RuntimeError(f"Error in feature extraction: {str(e)}")
