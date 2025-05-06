FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Setup environment
ENV PYTHONPATH=/app
WORKDIR /app/backend

# Run the app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]