import secrets
from contextlib import contextmanager

import psycopg2
import requests
from fastapi import FastAPI, Form, Request
from fastapi.responses import (FileResponse, HTMLResponse, JSONResponse,
                               RedirectResponse)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from psycopg2.extras import RealDictCursor
from starlette.middleware.sessions import SessionMiddleware

from custom_logging.logging import logging, setup_logging

app = FastAPI()
SECRET_KEY = secrets.token_urlsafe(32)
setup_logging()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
templates = Jinja2Templates(directory="website/templates")
app.mount("/static", StaticFiles(directory="website/static"), name="static")
conversation_history = []

DATABASE_CONFIG = {
    "dbname": "telcom",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}


@contextmanager
def get_db_connection():
    try:
        conn = psycopg2.connect(
            **DATABASE_CONFIG, cursor_factory=RealDictCursor)
        logging.info("Database connected")
        try:
            yield conn
        finally:
            conn.close()
    except:
        logging.error("Error while connecting with database")


def fetch_user_by_id(user_id: str):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM customer_data WHERE customerid = %s;", (user_id,))
                user = cur.fetchone()
    except Exception as e:
        logging.exception(f"Exception while selecting data from database {e}")
    return user


@app.get("/")
def read_root(request: Request):
    logging.info("running root function")
    return templates.TemplateResponse("login.html",{"request":request})


@app.post("/api/login")
async def login(request: Request, name: str = Form(...), user_id: str = Form(...)):
    logging.info("Fetching data")
    user_id = user_id.strip()
    user = fetch_user_by_id(user_id=user_id)
    request.session['user'] = name
    request.session['user_id'] = user_id
    request.session['user_details'] = user
    if not user:
        logging.info("NO user found")
        return RedirectResponse(url="/", status_code=303)
    logging.info("redirect to chatbot")
    return RedirectResponse(url="/chatbot", status_code=303)


@app.get("/dashboard")
def dashboard(request: Request):
    user = request.session.get('user_id')
    name = request.session.get('user')
    if not user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})


@app.get("/chatbot")
def chatbot(request: Request):
    logging.info("log in to chatbot")
    user = request.session.get('user_id')
    name = request.session.get('user')
    if not user:
        logging.info("Login if you need to access chatbot.")
        return RedirectResponse(url="/")
    return templates.TemplateResponse("chatbot.html", {"request": request, "user_name": name, "message": conversation_history})


RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"

@app.post("/chat", response_class=JSONResponse)
async def post_chat(request: Request, message: str = Form(...)):
    logging.info("Connecting to Rasa server")

    conversation_history.append({"sender": "user", "text": message})

    try:
        user_id = request.session.get('user_id')
        payload = {"sender": user_id, "message": message}
        response = requests.post(RASA_SERVER_URL, json=payload, timeout=15)
        response.raise_for_status()
        bot_responses = response.json()
        print(bot_responses)
        extracted_responses = " ".join([msg["text"] for msg in bot_responses if "text" in msg])

    except requests.exceptions.RequestException as e:
        logging.exception(f"Could not send data to Rasa server: {e}")
        extracted_responses = "Could not process the request. Please try again."

    conversation_history.append({"sender": "bot", "text": extracted_responses})
    return JSONResponse({"message": extracted_responses})


if __name__ == "__main__":
    import uvicorn
    logging.info("Start app")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_config=None)
