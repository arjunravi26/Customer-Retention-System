from agno.tools.toolkit import Toolkit
from typing import Dict, List, Union
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
import json

load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')

if not groq_api_key:
    print("Error: GROQ_API_KEY not found.")
    exit()

class AnalyzeCustomerTool(Toolkit):
    """A tool for analyzing customer data to generate insights for offer recommendations."""

    def __init__(self):
        super().__init__(name="customer_analysis_tool")

    def run(self, customer_data: Dict) -> str:
        """
        Analyzes the provided customer data to determine loyalty level, billing sensitivity,
        service type, contract stability, and customer value for offer eligibility.

        Args:
            customer_data (Dict): A dictionary containing customer data.
                Example: {"Tenure Months": 15, "Churn Score": 60, "Monthly Charges": 85.5,
                          "Internet Service": "Fiber optic", "Phone Service": "Yes",
                          "Contract": "One year", "CLTV": 3500}

        Returns:
            str: A JSON string of customer insights.
                Example: '{"loyalty": "high", "billing_sensitivity": "above average",
                          "service_type": "fiber_internet", "contract_stability": "high",
                          "customer_value": "medium"}'

        Input Schema:
            {
                "type": "object",
                "properties": {
                    "customer_data": {
                        "type": "object",
                        "properties": {
                            "Tenure Months": {"type": "integer"},
                            "Churn Score": {"type": "integer"},
                            "Monthly Charges": {"type": "number"},
                            "Internet Service": {"type": "string"},
                            "Phone Service": {"type": "string"},
                            "Contract": {"type": "string"},
                            "CLTV": {"type": "integer"}
                        }
                    }
                },
                "required": ["customer_data"]
            }
        """
        analysis: Dict[str, Union[str, float]] = {}

        tenure = customer_data.get("Tenure Months", 0)
        if tenure >= 12:
            analysis["loyalty"] = "high"
        elif tenure >= 6:
            analysis["loyalty"] = "medium"
        else:
            analysis["loyalty"] = "low"

        monthly_charges = customer_data.get("Monthly Charges", 0.0)
        if monthly_charges > 100:
            analysis["billing_sensitivity"] = "high"
        elif monthly_charges > 70:
            analysis["billing_sensitivity"] = "above average"
        elif monthly_charges > 50:
            analysis["billing_sensitivity"] = "average"
        else:
            analysis["billing_sensitivity"] = "low"

        internet_service = customer_data.get("Internet Service", "No")
        if internet_service == "Fiber optic":
            analysis["service_type"] = "fiber_internet"
        elif internet_service == "DSL":
            analysis["service_type"] = "dsl_internet"
        elif internet_service == "No" and customer_data.get("Phone Service", "No") == "Yes":
            analysis["service_type"] = "mobile_only"
        else:
            analysis["service_type"] = "unknown"

        contract = customer_data.get("Contract", "Month-to-month")
        if contract == "Month-to-month":
            analysis["contract_stability"] = "low"
        elif contract == "One year":
            analysis["contract_stability"] = "high"
        else:
            analysis["contract_stability"] = "very high"

        cltv = customer_data.get("CLTV", 0)
        if cltv > 4600:
            analysis["customer_value"] = "high"
        elif cltv > 3000:
            analysis["customer_value"] = "medium"
        else:
            analysis["customer_value"] = "low"

        return json.dumps(analysis)

class GetAvailableOffersTool(Toolkit):
    """A tool for retrieving a list of available customer offers."""

    def __init__(self):
        super().__init__(name="get_available_offers_tool")

    def run(self) -> str:
        """
        Retrieves a list of available offers that can be presented to customers.
        This tool does not require any input.

        Returns:
            str: A JSON string of available offers.
                Example: '[{"name": "Bill Discount", "description": "Save 20%...",
                          "categories": ["billing", "cost"]}, ...]'

        Output Schema:
            {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "categories": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }
        """
        offers = [
            {
                "name": "Bill Discount",
                "description": "Save 20% on your monthly bill for the next 6 months.",
                "categories": ["billing", "cost"]
            },
            {
                "name": "Speed Upgrade",
                "description": "Enjoy faster internet speeds on your plan for 3 months at no extra cost.",
                "categories": ["internet_speed", "performance"]
            },
            {
                "name": "Extra Data",
                "description": "Get an additional 10GB of data per month for the next 3 months.",
                "categories": ["data", "mobile"]
            },
            {
                "name": "Loyalty Bonus",
                "description": "As a valued customer, receive a $50 credit on your next bill.",
                "categories": ["loyalty", "billing"]
            }
        ]
        return json.dumps(offers)

