# ===========================================
# Base image
# ===========================================
FROM python:3.13-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# ===========================================
# Development stage
# ===========================================
FROM base AS dev

ENV ENVIRONMENT=development
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ===========================================
# Production stage
# ===========================================
FROM base AS prod

ENV ENVIRONMENT=production
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ===========================================
# Test stage
# ===========================================

