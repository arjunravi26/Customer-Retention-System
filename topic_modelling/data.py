import psycopg2
from psycopg2 import OperationalError, DatabaseError
from typing import List, Tuple
from logger import logging


def fetch_data() -> List[Tuple[str]]:
    """
    Fetches all message content sent by users from the 'customer_chat' table in the 'telcom' PostgreSQL database.

    Returns:
        List[Tuple[str]]: A list of tuples containing the user messages. Each tuple contains one string message.

    Raises:
        OperationalError: If the database connection fails.
        DatabaseError: If the SQL execution fails.
        Exception: For any other unexpected errors.
    """
    try:
        with psycopg2.connect(
            database="telcom",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        ) as conn:
            logging.info("Connected to PostgreSQL successfully.")

            with conn.cursor() as cursor:
                query: str = "SELECT message_content FROM customer_chat WHERE sender = 'user'"
                cursor.execute(query)
                results: List[Tuple[str]] = cursor.fetchall()
                logging.info(
                    f"Fetched {len(results)} rows from customer_chat.")
                chats = [doc[0] for doc in results]
                return chats

    except OperationalError as oe:
        logging.error(f"Database connection error: {oe}")
        raise oe

    except DatabaseError as de:
        logging.error(f"SQL query execution error: {de}")
        raise de

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise e
    
# fetch_data()
