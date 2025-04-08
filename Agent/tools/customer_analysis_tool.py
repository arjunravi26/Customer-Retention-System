from agno.tools.toolkit import Toolkit
from typing import Dict, List, Union
import json


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
        print(customer_data)
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
