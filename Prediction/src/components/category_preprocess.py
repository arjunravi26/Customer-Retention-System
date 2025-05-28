import os
from typing import Any, Dict, Tuple

import joblib
import pandas as pd
import yaml
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from src.logging import logging


class CategoricalPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, config_path: str, save_dir: str = "models"):
        """Initialize the Preprocessor with a configuration file and save directory.

        Args:
            config_path (str): Path to the YAML configuration file.
            save_dir (str): Directory to save the fitted preprocessor object.
        """
        self.config_path = config_path
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)  # Create save directory if it doesn't exist

        try:
            with open(config_path, 'r') as file:
                self.config: Dict[str, Any] = yaml.safe_load(file)
            self.categorical_features = self.config.get('categorical_features', [])
            self.target = self.config.get('target', '')
        except Exception as e:
            logging.error(f"Failed to load config.yaml file: {str(e)}")
            raise RuntimeError(f"Failed to load config.yaml file: {str(e)}")

        # Define columns for different encoding strategies
        self.label_encode_cols = ['Gender']
        self.binary_map_cols = {
            'Senior Citizen': {'No': 0, 'Yes': 1},
            'Partner': {'No': 1, 'Yes': 0},
            'Phone Service': {'No': 0, 'Yes': 1},
            'Paperless Billing': {'No': 0, 'Yes': 1}
        }
        self.target_encode_cols = [
            'Internet Service', 'Online Security', 'Online Backup',
            'Device Protection', 'Tech Support', 'Streaming TV', 'Streaming Movies',
            'Contract', 'Payment Method'
        ]
        self.onehot_cols = ['Multiple Lines']
        self.onehot_prefixes = {'Multiple Lines': 'phone_service'}

        # Initialize encoders
        self.label_encoder = LabelEncoder()
        self.target_encodings = {}
        self.onehot_encoders = {}

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        """Fit the preprocessor on the training data and save the fitted object.

        Args:
            X (pd.DataFrame): Input features.
            y (pd.Series, optional): Target variable for target encoding.

        Returns:
            self: Fitted preprocessor instance.
        """
        try:
            logging.info("Categorical Preprocessing fitting started...")

            # Fit LabelEncoder for 'Gender'
            if 'Gender' in X.columns:
                self.label_encoder.fit(X['Gender'])
            else:
                logging.warning("'Gender' column not found in input data.")

            # Fit target encodings
            if y is not None:
                df_combined = X.copy()
                df_combined[y.name] = y
                for col in self.target_encode_cols:
                    if col in X.columns:
                        encoding = df_combined.groupby(col)[y.name].mean()
                        print(encoding)
                        self.target_encodings[col] = encoding
                    else:
                        logging.warning(f"Target encoding column {col} not found in input data.")

            # Fit OneHotEncoder for one-hot encoded columns
            for col in self.onehot_cols:
                if col in X.columns:
                    print(col)
                    self.onehot_encoders[col] = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
                    self.onehot_encoders[col].fit(X[[col]])
                else:
                    logging.warning(f"One-hot encoding column {col} not found in input data.")
                    print(f"One-hot encoding column {col} not found in input data.")

            logging.info("Categorical Preprocessing fitting done.")
            return self

        except Exception as e:
            logging.error(f"Error in Preprocessor fit: {str(e)}")
            raise RuntimeError(f"Error in Preprocessor fit: {str(e)}")

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform the input data using fitted encoders.

        Args:
            X (pd.DataFrame): Input features to transform.

        Returns:
            pd.DataFrame: Transformed features.
        """
        try:
            logging.info("Categorical Preprocessing transform started...")
            X_transformed: pd.DataFrame = X.copy()

            # Apply LabelEncoder for 'Gender'
            if 'Gender' in X_transformed.columns:
                X_transformed['Gender'] = self.label_encoder.transform(X_transformed['Gender'])
            else:
                logging.warning("'Gender' column not found during transform.")

            # Apply binary mappings
            for col, mapping in self.binary_map_cols.items():
                if col in X_transformed.columns:
                    X_transformed[col] = X_transformed[col].map(mapping)
                    if X_transformed[col].isna().any():
                        logging.warning(f"Unknown values found in {col} during binary mapping.")
                        X_transformed[col].fillna(0, inplace=True)  # Default to 0 for unknown
                else:
                    logging.warning(f"Binary mapping column {col} not found in input data.")

            # Apply target encodings
            for col in self.target_encode_cols:
                if col in X_transformed.columns:
                    if col in self.target_encodings:
                        X_transformed[col] = X_transformed[col].map(self.target_encodings[col])
                        if X_transformed[col].isna().any():
                            logging.warning(f"Unknown categories in {col} during target encoding.")
                            X_transformed[col].fillna(self.target_encodings[col].mean(), inplace=True)
                    else:
                        print(f"Target encoding for {col} not fitted.")
                        raise ValueError(f"Target encoding for {col} not fitted.")

                else:
                    print(f"Target encoding column {col} not found in input data.")
                    logging.warning(f"Target encoding column {col} not found in input data.")

            # Apply one-hot encoding
            for col in self.onehot_cols:
                if col in X_transformed.columns:
                    if col in self.onehot_encoders:
                        encoded = self.onehot_encoders[col].transform(X_transformed[[col]])
                        encoded_df = pd.DataFrame(
                            encoded,
                            columns=[f"{self.onehot_prefixes[col]}_{cat}" for cat in self.onehot_encoders[col].categories_[0]],
                            index=X_transformed.index
                        )
                        X_transformed = pd.concat([X_transformed, encoded_df], axis=1)
                        X_transformed.drop(columns=[col], inplace=True)
                    else:
                        print(f"One-hot encoder for {col} not fitted.")
                        raise ValueError(f"One-hot encoder for {col} not fitted.")
                else:
                    print(f"One-hot encoding column {col} not found in input data.")
                    logging.warning(f"One-hot encoding column {col} not found in input data.")

            logging.info("Categorical Preprocessing transform done.")
            return X_transformed

        except Exception as e:
            logging.error(f"Error in Preprocessor transform: {str(e)}")
            raise RuntimeError(f"Error in Preprocessor transform: {str(e)}")

    def save(self, filename: str = "categorical_preprocessor.joblib"):
        """Save the fitted preprocessor to a file.

        Args:
            filename (str): Name of the file to save the preprocessor.
        """
        try:
            # save_path = os.path.join(self.save_dir, filename)
            joblib.dump(self, filename)
            logging.info(f"Preprocessor saved to {filename}")
        except Exception as e:
            logging.error(f"Error saving preprocessor: {str(e)}")
            raise RuntimeError(f"Error saving preprocessor: {str(e)}")


if __name__ == "__main__":
    preprocessor_path = "models/categorical_preprocessor.joblib"
    preprocessor = joblib.load(preprocessor_path)

# if __name__ == "__main__":
#     from src.pipeline.data_pipeline import DataLoadSplitPipeline

#     # Load and split data
#     data_load_pipeline = DataLoadSplitPipeline(
#         config_path='config.yaml', save_path='data/selected_data.xlsx')
#     X_train, X_test, y_train, y_test = data_load_pipeline.fit_transform()

#     # Initialize and fit preprocessor
#     preprocessor = CategoricalPreprocessor(config_path='config.yaml', save_dir='models')
#     preprocessor.fit(X_train, y_train)

#     # Transform training data
#     X_train_transformed = preprocessor.transform(X_train)
#     print("Transformed Training Data:")
#     print(X_train_transformed.head())

#     # Save the fitted preprocessor
#     preprocessor.save(filename="categorical_preprocessor.joblib")

#     # Load and transform test data using the saved preprocessor
#     X_test_transformed = CategoricalPreprocessor.load_and_transform(
#         X=X_test,
#         preprocessor_path=os.path.join('models', 'categorical_preprocessor.joblib')
#     )
#     print("\nTransformed Test Data:")
#     print(X_test_transformed.head())


