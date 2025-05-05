import requests
import json


def predict(customer_data, churn_api_url="http://127.0.0.1:8001/predict_churn"):
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(
            churn_api_url,
            headers=headers,
            json=customer_data
        )
        response.raise_for_status()
        prediction_result = response.json()
        if "churn_score" in prediction_result:
            churn_score = prediction_result["churn_score"]
            if isinstance(churn_score, list) and len(churn_score) > 1:
                churn_score = churn_score[1] * 100
            elif isinstance(churn_score, (int, float)):
                churn_score = churn_score * 100
            else:
                return json.dumps({"error": "Invalid churn_score format", "details": churn_score})
            return json.dumps({"churn_score": round(churn_score, 2)})
        else:
            return json.dumps({"error": "API response does not contain 'churn_score'", "details": prediction_result})
    except requests.exceptions.RequestException as e:
        return json.dumps({
            "error": "Error connecting to the churn prediction API",
            "details": str(e)
        })
    except json.JSONDecodeError:
        return json.dumps({
            "error": "Error decoding JSON response from the API",
            "details": response.text
        })
    except Exception as e:
        return json.dumps({
            "error": "An unexpected error occurred during churn prediction",
            "details": str(e)
        })
