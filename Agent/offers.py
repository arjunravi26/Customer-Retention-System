from typing import Dict, Optional
from agno.agent import Agent
from agno.models.groq import Groq
from tools.tools import analyze_customer

class OfferSelectionAgent:
    def __init__(self):
        self.offers = offers
        self.tools = {
            "analyze_customer": analyze_customer,
            "customer_chat_summary": customer_chat_summary
        }

        # Well-formatted prompt for the agent
        self.prompt = """
You are an Offer Selection Agent for a telecom company's customer retention system. Your task is to select the most suitable offer from a predefined list based on the customer's needs, using insights from customer data analysis and a summary of their chat history.

### Available Tools:
- **analyze_customer(customer_data)**: Takes customer_data (dict) and returns a dictionary with insights such as:
  - "loyalty": "low", "medium", "high"
  - "churn_risk": "low", "medium", "high"
  - "billing_sensitivity": "low", "medium", "high"
  - "service_type": e.g., "fiber_internet", "dsl_internet", "mobile_only"
  - "customer_value": "low", "medium", "high"
- **customer_chat_summary(chat_history)**: Takes chat_history (str) and returns a dictionary with:
  - "summary": A concise summary of the chat (e.g., "Customer complained about high bill and threatened to switch.")
  - "sentiment": "positive", "negative", "neutral"
  - "main_issue": e.g., "billing", "internet_speed", "data", or None

### Offer List:
{offer_list}

### Instructions:
1. **Analyze Customer Data:**
   - Use `analyze_customer` with the provided `customer_data` to get `customer_analysis`.
   - Identify potential needs (e.g., high billing sensitivity, high loyalty).

2. **Summarize Chat History:**
   - Use `customer_chat_summary` with the provided `chat_history` to get `chat_summary`.
   - Extract the `main_issue` and `sentiment` to pinpoint the customer's primary concern.

3. **Determine Customer Needs:**
   - Combine insights from `customer_analysis` and `chat_summary`:
     - If `chat_summary["main_issue"]` is not None, prioritize it as the primary need.
     - Supplement with `customer_analysis`:
       - "billing" if `billing_sensitivity` is "medium" or "high" or `churn_reason` is "price too high"
       - "internet_speed" if `service_type` is internet-related (e.g., "fiber_internet")
       - "data" if `service_type` is "mobile_only"
       - "loyalty" if `loyalty` is "high" and `sentiment` is "positive"

4. **Select the Best Offer:**
   - From the `offers` list, find the offer whose `categories` best match the primary need:
     - Prioritize `chat_summary["main_issue"]` if present.
     - If no match, use needs from `customer_analysis`.
     - If multiple offers match, choose the first one.
   - Fallback: If no clear need is identified but `customer_value` or `loyalty` is "high", select "Loyalty Bonus".
   - If no offer fits, return None.

5. **Output Your Decision:**
   - Return a dictionary in this format:
     ```json
     {
       "selected_offer": "offer_name" or None,
       "reason": "Explanation of why this offer was chosen"
     }
     """
        self.agent =
    def run(self):