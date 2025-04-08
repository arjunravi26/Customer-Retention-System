import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
import json
from Agent.tools.customer_analysis_tool import AnalyzeCustomerTool
from Agent.tools.available_offer_tool import GetAvailableOffersTool
from Agent.tools.customer_data_tool import CustomeData
from Agent.tools.prediction_tool import ChurnPredictionTool
from Agent.logger import logging

# Load environment variables
load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')

if not groq_api_key:
    print("Error: GROQ_API_KEY not found.")
    exit()

# Initialize tool instances
customer_data = CustomeData("0003-MKNFE")
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

print(customer_input)
analyze_tool = AnalyzeCustomerTool()
offers_tool = GetAvailableOffersTool()
churn_score_tool = ChurnPredictionTool(api_url = "http://127.0.0.1:8000/predict_churn")

# Initialize the agent with the churn score tool included
write_agent = Agent(
    model=Groq(api_key=groq_api_key),
    description="An AI salesperson that crafts personalized offer letters to retain customers, using provided customer data, churn score percentage, and tool outputs, applying reciprocity, scarcity, social proof, and emotional appeal.",
    tools=[analyze_tool, offers_tool, churn_score_tool]
)

# Refined query incorporating churn score percentage
query = (
    "You are a salesperson tasked with retaining customers using only the provided customer data and tool outputs. "
    "Analyze this customer data with the customer_analysis_tool: "
    f"{json.dumps(customer_input)}. "
    "Retrieve the churn score percentage using the churn_prediction_tool with the customer data. "
    "Retrieve all available offers with the get_available_offers_tool. "
    "Based solely on the customer’s profile from the analysis (e.g., loyalty, billing sensitivity, service type, contract stability, customer value) "
    "and their churn score percentage, select the single best offer from the available offers that matches their needs, preferences, and likelihood of leaving. "
    "For example, if the churn score is high (e.g., >70%), prioritize offers with significant discounts or added value; "
    "if moderate (e.g., 30-70%), focus on loyalty rewards; if low (<30%), emphasize appreciation. "
    "Write a concise, persuasive, and personalized offer letter in a warm, engaging tone. "
    "Incorporate psychological principles: reciprocity (reward their commitment), "
    "and make the offer emotionally appealing (make them feel valued). "
    "Use only the exact offer description from the tool and data from the customer data—do not mention tools, add unverified details, alter the offer, "
    "or include confidential customer data such as 'CLTV' or 'Churn Score,' which the company must keep private and should not be visible to the customer. "
    "Return only the final offer letter, formatted as a professional email with subject line, greeting, body, and signature."
)

# Run the agent with the query
response = write_agent.run(query)

# Output the offer letter
logging.info(f"\nPersonalized Offer Letter:\n {response}")

# Debug outputs for verification
customer_insights = analyze_tool.run(customer_input)
logging.info(f"\n[Debug] Customer Insights: {customer_insights}")
available_offers = offers_tool.run()
logging.info(f"[Debug] Available Offers: {available_offers}")
churn_score = churn_score_tool.run(customer_input)
print(churn_score)
logging.info(f"[Debug] Churn Score Percentage: {churn_score}")
logging.info(response.content)
print(response.content)