# if __name__ == '__main__':
#     import os
#     from dotenv import load_dotenv
#     from agno.agent import Agent
#     from agno.models.groq import Groq

#     load_dotenv()
#     groq_api_key = os.getenv('GROQ_API_KEY')

#     if not groq_api_key:
#         print("Error: GROQ_API_KEY not found.")
#         exit()

#     # Sample customer data
#     sample_customer_data = {
#         "Tenure Months": 15,
#         "Churn Score": 60,
#         "Monthly Charges": 85.5,
#         "Internet Service": "Fiber optic",
#         "Phone Service": "Yes",
#         "Contract": "One year",
#         "CLTV": 3500
#     }

#     # Initialize tool instances
#     analyze_tool = AnalyzeCustomerTool()
#     offers_tool = GetAvailableOffersTool()

#     # Initialize the agent with tool instances
#     agent = Agent(
#         model=Groq(api_key=groq_api_key),
#         description="An AI agent that can analyze customer data and suggest relevant offers.",
#         tools=[analyze_tool, offers_tool]  # Pass tool instances
#     )

#     # Example query
#     query = (
#         "Use the customer_analysis_tool to analyze this customer data: "
#         f"{json.dumps(sample_customer_data)} and then use the get_available_offers_tool "
#         "to list the available offers."
#     )
#     response = agent.run(query)
#     print("\nAgent Response:", response)

#     # For direct testing
#     customer_insights = analyze_tool.run(sample_customer_data)  # Pass without keyword
#     print("\nDirect Customer Insights:", customer_insights)

#     available_offers = offers_tool.run()
#     print("\nDirect Available Offers:", available_offers)

if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    from agno.agent import Agent
    from agno.models.groq import Groq
    import json

    load_dotenv()
    groq_api_key = os.getenv('GROQ_API_KEY')

    if not groq_api_key:
        print("Error: GROQ_API_KEY not found.")
        exit()

    # Sample customer data
    sample_customer_data = {
        "Tenure Months": 15,
        "Churn Score": 60,
        "Monthly Charges": 85.5,
        "Internet Service": "Fiber optic",
        "Phone Service": "Yes",
        "Contract": "One year",
        "CLTV": 3500
    }

    # Initialize tool instances
    analyze_tool = AnalyzeCustomerTool()
    offers_tool = GetAvailableOffersTool()

    # Initialize the agent with a focused description
    agent = Agent(
        model=Groq(api_key=groq_api_key),
        description="An expert AI salesperson with psychological mastery, designed to retain customers by crafting personalized, irresistible offer letters using reciprocity, scarcity, social proof, and emotional appeal.",
        tools=[analyze_tool, offers_tool]
    )

    # Refined query to get only the offer letter
    query = (
        "You are an expert salesperson with deep psychological insight, tasked with retaining customers. "
        "Use the customer_analysis_tool to analyze this customer data: "
        f"{json.dumps(sample_customer_data)}. "
        "Then, use the get_available_offers_tool to retrieve all available offers. "
        "Based on the customer’s profile (e.g., loyalty, billing sensitivity, service type, customer value), "
        "select the single best offer that matches their needs and motivations. "
        "Write a concise, persuasive, and personalized offer letter to the customer in a warm, engaging tone. "
        "Incorporate psychological principles: reciprocity (reward their loyalty), scarcity (highlight a limited-time offer), "
        "social proof (mention others’ satisfaction), and emotional appeal (make them feel valued). "
        "Include a clear call to action. Return only the final offer letter, formatted as a professional email with subject line, "
        "greeting, body, and signature—no analysis or extra details."
    )
    response = agent.run(query)

    # Output the clean offer letter
    print("\nPersonalized Offer Letter:\n", response)

    # Optional debugging outputs
    customer_insights = analyze_tool.run(sample_customer_data)
    print("\n[Debug] Direct Customer Insights:", customer_insights)
    available_offers = offers_tool.run()
    print("[Debug] Direct Available Offers:", available_offers)
    print(response.content)