# Use a minimal Python image
FROM python:3.11-slim

# Set environment variables to prevent Python from buffering output and to ensure utf-8
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies (includes libsqlite3.so.0)
RUN apt-get update && apt-get install -y \
    libsqlite3-0 \
    sqlite3 \
    curl \
    git \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy and install Python dependencies
RUN pip install uv

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/entrypoint.sh

EXPOSE 8080

# Single fixed entrypoint, no CMD needed
ENTRYPOINT ["/app/entrypoint.sh"]
