# CFO Bot Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY cfobot/ ./cfobot/
COPY cfobot.py .
COPY pyproject.toml .

# Create non-root user for security
RUN groupadd -r cfobot && useradd -r -g cfobot cfobot
RUN chown -R cfobot:cfobot /app
USER cfobot

# Create downloads directory
RUN mkdir -p /home/cfobot/Downloads

# Set default command
CMD ["python", "cfobot.py"]
