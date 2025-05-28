
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted, SlotSet
from custom_logging.logging import logging, setup_logging
import psycopg2
import decimal
setup_logging()


class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="I'm sorry, I didn't understand that. Could you please rephrase?")
        logging.info("rasa chatbot cannot understand the user message")
        return [UserUtteranceReverted()]


class ActionGetConfidence(Action):
    def name(self):
        return "action_get_confidence"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        latest_intent = tracker.latest_message['intent']
        intent_name = latest_intent.get('name')
        confidence = latest_intent.get('confidence')

        dispatcher.utter_message(
            text=f"The detected intent is '{intent_name}' with confidence {confidence:.2f}")
        logging.info(
            f"The detected intent is '{intent_name}' with confidence {confidence:.2f}")
        return [UserUtteranceReverted()]


def fetch_user_data(user_id):
    try:
        conn = psycopg2.connect(
            database="telcom",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        logging.info("Connected to PostgreSQL database successfully")
        query = f"SELECT * from customer_data where customerid = {user_id}"
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchone()
        logging.info(f"Result from the db about available plans: {results}")
        return results
    except psycopg2.Error as e:
        logging.exception(
            f"An error occurred while fetching available plans {e}")
        print(f"An error occurred while fetching available plans {e}")
        return []
    except Exception as e:
        logging.exception(
            f"An error occurred while fetching available plans {e}")
        print(f"An error occurred while fetching available plans {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


class ActionCustomResponse(Action):
    def name(self):
        return "utter_greet"

    def run(self, dispatcher, tracker, domain):
        user_id = tracker.sender_id
        logging.info(f"Sender id is {user_id}")
        user_data = fetch_user_data(user_id)
        response = f"Hello {user_data['name']}, how can I assist you today?"
        dispatcher.utter_message(text=response)
        return []

class ActionUserPlan(Action):
    def name(self) -> Text:
        return "action_user_plan"
    def run(self, dispatcher, tracker, domain):
        sender_id = tracker.sender_id
        message = tracker.latest_message.get("text", "")
        intent = tracker.latest_message.get("intent", {}).get("name", "")
        entities = tracker.latest_message.get("entities", [])
        logging.info(f"Payload received - sender_id: {sender_id}, message: {message}, intent: {intent}, entities: {entities}")

        user_id = tracker.sender_id
        # dispatcher.utter_message(text=f"Fetching plan for user {user_id}")
        logging.info(f"Sender id is {user_id}")
        try:
            conn = psycopg2.connect(
                database="telcom",
                user="postgres",
                password="postgres",
                host="localhost",
                port="5432"
            )
            logging.info("Connected to PostgreSQL database successfully")
            query = f"SELECT plan_id from customer_plans where customer_id = %s"
            cursor = conn.cursor()
            cursor.execute(query,(user_id,))
            plan_id = cursor.fetchone()
            logging.info(f"User plan id is {plan_id}")
            query = f"SELECT  plan_name, monthly_fee, data_allowance_gb, voice_minutes, sms_allowance, description from telecom_plans where plan_id = %s"
            cursor = conn.cursor()
            cursor.execute(query,(plan_id,))
            plan_details = cursor.fetchone()
            logging.info(f"Result from the db about user plan plans: {plan_details}")
            if plan_details:
                plan_name, monthly_fee, data_allowance, voice_minutes, sms_allowance, description = plan_details
                response = (
                    f"Your plan: {plan_name}\n"
                    f"Monthly Fee: ${monthly_fee}\n"
                    f"Data Allowance: {data_allowance} GB\n"
                    f"Voice Minutes: {voice_minutes}\n"
                    f"SMS Allowance: {sms_allowance}\n"
                    f"Description: {description}"
                )
                logging.info(f"User plan details: {response}")
                dispatcher.utter_message(text=response)
        except psycopg2.Error as e:
            logging.exception(
                f"An error occurred while fetching available plans {e}")
            print(f"An error occurred while fetching available plans {e}")
            return []
        except Exception as e:
            logging.exception(
                f"An error occurred while fetching available plans {e}")
            print(f"An error occurred while fetching available plans {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()


class ActionQueryAvailablePlan(Action):
    def name(self) -> Text:
        return "action_query_available_plan"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            conn = psycopg2.connect(
                database="telcom",
                user="postgres",
                password="postgres",
                host="localhost",
                port="5432"
            )
            logging.info("Connected to PostgreSQL database successfully")
            query = "SELECT plan_name, monthly_fee, data_allowance_gb, voice_minutes, sms_allowance, description FROM telecom_plans ORDER BY RANDOM() LIMIT 5"
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            logging.info(
                f"Result from the db about available plans: {results}")
            if results:
                formatted_plans = ""
                for row in results:
                    plan_name = row[0]
                    monthly_fee = row[1] if row[1] is not None else decimal.Decimal(
                        '0.00')
                    data_allowance = row[2] if row[2] is not None else 0
                    voice_minutes = row[3] if row[3] is not None else 0
                    sms_allowance = row[4] if row[4] is not None else 0
                    description = row[5]

                    formatted_plans += f"""
                    📱 **{plan_name}**
                    - Monthly Fee: ${monthly_fee:.2f}
                    - Data Allowance: {data_allowance} GB
                    - Voice Minutes: {voice_minutes} mins
                    - SMS Allowance: {sms_allowance} SMS
                    - Description: {description}
                    """

                logging.info(f"Formatted available plans: {formatted_plans}")
                print(f"Formatted available plans: {formatted_plans}")

                # Send message to user as well
                dispatcher.utter_message(
                    text=f"Here are some available plans:\n{formatted_plans}")

                # Proper SlotSet event return
                return [SlotSet("available_plans", formatted_plans)]
            else:
                dispatcher.utter_message(text="No available plans found.")
                return []
        except psycopg2.Error as e:
            logging.exception(
                f"An error occurred while fetching available plans {e}")
            print(f"An error occurred while fetching available plans {e}")
            dispatcher.utter_message(
                text="An error occurred while fetching available plans.")
            return []
        except Exception as e:
            logging.exception(
                f"An error occurred while fetching available plans {e}")
            print(f"An error occurred while fetching available plans {e}")
            dispatcher.utter_message(
                text="An error occurred while fetching available plans.")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
