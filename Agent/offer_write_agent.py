# generate_offer.py
import os
import json
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
from Agent.tools.customer_analysis_tool import AnalyzeCustomerTool
from Agent.tools.available_offer_tool import GetAvailableOffersTool
from Agent.tools.customer_data_tool import CustomeData
from Agent.tools.prediction_tool import ChurnPredictionTool
from Agent.logger import logging

load_dotenv(dotenv_path='agent/.env')
groq_api_key = os.getenv('GROQ_API_KEY')

if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in environment variables.")

def generate_offer_letter(customer_id: str) -> dict:
    customer_data = CustomeData(customer_id)
    customer_info = customer_data.run()
    customer_dict = json.loads(customer_info)

    customer_input = {
        "Gender": customer_dict["gender"],
        "Senior_Citizen": customer_dict["senior_citizen"],
        "Partner": customer_dict["partner"],
        "Tenure_Months": customer_dict["tenure_months"],
        "Phone_Service": customer_dict["phone_service"],
        "Internet_Service": customer_dict["internet_service"],
        "Online_Security": customer_dict["online_security"],
        "Online_Backup": customer_dict["online_backup"],
        "Device_Protection": customer_dict["device_protection"],
        "Tech_Support": customer_dict["tech_support"],
        "Streaming_TV": customer_dict["streaming_tv"],
        "Streaming_Movies": customer_dict["streaming_movies"],
        "Contract": customer_dict["contract"],
        "Paperless_Billing": customer_dict["paperless_billing"],
        "Payment_Method": customer_dict["payment_method"],
        "Monthly_Charges": customer_dict["monthly_charges"],
        "Total_Charges": float(customer_dict["total_charges"]),
        "CLTV": float(customer_dict["cltv"])
    }

    analyze_tool = AnalyzeCustomerTool()
    offers_tool = GetAvailableOffersTool()
    churn_score_tool = ChurnPredictionTool(api_url="http://127.0.0.1:8001/predict_churn")

    write_agent = Agent(
        model=Groq(api_key=groq_api_key),
        description=(
            "An AI salesperson that crafts personalized offer letters to retain customers, using provided customer data, "
            "churn score percentage, and tool outputs, applying reciprocity, scarcity, social proof, and emotional appeal."
        ),
        tools=[analyze_tool, offers_tool, churn_score_tool]
    )

    query = (
        "You are a salesperson tasked with retaining customers using only the provided customer data and tool outputs. "
        f"Analyze this customer data with the customer_analysis_tool: {json.dumps(customer_input)}. "
        "Retrieve the churn score percentage using the churn_prediction_tool with the customer data. "
        "Retrieve all available offers with the get_available_offers_tool. "
        "Based solely on the customer’s profile from the analysis (e.g., loyalty, billing sensitivity, service type, contract stability, customer value) "
        "and their churn score percentage, select the single best offer from the available offers that matches their needs, preferences, and likelihood of leaving. "
        "Write a concise, persuasive, and personalized offer letter in a warm, engaging tone. "
        "Return only the final offer letter, formatted as a professional email with subject line, greeting, body, and signature signed off as 'Customer Service Team, Telcom Company'."
    )

    response = write_agent.run(query)

    customer_insights = analyze_tool.run(customer_input)
    available_offers = offers_tool.run()
    churn_score = churn_score_tool.run(customer_input)

    logging.info(f"Customer Insights: {customer_insights}")
    logging.info(f"Available Offers: {available_offers}")
    logging.info(f"Churn Score Percentage: {churn_score}")
    logging.info(f"Generated Offer Letter: {response.content}")

    return {
        "customer_id": customer_id,
        "churn_score": churn_score,
        "offer_letter": response.content
    }
