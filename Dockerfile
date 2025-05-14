# Stage 1: Build stage
FROM python:3.11-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev build-essential && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Stage 2: Final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
