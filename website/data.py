import psycopg2
from psycopg2 import OperationalError, DatabaseError
from typing import List, Tuple
import os
import psycopg2
from psycopg2 import OperationalError, DatabaseError
from urllib.parse import urlparse
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
