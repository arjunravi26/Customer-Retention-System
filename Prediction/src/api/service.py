import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.logging import logging
from src.pipeline.prediction_pipeline import PredictionPipeline

app = FastAPI()

try:
    prediction_pipeline = PredictionPipeline('config.yaml')
    logging.info("PredictionPipeline initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize PredictionPipeline: {e}")
    prediction_pipeline = None
    raise

class CustomerData(BaseModel):
    Gender: str
    Senior_Citizen: str
    Partner: str
    Tenure_Months: int
    Phone_Service: str
    Internet_Service: str
    Online_Security: str
    Online_Backup: str
    Device_Protection: str
    Tech_Support: str
    Streaming_TV: str
    Streaming_Movies: str
    Contract: str
    Paperless_Billing: str
    Payment_Method: str
    Monthly_Charges: float
    Total_Charges: float
    CLTV: float

class ChurnPredictionResponse(BaseModel):
    churn_score: list

@app.post("/predict_churn", response_model=ChurnPredictionResponse)
async def predict_churn(customer_data: CustomerData):
    if prediction_pipeline is None:
        raise HTTPException(status_code=500, detail="Prediction pipeline not initialized")

    try:
        input_dict = customer_data.model_dump()
        input_df = pd.DataFrame([input_dict])
        logging.info(f"Raw input data: {input_df.to_dict(orient='records')}")

        input_df = input_df.rename(columns={
            'Senior_Citizen': 'Senior Citizen',
            'Tenure_Months': 'Tenure Months',
            'Phone_Service': 'Phone Service',
            'Internet_Service': 'Internet Service',
            'Online_Security': 'Online Security',
            'Online_Backup': 'Online Backup',
            'Device_Protection': 'Device Protection',
            'Tech_Support': 'Tech Support',
            'Streaming_TV': 'Streaming TV',
            'Streaming_Movies': 'Streaming Movies',
            'Paperless_Billing': 'Paperless Billing',
            'Payment_Method': 'Payment Method',
            'Monthly_Charges': 'Monthly Charges',
            'Total_Charges': 'Total Charges'
        })

        churn_score = prediction_pipeline.transform_predict(input_df)[0]
        logging.info(f"Predicted churn score: {churn_score}")
        return {"churn_score": churn_score}

    except Exception as e:
        logging.error(f"Prediction error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)