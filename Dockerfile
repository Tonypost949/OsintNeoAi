# Dockerfile for Render.com deployment
# This is a template. Adjust based on your backend language (Python, Node.js, Kotlin, etc.)

# Example for a Python/FastAPI backend:
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Render defaults to port 10000
EXPOSE 10000
ENV PORT=10000

# Start command (Example: FastAPI)
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]

# Placeholder: Simple python server
CMD ["python", "-m", "http.server", "10000"]
