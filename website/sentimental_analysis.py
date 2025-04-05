from logger import logging
from transformers import pipeline
from dotenv import load_dotenv


class SentimentalAnalysis:
    "Sentimental Analysis model using hugging face to evaluate the sentiment of customer chats."

    def __init__(self):
        logging.info(f"Initialized Sentimental Analysis model.")
        try:
            load_dotenv()
            self.model = pipeline('sentiment-analysis', device='cuda')
        except Exception as e:
            logging.error(f"Error in creating sentimental model {e}")
            raise e

    def analysis(self, text: str) -> str:
        try:
            logging.info(f"Started analysis text is {text}")
            sentiment = self.model.predict(text)
            return sentiment
        except Exception as e:
            logging.error(f"Error in analysis {e}")
            raise e


if __name__ == "__main__":
    sentiment_anlaysis = SentimentalAnalysis()
    result = sentiment_anlaysis.analysis("I love you.")
    print(result)
