FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright
RUN pip install playwright
RUN playwright install chromium
RUN playwright install-deps

# Install spaCy model
RUN python -m spacy download en_core_web_lg

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p data/resume data/reports data/logs

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "web_dashboard.app:app"]
