
# if __name__ == '__main__':
#     import os
#     from dotenv import load_dotenv
#     from agno.agent import Agent
#     from agno.models.groq import Groq
#     import json

#     # Load environment variables
#     load_dotenv()
#     groq_api_key = os.getenv('GROQ_API_KEY')

#     if not groq_api_key:
#         print("Error: GROQ_API_KEY not found.")
#         exit()

#     # Customer data (second run)
#     customer_data = {
#         "Tenure Months": 2,
#         "Churn Score": 10,
#         "Monthly Charges": 25.5,
#         "Internet Service": "Fiber optic",
#         "Phone Service": "Yes",
#         "Contract": "One year",
#         "CLTV": 3500
#     }
#     needed_data = ["Tenure Months","Churn Score","Monthly Charges","Internet Service","Contract","CLTV"]
#     filtered_data = {key:value for key,value in customer_data.items()}

#     # Initialize tool instances
#     analyze_tool = AnalyzeCustomerTool()  # Returns real insights
#     offers_tool = GetAvailableOffersTool()  # Returns real offers

#     # Initialize the agent
#     agent = Agent(
#         model=Groq(api_key=groq_api_key),
#         description="An AI salesperson that crafts personalized offer letters to retain customers, using only provided customer data and tool outputs, applying reciprocity, scarcity, social proof, and emotional appeal.",
#         tools=[analyze_tool, offers_tool]
#     )

#     # Refined query without specific end-date
#     query = (
#         "You are an salesperson tasked with retaining customers using only the provided customer data and tool outputs. "
#         "Analyze this customer data with the customer_analysis_tool: "
#         f"{json.dumps(customer_data)}. "
#         "Retrieve all available offers with the get_available_offers_tool. "
#         "Based solely on the customer’s profile from the analysis (e.g., loyalty, billing sensitivity, service type, contract stability, customer value), "
#         "select the single best offer from the available offers that matches their needs and preferences. "
#         "Write a concise, persuasive, and personalized offer letter in a warm, engaging tone. "
#         "Incorporate psychological principles: reciprocity (reward their commitment),"
#         "make the offer emotional appealing (make them feel valued). "
#         "Use only the exact offer description from the tool and data from the customer data—do not mention tools, add unverified details, alter the offer,"
#         "or include confidential customer data such as 'CLTV' or 'Churn Score,' which the company must keep private and should not be visible to the customer."
#         "Return only the final offer letter, formatted as a professional email with subject line, greeting, body, and signature."
#     )
#     response = agent.run(query)

#     # Output the offer letter
#     print("\nPersonalized Offer Letter:\n", response)

#     # Debug outputs for verification
#     customer_insights = analyze_tool.run(customer_data)
#     print("\n[Debug] Customer Insights:", customer_insights)
#     available_offers = offers_tool.run()
#     print("[Debug] Available Offers:", available_offers)
#     print(response.content)