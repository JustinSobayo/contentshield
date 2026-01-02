# Use Python 3.10 slim image for smaller size
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# ffmpeg: for video processing
# curl: for healthchecks
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY backend/ .

# Expose port (Railway overrides this with $PORT)
EXPOSE 8000

# Command to run the application (using uvicorn)
# Use $PORT environment variable for Railway compatibility
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
