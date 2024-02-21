FROM python:3.11-slim-buster

# Environment Variables
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app

# set working directory in container
WORKDIR /app

# Copy and install packages
COPY requirements.txt /app

# Install system packages required for compiling Python extensions
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "uvicorn[standard]" gunicorn

RUN pip install watchdog

# Run locally
CMD gunicorn --bind 0.0.0.0:8050 app:server

# # Run the web service on container startup, can specify more than one webworker if desired
# ENTRYPOINT gunicorn --bind :$PORT --log-level info --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 3 --timeout 
#0 app:app




