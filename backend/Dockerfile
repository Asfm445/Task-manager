FROM python:3.13-slim

# Set working directory inside the container
WORKDIR /app

# Copy everything from current directory to /app
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port for FastAPI
EXPOSE 8001

# Command to run FastAPI
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
