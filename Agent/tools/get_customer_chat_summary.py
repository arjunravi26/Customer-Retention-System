from agno.tools.toolkit import Toolkit
from typing import Dict, List, Union
import json
import psycopg2

class RetrieveLastChatTool(Toolkit):
    """A tool for retrieving the last chat conversation for a given customer."""

    def __init__(self, customer_id):
        super().__init__(name="retrieve_last_chat")
        self.customer_id = customer_id

    def run(self) -> str:
        """
        Retrieves the last chat conversation for the given customer ID from the PostgreSQL database.

        Returns:
            str: A JSON string containing a list of messages from the last chat.
                 Each message is a dictionary with 'sender' and 'message_content' keys.
                 Example: '[{"sender": "user", "message_content": "Hello"}, {"sender": "chatbot", "message_content": "Hi, how can I help you?"}]'
                 Returns '{"message": "No chat history found for this customer."}' if no chat is found.

        Output Schema:
            {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "sender": {"type": "string", "enum": ["user", "chatbot"]},
                        "message_content": {"type": "string"}
                    }
                }
            }
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
            print(f"Connected to PostgreSQL for retrieving last chat for customer: {self.customer_id}")
            cursor = conn.cursor()

            # Find the chat_id of the most recent chat for the customer
            query_last_chat_id = """
                SELECT chat_id
                FROM customer_chat
                WHERE customer_id = %s
                ORDER BY timestamp DESC
                LIMIT 1;
            """
            cursor.execute(query_last_chat_id, (self.customer_id,))
            last_chat_result = cursor.fetchone()

            if last_chat_result:
                last_chat_id = last_chat_result[0]
                # Retrieve all messages from the last chat session
                query_messages = """
                    SELECT sender, message_content
                    FROM customer_chat
                    WHERE chat_id = %s AND customer_id = %s
                    ORDER BY timestamp ASC;
                """
                cursor.execute(query_messages, (last_chat_id, self.customer_id))
                messages_data = cursor.fetchall()
                messages_list = [{"sender": sender, "message_content": content} for sender, content in messages_data]
                return json.dumps(messages_list)
            else:
                return json.dumps({"message": "No chat history found for this customer."})

        except psycopg2.Error as e:
            print(f"Error retrieving last chat from PostgreSQL: {e}")
            return json.dumps({"error": "Database error while retrieving chat history."})
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                print("Connection to PostgreSQL closed after retrieving last chat.")

if __name__ == '__main__':
    # Example usage (for testing purposes)
    customer_id_to_retrieve = "user123"  # Replace with an actual customer ID from your database
    last_chat_retriever = RetrieveLastChatTool(customer_id=customer_id_to_retrieve)
    last_chat_json = last_chat_retriever.run()
    print("\nLast Chat History:")
    print(last_chat_json)

    customer_id_no_chat = "new_user"  # Replace with a customer ID that has no chat history
    last_chat_retriever_no_chat = RetrieveLastChatTool(customer_id=customer_id_no_chat)
    last_chat_no_chat_json = last_chat_retriever_no_chat.run()
    print("\nLast Chat History (No Chat):")
    print(last_chat_no_chat_json)