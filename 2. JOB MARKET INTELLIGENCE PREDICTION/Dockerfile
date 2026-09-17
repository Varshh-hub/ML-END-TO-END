FROM python:3.11-slim

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Don't buffer Python output
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first for Docker caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY app.py .
COPY job_market_model.pkl .
COPY web ./web

# Flask port
EXPOSE 5000

# Production server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]