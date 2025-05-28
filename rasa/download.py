from transformers import AutoTokenizer,TFAutoModel
from dotenv import load_dotenv
import os

load_dotenv()

# These lines are now safe for public models
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
model = TFAutoModel.from_pretrained("distilbert-base-uncased")

print("Model and tokenizer downloaded successfully.")

