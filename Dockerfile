# Use Python 3.10 slim image for smaller size
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and other libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY data/ ./data/

# Create directories for models and outputs
RUN mkdir -p /app/models /data/videos /data/outputs

# Set up volume mounts
VOLUME ["/data/videos", "/data/outputs"]

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "src/main.py", "--video", "/data/videos/input.mp4", "--output", "/data/outputs"]
