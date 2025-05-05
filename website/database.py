import psycopg2


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
    """
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(
            database="telcom",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        query = """
            INSERT INTO customer_chat (chat_id, customer_id, sender, message_content)
            VALUES (%s, %s, %s, %s);
        """
        cursor.execute(query, (chat_id, customer_id, sender, message_content))
        conn.commit()
        print(f"Message inserted successfully into chat ID: {chat_id}, customer ID: {customer_id}, sender: {sender}")
        return True

    except psycopg2.Error as e:
        print(f"Error inserting message into PostgreSQL database: {e}")
        if conn:
            conn.rollback()  # Rollback the transaction in case of an error
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("Connection to PostgreSQL closed after attempting to insert message.")

if __name__ == '__main__':
    # Example usage:
    chat_id_example = "user123_20250407152500_abc123"  # Replace with an actual chat ID
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

    # You can also try inserting with a different chat ID for the same customer
    chat_id_example_2 = "user123_20250407153000_def456"
    user_message_2 = "Thank you!"
    if insert_chat_message(chat_id_example_2, customer_id_example, "user", user_message_2):
        print(f"User message inserted into new chat ID: {chat_id_example_2}")
    else:
        print(f"Failed to insert user message into new chat ID: {chat_id_example_2}")