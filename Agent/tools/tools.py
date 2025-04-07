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

if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    from agno.agent import Agent
    from agno.models.groq import Groq

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

    # Initialize the agent with tool instances
    agent = Agent(
        model=Groq(api_key=groq_api_key),
        description="An AI agent that can analyze customer data and suggest relevant offers.",
        tools=[analyze_tool, offers_tool]  # Pass tool instances
    )

    # Example query
    query = (
        "Use the customer_analysis_tool to analyze this customer data: "
        f"{json.dumps(sample_customer_data)} and then use the get_available_offers_tool "
        "to list the available offers."
    )
    response = agent.run(query)
    print("\nAgent Response:", response)

    # For direct testing
    customer_insights = analyze_tool.run(sample_customer_data)  # Pass without keyword
    print("\nDirect Customer Insights:", customer_insights)

    available_offers = offers_tool.run()
    print("\nDirect Available Offers:", available_offers)
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

    # Initialize the agent with enhanced description and tools
    agent = Agent(
        model=Groq(api_key=groq_api_key),
        description="An expert AI salesperson leveraging psychology to retain customers with tailored, irresistible offers.",
        tools=[analyze_tool, offers_tool]
    )

    # Query to analyze customer data and fetch offers
    query = (
        "Use the customer_analysis_tool to analyze this customer data: "
        f"{json.dumps(sample_customer_data)} and then use the get_available_offers_tool "
        "to retrieve all available offers. Based on the analysis, select the best offer "
        "and craft a persuasive, personalized offer letter to retain the customer. Use "
        "psychological principles like reciprocity, scarcity, social proof, and emotional "
        "appeal to make the letter compelling and attractive."
    )
    response = agent.run(query)

    # Process the response to extract insights and offers, then generate the letter
    try:
        # Assuming the agent returns a string that we can parse or use directly
        # For simplicity, we'll simulate the logic here if the agent doesn't handle it fully
        customer_insights = json.loads(analyze_tool.run(sample_customer_data))
        all_offers = json.loads(offers_tool.run())

        # Select the best offer based on customer insights
        best_offer = None
        if customer_insights["loyalty"] in ["high", "medium"]:
            # Prioritize loyalty or billing-related offers for loyal customers
            for offer in all_offers:
                if "loyalty" in offer["categories"] or "billing" in offer["categories"]:
                    best_offer = offer
                    break
        elif customer_insights["billing_sensitivity"] in ["high", "above average"]:
            # Focus on cost-saving offers for price-sensitive customers
            for offer in all_offers:
                if "billing" in offer["categories"] or "cost" in offer["categories"]:
                    best_offer = offer
                    break
        elif customer_insights["service_type"] == "fiber_internet":
            # Offer performance upgrades for fiber users
            for offer in all_offers:
                if "internet_speed" in offer["categories"]:
                    best_offer = offer
                    break
        if not best_offer:
            best_offer = all_offers[0]  # Fallback to first offer

        # Craft the persuasive offer letter
        loyalty_level = customer_insights["loyalty"]
        customer_value = customer_insights["customer_value"]

        if loyalty_level == "high":
            intro = (
                "Dear Valued Customer,\n\n"
                "As one of our most loyal members—over 15 months strong!—we can’t imagine our community without you. "
                "Your trust in us is something we cherish deeply, and we’re here to show our gratitude in a big way."
            )
        elif loyalty_level == "medium":
            intro = (
                "Dear Valued Customer,\n\n"
                "You’ve been with us for a while now, and we’re thrilled to have you as part of our family! "
                "We know you have choices, so we want to make sure you feel extra special for sticking with us."
            )
        else:
            intro = (
                "Dear Customer,\n\n"
                "We’ve noticed you’re exploring what we have to offer, and we’re excited to make your experience even better! "
                "Let’s turn your journey with us into something truly rewarding."
            )

        # Psychological hooks: Scarcity, reciprocity, social proof
        offer_body = (
            f"That’s why we’re offering you an exclusive deal: **{best_offer['name']}**—{best_offer['description']} "
            "This isn’t just any offer—it’s tailored just for you because of your unique value to us "
            f"(our data says you’re in our {customer_value} tier of amazing customers!). "
            "Thousands of customers like you have loved this perk, and we’re giving it to you as a heartfelt thank-you. "
            "But hurry—this special offer is only available for a limited time, and we’d hate for you to miss out!"
        )

        # Call to action with emotional appeal
        closing = (
            "\n\nLet’s keep this relationship thriving—accept this offer today and enjoy the benefits you truly deserve. "
            "Reach out to us now at [contact info] or simply reply ‘YES’ to claim it. "
            "We’re excited to see you smile!\n\n"
            "Warm regards,\nYour Dedicated Team"
        )

        # Combine into the full letter
        offer_letter = f"{intro}\n\n{offer_body}{closing}"
        print("\nPersonalized Offer Letter:\n", offer_letter)

    except Exception as e:
        print("\nAgent Response:", response)
        print("Error processing response:", e)

    # For direct testing (optional)
    customer_insights = analyze_tool.run(sample_customer_data)
    print("\nDirect Customer Insights:", customer_insights)
    available_offers = offers_tool.run()
    print("\nDirect Available Offers:", available_offers)
    print(offer_letter)