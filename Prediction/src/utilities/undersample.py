import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors


def undersample_majority(majority_class, y_majority, k=5, percentile=20, eps=0.5, min_samples=2):
    """
    Undersamples the majority class by keeping sparse points (with high average k-NN distances)
    and one representative from each dense cluster.

    Parameters:
    - majority_class: pd.DataFrame with the feature values of the majority class.
    - y_majority: pd.Series with labels corresponding to majority_class.
    - k: int, number of neighbors to use in k-NN (default=5).
    - percentile: float, percentile threshold to differentiate sparse and dense points (default=20).
    - eps: float, DBSCAN eps parameter for clustering dense points (default=0.5).
    - min_samples: int, DBSCAN min_samples parameter (default=2).

    Returns:
    - X_majority_reduced: pd.DataFrame, reduced majority class features.
    - y_majority_reduced: pd.Series, reduced majority class labels.
    """

    nn = NearestNeighbors(n_neighbors=k)
    nn.fit(majority_class)
    distances, indices = nn.kneighbors(majority_class)
    avg_distances = np.mean(distances, axis=1)

    threshold = np.percentile(avg_distances, percentile)

    sparse_idx = np.where(avg_distances > threshold)[0]
    dense_idx = np.where(avg_distances <= threshold)[0]

    dense_data = majority_class.iloc[dense_idx]
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    cluster_labels = dbscan.fit_predict(dense_data)

    dense_representatives = []
    unique_labels = np.unique(cluster_labels)

    for label in unique_labels:
        if label == -1:
            continue
        cluster_local_indices = np.where(cluster_labels == label)[0]
        representative_original_idx = dense_idx[cluster_local_indices[0]]
        dense_representatives.append(representative_original_idx)

    noise_indices = dense_idx[cluster_labels == -1]

    final_keep_idx = np.concatenate(
        [sparse_idx, np.array(dense_representatives), noise_indices])
    final_keep_idx = np.unique(final_keep_idx)

    X_majority_reduced = majority_class.iloc[final_keep_idx]
    y_majority_reduced = y_majority.iloc[final_keep_idx]

    return X_majority_reduced, y_majority_reduced
