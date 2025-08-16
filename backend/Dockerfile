# ===========================================
# Base image
# ===========================================
FROM python:3.13-slim-bookworm

# Prevents Python from writing .pyc files & ensures logs are flushed
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ===========================================
# System dependencies
# ===========================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ===========================================
# Set workdir
# ===========================================
WORKDIR /app

# ===========================================
# Install dependencies
# ===========================================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ===========================================
# Copy project
# ===========================================
COPY . .

# ===========================================
# Expose port & command
# ===========================================
EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
