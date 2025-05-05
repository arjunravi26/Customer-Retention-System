from agno.tools.toolkit import Toolkit
from typing import Dict, List, Union
import json
import psycopg2

class CustomeData(Toolkit):
    """A tool for retrieving customer data from the database"""

    def __init__(self, customer_id):
        super().__init__(name="get_customer_data")
        self.customer_id = customer_id

    def run(self) -> str:
        """
        Retrieves the information about the customer from the PostgreSQL database
        based on the provided customer ID.

        Returns:
            str: A JSON string containing the customer's data.
                 Example: '{"CustomerID": "123", "TenureMonths": 24, "MonthlyCharges": 95.0, ...}'
                 Returns '{}' if no customer data is found for the given ID.

   
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
            print("Connected to PostgreSQL database successfully for fetching customer data.")
            cursor = conn.cursor()
            query = "SELECT * FROM customer_data WHERE CustomerID = %s"
            cursor.execute(query, (self.customer_id,))
            customer_data = cursor.fetchone()

            if customer_data:
                column_names = [desc[0] for desc in cursor.description]
                customer_dict = dict(zip(column_names, customer_data))
                return json.dumps(customer_dict)
            else:
                return json.dumps({})  # Return empty JSON if no data found

        except psycopg2.Error as e:
            print(f"Error fetching customer data from PostgreSQL database: {e}")
            return json.dumps({})  # Return empty JSON in case of an error
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                print("Connection to PostgreSQL database closed.")

if __name__ == '__main__':
    # Example usage (for testing purposes)
    customer_data_tool = CustomeData(customer_id="0002-ORFBO")  # Replace with an actual customer ID from your database
    customer_info_json = customer_data_tool.run()
    print("\nCustomer Information:")
    print(customer_info_json)

    customer_data_tool_not_found = CustomeData(customer_id="nonexistent")
    customer_info_not_found_json = customer_data_tool_not_found.run()
    print("\nCustomer Information (Not Found):")
    print(customer_info_not_found_json)