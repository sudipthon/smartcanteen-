# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set environment variables to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    &&pkg-config \
    &&build-essential \
    && pip install virtualenvwrapper poetry==1.4.2 \
    # libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ["poetry.lock", "pyproject.toml", "./"]
RUN poetry install --no-root



# Copy the Django project into the Docker image
COPY ./canteen/ .

# Expose the port the app runs on
EXPOSE 8000

COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh
