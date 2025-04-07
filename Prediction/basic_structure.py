import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import logging
import os
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)


class DataLoader:
    """Class to handle data loading from a specified source."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_data(self) -> pd.DataFrame:
        """Load data from a CSV file with error handling."""
        try:
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(
                    f"Data file not found at {self.file_path}")
            data = pd.read_csv(self.file_path)
            logging.info(
                f"Data loaded successfully from {self.file_path}. Shape: {data.shape}")
            return data
        except Exception as e:
            logging.error(f"Error loading data: {str(e)}")
            raise


class Preprocessor:
    """Class to handle data preprocessing including imputation and encoding."""

    def __init__(self, numerical_features: list, categorical_features: list):
        self.numerical_features = numerical_features
        self.categorical_features = categorical_features
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', Pipeline(steps=[
                    ('imputer', SimpleImputer(strategy='mean')),
                    ('scaler', StandardScaler())
                ]), numerical_features),
                ('cat', Pipeline(steps=[
                    ('imputer', SimpleImputer(strategy='most_frequent')),
                    ('onehot', OneHotEncoder(
                        handle_unknown='ignore', sparse_output=False))
                ]), categorical_features)
            ])

    def fit_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Fit and transform the data."""
        try:
            transformed_data = self.preprocessor.fit_transform(data)
            logging.info("Data preprocessing completed.")
            return transformed_data
        except Exception as e:
            logging.error(f"Error in preprocessing: {str(e)}")
            raise

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform new data using the fitted preprocessor."""
        try:
            transformed_data = self.preprocessor.transform(data)
            return transformed_data
        except Exception as e:
            logging.error(f"Error transforming data: {str(e)}")
            raise


class ChurnPredictionPipeline:
    """Main pipeline class for training and predicting customer churn."""

    def __init__(self, config_path: str):
        """Initialize the pipeline with configuration from a YAML file."""
        try:
            with open(config_path, 'r') as file:
                self.config = yaml.safe_load(file)
            self.numerical_features = self.config['numerical_features']
            self.categorical_features = self.config['categorical_features']
            self.target = self.config['target']
            self.model_path = self.config.get(
                'model_path', 'models/churn_pipeline.pkl')

            # Define the full pipeline
            self.preprocessor = Preprocessor(
                self.numerical_features, self.categorical_features)
            self.model = RandomForestClassifier(random_state=42)
            self.pipeline = Pipeline(steps=[
                ('preprocessor', self.preprocessor.preprocessor),
                ('classifier', self.model)
            ])
            logging.info("Pipeline initialized with configuration.")
        except Exception as e:
            logging.error(f"Error initializing pipeline: {str(e)}")
            raise

    def validate_data(self, data: pd.DataFrame, include_target: bool = True) -> None:
        """Validate that the data contains all required columns."""
        required_columns = self.numerical_features + self.categorical_features
        if include_target:
            required_columns += [self.target]
        missing_columns = [
            col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing columns in data: {missing_columns}")

    def train(self, data: pd.DataFrame) -> tuple:
        """Train the pipeline on the provided dataset."""
        try:
            self.validate_data(data, include_target=True)
            X = data[self.numerical_features + self.categorical_features]
            y = data[self.target]
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42)

            self.pipeline.fit(X_train, y_train)
            y_pred = self.pipeline.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred)
            logging.info(f"Training completed. Accuracy: {accuracy}")
            logging.info(f"Classification Report:\n{report}")
            return accuracy, report
        except Exception as e:
            logging.error(f"Error during training: {str(e)}")
            raise

    def predict(self, data: pd.DataFrame) -> pd.Series:
        """Make predictions on new data."""
        try:
            self.validate_data(data, include_target=False)
            X = data[self.numerical_features + self.categorical_features]
            predictions = self.pipeline.predict(X)
            logging.info("Predictions generated successfully.")
            return pd.Series(predictions, index=data.index)
        except Exception as e:
            logging.error(f"Error during prediction: {str(e)}")
            raise

    def save_pipeline(self) -> None:
        """Save the trained pipeline to disk."""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.pipeline, self.model_path)
            logging.info(f"Pipeline saved to {self.model_path}")
        except Exception as e:
            logging.error(f"Error saving pipeline: {str(e)}")
            raise

    @staticmethod
    def load_pipeline(model_path: str) -> Pipeline:
        """Load a saved pipeline from disk."""
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(
                    f"Pipeline file not found at {model_path}")
            pipeline = joblib.load(model_path)
            logging.info(f"Pipeline loaded from {model_path}")
            return pipeline
        except Exception as e:
            logging.error(f"Error loading pipeline: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    # Example configuration (config.yaml)
    config_content = """
    numerical_features:
      - tenure
      - MonthlyCharges
      - TotalCharges
    categorical_features:
      - gender
      - InternetService
      - Contract
    target: Churn
    model_path: models/churn_pipeline.pkl
    """
    with open('config.yaml', 'w') as f:
        f.write(config_content)

    # Load data
    data_loader = DataLoader('data/customer_churn.csv')
    data = data_loader.load_data()

    # Initialize and train pipeline
    pipeline = ChurnPredictionPipeline('config.yaml')
    accuracy, report = pipeline.train(data)

    # Save the trained pipeline
    pipeline.save_pipeline()

    # Example prediction on new data
    # new_data = pd.read_csv('new_data.csv')
    # predictions = pipeline.predict(new_data)
