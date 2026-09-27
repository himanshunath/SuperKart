# Lightweight Python base image
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the Streamlit app
COPY . .

# Streamlit listens on port 8501
EXPOSE 8501

# Run Streamlit headless, reachable from outside the container
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]
