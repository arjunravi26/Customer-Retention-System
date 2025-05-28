# Use Python 3.11 slim base image
FROM python:3.11-slim

# Switch to root user for system package installation
USER root

# Install build dependencies for ML libraries (e.g., numpy, scipy)
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Update pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and model
COPY . .

# Expose FastAPI port
EXPOSE 8003

# Command to run FastAPI app
CMD ["uvicorn", "src.api.service:app", "--host", "0.0.0.0", "--port", "8003"]