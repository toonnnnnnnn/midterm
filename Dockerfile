# Use Debian as base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Expose port 5000 (as specified in the FastHTML app)
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
