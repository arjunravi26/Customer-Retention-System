import requests
import json
from data import fetch_data
from logger import logging
from config import get_service_url
def send_documents(documents):
    """Send documents to the API for topic modeling."""
    url = get_service_url('topic_modeling_process')
    payload = {"documents": documents}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logging.info(f"Send documnet {payload}")
        print("Process Response:", response.json())
    except requests.RequestException as e:
        logging.info(f"Error in sending documents: {str(e)}")
        print(f"Error sending documents: {str(e)}")

def receive_topics():
    """Retrieve topics from the API."""
    url = get_service_url('topic_modeling_topic')
    try:
        response = requests.get(url)
        response.raise_for_status()
        topics = response.json()
        print("Process Response:", response.json())
        print("Topics:")
        logging.info("Topics: ")

        for topic in topics:
            print(f"- {topic['topic_name']}: {topic['description']}")
            logging.info(f"- {topic['topic_name']}: {topic['description']} (Frequency: {topic['top_words']})")
        return topics[:10]
    except requests.RequestException as e:
        logging.info(f"Error retrieving topics: {str(e)}")
        print(f"Error retrieving topics: {str(e)}")
        return []


# if __name__ == "__main__":
#     # Sample documents (replace with your data)

#     documents = fetch_data()
#     # Send documents for processing
#     send_documents(documents)

#     # Retrieve and print topics
#     topics = get_topics()
#     print(topics)

#     # Retrieve documents for the first topic (if available)
#     if topics:
#         first_topic_id = topics[0]["topic_id"]
#         print(get_documents_by_topic(first_topic_id))