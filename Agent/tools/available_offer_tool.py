from agno.tools.toolkit import Toolkit
from typing import Dict, List, Union
import json


class GetAvailableOffersTool(Toolkit):
    """A tool for retrieving a list of available customer offers."""

    def __init__(self):
        super().__init__(name="get_available_offers_tool")

    def run(self) -> str:
        """
        Retrieves a list of available offers that can be presented to customers.
        This tool does not require any input.

        Args:
            customer_id (str): customer_id of the user.
            Example: '0002-ORFBO'
        Returns:
            str: A JSON string of available offers.
                Example: '[{"name": "Bill Discount", "description": "Save 20%...",
                          "categories": ["billing", "cost"]}, ...]'
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
