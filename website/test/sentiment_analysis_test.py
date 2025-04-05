import unittest
from unittest.mock import patch, MagicMock
from sentimental_analysis import SentimentalAnalysis

class TestSentimentalAnalysis(unittest.TestCase):

    @patch('sentimental_analysis.pipeline')  # Patch pipeline from transformers
    def test_model_initialization(self, mock_pipeline):
        mock_pipeline.return_value = MagicMock()
        model = SentimentalAnalysis()
        self.assertIsNotNone(model.model)

    @patch('sentimental_analysis.pipeline')
    def test_analysis_positive(self, mock_pipeline):
        # Mock pipeline and its return value
        mock_model = MagicMock()
        mock_model.predict.return_value = [{'label': 'POSITIVE', 'score': 0.99}]
        mock_pipeline.return_value = mock_model

        sa = SentimentalAnalysis()
        result = sa.analysis("You are awesome!")

        self.assertEqual(result, [{'label': 'POSITIVE', 'score': 0.99}])
        mock_model.predict.assert_called_once_with("You are awesome!")

    @patch('sentimental_analysis.pipeline')
    def test_analysis_error_handling(self, mock_pipeline):
        mock_model = MagicMock()
        mock_model.predict.side_effect = Exception("Mocked Error")
        mock_pipeline.return_value = mock_model

        sa = SentimentalAnalysis()
        with self.assertRaises(Exception) as context:
            sa.analysis("This will fail")

        self.assertIn("Mocked Error", str(context.exception))

if __name__ == "__main__":
    unittest.main()
