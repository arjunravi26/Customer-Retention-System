import pandas as pd
import numpy as np
import yaml
from typing import Dict, Any
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from src.logging import logging
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import RobustScaler
from src.utilities.log_transformer import LogTransformer
import joblib
import os

class NumericalPreprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, config_path: str, save_dir: str = "models"):
        """Initialize the Preprocessor with a configuration file and save directory.

        Args:
            config_path (str): Path to the YAML configuration file.
            save_dir (str): Directory to save the fitted preprocessor object.
        """
        logging.info("Numerical Preprocessor Initialized.")
        self.config_path = config_path
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)  # Create save directory if it doesn't exist

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

    def _handle_empty_total_charges(self, X: pd.DataFrame) -> pd.DataFrame:
        """Handle empty or invalid values in 'Total Charges' column.

        Args:
            X (pd.DataFrame): Input features.

        Returns:
            pd.DataFrame: DataFrame with 'Total Charges' imputed and converted to float.
        """
        try:
            logging.info("Handling empty total charges.")
            X_transformed = X.copy()
            if 'Total Charges' in X_transformed.columns:
                # Identify valid numeric rows and invalid rows
                mask = X_transformed['Total Charges'].apply(lambda x: isinstance(x, (int, float)) and not pd.isna(x))
                null_rows = X_transformed[~mask]
                not_null_rows = X_transformed[mask]

                # Impute valid rows during fit, or transform all during transform
                if len(not_null_rows) > 0:
                    if not hasattr(self.total_charges_imputer, 'statistics_'):  # If not fitted
                        self.total_charges_imputer.fit(not_null_rows['Total Charges'].to_numpy().reshape(-1, 1))
                    imputed_values = self.total_charges_imputer.transform(
                        not_null_rows['Total Charges'].astype(float).values.reshape(-1, 1)
                    )
                    X_transformed.loc[mask, 'Total Charges'] = imputed_values.flatten()

                # Impute invalid rows (NaN or non-numeric)
                if len(null_rows) > 0:
                    imputed_values = self.total_charges_imputer.transform(
                        np.array([np.nan] * len(null_rows)).reshape(-1, 1)
                    )
                    X_transformed.loc[null_rows.index, 'Total Charges'] = imputed_values.flatten()

                X_transformed['Total Charges'] = X_transformed['Total Charges'].astype(float)
            else:
                logging.warning("'Total Charges' column not found in input data.")
            logging.info("Successfully handled empty total charges.")
            return X_transformed
        except Exception as e:
            raise RuntimeError(f"Error in handling null value in total charges: {str(e)}")

    def fit(self, X: pd.DataFrame, y: pd.Series = None):
        """Fit the preprocessor on the training data.

        Args:
            X (pd.DataFrame): Input features.
            y (pd.Series, optional): Target variable (not used here).

        Returns:
            self: Fitted preprocessor instance.
        """
        try:
            logging.info("Numerical Preprocessor fit started...")
            X_transformed = X.copy()

            # Fit imputer for 'Total Charges'
            if 'Total Charges' in X_transformed.columns:
                X_transformed = self._handle_empty_total_charges(X_transformed)
            else:
                logging.warning("'Total Charges' column not found during fit.")

            # Fit scaling pipeline
            if all(col in X_transformed.columns for col in self.scale_cols):
                self.scaling_pipeline.fit(X_transformed[self.scale_cols])
            else:
                missing_cols = [col for col in self.scale_cols if col not in X_transformed.columns]
                logging.warning(f"Scaling columns missing in input data: {missing_cols}")

            logging.info("Numerical Preprocessor fit ended.")
            return self
        except Exception as e:
            logging.error(f"Error in Preprocessor fit: {str(e)}")
            raise RuntimeError(f"Error in Preprocessor fit: {str(e)}")

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform the input data using fitted imputer and scaling pipeline.

        Args:
            X (pd.DataFrame): Input features to transform.

        Returns:
            pd.DataFrame: Transformed features.
        """
        try:
            logging.info("Numerical Preprocessor transform started...")
            X_transformed = X.copy()

            # Apply imputation to 'Total Charges'
            if 'Total Charges' in X_transformed.columns:
                X_transformed = self._handle_empty_total_charges(X_transformed)
            else:
                logging.warning("'Total Charges' column not found during transform.")

            # Apply scaling pipeline
            if all(col in X_transformed.columns for col in self.scale_cols):
                X_transformed[self.scale_cols] = self.scaling_pipeline.transform(X_transformed[self.scale_cols])
            else:
                missing_cols = [col for col in self.scale_cols if col not in X_transformed.columns]
                logging.warning(f"Scaling columns missing in input data during transform: {missing_cols}")

            logging.info("Numerical Preprocessor transform ended.")
            return X_transformed
        except Exception as e:
            logging.error(f"Error in Preprocessor transform: {str(e)}")
            raise RuntimeError(f"Error in Preprocessor transform: {str(e)}")

    def save(self, filename: str = "numerical_preprocessor.joblib"):
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

# if __name__ == "__main__":
#     from src.pipeline.data_pipeline import DataLoadSplitPipeline
#     from src.components.category_preprocess import CategoricalPreprocessor

#     # Load and split data
#     data_load_pipeline = DataLoadSplitPipeline(
#         config_path='config.yaml', save_path='data/selected_data.xlsx')
#     X_train, X_test, y_train, y_test = data_load_pipeline.fit_transform()

#     # Preprocess categorical features
#     categorical_preprocessor = CategoricalPreprocessor(config_path='config.yaml')
#     categorical_preprocessor.fit(X_train, y_train)
#     X_train_cat = categorical_preprocessor.transform(X_train)
#     X_test_cat = categorical_preprocessor.transform(X_test)

#     # Preprocess numerical features
#     numerical_preprocessor = NumericalPreprocessor(config_path='config.yaml', save_dir='models')
#     numerical_preprocessor.fit(X_train_cat, y_train)
#     X_train_transformed = numerical_preprocessor.transform(X_train_cat)
#     print("Transformed Training Data:")
#     print(X_train_transformed.head())

#     # Save the fitted preprocessor
#     numerical_preprocessor.save(filename="numerical_preprocessor.joblib")

#     # Load and transform test data using the saved preprocessor
#     X_test_transformed = NumericalPreprocessor.load_and_transform(
#         X=X_test_cat,
#         preprocessor_path=os.path.join('models', 'numerical_preprocessor.joblib')
#     )
#     print("\nTransformed Test Data:")
#     print(X_test_transformed.head())

import pandas as pd
from src.pipeline.data_pipeline import DataLoadSplitPipeline
from src.components.category_preprocess import CategoricalPreprocessor
from src.components.numerical_preprocess import NumericalPreprocessor
from sklearn.linear_model import LogisticRegression
import joblib
from src.logging import logging

if __name__ == "__main__":
    # Load data
    data_pipeline = DataLoadSplitPipeline(config_path='config.yaml', save_path='data/selected_data.xlsx')
    X_train, X_test, y_train, y_test = data_pipeline.fit_transform()

    # Preprocess categorical features
    cat_preprocessor = CategoricalPreprocessor(config_path='config.yaml')
    cat_preprocessor.fit(X_train, y_train)
    X_train_cat = cat_preprocessor.transform(X_train)

    # Preprocess numerical features
    num_preprocessor = NumericalPreprocessor(config_path='config.yaml')
    num_preprocessor.fit(X_train_cat, y_train)
    X_train_transformed = num_preprocessor.transform(X_train_cat)
    from src.components.model_trainer import ModelTrainer

    # # Train model
    # model = LogisticRegression()
    # model.fit(X_train_transformed, y_train)
    # model_trainer = ModelTrainer('config.yaml')
    # model_trainer.fit(X_train_transformed,y_train)
    # model_trainer.transform(X_train_transformed,y_train)

    # Save preprocessors and model
    joblib.dump(cat_preprocessor, 'models/categorical_preprocessor.joblib')
    joblib.dump(num_preprocessor, 'models/numerical_preprocessor.joblib')
    # joblib.dump(model, 'models/churn_model.pkl')
    logging.info("Models and preprocessors saved successfully.")