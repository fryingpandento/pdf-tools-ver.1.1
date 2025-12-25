# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system dependencies (Poppler is required for pdf2image)
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set functionality directory
WORKDIR /app

# Copy requirement file first to leverage Docker cache
COPY requirements.txt /app/requirements.txt

# Install python dependencies
# Using --no-cache-dir to keep image small
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy the rest of the application
COPY . /app

# Expose port (Render sets PORT env)
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]
