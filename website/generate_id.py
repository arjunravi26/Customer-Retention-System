import datetime
import uuid

def generate_chat_id(customer_id):
    """Generates a unique chat ID for a given customer."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    return f"{customer_id}_{timestamp}_{unique_id}"