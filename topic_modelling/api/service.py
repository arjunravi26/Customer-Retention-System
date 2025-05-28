from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from pydantic import BaseModel
from nmf import TextPreprocessor, TopicModelingPipeline
from logger import logging
app = FastAPI(title="Top2Vec Topic Modeling API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DocumentInput(BaseModel):
    documents: List[str]


class Topic(BaseModel):
    topic_id: int
    topic_name: str
    description: str
    frequency: int


class Results(BaseModel):
    topics: List[Topic]


results = None
preprocessor = TextPreprocessor()
pipeline = TopicModelingPipeline(n_topics=5)


@app.post("/process")
async def process_documents(input_data: DocumentInput):
    """Process documents and generate topic modeling results."""
    global results
    try:
        documents = input_data.documents
        if not documents:
            logging.info("No documents provided")
            raise HTTPException(
                status_code=400, detail="No documents provided")

        if any(not doc.strip() for doc in documents):
            logging.info("Some documents are empty")
            raise HTTPException(
                status_code=400, detail="Some documents are empty")

        _, cleaned = preprocessor.preprocess(documents)

        model = pipeline.fit_nmf(cleaned)
        results = pipeline.get_nmf_results()
        logging.info("Topic modeling completed")
        return {"status": "success", "message": "Topic modeling completed"}
    except Exception as e:
        logging.info(f"Error processing documents: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing documents: {str(e)}")


@app.get("/topics", response_model=List[Topic])
async def get_topics():
    """Get all topics with name, description, frequency, and mentions."""
    if not results or not results["topics"]:
        logging.info("No topics available. Run /process first.")
        raise HTTPException(
            status_code=404, detail="No topics available. Run /process first.")
    logging.info(f"send available topics")
    return JSONResponse(content=results["topics"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005,reload=True, log_config=None)

