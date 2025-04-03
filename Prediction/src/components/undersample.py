# src/components/undersampler.py
import pandas as pd
from sklearn.base import BaseEstimator
from src.logging import logging
from typing import Tuple
from src.utilities.undersample import undersample_majority

class Undersampler(BaseEstimator):
    """Class to undersample the majority class in a dataset using k-NN and DBSCAN clustering.

    Attributes:
        k (int): Number of neighbors to use in k-NN.
        percentile (float): Percentile threshold to differentiate sparse and dense points.
        eps (float): DBSCAN eps parameter for clustering dense points.
        min_samples (int): DBSCAN min_samples parameter.
    """

    def __init__(self, k: int = 5, percentile: float = 20, eps: float = 0.5, min_samples: int = 2):
        """Initialize the Undersampler with parameters for the undersampling process.

        Args:
            k (int): Number of neighbors to use in k-NN (default=5).
            percentile (float): Percentile threshold to differentiate sparse and dense points (default=20).
            eps (float): DBSCAN eps parameter for clustering dense points (default=0.5).
            min_samples (int): DBSCAN min_samples parameter (default=2).
        """
        logging.info(f"Under Sampler Initalizied.")
        self.k = k
        self.percentile = percentile
        self.eps = eps
        self.min_samples = min_samples

    def fit_resample(self, X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
        """Undersample the majority class in the dataset.

        Args:
            X (pd.DataFrame): Input features.
            y (pd.Series, optional): Target variable.

        Returns:
            Tuple[pd.DataFrame, pd.Series]: Reduced dataset (X_reduced, y_reduced).
        """
        try:
            logging.info("Starting undersampling of majority class...")
            if X.empty or y.empty:
                raise ValueError("Input data or labels are empty.")
            if len(X) != len(y):
                raise ValueError("X and y must have the same length.")

            class_counts = y.value_counts()
            majority_class_label = class_counts.idxmax()
            minority_class_label = class_counts.idxmin()

            logging.info(f"Majority class: {majority_class_label}, count: {class_counts[majority_class_label]}")
            logging.info(f"Minority class: {minority_class_label}, count: {class_counts[minority_class_label]}")

            majority_idx = y == majority_class_label
            minority_idx = y == minority_class_label

            X_majority = X[majority_idx].reset_index(drop=True)
            y_majority = y[majority_idx].reset_index(drop=True)
            X_minority = X[minority_idx].reset_index(drop=True)
            y_minority = y[minority_idx].reset_index(drop=True)

            X_majority_reduced, y_majority_reduced = undersample_majority(
                majority_class=X_majority,
                y_majority=y_majority,
                k=self.k,
                percentile=self.percentile,
                eps=self.eps,
                min_samples=self.min_samples
            )

            X_reduced = pd.concat([X_majority_reduced, X_minority], axis=0).reset_index(drop=True)
            y_reduced = pd.concat([y_majority_reduced, y_minority], axis=0).reset_index(drop=True)

            logging.info(f"Reduced majority class to {len(X_majority_reduced)} samples.")
            logging.info(f"Final dataset size: {len(X_reduced)} samples.")
            logging.info(f"Under Sampling finished.")

            return X_reduced,y_reduced
        except Exception as e:
            logging.error(f"Error in Undersampler transform: {str(e)}")
            raise RuntimeError(f"Error in Undersampler transform: {str(e)}")