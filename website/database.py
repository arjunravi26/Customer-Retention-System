import os
import psycopg2
from psycopg2 import OperationalError, DatabaseError
from urllib.parse import urlparse
from logger import logging

def insert_chat_message(chat_id: str, customer_id: str, sender: str, message_content: str) -> bool:
    """
    Inserts a new chat message into the customer_chat table in the PostgreSQL database.

    Args:
        chat_id (str): The ID of the chat session.
        customer_id (str): The ID of the customer.
        sender (str): The sender of the message ('user' or 'chatbot').
        message_content (str): The content of the message.

    Returns:
        bool: True if the message was inserted successfully, False otherwise.

    Raises:
        OperationalError: If the database connection fails.
        DatabaseError: If the SQL execution fails.
        Exception: For any other unexpected errors.
    """
    conn = None
    cursor = None
    try:
        # Get DATABASE_URL from environment variable
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/telcom")
        parsed_url = urlparse(database_url)

        # Extract connection parameters
        db_params = {
            "database": parsed_url.path.lstrip("/"),
            "user": parsed_url.username,
            "password": parsed_url.password,
            "host": parsed_url.hostname,
            "port": parsed_url.port or 5432
        }

        logging.debug(f"Attempting to connect with params: {db_params}")
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        query = """
            INSERT INTO customer_chat (chat_id, customer_id, sender, message_content)
            VALUES (%s, %s, %s, %s);
        """
        cursor.execute(query, (chat_id, customer_id, sender, message_content))
        conn.commit()
        logging.info(f"Message inserted successfully into chat ID: {chat_id}, customer ID: {customer_id}, sender: {sender}")
        return True

    except OperationalError as oe:
        logging.error(f"Database connection error: {oe}")
        return False

    except DatabaseError as de:
        logging.error(f"SQL query execution error: {de}")
        if conn:
            conn.rollback()
        return False

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            logging.info("Connection to PostgreSQL closed after attempting to insert message.")

if __name__ == '__main__':
    # Example usage:
    chat_id_example = "user123_20250407152500_abc123"
    customer_id_example = "user123"
    user_message = "Hello, I have a question about my bill."
    chatbot_response = "Hi there! I'd be happy to help. What's your question?"

    # Insert a user message
    if insert_chat_message(chat_id_example, customer_id_example, "user", user_message):
        print("User message inserted.")
    else:
        print("Failed to insert user message.")

    # Insert a chatbot response
    if insert_chat_message(chat_id_example, customer_id_example, "chatbot", chatbot_response):
        print("Chatbot response inserted.")
    else:
        print("Failed to insert chatbot response.")

    # Insert with a different chat ID
    chat_id_example_2 = "user123_20250407153000_def456"
    user_message_2 = "Thank you!"
    if insert_chat_message(chat_id_example_2, customer_id_example, "user", user_message_2):
        print(f"User message inserted into new chat ID: {chat_id_example_2}")
    else:
        print(f"Failed to insert user message into new chat ID: {chat_id_example_2}")