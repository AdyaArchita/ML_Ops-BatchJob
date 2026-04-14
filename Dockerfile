# Use python:3.9-slim as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the image
COPY . .

# Create empty files for outputs (optional, but good for clarity)
RUN touch metrics.json run.log

# Command to automatically run the batch job
CMD ["python", "run.py", "--input", "data.csv", "--config", "config.yaml", "--output", "metrics.json", "--log-file", "run.log"]
