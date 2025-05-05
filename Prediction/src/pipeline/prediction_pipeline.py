# src/pipeline/prediction_pipeline.py
import pandas as pd
from src.pipeline.data_pipeline import DataLoadSplitPipeline
from src.components.category_preprocess import CategoricalPreprocessor
from src.components.numerical_preprocess import NumericalPreprocessor
import joblib
import os
import yaml
from src.logging import logging
from sklearn.metrics import accuracy_score

class PredictionPipeline:
    def __init__(self, config_path: str):
        """
        Initialize the PredictionPipeline with pre-fitted preprocessors and model.

        Args:
            config_path (str): Path to the configuration file specifying model paths.
        """
        self.config_path = config_path
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            # Use config to specify paths, with defaults
            self.cat_preprocessor_path = config.get('categorical_preprocessor_path', 'models/categorical_preprocessor.joblib')
            self.num_preprocessor_path = config.get('numerical_preprocessor_path', 'models/numerical_preprocessor.joblib')
            self.model_path = config.get('model_path', 'models/churn_model.pkl')
            # Load pre-fitted preprocessors and model once
            self.cat_preprocessor = joblib.load(self.cat_preprocessor_path)
            logging.info(f"Categorical preprocessor loaded from {self.cat_preprocessor_path}")
            self.num_preprocessor = joblib.load(self.num_preprocessor_path)
            logging.info(f"Numerical preprocessor loaded from {self.num_preprocessor_path}")
            self.model = joblib.load(self.model_path)
            logging.info(f"Model loaded from {self.model_path}")
        except FileNotFoundError as e:
            logging.error(f"File not found during initialization: {e}")
            raise
        except Exception as e:
            logging.error(f"Error initializing PredictionPipeline: {e}", exc_info=True)
            raise

    def transform_predict(self, X: pd.DataFrame):
        """
        Transform input data and predict churn scores.

        Args:
            X (pd.DataFrame): Input features.

        Returns:
            numpy.ndarray: Predicted churn scores.
        """
        try:
            print('here')
            logging.info(f"Input data columns: {X.columns.tolist()}")
            logging.info(f"Input data sample: {X.iloc[0].to_dict()}")

            # Apply categorical preprocessing
            # print('here',self.cat_preprocessor.transform())
            X_cat = self.cat_preprocessor.transform(X)
            print(f"complete categorical preprocessing {X_cat}")
            logging.info("Categorical preprocessing completed.")

            # Apply numerical preprocessing
            X_transformed = self.num_preprocessor.transform(X_cat)
            logging.info(f"Numerical preprocessing completed. Transformed shape: {X_transformed.shape}")
            print(f"complete numerical preprocessing {X_transformed}")
            # Predict
            print(self.model.feature_names_in_)
            predictions = self.model.predict_proba(X_transformed)
            logging.info(f"Prediction completed: {predictions}")
            print(predictions)
            return predictions

        except Exception as e:
            logging.error(f"Error in transform_predict: {e}", exc_info=True)
            raise e

if __name__ == "__main__":
    data_pipeline = DataLoadSplitPipeline(config_path='config.yaml', save_path='data/selected_data.xlsx')
    X_train, X_test, y_train, y_test = data_pipeline.fit_transform()
    prediction_pipeline = PredictionPipeline('config.yaml')
    y_pred = prediction_pipeline.transform_predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    logging.info(f"Prediction is {y_pred}\n and the accuracy is {accuracy}")
    print(f"Accuracy: {accuracy}")