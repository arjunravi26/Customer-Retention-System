import pandas as pd
import yaml
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from src.logging import logging
from typing import Dict, Any

class HyperparameterTuner:
    """Class to perform hyperparameter tuning for Logistic Regression using GridSearchCV."""

    def __init__(self, config_path: str):
        """Initialize the HyperparameterTuner with configuration.

        Args:
            config_path (str): Path to the YAML configuration file.
        """
        logging.info(f"Hyperparameter Tuner Initialized")
        self.config_path = config_path
        try:
            with open(config_path, 'r') as file:
                self.config: Dict[str, Any] = yaml.safe_load(file)
            self.param_grid = self.config.get('param_grid', {})
        except Exception as e:
            logging.error(f"Failed to load config.yaml file: {str(e)}")
            raise RuntimeError(f"Failed to load config.yaml file: {str(e)}")

    def tune(self, X_train: pd.DataFrame, y_train: pd.Series) -> Dict[str, Any]:
        """Perform hyperparameter tuning using GridSearchCV.

        Args:
            X_train (pd.DataFrame): Training features.
            y_train (pd.Series): Training labels.

        Returns:
            Dict[str, Any]: Best parameters found during tuning.
        """
        try:
            logging.info("Starting hyperparameter tuning with GridSearchCV...")

            if X_train.empty or y_train.empty:
                raise ValueError("Training data or labels are empty.")

            model = LogisticRegression(random_state=42)

            grid_search = GridSearchCV(
                estimator=model,
                param_grid=self.param_grid,
                cv=5,
                scoring='f1',
                n_jobs=-1,
                verbose=1
            )

            grid_search.fit(X_train, y_train)
            logging.info("Hyperparameter tuning completed successfully.")

            best_params = grid_search.best_params_
            best_score = grid_search.best_score_
            logging.info(f"Best parameters: {best_params}")
            logging.info(f"Best F1 score: {best_score}")

            return best_params
        except Exception as e:
            logging.error(f"Error in HyperparameterTuner tune: {str(e)}")
            raise RuntimeError(f"Error in HyperparameterTuner tune: {str(e)}")

    def update_config(self, best_params: Dict[str, Any]):
        """Update the config file with the best parameters.

        Args:
            best_params (Dict[str, Any]): Best parameters to save.
        """
        try:
            logging.info(f"Hyperparameter updation started")
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)

            config['model_params'] = best_params

            with open(self.config_path, 'w') as file:
                yaml.safe_dump(config, file)
            logging.info("Config file updated with best parameters.")
        except Exception as e:
            logging.error(f"Error updating config with best parameters: {str(e)}")
            raise RuntimeError(f"Error updating config with best parameters: {str(e)}")
