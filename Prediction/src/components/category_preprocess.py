import pandas as pd
import yaml
from typing import Dict, Any, Tuple
from sklearn.preprocessing import LabelEncoder
from src.logging import logging
from sklearn.base import BaseEstimator, TransformerMixin
from typing import Dict, Any
from sklearn.base import BaseEstimator, TransformerMixin


class CategoricalPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, config_path: str):
        """Initialize the Preprocessor with a configuration file.

        Args:
            config_path (str): Path to the YAML configuration file.
        """
        self.config_path = config_path
        try:
            with open(config_path, 'r') as file:
                self.config: Dict[str, Any] = yaml.safe_load(file)
            self.categorical_features = self.config.get(
                'categorical_features', [])
            self.target = self.config.get('target', '')
        except Exception as e:
            logging.error(f"Failed to load config.yaml file: {str(e)}")
            raise RuntimeError(f"Failed to load config.yaml file: {str(e)}")

        self.label_encode_cols = ['Gender']
        self.binary_map_cols = {
            'Senior Citizen': {'No': 0, 'Yes': 1},
            'Partner': {'No': 1, 'Yes': 0},
            'Phone Service': {'No': 0, 'Yes': 1},
            'Paperless Billing': {'No': 0, 'Yes': 1}
        }
        self.target_encode_cols = [
            'Dependents', 'Internet Service', 'Online Security', 'Online Backup',
            'Device Protection', 'Tech Support', 'Streaming TV', 'Streaming Movies',
            'Contract', 'Payment Method'
        ]
        self.onehot_cols = ['Multiple Lines']
        self.onehot_prefixes = {'Multiple Lines': 'phone_service'}

        # Initialize encoders and scalers
        self.label_encoder = LabelEncoder()
        self.target_encodings = {}

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        """Fit the preprocessor on the training data.

        Args:
            X (pd.DataFrame): Input features.
            y (pd.Series, optional): Target variable for target encoding.

        Returns:
            self: Fitted preprocessor instance.
        """
        try:
            logging.info(f"Categorical Preprocessing fitting started...")
            if 'Gender' in X.columns:
                self.label_encoder.fit(X['Gender'])

            if y is not None:
                df_combined = X.copy()
                df_combined[y.name] = y
                for col in self.target_encode_cols:
                    if col in X.columns:
                        encoding = df_combined.groupby(col)[y.name].mean()
                        self.target_encodings[col] = encoding
            logging.info(f"Categorical Preprocessing fitting done.")
            return self
        except Exception as e:
            logging.error(f"Error in Preprocessor fit: {str(e)}")
            raise RuntimeError(f"Error in Preprocessor fit: {str(e)}")

    def transform(self, X: pd.DataFrame, y: pd.Series = None) -> Tuple[pd.DataFrame, pd.Series]:
        """Transform the input data using fitted encoders and scalers.

        Args:
            X (pd.DataFrame): Input features to transform.

        Returns:
            pd.DataFrame: Transformed features.
        """
        try:
            logging.info(f"Categorical Preprocessing transform started...")
            X_transformed: pd.DataFrame = X.copy()

            if 'Gender' in X_transformed.columns:
                X_transformed['Gender'] = self.label_encoder.transform(
                    X_transformed['Gender'])

            for col, mapping in self.binary_map_cols.items():
                if col in X_transformed.columns:
                    X_transformed[col] = X_transformed[col].map(mapping)

            for col in self.target_encode_cols:
                if col in X_transformed.columns:
                    if col in self.target_encodings:
                        X_transformed[col] = X_transformed[col].map(
                            self.target_encodings[col])
                    else:
                        raise ValueError(
                            f"Target encoding for {col} not fitted.")

            for col in self.onehot_cols:
                if col in X_transformed.columns:
                    encoded = pd.get_dummies(
                        X_transformed[col], dtype=int, prefix=self.onehot_prefixes[col])
                    X_transformed = pd.concat([X_transformed, encoded], axis=1)
                    X_transformed.drop(columns=[col], inplace=True)
            logging.info(f"Categorical Preprocessing transform done.")
            return X_transformed
        except Exception as e:
            raise RuntimeError(f"Error in Preprocessor transform: {str(e)}")


if __name__ == "__main__":
    from src.pipeline.data_pipeline import DataLoadSplitPipeline
    data_load_pipeline = DataLoadSplitPipeline(
        config_path='config.yaml', save_path='data/selected_data.xlsx')
    X_train, X_test, y_train, y_test = data_load_pipeline.fit_transform()
    preprocessor = CategoricalPreprocessor(config_path='config.yaml')
    preprocessor.fit(X_train, y_train)
    X_transformed = preprocessor.transform(X_train, y_train)
    print(X_transformed)
