import json
import os
import secrets
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

import asyncpg
import pandas as pd
import psycopg2
import requests
from config import get_service_url
from database import insert_chat_message
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from generate_id import generate_chat_id
from get_admin import get_admin
from logger import logging
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from send_email import send, send_email
from starlette.middleware.sessions import SessionMiddleware
from top2vec_model import receive_topics, send_documents

from data import fetch_data
from prediction import predict

app = FastAPI()
SECRET_KEY = secrets.token_urlsafe(32)
BASE_DIR = Path(__file__).resolve().parent
static_dir = BASE_DIR / "static"
template_dir = BASE_DIR / "templates"
if not static_dir.is_dir():
    raise RuntimeError(f"Cannot find static folder at {static_dir}")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
templates = Jinja2Templates(directory=template_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")
conversation_history = []

DATABASE_CONFIG = {
    "dbname": "telcom",
    "user": "postgres",
    "password": "postgres",
    "host": "postgres",
    "port": "5432"
}

class OfferRequest(BaseModel):
    customer_ids: List[str]

def get_db_params() -> Dict[str, str]:
    """
    Parse DATABASE_URL environment variable to extract connection parameters.

    Returns:
        Dict[str, str]: Dictionary with database connection parameters.
    """
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/telcom")
    parsed_url = urlparse(database_url)
    return {
        "database": parsed_url.path.lstrip("/"),
        "user": parsed_url.username,
        "password": parsed_url.password,
        "host": parsed_url.hostname,
        "port": str(parsed_url.port or 5432)
    }

@contextmanager
def get_db_connection():
    """
    Context manager for a PostgreSQL database connection using psycopg2.

    Yields:
        psycopg2.connection: A database connection object.

    Raises:
        OperationalError: If the database connection fails.
    """
    conn = None
    try:
        db_params = get_db_params()
        logging.debug(f"Attempting to connect with params: {db_params}")
        conn = psycopg2.connect(**db_params, cursor_factory=RealDictCursor)
        logging.info("Database connected")
        yield conn
    except Exception as oe:
        logging.error(f"Database connection error: {oe}")
        raise
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed")

async def fetch_user_by_id(user_id: str) -> Optional[Dict]:
    """
    Fetches a user by their customer ID from the 'customer_data' table in the 'telcom' PostgreSQL database.

    Args:
        user_id (str): The customer ID to fetch.

    Returns:
        Optional[Dict]: A dictionary containing the user data if found, None otherwise.

    Raises:
        Exception: For database connection or query errors.
    """
    try:
        db_params = get_db_params()
        logging.debug(f"Attempting async connection with params: {db_params}")
        conn = await asyncpg.connect(**db_params)
        user = await conn.fetchrow("SELECT * FROM customer_data WHERE customerid = $1", user_id)
        await conn.close()
        logging.info(f"Fetched user with customerid: {user_id}")
        return dict(user) if user else None
    except Exception as e:
        logging.error(f"Error fetching user: {e}")
        return None


@app.get("/")
def read_root(request: Request):
    logging.info("running root function")
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/api/login")
async def login(request: Request, name: str = Form(...), user_id: str = Form(...)):
    logging.info("Fetching data")
    user_id = user_id.strip()
    user = await fetch_user_by_id(user_id=user_id)
    request.session['user'] = name
    request.session['user_id'] = user_id
    request.session['user_details'] = user
    if not user:
        logging.info("NO user found")
        return RedirectResponse(url="/", status_code=303)
    logging.info("redirect to chatbot")
    return RedirectResponse(url="/chatbot", status_code=303)


@app.post("/api/admin-login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    logging.info("Fetching data")
    db_username, db_password = get_admin()
    if username == db_username and password == db_password:
        request.session['admin_name'] = username
        return RedirectResponse(url="/dashboard", status_code=303)
    else:
        return HTMLResponse(content="Invalid username or password", status_code=401)


@app.get("/dashboard")
def dashboard(request: Request):
    admin = request.session.get('admin_name')
    if not admin:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/chatbot")
def chatbot(request: Request):
    logging.info("log in to chatbot")
    user = request.session.get('user_id')
    name = request.session.get('user')
    if not user:
        logging.info("Login if you need to access chatbot.")
        return RedirectResponse(url="/")
    return templates.TemplateResponse("chatbot.html", {"request": request, "user_name": name, "message": conversation_history})

@app.get("/admin-login")
def admin_login(request: Request):
    logging.info("log in to admin")
    return templates.TemplateResponse("admin_login.html", {"request": request})

# RASA_SERVER_URL = get_service_url('rasa')
RASA_SERVER_URL = os.getenv("RASA_SERVER_URL", "http://34.42.54.22:5005/webhooks/rest/webhook")

@app.post("/chat", response_class=JSONResponse)
async def post_chat(request: Request, message: str = Form(...)):

    logging.info("Connecting to Rasa server")
    customer_id = request.session.get('user_id')
    chat_id = generate_chat_id(customer_id)
    insert_chat_message(chat_id, customer_id, "user", message)
    conversation_history.append({"sender": "user", "text": message})
    user_id = request.session.get('user_id')
    try:
        user_id = request.session.get('user_id')
        payload = {"sender": user_id, "message": message}
        logging.info(f"Sending payload to Rasa: {payload}")
        logging.info(f"Rasa url is {RASA_SERVER_URL}")

        print(f"Rasa url is {RASA_SERVER_URL}")
        response = requests.post("http://34.42.54.22:5005/webhooks/rest/webhook", json=payload, timeout=15)
        response.raise_for_status()
        bot_responses = response.json()
        print(f"Rasa raw response: {bot_responses}")
        logging.info(f"Rasa raw response: {bot_responses}")
        if not bot_responses:
            extracted_responses = "Sorry, I didn’t understand your request. Please try again."
            extracted_responses = "I understand your concern about slow internet. Try rebooting your device and router. If the problem continues, our technical support team is available to help."
        else:
            extracted_responses = " ".join(
                [msg["text"] for msg in bot_responses if "text" in msg])

    except requests.exceptions.RequestException as e:
        logging.exception(f"Could not send data to Rasa server: {e}")
        extracted_responses = "Could not process the request. Please try again."
        extracted_responses = "I understand your concern about slow internet. Try rebooting your device and router. If the problem continues, our technical support team is available to help."

    customer_id = request.session.get('user_id')
    chat_id = generate_chat_id(customer_id)
    insert_chat_message(chat_id, customer_id, "chatbot", extracted_responses)
    conversation_history.append({"sender": "bot", "text": extracted_responses})
    return JSONResponse({"message": extracted_responses})

def get_customer_db():
    users = []
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM customer_data limit 30;")
                users = cur.fetchall()
    except HTTPException:
        raise HTTPException(status_code=404, detail="No users found.")
    except Exception as e:
        logging.exception(f"Exception while selecting data from database {e}")
    return users

def get_loyalty(user):
    contract = user.get("contract", "").lower()
    if "month" in contract:
        return "Low"
    elif "one year" in contract:
        return "Medium"
    elif "two year" in contract:
        return "High"
    else:
        return "Unknown"

def get_customer():
    users = get_customer_db()
    if not users:
        raise HTTPException(status_code=404, detail="No users found.")
    customers = []
    for user in users:
        features = {
            "Gender":             user["gender"],
            "Senior_Citizen":     user["senior_citizen"],
            "Partner":            user["partner"],
            "Tenure_Months":      user["tenure_months"],
            "Phone_Service":      user["phone_service"],
            "Internet_Service":   user["internet_service"],
            "Online_Security":    user["online_security"],
            "Online_Backup":      user["online_backup"],
            "Device_Protection":  user["device_protection"],
            "Tech_Support":       user["tech_support"],
            "Streaming_TV":       user["streaming_tv"],
            "Streaming_Movies":   user["streaming_movies"],
            "Contract":           user["contract"],
            "Paperless_Billing":  user["paperless_billing"],
            "Payment_Method":     user["payment_method"],
            "Monthly_Charges":    float(user["monthly_charges"]),
            "Total_Charges":      float(user["total_charges"]) if user["total_charges"] not in (None, "") else 0.0,
            "CLTV":               float(user["cltv"]),
        }
        prediction_url = get_service_url('ml_service')
        prediction_json = predict(features,churn_api_url=prediction_url)
        try:
            result = json.loads(prediction_json)
            churn_score = result.get("churn_score")
            logging.info(f"Prediction score for {user['customerid']} is {churn_score}")
        except json.JSONDecodeError:
            logging.error(f"Could not decode prediction JSON: {prediction_json}")
            churn_score = None

        customers.append({
            "customer_id":      user["customerid"],
            "loyalty":          get_loyalty(user),
            "churn_probability": churn_score,
        })

    return customers


@app.get("/api/customers")
async def fetch_users():
    try:
        return get_customer()
    except Exception as e:
        logging.exception("Error in fetch_users")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/topics")
async def get_topics():
    documents = fetch_data()
    send_documents(documents)
    return receive_topics()


@app.post("/api/send-offer")
async def send_offer(request: OfferRequest):
    try:
        logging.info("In send offer")
        customer_ids = request.customer_ids
        print(f"Customer id is {customer_ids}")
        if not customer_ids:
            return {"status": "error", "message": "No customers selected"}
        logging.info(f"Customer id is {customer_ids}")
        email_url = get_service_url('agno')
        send_email(customer_id=customer_ids[0],email_url=email_url)
        return {"status": "success", "message": f"Offers sent to {len(customer_ids)} customers"}
    except Exception as e:
        logging.info(f"Error in send offer {e}")


if __name__ == "__main__":
    import uvicorn
    logging.info("Start app")
    uvicorn.run("main:app", host="0.0.0.0", port=8000,
                reload=True, log_config=None)
