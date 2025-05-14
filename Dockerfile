# Use the official Python image as a base
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Set environment variables
ENV WORKERS=4
ENV TIMEOUT=60

# Command to run the application (gunicorn is recommended for production)
# CMD ["flask", "run", "--host=0.0.0.0"]
CMD ["bash", "-c", "gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--workers", "$WORKERS", "--timeout", "$TIMEOUT"]

# Use the following command to build the Docker image
# docker build -t font-proxy .
# or for multi-arch
# docker buildx build --platform linux/amd64,linux/arm64 -t font-proxy .
