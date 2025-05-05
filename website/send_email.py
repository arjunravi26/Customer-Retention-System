import requests
import json
from .logger import logging

def send_email(customer_id, email_url="http://127.0.0.1:8002/generate_offer"):
    try:
        logging.info("Sending email request to the offer generation service...")
        headers = {'Content-Type': 'application/json'}
        payload = {"customer_id": customer_id}
        print(f"→ Sending POST to {email_url} with payload: {payload}")

        response = requests.post(email_url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        logging.info(f"Email repsonse is {data}")
        mail = data.get("offer_letter")
        logging.info(f"Generated email content:\n{mail}")
        return mail

    except Exception as e:
        logging.error(f"Error in send_email: {e}")
        return None
