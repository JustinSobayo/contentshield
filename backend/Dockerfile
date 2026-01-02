# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from the context root (which will be 'backend/')
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Expose port (Railway overrides this with $PORT)
EXPOSE 8000

# Start application using uvicorn
# We use the shell form to ensure $PORT expansion
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
