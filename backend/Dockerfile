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

# Entry point script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ===========================================
# Production stage
# ===========================================
FROM base AS prod

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV ENVIRONMENT=production
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ===========================================
# Test stage
# ===========================================
FROM base AS test

RUN pip install --no-cache-dir pytest
ENTRYPOINT ["/entrypoint.sh"]
CMD ["pytest", "-v", "tests"]
