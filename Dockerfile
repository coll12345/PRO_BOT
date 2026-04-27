# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project (including .session files)
COPY . .

# Expose port for health check
ENV PORT=8000
EXPOSE 8000

# Run the unified bot
CMD ["python", "main.py"]

