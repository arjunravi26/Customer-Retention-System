FROM python:3.11-slim

WORKDIR /

RUN apt-get update && apt-get install -y gcc

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./ ./

RUN mkdir -p /logs && chmod -R 777 /logs

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
