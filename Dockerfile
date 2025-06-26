# Force building an "intel" image on a Mac with ARM64
# FROM --platform=linux/amd64 python:3.12-slim

# Use native architecture
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application
COPY . .

# Expose the port your app runs on
EXPOSE 8080

# Command to run the application
CMD ["flask", "run", "-p 8080",  "--host=0.0.0.0"]