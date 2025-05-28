import json
from typing import Dict

import requests
from agno.tools.toolkit import Toolkit


class ChurnPredictionTool(Toolkit):
    """A tool for predicting customer churn score using an external API service."""

    def __init__(self, api_url: str = "http://ml_service:8003/predict_churn"):
        """
        Initializes the ChurnPredictionTool.

        Args:
            api_url (str): The URL of the churn prediction API service.
                           This API should accept customer data as a JSON payload
                           and return a JSON response containing the churn score.
        """
        super().__init__(name="predict_churn_score")
        self.api_url = api_url

    def run(self, customer_data: Dict) -> str:
        """
        Predicts the churn score for a given customer using the external API service.

        Args:
            customer_data (Dict): A dictionary containing the customer's data
                                   in the format expected by the prediction API.

        Returns:
            str: A JSON string containing a list of churn score.
                 Example: '{"churn_score": 0.85}'
                 Returns a JSON string with an error message if the API call fails.
                 Example of error: '{"error": "API request failed", "details": "..."}'


        """
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                self.api_url, headers=headers, json=customer_data)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            prediction_result = response.json()
            if "churn_score" in prediction_result:
                # if len(prediction_result['churn_score']) == 2:
                #     churn_score = prediction_result['churn_score'][1] * 100
                # else:
                #     print(prediction_result)
                churn_score = prediction_result['churn_score'][1] * 100
                    # return json.dumps({'churn_error':'No Score found'})
                return json.dumps({"churn_score": churn_score})
            else:
                return json.dumps({"error": "API response does not contain 'churn_score'", "details": prediction_result})

        except requests.exceptions.RequestException as e:
            return json.dumps({"error": "Error connecting to the churn prediction API", "details": str(e)})
        except json.JSONDecodeError:
            return json.dumps({"error": "Error decoding JSON response from the API", "details": response.text})
        except Exception as e:
            return json.dumps({"error": "An unexpected error occurred during churn prediction", "details": str(e)})


if __name__ == '__main__':
    # Replace with your FastAPI API URL
    churn_api_url = "http://127.0.0.1:8000/predict_churn"

    # Sample customer data with all required features matching CustomerData model
    sample_customer_data = {
        "Tenure_Months": 18,
        "Monthly_Charges": 75.0,
        "Total_Charges": 1350.0,
        "CLTV": 2000.0,
        "Gender": "Male",
        "Senior_Citizen": "No",
        "Partner": "Yes",
        "Phone_Service": "Yes",
        "Paperless_Billing": "Yes",
        "Internet_Service": "DSL",
        "Online_Security": "Yes",
        "Online_Backup": "No",
        "Device_Protection": "Yes",
        "Tech_Support": "No",
        "Streaming_TV": "Yes",
        "Streaming_Movies": "No",
        "Contract": "Month-to-month",
        "Payment_Method": "Electronic check",
        # "Multiple_Lines": "Yes"
    }

    # Test the churn prediction
    churn_predictor = ChurnPredictionTool(api_url=churn_api_url)
    churn_score_json = churn_predictor.run(sample_customer_data)
    print("\nChurn Prediction Result:")
    print(churn_score_json)

    # Example of an API URL that might return an error
    error_api_url = "http://httpbin.org/status/404"
    error_predictor = ChurnPredictionTool(api_url=error_api_url)
    error_result_json = error_predictor.run(sample_customer_data)
    print("\nError Prediction Result:")
    print(error_result_json)