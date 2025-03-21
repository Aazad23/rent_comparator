# Use Python base image
FROM python:3.9-slim-buster

# Set working directory
WORKDIR /app
COPY config/properties.env /app/properties.env
# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app


RUN set -a && . /app/properties.env && set +a
# Expose port
EXPOSE 9090
# Run the FastAPI application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9090","--workers","1"]