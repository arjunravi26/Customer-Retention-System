from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# In a production scenario, you would use sessions or a database to maintain conversation state.
# Here, we simulate conversation history with a simple in-memory list (reset on each page load).
conversation_history = []

RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"



@app.post("/chat", response_class=HTMLResponse)
async def post_chat(request: Request, message: str = Form(...)):
    global conversation_history

    # Append user's message to the conversation history.
    conversation_history.append({"sender": "user", "text": message})

    # Here you would send the user's message to your Rasa server.
    # For example:
    try:
        payload = {"sender": "user", "message": message}
        response = requests.post(RASA_SERVER_URL, json=payload)
        response.raise_for_status()
        print(f"{response.raise_for_status()}fsdaf")
        bot_responses = response.json()  # Expecting a list of messages
    except Exception as e:
        bot_responses = [{"text": "Sorry, I couldn't process your request."}]

    # Append bot responses to conversation history.
    for bot_msg in bot_responses:
        conversation_history.append({"sender": "bot", "text": bot_msg.get("text", "")})

    return templates.TemplateResponse("chatbot.html", {"request": request, "messages": conversation_history})
