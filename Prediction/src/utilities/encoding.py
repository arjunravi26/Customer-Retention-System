import pandas as pd


# EncodedValue = λ × CategoryMean + (1−λ) × GlobalMean
def target_encode(df: pd.DataFrame, category_col: str, target_col: str, alpha=5):
    """
    Apply smoothing to category encoding using pandas.

    Parameters:
    df (pd.DataFrame): DataFrame containing the categorical and target columns.
    category_col (str): Name of the categorical column.
    target_col (str): Name of the target column.
    alpha (int): Smoothing parameter (higher values give more weight to the category mean).

    Returns:
    pd.Series: Smoothed encoding values for each category.
    """
    category_stats = df.groupby(category_col)[
        target_col].agg(['count', 'mean'])
    global_mean = df[target_col].mean()

    lambda_val = category_stats['count'] / (category_stats['count'] + alpha)
    smoothed_values = lambda_val * \
        category_stats['mean'] + (1 - lambda_val) * global_mean
    print(smoothed_values)

    return df[category_col].map(smoothed_values)
