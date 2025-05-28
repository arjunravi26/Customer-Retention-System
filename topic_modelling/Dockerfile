# Use Python 3.11 slim base image
FROM python:3.11-slim

# Switch to root user for system package installation
USER root

# Install build dependencies for Top2Vec dependencies (numpy, scipy, umap-learn, hdbscan)
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Update pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm


# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8004

# Command to run FastAPI app
CMD ["uvicorn", "api.service:app", "--host", "0.0.0.0", "--port", "8004"]


# # Use a prebuilt image with PyTorch (CPU version) to avoid heavy torch installation time
# FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime


# # Set environment variables to prevent Python from writing .pyc files and using buffered output
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# # Set the working directory
# WORKDIR /

# # Install system dependencies needed for Top2Vec and related libraries
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     g++ \
#     libopenblas-dev \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# # Upgrade pip and install Python dependencies using wheels (faster, avoids source builds)
# COPY requirements.txt .
# RUN pip install --upgrade pip setuptools wheel
# RUN pip install --prefer-binary -r requirements.txt
# RUN python -m spacy download en_core_web_sm


# # Copy the rest of the application code
# COPY . .

# # Expose the port FastAPI will run on
# EXPOSE 8004

# # Run the FastAPI application with uvicorn
# CMD ["uvicorn", "api.service:app", "--host", "0.0.0.0", "--port", "8004"]


# # ── Stage 1: Build wheels (including CPU-only PyTorch) ──