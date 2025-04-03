import pandas as pd
import numpy as np
import yaml
from typing import Dict, Any
from sklearn.pipeline import Pipeline

from sklearn.impute import SimpleImputer
from src.logging import logging
from sklearn.base import BaseEstimator, TransformerMixin
from typing import Dict, Any
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder, RobustScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from src.utilities.log_transformer import LogTransformer


class NumericalPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, config_path: str):
        """Initialize the Preprocessor with a configuration file.

        Args:
            config_path (str): Path to the YAML configuration file.
        """
        self.config_path = config_path
        try:
            with open(config_path, 'r') as file:
                self.config: Dict[str, Any] = yaml.safe_load(file)
            self.numerical_features = self.config.get('numerical_features', [])
            self.target = self.config.get('target', '')
        except Exception as e:
            logging.error(f"Failed to load config.yaml file: {str(e)}")
            raise RuntimeError(f"Failed to load config.yaml file: {str(e)}")

        self.scale_cols = ['Total Charges', 'Monthly Charges', 'CLTV']

        self.scaling_pipeline = Pipeline([
            ('log_transform', LogTransformer()),
            ('scaler', RobustScaler())
        ])
        self.total_charges_imputer = SimpleImputer(strategy='median')

    def _handle_empty_total_charges(self, X: pd.DataFrame):
        try:
            if 'Total Charges' in X.columns:
                mask = X['Total Charges'].apply(
                    lambda x: isinstance(x, (int, float)))
                null_rows = X[~mask]
                not_null_rows = X[mask]

                if len(not_null_rows) > 0:
                    self.total_charges_imputer.fit(
                        not_null_rows['Total Charges'].to_numpy().reshape(-1, 1))
                    imputed_values = self.total_charges_imputer.transform(
                        not_null_rows['Total Charges'].astype(
                            float).values.reshape(-1, 1)
                    )
                    X.loc[mask, 'Total Charges'] = imputed_values.flatten()

                if len(null_rows) > 0:
                    imputed_values = self.total_charges_imputer.transform(
                        np.array([np.nan] * len(null_rows)).reshape(-1, 1)
                    )
                    X.loc[null_rows.index,
                          'Total Charges'] = imputed_values.flatten()

                X['Total Charges'] = X['Total Charges'].astype(
                    float)
        except Exception as e:
            raise RuntimeError(
                f"Error in Handling null value in total charges: {str(e)}")

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        """Fit the preprocessor on the training data.

        Args:
            X (pd.DataFrame): Input features.
            y (pd.Series, optional): Target variable for target encoding.

        Returns:
            self: Fitted preprocessor instance.
        """
        try:

            if 'Total Charges' in X.columns:
                self._handle_empty_total_charges(X)
                X['Total Charges'] = X['Total Charges'].astype(
                    float)

            if all(col in X.columns for col in self.scale_cols):
                self.scaling_pipeline.fit(X[self.scale_cols])

            return self
        except Exception as e:
            raise RuntimeError(f"Error in Preprocessor fit: {str(e)}")

    def transform(self, X: pd.DataFrame, y: pd.Series = None) -> pd.DataFrame:
        """Transform the input data using fitted encoders and scalers.

        Args:
            X (pd.DataFrame): Input features to transform.

        Returns:
            pd.DataFrame: Transformed features.
        """
        try:
            X_transformed: pd.DataFrame = X.copy()
            if 'Total Charges' in X_transformed.columns:
                self._handle_empty_total_charges(X_transformed)
                X_transformed['Total Charges'] = X_transformed['Total Charges'].astype(
                    float)
            if all(col in X_transformed.columns for col in self.scale_cols):
                X_transformed[self.scale_cols] = self.scaling_pipeline.transform(
                    X_transformed[self.scale_cols])

            return X_transformed
        except Exception as e:
            raise RuntimeError(f"Error in Preprocessor transform: {str(e)}")


if __name__ == "__main__":
    from src.pipeline.data_pipeline import DataLoadSplitPipeline
    from src.components.category_preprocess import CategoricalPreprocessor
    data_load_pipeline = DataLoadSplitPipeline(
        config_path='config.yaml', save_path='data/selected_data.xlsx')
    X_train, X_test, y_train, y_test = data_load_pipeline.fit_transform()
    categorical_preprocessor = CategoricalPreprocessor(
        config_path='config.yaml')
    categorical_preprocessor.fit(X_train, y_train)
    X_transformed, y = categorical_preprocessor.transform(X_train, y_train)
    numerical_preprocessor = NumericalPreprocessor(config_path='config.yaml')
    numerical_preprocessor.fit(X_transformed, y_train)
    X_transformed, y = numerical_preprocessor.transform(X_transformed, y)
