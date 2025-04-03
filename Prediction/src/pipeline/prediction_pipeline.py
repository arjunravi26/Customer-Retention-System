import pandas as pd
import joblib
from src.components.category_preprocess import CategoricalPreprocessor
from src.components.numerical_preprocess import NumericalPreprocessor
from src.pipeline.data_pipeline import DataLoadSplitPipeline
from src.logging import logging
from sklearn.metrics import accuracy_score
class PredictionPipeline:
    def __init__(self, config_path: str, model_path: str = None):
        self.config_path = config_path
        self.model_path = model_path
        try:
            self.categorical_preprocessor = CategoricalPreprocessor(
                config_path)
            self.numerical_preprocessor = NumericalPreprocessor(config_path)
            self.model = joblib.load(model_path)
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize PredictionPipeline: {str(e)}")

    def fit(self, X: pd.DataFrame, y=pd.Series):
        self.categorical_preprocessor.fit(X, y)
        self.numerical_preprocessor.fit(X, y)
        return self

    def transform(self, X: pd.DataFrame, y: pd.Series) -> pd.Series:
        try:
            X_transformed= self.categorical_preprocessor.transform(X, y)
            X_transformed= self.numerical_preprocessor.transform(
                X_transformed, y)
            predictions = self.model.predict(X_transformed)
            return pd.Series(predictions, index=X.index, name='predictions')
        except Exception as e:
            raise RuntimeError(
                f"Error in PredictionPipeline transform: {str(e)}")

if __name__ == "__main__":
    data_pipeline = DataLoadSplitPipeline(config_path='config.yaml',save_path='data/selected_data.xlsx')
    X_train,X_test,y_train,y_test = data_pipeline.fit_transform()
    prediction_pipeline = PredictionPipeline('config.yaml','models/churn_model.pkl')
    prediction_pipeline.fit(X_train,y_train)
    y_pred = prediction_pipeline.transform(X_test,y_test)
    logging.info(f"Prediction is {y_pred}\n and the accuracy is {accuracy_score(y_pred,y_train)}")
    print(accuracy_score(y_pred,y_train))
