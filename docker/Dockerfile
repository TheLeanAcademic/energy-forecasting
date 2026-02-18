FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY src/ src/
COPY configs/ configs/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create data and results directories
RUN mkdir -p /app/data /app/results

# Set entrypoint
ENTRYPOINT ["bench"]
