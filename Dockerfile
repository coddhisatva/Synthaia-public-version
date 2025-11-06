FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    fluidsynth \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Expose port
EXPOSE 10000

# Start command
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "10000"]

