# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker caching
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Set environment variable for Cloud Run port
ENV PORT 8080

# Expose port for Cloud Run health checks
EXPOSE 8080

# Run your main script
CMD ["python", "main.py"]
