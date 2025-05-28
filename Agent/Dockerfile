FROM python:3.11-slim

# Switch to root user for system package installation
USER root

# Install build dependencies for tokenizers and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /

# Copy requirements file
COPY requirements.txt .

# Update pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8002

# Command to run FastAPI app
CMD ["uvicorn", "api.service:app", "--host", "0.0.0.0", "--port", "8002"]