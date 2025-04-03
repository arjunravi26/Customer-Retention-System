from sklearn.pipeline import Pipeline
from src.components.data_ingestion import DataLoader
from src.components.feature_extraction import FeatureExtraction
from src.components.split_data import SplitData
from typing import Tuple
import pandas as pd
class DataLoadSplitPipeline:
    def __init__(self, config_path: str, save_path: str):
        self.config_path = config_path
        self.save_path = save_path
        try:
            self.pipeline = Pipeline(steps=[
                ('data_loader', DataLoader(config_path)),
                ('feature_extraction', FeatureExtraction(config_path)),
                ('split_data', SplitData(config_path))
            ])
        except Exception as e:
            raise RuntimeError(f"Failed to initialize DataLoadSplitPipeline: {str(e)}")

    def fit_transform(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        try:
            X_train, X_test, y_train, y_test = self.pipeline.fit_transform(None)
            return (X_train, X_test, y_train, y_test)
        except Exception as e:
            raise RuntimeError(f"Error in DataLoadSplitPipeline fit_transform: {str(e)}")
