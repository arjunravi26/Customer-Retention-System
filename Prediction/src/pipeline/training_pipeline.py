from sklearn.pipeline import Pipeline
from src.components.category_preprocess import CategoricalPreprocessor
from src.components.numerical_preprocess import NumericalPreprocessor
from src.components.model_trainer import ModelTrainer
from src.components.model_evaluation import ModelEvaluator
from src.components.hyperparamer_tuning import HyperparameterTuner
from src.pipeline.data_pipeline import DataLoadSplitPipeline
from src.components.undersample import Undersampler
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
from src.logging import logging
import pandas as pd


class TrainEvaluatePipeline:
    def __init__(self, config_path: str, sampling_strategy: int = 0.7):
        """Initialize the TrainEvaluatePipeline with configuration.

        Args:
            config_path (str): Path to the YAML configuration file.
        """
        self.config_path = config_path
        try:
            # Initialize preprocessing pipeline
            self.preprocessor = Pipeline(steps=[
                ('cat_preprocess', CategoricalPreprocessor(config_path)),
                ('num_preprocess', NumericalPreprocessor(config_path))
            ])
            self.data_balance_pipeline = ImbPipeline(steps=[
                ('undersampler', Undersampler(k=5, percentile=20, eps=0.5, min_samples=2)),
                ('oversampler', SMOTE(sampling_strategy=sampling_strategy, random_state=42))
            ])
            self.training_pipeline = Pipeline(steps=[
                ('model_trainer', ModelTrainer(config_path)),
                ('model_evaluator', ModelEvaluator(config_path))
            ])
            logging.info("TrainEvaluatePipeline initialized successfully.")
        except Exception as e:
            logging.error(
                f"Failed to initialize TrainEvaluatePipeline: {str(e)}")
            raise RuntimeError(
                f"Failed to initialize TrainEvaluatePipeline: {str(e)}")

    def fit_transform(self, X_train: pd.DataFrame, X_test: pd.DataFrame, y_train: pd.Series, y_test: pd.Series) -> dict:
        """Fit and transform the data through the pipeline.

        Args:
            data (Tuple): Tuple containing (X_train, X_test, y_train, y_test).

        Returns:
            dict: Evaluation metrics from ModelEvaluator.
        """
        try:
            logging.info("Starting TrainEvaluatePipeline fit_transform...")

            logging.info("Preprocessing training data...")
            X_train_transformed = self.preprocessor.fit_transform(
                X_train, y_train)
            logging.info("Preprocessing test data...")
            X_test_transformed = self.preprocessor.transform(X_test)
            X_train_resampled, y_train_resampled = self.data_balance_pipeline.fit_resample(
                X_train_transformed, y_train)
            logging.info("Starting hyperparameter tuning...")
            tuner = HyperparameterTuner(config_path=self.config_path)
            best_params = tuner.tune(X_train_resampled, y_train_resampled)
            tuner.update_config(best_params)
            logging.info("Hyperparameter tuning completed.")

            self.training_pipeline.steps[0] = (
                'model_trainer', ModelTrainer(self.config_path))
            logging.info("ModelTrainer reinitialized with best parameters.")

            logging.info("Starting training and evaluation...")
            metrics = self.training_pipeline.fit_transform(
                (X_train_resampled, X_test_transformed, y_train_resampled, y_test)
            )
            logging.info(
                "TrainEvaluatePipeline fit_transform completed successfully.")
            return metrics
        except Exception as e:
            logging.error(
                f"Error in TrainEvaluatePipeline fit_transform: {str(e)}")
            raise RuntimeError(
                f"Error in TrainEvaluatePipeline fit_transform: {str(e)}")

# if __name__ == "__main__":
#     try:
#         logging.info("Starting training pipeline execution...")
#         data_pipeline = DataLoadSplitPipeline(
#             config_path='config.yaml',
#             save_path='data/selected_data.xlsx'
#         )
#         X_train, X_test, y_train, y_test = data_pipeline.fit_transform()
#         train_pipeline = TrainEvaluatePipeline('config.yaml')
#         result = train_pipeline.fit_transform((X_train, X_test, y_train, y_test))
#         print("Evaluation Metrics:", result)
#         logging.info("Training pipeline execution completed successfully.")
#     except Exception as e:
#         logging.error(f"Error in main execution: {str(e)}")
#         raise


if __name__ == "__main__":
    data_pipeline = DataLoadSplitPipeline(
        config_path='config.yaml', save_path='data/selected_data.xlsx')
    X_train, X_test, y_train, y_test = data_pipeline.fit_transform()
    train_pipeline = TrainEvaluatePipeline('config.yaml')
    result = train_pipeline.fit_transform(X_train, X_test, y_train, y_test)
    print(result)