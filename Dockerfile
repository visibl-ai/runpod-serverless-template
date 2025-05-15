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

# Install runtime dependencies (without development dependencies)
RUN poetry install --no-interaction --without dev --no-root

# Copy the template package and application files
COPY runpod_serverless_template runpod_serverless_template/
COPY examples examples/
COPY handler.py ./

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Start the handler
CMD ["python", "-u", "handler.py"]
