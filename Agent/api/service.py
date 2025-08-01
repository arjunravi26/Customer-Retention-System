# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from offer_write_agent import generate_offer_letter
from logger import logging
app = FastAPI(title="Customer Retention API", description="API to generate personalized retention offer letters", version="1.0.0")

class CustomerRequest(BaseModel):
    customer_id: str

@app.post("/generate_offer")
def generate_offer(request: CustomerRequest):
    try:
        result = generate_offer_letter(request.customer_id)
        return result
    except Exception as e:
        logging.info(f"Error in email generation {e}")
        raise HTTPException(status_code=500, detail=str(e))
