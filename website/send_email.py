import requests
import json
from logger import logging
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
load_dotenv()
def send_email(customer_id, email_url="http://agno/generate_offer"):
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
        print(type(mail))
        logging.info(f"Mail type is {type(mail)}")
        send(mail)
        logging.info(f"Generated email content:\n{mail}")
        return mail

    except Exception as e:
        logging.error(f"Error in send_email: {e}")
    return None
def send(content: str):
    """Function to send email automatically to the user after the agent """
    try:
        # Create the email message
        msg = EmailMessage()
        msg['Subject'] = 'Customer Satisfaction'
        msg['From'] = 'arjunravi1523@gmail.com'  # Ensure this is the correct sender email
        msg['To'] = 'arjunravi726@gmail.com'  # Replace with the recipient's email
        msg.set_content(content)

        # SMTP configuration for SSL
        smtp_server = 'smtp.gmail.com'
        port = 465  # Port 465 for SSL
        sender_email = 'arjunravi1523@gmail.com'  # Ensure this is the correct sender email
        password = os.getenv('PASSWORD')  # Password from .env file

        if not password:
            logging.error("Password is not set in the environment variables.")
            return

        logging.info(f"Attempting to send email using the password: {password}")

        # Send the email using SSL (no need for starttls())
        with smtplib.SMTP_SSL(smtp_server, port) as server:  # Use SSL connection
            server.login(sender_email, password)
            server.send_message(msg)
            logging.info("Email sent successfully.")

    except Exception as e:
        logging.error(f"Error in sending email: {e}")
        print(f"Error in mail sending {e}")

