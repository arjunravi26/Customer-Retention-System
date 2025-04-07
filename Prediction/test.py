# import unittest

# class TestStringMethods(unittest.TestCase):

#     def test_upper(self):
#         self.assertEqual('foo'.upper(), 'FOO')

#     def test_isupper(self):
#         self.assertTrue('FOO'.isupper())
#         self.assertFalse('Foo'.islower())
#         self.assertTrue('foo'.islower())


#     def test_split(self):
#         s = 'hello world'
#         self.assertEqual(s.split(), ['hello', 'world'])
#         # check that s.split fails when the separator is not a string
#         with self.assertRaises(TypeError):
#             s.split(2)

# if __name__ == '__main__':
#     unittest.main()

from sklearn.datasets import make_classification
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import numpy as np


def test_load_data():
    X, y = make_classification(n_samples=100, n_features=4, random_state=42)
    assert X.shape == (100, 4), "The shape of X should be (100, 4)"
    assert y.shape == (100,), "The shape of y should be (100,)"


test_load_data()


def test_transform_data():
    X, y = make_classification(n_features=4, n_samples=100, random_state=42)
    scaler = StandardScaler()
    X_mean = 0
    X_std = 1.000010013
    X_scaled = scaler.fit_transform(X)
    assert np.isclose(np.mean(X_scaled), 0), f"The mean value of X Scaled is {np.mean(X_scaled)} and the expected value is {X_mean}"
    assert np.isclose(np.std(X_scaled), 1.000010013), f"The std value of X Scaled is {np.std(X_scaled)} and the expected value is {X_std}"


test_transform_data()


def test_model_training():
    X, y = make_classification(n_samples=100, n_features=4, random_state=42)
    model = LogisticRegression(random_state=42)
    assert hasattr(
        model, "coef_"), "The model have coef_ after training"
    model.fit(X, y)



test_model_training()


def test_model_integration():
    X, y = make_classification(n_samples=100, n_features=2, random_state=42)
    model = LogisticRegression(random_state=42).fit(X, y)
    predictions = model.predict(X)
    assert set(predictions) <= {0, 1}, "Predictions should be 0 or 1"

test_model_integration()
