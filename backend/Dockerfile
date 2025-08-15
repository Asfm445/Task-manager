FROM python:3.13-slim

WORKDIR /app

# Install system dependencies (required for bcrypt)
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure bcrypt is reinstalled correctly
RUN pip uninstall -y bcrypt && pip install --no-cache-dir bcrypt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]