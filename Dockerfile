FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy poetry configuration and README
COPY pyproject.toml poetry.lock* README.md ./

# Configure poetry to not use a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies (without development dependencies)
RUN poetry install --no-interaction --without dev --no-root

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Start the handler
CMD ["python", "-u", "handler.py"]
